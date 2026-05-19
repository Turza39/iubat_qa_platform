from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import or_, func

from database import get_db
from models.user import User
from models.tag import Tag
from models.question import Question
from models.answer import Answer
from models.vote import Vote
from schemas.question import (
    QuestionListSchema,
    QuestionCreateSchema,
    QuestionUpdateSchema,
    TagListSchema
)
from dependencies.auth import get_current_user
from utils.password import create_slug
from config import settings
from utils.redis_cache import get_cached_json, set_cached_json, delete_pattern
from utils.tasks import publish_activity_event

router = APIRouter(prefix="/api/questions", tags=["questions"])


def resolve_tags(db: Session, tag_names: list[str]) -> list[Tag]:
    """
    Resolve tag names or legacy numeric tag IDs to Tag objects.
    Use a single query for existing tags and create missing tags.
    """
    if not tag_names:
        return []

    if len(tag_names) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can add a maximum of 5 tags."
        )

    cleaned_slugs = []
    slug_to_name = {}
    tag_ids = []
    unique_ids = set()

    for tag_name in tag_names:
        if tag_name is None:
            continue

        raw_value = str(tag_name).strip()
        if not raw_value or len(raw_value) > 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name must be between 1 and 50 characters."
            )

        if raw_value.isdigit():
            tag_id = int(raw_value)
            if tag_id not in unique_ids:
                unique_ids.add(tag_id)
                tag_ids.append(tag_id)
            continue

        slug = create_slug(raw_value)
        if slug not in slug_to_name:
            cleaned_slugs.append(slug)
            slug_to_name[slug] = raw_value

    conditions = []
    if cleaned_slugs:
        conditions.append(Tag.slug.in_(cleaned_slugs))
    if tag_ids:
        conditions.append(Tag.id.in_(tag_ids))

    existing_tags = []
    if conditions:
        existing_tags = db.query(Tag).filter(or_(*conditions)).all()

    existing_slug_map = {tag.slug: tag for tag in existing_tags}
    existing_id_map = {tag.id: tag for tag in existing_tags}

    result_tags = []

    for tag_id in tag_ids:
        if tag_id not in existing_id_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tag ID: {tag_id}"
            )
        result_tags.append(existing_id_map[tag_id])

    for slug in cleaned_slugs:
        if slug in existing_slug_map:
            result_tags.append(existing_slug_map[slug])
        else:
            new_tag = Tag(name=slug_to_name[slug], slug=slug)
            db.add(new_tag)
            db.flush()
            result_tags.append(new_tag)

    return result_tags


@router.get("/tags/", response_model=list[TagListSchema])
async def list_tags(db: Session = Depends(get_db)):
    cache_key = "tags:list"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return cached

    tags = db.query(Tag).order_by(Tag.name.asc()).all()
    response = [
        {"id": tag.id, "name": tag.name, "slug": tag.slug}
        for tag in tags
    ]
    await set_cached_json(cache_key, response, settings.CACHE_TTL_TAGS)
    return response


@router.get("/", response_model=list[QuestionListSchema])
async def list_questions(
    search: str = Query(None, description="Search in title or body"),
    tag: str = Query(None, description="Filter by tag slug"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Optimized:
    - eager loads author and tags
    - bulk counts votes/answers
    - avoids len(q.votes), len(q.answers)
    """
    cache_key = f"questions:list:search={search or ''}:tag={tag or ''}:skip={skip}:limit={limit}"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return cached

    query = db.query(Question).options(
        joinedload(Question.author),
        selectinload(Question.tags)
    )

    if search:
        query = query.filter(
            or_(
                Question.title.ilike(f"%{search}%"),
                Question.body.ilike(f"%{search}%")
            )
        )

    if tag:
        query = query.join(Question.tags).filter(Tag.slug == tag)

    questions = (
        query.order_by(Question.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    question_ids = [q.id for q in questions]

    vote_counts = {}
    answer_counts = {}

    if question_ids:
        vote_rows = (
            db.query(Vote.question_id, func.count(Vote.id))
            .filter(Vote.question_id.in_(question_ids))
            .group_by(Vote.question_id)
            .all()
        )
        vote_counts = {question_id: count for question_id, count in vote_rows}

        answer_rows = (
            db.query(Answer.question_id, func.count(Answer.id))
            .filter(Answer.question_id.in_(question_ids))
            .group_by(Answer.question_id)
            .all()
        )
        answer_counts = {question_id: count for question_id, count in answer_rows}

    result = []
    for q in questions:
        result.append({
            "id": q.id,
            "title": q.title,
            "author": {
                "id": q.author.id,
                "username": q.author.username,
                "verification_status": q.author.verification_status,
            },
            "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in q.tags],
            "upvote_count": vote_counts.get(q.id, 0),
            "answer_count": answer_counts.get(q.id, 0),
            "created_at": q.created_at,
        })

    await set_cached_json(cache_key, result, settings.CACHE_TTL_QUESTION_LIST)
    return result


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tags = resolve_tags(db, question_data.tags or [])

    question = Question(
        title=question_data.title,
        body=question_data.body,
        author_id=current_user.id
    )

    if tags:
        question.tags = tags

    db.add(question)
    db.commit()
    db.refresh(question)

    await delete_pattern("questions:list:*")
    await delete_pattern("question:detail:*")
    await delete_pattern("answers:list:*")
    publish_activity_event.delay("question.created", {
        "question_id": question.id,
        "author_id": current_user.id,
    })

    return {
        "id": question.id,
        "title": question.title,
        "body": question.body,
        "author": {
            "id": question.author.id,
            "username": question.author.username,
        },
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in question.tags],
        "upvote_count": 0,
        "answer_count": 0,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }


@router.get("/{question_id}/")
async def get_question_detail(
    question_id: int,
    answer_skip: int = Query(0, ge=0),
    answer_limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Important change:
    - answers are now paginated
    - avoids returning all answers for huge questions
    """
    question = (
        db.query(Question)
        .options(
            joinedload(Question.author),
            selectinload(Question.tags)
        )
        .filter(Question.id == question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )

    cache_key = f"question:detail:{question_id}:skip={answer_skip}:limit={answer_limit}"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return cached

    answers = (
        db.query(Answer)
        .options(joinedload(Answer.author))
        .filter(Answer.question_id == question_id)
        .order_by(Answer.created_at.desc())
        .offset(answer_skip)
        .limit(answer_limit)
        .all()
    )

    total_answer_count = (
        db.query(func.count(Answer.id))
        .filter(Answer.question_id == question_id)
        .scalar() or 0
    )

    question_vote_count = (
        db.query(func.count(Vote.id))
        .filter(Vote.question_id == question_id)
        .scalar() or 0
    )

    answer_ids = [a.id for a in answers]
    answer_vote_counts = {}

    if answer_ids:
        answer_vote_rows = (
            db.query(Vote.answer_id, func.count(Vote.id))
            .filter(Vote.answer_id.in_(answer_ids))
            .group_by(Vote.answer_id)
            .all()
        )
        answer_vote_counts = {answer_id: count for answer_id, count in answer_vote_rows}

    answer_list = []
    for answer in answers:
        answer_list.append({
            "id": answer.id,
            "body": answer.body,
            "question": answer.question_id,
            "author": {
                "id": answer.author.id,
                "username": answer.author.username,
            },
            "upvote_count": answer_vote_counts.get(answer.id, 0),
            "created_at": answer.created_at,
            "updated_at": answer.updated_at,
        })

    question_data = {
        "id": question.id,
        "title": question.title,
        "body": question.body,
        "author": {
            "id": question.author.id,
            "username": question.author.username,
        },
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in question.tags],
        "upvote_count": question_vote_count,
        "answer_count": total_answer_count,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }

    response = {
        "question": question_data,
        "answers": answer_list,
        "answers_pagination": {
            "skip": answer_skip,
            "limit": answer_limit,
            "returned": len(answer_list),
            "total": total_answer_count,
        }
    }
    await set_cached_json(cache_key, response, settings.CACHE_TTL_QUESTION_DETAIL)
    return response


@router.put("/{question_id}/")
async def update_question(
    question_id: int,
    question_data: QuestionUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = (
        db.query(Question)
        .options(joinedload(Question.author), selectinload(Question.tags))
        .filter(Question.id == question_id)
        .first()
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )

    if question.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own questions."
        )

    if question_data.title is not None:
        question.title = question_data.title

    if question_data.body is not None:
        question.body = question_data.body

    if question_data.tags is not None:
        question.tags = resolve_tags(db, question_data.tags)

    db.commit()
    db.refresh(question)

    await delete_pattern("questions:list:*")
    await delete_pattern("question:detail:*")
    await delete_pattern("answers:list:*")
    publish_activity_event.delay("question.updated", {
        "question_id": question.id,
        "author_id": current_user.id,
    })

    upvote_count = (
        db.query(func.count(Vote.id))
        .filter(Vote.question_id == question.id)
        .scalar() or 0
    )

    answer_count = (
        db.query(func.count(Answer.id))
        .filter(Answer.question_id == question.id)
        .scalar() or 0
    )

    return {
        "id": question.id,
        "title": question.title,
        "body": question.body,
        "author": {
            "id": question.author.id,
            "username": question.author.username,
        },
        "tags": [{"id": t.id, "name": t.name, "slug": t.slug} for t in question.tags],
        "upvote_count": upvote_count,
        "answer_count": answer_count,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }


@router.delete("/{question_id}/")
async def delete_question(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )

    if question.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own questions."
        )

    db.delete(question)
    db.commit()

    await delete_pattern("questions:list:*")
    await delete_pattern("question:detail:*")
    await delete_pattern("answers:list:*")
    publish_activity_event.delay("question.deleted", {
        "question_id": question_id,
        "author_id": current_user.id,
    })

    return {"detail": "Question deleted successfully."}
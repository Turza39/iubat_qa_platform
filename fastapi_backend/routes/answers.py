from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from database import get_db
from models.user import User
from models.answer import Answer
from models.question import Question
from models.vote import Vote
from schemas.answer import AnswerCreateSchema, AnswerUpdateSchema
from dependencies.auth import get_verified_user

router = APIRouter(prefix="/api/answers", tags=["answers"])


@router.post("/questions/{question_id}/")
async def post_answer(
    question_id: int,
    answer_data: AnswerCreateSchema,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )

    answer = Answer(
        body=answer_data.body,
        question_id=question_id,
        author_id=current_user.id
    )

    db.add(answer)
    db.commit()
    db.refresh(answer)

    return {
        "id": answer.id,
        "body": answer.body,
        "question": answer.question_id,
        "author": {
            "id": answer.author.id,
            "username": answer.author.username,
        },
        "upvote_count": 0,
        "created_at": answer.created_at,
        "updated_at": answer.updated_at,
    }


@router.get("/questions/{question_id}/")
async def get_answers(
    question_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found."
        )

    answers = (
        db.query(Answer)
        .options(joinedload(Answer.author))
        .filter(Answer.question_id == question_id)
        .order_by(Answer.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    answer_ids = [a.id for a in answers]
    vote_counts = {}

    if answer_ids:
        vote_rows = (
            db.query(Vote.answer_id, func.count(Vote.id))
            .filter(Vote.answer_id.in_(answer_ids))
            .group_by(Vote.answer_id)
            .all()
        )
        vote_counts = {answer_id: count for answer_id, count in vote_rows}

    result = []
    for answer in answers:
        result.append({
            "id": answer.id,
            "body": answer.body,
            "question": answer.question_id,
            "author": {
                "id": answer.author.id,
                "username": answer.author.username,
            },
            "upvote_count": vote_counts.get(answer.id, 0),
            "created_at": answer.created_at,
            "updated_at": answer.updated_at,
        })

    return result


@router.put("/questions/{question_id}/")
async def update_answer(
    question_id: int,
    answer_data: AnswerUpdateSchema,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    answer = (
        db.query(Answer)
        .options(joinedload(Answer.author))
        .filter(
            Answer.question_id == question_id,
            Answer.author_id == current_user.id
        )
        .first()
    )

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found."
        )

    answer.body = answer_data.body
    db.commit()
    db.refresh(answer)

    upvote_count = (
        db.query(func.count(Vote.id))
        .filter(Vote.answer_id == answer.id)
        .scalar() or 0
    )

    return {
        "id": answer.id,
        "body": answer.body,
        "question": answer.question_id,
        "author": {
            "id": answer.author.id,
            "username": answer.author.username,
        },
        "upvote_count": upvote_count,
        "created_at": answer.created_at,
        "updated_at": answer.updated_at,
    }


@router.delete("/questions/{question_id}/")
async def delete_answer(
    question_id: int,
    current_user: User = Depends(get_verified_user),
    db: Session = Depends(get_db)
):
    answer = db.query(Answer).filter(
        Answer.question_id == question_id,
        Answer.author_id == current_user.id
    ).first()

    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found."
        )

    db.delete(answer)
    db.commit()

    return {"detail": "Answer deleted successfully"}
"""
Vote endpoints for upvoting questions and answers.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models.user import User
from models.question import Question
from models.answer import Answer
from models.vote import Vote
from schemas.vote import VoteSchema, VoteToggleResponseSchema, VoteStatsSchema
from dependencies.auth import get_current_user
from config import settings
from utils.redis_cache import get_cached_json, set_cached_json, delete_pattern
from utils.tasks import publish_activity_event

router = APIRouter(prefix="/api/votes", tags=["votes"])


# ============================================================================
# Question Vote Endpoints
# ============================================================================

@router.post(
    "/questions/{question_id}/",
    response_model=VoteToggleResponseSchema,
    summary="Toggle upvote on a question",
    responses={
        200: {"description": "Vote toggled successfully"},
        400: {"description": "Cannot vote on own question"},
        401: {"description": "Not authenticated"},
        404: {"description": "Question not found"},
    }
)
async def toggle_question_vote(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle upvote on a question.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    - Cannot vote on your own question
    
    **Behavior:**
    - If user has already voted: removes the vote
    - If user hasn't voted: adds the vote
    
    **Response:**
    - message: "Vote added" or "Vote removed"
    - upvote_count: Updated upvote count for the question
    - voted: Whether user currently has voted
    """
    # Get question
    question = db.query(Question).filter(Question.id == question_id).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user is the author
    if question.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot vote on your own question"
        )
    
    # Check if vote already exists
    existing_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.question_id == question_id
    ).first()
    
    if existing_vote:
        # Remove vote
        db.delete(existing_vote)
        db.commit()
        
        # Get updated upvote count
        upvote_count = db.query(func.count(Vote.id)).filter(
            Vote.question_id == question_id
        ).scalar() or 0
        
        await delete_pattern("questions:list:*")
        await delete_pattern("question:detail:*")
        await delete_pattern("votes:stats")
        publish_activity_event.delay("question.vote.toggled", {
            "question_id": question_id,
            "user_id": current_user.id,
            "action": "removed",
        })

        return VoteToggleResponseSchema(
            message="Vote removed",
            upvote_count=upvote_count,
            voted=False
        )
    else:
        # Add vote
        new_vote = Vote(
            user_id=current_user.id,
            question_id=question_id
        )
        db.add(new_vote)
        db.commit()
        
        # Get updated upvote count
        upvote_count = db.query(func.count(Vote.id)).filter(
            Vote.question_id == question_id
        ).scalar() or 0
        
        await delete_pattern("questions:list:*")
        await delete_pattern("question:detail:*")
        await delete_pattern("votes:stats")
        publish_activity_event.delay("question.vote.toggled", {
            "question_id": question_id,
            "user_id": current_user.id,
            "action": "added",
        })

        return VoteToggleResponseSchema(
            message="Vote added",
            upvote_count=upvote_count,
            voted=True
        )


# ============================================================================
# Answer Vote Endpoints
# ============================================================================

@router.post(
    "/answers/{answer_id}/",
    response_model=VoteToggleResponseSchema,
    summary="Toggle upvote on an answer",
    responses={
        200: {"description": "Vote toggled successfully"},
        400: {"description": "Cannot vote on own answer"},
        401: {"description": "Not authenticated"},
        404: {"description": "Answer not found"},
    }
)
async def toggle_answer_vote(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle upvote on an answer.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    - Cannot vote on your own answer
    
    **Behavior:**
    - If user has already voted: removes the vote
    - If user hasn't voted: adds the vote
    
    **Response:**
    - message: "Vote added" or "Vote removed"
    - upvote_count: Updated upvote count for the answer
    - voted: Whether user currently has voted
    """
    # Get answer
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    
    # Check if user is the author
    if answer.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot vote on your own answer"
        )
    
    # Check if vote already exists
    existing_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.answer_id == answer_id
    ).first()
    
    if existing_vote:
        # Remove vote
        db.delete(existing_vote)
        db.commit()
        
        # Get updated upvote count
        upvote_count = db.query(func.count(Vote.id)).filter(
            Vote.answer_id == answer_id
        ).scalar() or 0
        
        await delete_pattern("answers:list:*")
        await delete_pattern("question:detail:*")
        await delete_pattern("votes:stats")
        publish_activity_event.delay("answer.vote.toggled", {
            "answer_id": answer_id,
            "user_id": current_user.id,
            "action": "removed",
        })
        
        return VoteToggleResponseSchema(
            message="Vote removed",
            upvote_count=upvote_count,
            voted=False
        )
    else:
        # Add vote
        new_vote = Vote(
            user_id=current_user.id,
            answer_id=answer_id
        )
        db.add(new_vote)
        db.commit()
        
        # Get updated upvote count
        upvote_count = db.query(func.count(Vote.id)).filter(
            Vote.answer_id == answer_id
        ).scalar() or 0
        
        await delete_pattern("answers:list:*")
        await delete_pattern("question:detail:*")
        await delete_pattern("votes:stats")
        publish_activity_event.delay("answer.vote.toggled", {
            "answer_id": answer_id,
            "user_id": current_user.id,
            "action": "added",
        })
        
        return VoteToggleResponseSchema(
            message="Vote added",
            upvote_count=upvote_count,
            voted=True
        )


# ============================================================================
# Vote Stats Endpoints
# ============================================================================

@router.get(
    "/stats/",
    response_model=VoteStatsSchema,
    summary="Get vote statistics",
    responses={
        200: {"description": "Statistics retrieved successfully"},
    }
)
async def get_vote_stats(db: Session = Depends(get_db)):
    """
    Get overall vote statistics.
    
    **Response:**
    - total_votes: Total number of votes in the system
    - total_question_votes: Total votes on questions
    - total_answer_votes: Total votes on answers
    """
    cache_key = "votes:stats"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return cached

    total_votes = db.query(func.count(Vote.id)).scalar() or 0
    
    total_question_votes = db.query(func.count(Vote.id)).filter(
        Vote.question_id.isnot(None)
    ).scalar() or 0
    
    total_answer_votes = db.query(func.count(Vote.id)).filter(
        Vote.answer_id.isnot(None)
    ).scalar() or 0
    
    response = VoteStatsSchema(
        total_votes=total_votes,
        total_question_votes=total_question_votes,
        total_answer_votes=total_answer_votes
    )
    await set_cached_json(cache_key, response.dict(), settings.CACHE_TTL_VOTE_STATS)
    return response


# ============================================================================
# Check User Vote Status
# ============================================================================

@router.get(
    "/question/{question_id}/status/",
    response_model=dict,
    summary="Check if user voted on a question",
    responses={
        200: {"description": "Vote status retrieved"},
        401: {"description": "Not authenticated"},
        404: {"description": "Question not found"},
    }
)
async def check_question_vote_status(
    question_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if the current user has voted on a specific question.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    
    **Response:**
    - voted: Boolean indicating if user has voted
    - upvote_count: Total upvote count for the question
    """
    # Check if question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Check if user voted
    user_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.question_id == question_id
    ).first()
    
    # Get upvote count
    upvote_count = db.query(func.count(Vote.id)).filter(
        Vote.question_id == question_id
    ).scalar() or 0
    
    return {
        "voted": user_vote is not None,
        "upvote_count": upvote_count
    }


@router.get(
    "/answer/{answer_id}/status/",
    response_model=dict,
    summary="Check if user voted on an answer",
    responses={
        200: {"description": "Vote status retrieved"},
        401: {"description": "Not authenticated"},
        404: {"description": "Answer not found"},
    }
)
async def check_answer_vote_status(
    answer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if the current user has voted on a specific answer.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    
    **Response:**
    - voted: Boolean indicating if user has voted
    - upvote_count: Total upvote count for the answer
    """
    # Check if answer exists
    answer = db.query(Answer).filter(Answer.id == answer_id).first()
    if not answer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Answer not found"
        )
    
    # Check if user voted
    user_vote = db.query(Vote).filter(
        Vote.user_id == current_user.id,
        Vote.answer_id == answer_id
    ).first()
    
    # Get upvote count
    upvote_count = db.query(func.count(Vote.id)).filter(
        Vote.answer_id == answer_id
    ).scalar() or 0
    
    return {
        "voted": user_vote is not None,
        "upvote_count": upvote_count
    }

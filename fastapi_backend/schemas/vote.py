from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class VoteSchema(BaseModel):
    """Vote response schema"""
    id: int
    user_id: int
    question_id: Optional[int] = None
    answer_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class VoteToggleResponseSchema(BaseModel):
    """Response for vote toggle operations"""
    message: str = Field(..., description="Action message (Vote added/removed)")
    upvote_count: int = Field(..., description="Updated upvote count")
    voted: bool = Field(..., description="Whether user has voted or not")
    
    class Config:
        from_attributes = True


class VoteStatsSchema(BaseModel):
    """Statistics for votes"""
    total_votes: int = Field(..., description="Total number of votes")
    total_question_votes: int = Field(..., description="Total votes on questions")
    total_answer_votes: int = Field(..., description="Total votes on answers")
    
    class Config:
        from_attributes = True

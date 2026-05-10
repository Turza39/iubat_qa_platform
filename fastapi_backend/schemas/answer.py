from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from schemas.user import UserPublicSchema


class AnswerCreateSchema(BaseModel):
    body: str = Field(..., max_length=5000)
    question: int
    
    class Config:
        from_attributes = True


class AnswerSchema(BaseModel):
    id: int
    body: str
    question: int
    author: UserPublicSchema
    upvote_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnswerUpdateSchema(BaseModel):
    body: str = Field(..., max_length=5000)
    
    class Config:
        from_attributes = True

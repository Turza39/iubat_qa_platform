from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from schemas.user import UserPublicSchema
from schemas.tag import TagSchema


class QuestionListSchema(BaseModel):
    """
    Lightweight schema for question lists (home page, profile page).
    
    Equivalent to Django's QuestionListSerializer.
    """
    id: int
    title: str
    author: UserPublicSchema
    tags: List[TagSchema]
    upvote_count: int
    answer_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionDetailSchema(BaseModel):
    """
    Full schema for the question detail page.
    
    Equivalent to Django's QuestionDetailSerializer.
    """
    id: int
    title: str
    body: str
    author: UserPublicSchema
    tags: List[TagSchema]
    upvote_count: int
    answer_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QuestionCreateSchema(BaseModel):
    """Schema for creating a new question"""
    title: str = Field(..., min_length=5, max_length=200)
    body: str = Field(..., min_length=10, max_length=5000)
    tags: Optional[List[str]] = Field(default=[], max_items=5, description="Tag names (will be created if they don't exist)")
    
    class Config:
        from_attributes = True


class QuestionUpdateSchema(BaseModel):
    """Schema for updating a question"""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    body: Optional[str] = Field(None, min_length=10, max_length=5000)
    tags: Optional[List[str]] = Field(None, max_items=5, description="Tag names (will be created if they don't exist)")
    
    class Config:
        from_attributes = True


class QuestionWithAnswersSchema(BaseModel):
    """Schema for question with its answers"""
    question: QuestionDetailSchema
    answers: List = []  # Will be populated with answer data


class TagListSchema(BaseModel):
    """Schema for tag list response"""
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True

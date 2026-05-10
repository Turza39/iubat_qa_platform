from pydantic import BaseModel
from typing import Optional


class TagSchema(BaseModel):
    """
    Tag schema for question categorization.
    
    Equivalent to Django's TagSerializer.
    """
    id: int
    name: str
    slug: str
    
    class Config:
        from_attributes = True


class TagCreateSchema(BaseModel):
    """Schema for creating a new tag"""
    name: str
    slug: str


class TagUpdateSchema(BaseModel):
    """Schema for updating a tag"""
    name: Optional[str] = None
    slug: Optional[str] = None

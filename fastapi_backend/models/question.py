from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from models.tag import question_tags


class Question(Base):
    """
    Question model for the IUBAT QA Platform.
    
    Equivalent to Django's Question model in questions app.
    """
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), index=True, nullable=False)
    body = Column(Text, nullable=False)  # max_length: 5000 (validation in schema)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table arguments with indexes
    __table_args__ = (
        Index('ix_questions_author_id', 'author_id'),
    )
    
    # Relationships
    author = relationship("User", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="question", cascade="all, delete-orphan")
    tags = relationship(
        "Tag",
        secondary=question_tags,
        backref="questions"
    )
    
    def __repr__(self):
        return f"<Question(id={self.id}, title={self.title}, author_id={self.author_id})>"
    
    def __str__(self):
        return self.title

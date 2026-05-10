from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Answer(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, index=True)
    body = Column(Text)  # max_length equivalent is handled at serializer level
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Table arguments with indexes
    __table_args__ = (
        Index('ix_answers_author_id', 'author_id'),
        Index('ix_answers_created_at', 'created_at'),
        Index('ix_answers_question_id', 'question_id'),
        Index('ix_answers_question_author', 'question_id', 'author_id'),
    )
    
    # Relationships
    question = relationship("Question", back_populates="answers")
    author = relationship("User", back_populates="answers")
    votes = relationship("Vote", back_populates="answer", cascade="all, delete-orphan")
    
    def __str__(self):
        return f'Answer by {self.author.username} on {self.question.title}'

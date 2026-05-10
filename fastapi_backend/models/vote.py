from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Vote(Base):
    """
    Vote model for upvoting questions and answers.
    
    Equivalent to Django's Vote model. Users can upvote questions or answers.
    Each user can only vote once per question/answer (toggle).
    """
    __tablename__ = "votes"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=True, index=True)
    answer_id = Column(Integer, ForeignKey("answers.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="votes")
    answer = relationship("Answer", back_populates="votes")
    question = relationship("Question", back_populates="votes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'question_id', name='unique_vote_per_user_per_question'),
        UniqueConstraint('user_id', 'answer_id', name='unique_vote_per_user_per_answer'),
    )
    
    def __repr__(self):
        if self.question_id:
            return f"<Vote(user_id={self.user_id}, question_id={self.question_id})>"
        return f"<Vote(user_id={self.user_id}, answer_id={self.answer_id})>"
    
    def __str__(self):
        if self.question_id:
            return f"User {self.user_id} voted on question {self.question_id}"
        return f"User {self.user_id} voted on answer {self.answer_id}"

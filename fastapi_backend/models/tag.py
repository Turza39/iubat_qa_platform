from sqlalchemy import Column, Integer, String, Table, ForeignKey
from database import Base

# Association table for many-to-many relationship between Question and Tag
question_tags = Table(
    'question_tags',
    Base.metadata,
    Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


class Tag(Base):
    """
    Tag model for categorizing questions.
    
    Equivalent to Django's Tag model in questions app.
    """
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    
    def __repr__(self):
        return f"<Tag(id={self.id}, name={self.name}, slug={self.slug})>"
    
    def __str__(self):
        return self.name

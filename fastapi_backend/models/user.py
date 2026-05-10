from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class VerificationStatus(str, enum.Enum):
    """Equivalent to Django's choices for verification_status"""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class VerificationRequestStatus(str, enum.Enum):
    """Status for verification requests"""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class User(Base):
    """
    Custom User model - Maps to Django's User model in the database.
    
    This model matches the existing PostgreSQL schema created by Django's
    authentication system, ensuring compatibility with the existing database.
    """
    __tablename__ = "users"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # User Information (from Django's AbstractBaseUser)
    username = Column(String(150), unique=True, index=True, nullable=False)
    email = Column(String(254), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Django uses 'password', not 'password_hash'
    
    # Verification Status
    verification_status = Column(
        String(20),
        default="unverified",
        nullable=False
    )
    
    # Django User Fields
    is_active = Column(Boolean, default=True, nullable=False)
    is_staff = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    date_joined = Column(DateTime, nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    answers = relationship(
        "Answer",
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys="Answer.author_id"
    )
    questions = relationship(
        "Question",
        back_populates="author",
        cascade="all, delete-orphan",
        foreign_keys="Question.author_id"
    )
    votes = relationship(
        "Vote",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    verification_request = relationship(
        "VerificationRequest",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    @property
    def is_verified(self):
        """Computed property: True if verification_status is 'verified'"""
        return self.verification_status == "verified"
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, is_verified={self.is_verified})>"
    
    def __str__(self):
        return self.username


class VerificationRequest(Base):
    """
    Verification request model (equivalent to Django's VerificationRequest)
    
    Stores user ID verification submissions with status tracking.
    """
    __tablename__ = "verification_requests"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Data
    image_path = Column(String(255), nullable=False)  # Path to uploaded verification image
    status = Column(
        String(20),
        default=VerificationRequestStatus.PENDING,
        nullable=False
    )
    
    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="verification_request")
    
    def __repr__(self):
        return f"<VerificationRequest(user_id={self.user_id}, status={self.status})>"
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"


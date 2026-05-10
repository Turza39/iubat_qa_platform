from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class VerificationStatusEnum(str, Enum):
    unverified = "unverified"
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


# ============================================================================
# Registration & Login Schemas
# ============================================================================

class RegisterSchema(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=150, description="Unique username")
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    confirm_password: str = Field(..., description="Password confirmation")
    
    class Config:
        from_attributes = True


class LoginSchema(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    
    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    """Schema for JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        from_attributes = True


class TokenRefreshSchema(BaseModel):
    """Schema for token refresh request"""
    refresh_token: str = Field(..., description="Refresh token")
    
    class Config:
        from_attributes = True


# ============================================================================
# User Profile Schemas
# ============================================================================

class UserPublicSchema(BaseModel):
    """Public user information (safe to expose)"""
    id: int
    username: str
    verification_status: VerificationStatusEnum
    
    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    """Complete user information"""
    id: int
    username: str
    email: str
    is_verified: bool
    verification_status: VerificationStatusEnum
    date_joined: datetime
    is_active: bool = True
    is_staff: bool = False
    
    class Config:
        from_attributes = True


class UserCreateSchema(BaseModel):
    """Schema for creating a user"""
    username: str = Field(..., min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserUpdateSchema(BaseModel):
    """Schema for updating user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=150)
    email: Optional[EmailStr] = None
    current_password: Optional[str] = Field(None, description="Required if changing username/email")
    
    class Config:
        from_attributes = True


class UserProfileSchema(BaseModel):
    """Complete user profile with all details"""
    id: int
    username: str
    email: str
    is_verified: bool
    verification_status: VerificationStatusEnum
    date_joined: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    is_staff: bool = False
    
    class Config:
        from_attributes = True


# ============================================================================
# Verification Schemas
# ============================================================================

class VerificationRequestStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"


class VerificationRequestSchema(BaseModel):
    """Schema for verification request"""
    id: int
    user_id: int
    status: VerificationRequestStatus
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VerificationSubmitSchema(BaseModel):
    """Schema for submitting verification image"""
    image: str = Field(..., description="Base64 encoded image or file path")
    
    class Config:
        from_attributes = True

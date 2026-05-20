"""
User endpoints for registration, authentication, profile, and verification.
"""
from fastapi import APIRouter, HTTPException, status, Depends, File, UploadFile
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import Optional
import os
import re
from datetime import datetime

from database import get_db
from models.user import User, VerificationRequest
from models.question import Question
from models.answer import Answer
from models.vote import Vote
from schemas.user import (
    RegisterSchema,
    LoginSchema,
    TokenSchema,
    UserSchema,
    UserProfileSchema,
    UserUpdateSchema,
    VerificationRequestSchema,
    VerificationSubmitSchema,
    UserPublicSchema,
)
from dependencies.auth import (
    get_current_user,
    get_verified_user,
    create_tokens,
    verify_token,
)
from utils.password import hash_password, verify_password
from config import settings
from utils.redis_cache import get_cached_json, set_cached_json
from utils.tasks import send_welcome_email, process_verification_request
from utils.supabase_utils import upload_to_supabase, delete_from_supabase, is_supabase_configured

router = APIRouter(prefix="/api/users", tags=["users"])


# ============================================================================
# Registration & Authentication Endpoints
# ============================================================================

@router.post(
    "/register/",
    response_model=TokenSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    responses={
        201: {"description": "Account created successfully with auth token"},
        400: {"description": "Invalid input or email/username already exists"},
    }
)
async def register(
    data: RegisterSchema,
    db: Session = Depends(get_db)
):
    """
    Register a new user account and automatically log in.
    
    **Requirements:**
    - Username must be 3-150 characters
    - Email must be valid and unique
    - Password must be at least 6 characters
    - Passwords must match
    
    **Response:**
    - 201: User created successfully with JWT token for automatic login
    - 400: Validation error (duplicate email/username, mismatched passwords)
    """
    # Validate passwords match
    if data.password != data.confirm_password:
        print(f"❌ Registration failed: Passwords do not match")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == data.email).first()
    if existing_email:
        print(f"❌ Registration failed: Email '{data.email}' already registered")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == data.username).first()
    if existing_username:
        print(f"❌ Registration failed: Username '{data.username}' already taken")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken"
        )
    
    try:
        # Create new user
        user = User(
            username=data.username,
            email=data.email,
            password=hash_password(data.password),
            date_joined=datetime.utcnow(),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Registration successful: User '{user.username}' (ID: {user.id})")
        
        # Auto-login: Generate tokens for the new user
        tokens = create_tokens(user.id)
        print(f"✅ Auto-login: Generated JWT token for user '{user.username}'")

        # Email service disabled - no welcome email
        # send_welcome_email.delay(user.email, user.username)
        
        return TokenSchema(**tokens)
    except IntegrityError as e:
        db.rollback()
        print(f"❌ Registration failed: Database integrity error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating account. Email or username may already exist"
        )
    except Exception as e:
        db.rollback()
        print(f"❌ Registration failed: Unexpected error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error creating account. Please try again."
        )


@router.post(
    "/login/",
    response_model=TokenSchema,
    summary="Login with email and password",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        404: {"description": "User not found"},
    }
)
async def login(
    data: LoginSchema,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token.
    
    **Requirements:**
    - Valid email address
    - Correct password
    
    **Response:**
    - access_token: JWT token for authenticated requests
    - token_type: Always "bearer"
    - expires_in: Token expiration time in seconds
    """
    # Find user by email
    user = db.query(User).filter(User.email == data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify password
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Generate tokens
    tokens = create_tokens(user.id)
    
    return TokenSchema(**tokens)


# ============================================================================
# User Profile Endpoints
# ============================================================================

@router.get(
    "/profile/",
    response_model=UserProfileSchema,
    summary="Get current user's profile",
    responses={
        200: {"description": "Profile retrieved successfully"},
        401: {"description": "Not authenticated"},
    }
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current authenticated user's profile information.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    
    **Response:**
    - User profile with all details
    """
    try:
        print(f"✅ Profile endpoint called for user: {current_user.username} (ID: {current_user.id})")

        user = (
            db.query(User)
            .options(
                selectinload(User.questions).selectinload(Question.tags)
            )
            .filter(User.id == current_user.id)
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        question_ids = [question.id for question in user.questions]
        vote_counts = {}
        answer_counts = {}

        if question_ids:
            vote_rows = (
                db.query(Vote.question_id, func.count(Vote.id))
                .filter(Vote.question_id.in_(question_ids))
                .group_by(Vote.question_id)
                .all()
            )
            vote_counts = {question_id: count for question_id, count in vote_rows}

            answer_rows = (
                db.query(Answer.question_id, func.count(Answer.id))
                .filter(Answer.question_id.in_(question_ids))
                .group_by(Answer.question_id)
                .all()
            )
            answer_counts = {question_id: count for question_id, count in answer_rows}

        questions_data = []
        for question in user.questions:
            questions_data.append({
                "id": question.id,
                "title": question.title,
                "author": {
                    "id": question.author.id,
                    "username": question.author.username,
                    "verification_status": question.author.verification_status,
                },
                "tags": [
                    {"id": tag.id, "name": tag.name, "slug": tag.slug}
                    for tag in question.tags
                ],
                "upvote_count": vote_counts.get(question.id, 0),
                "answer_count": answer_counts.get(question.id, 0),
                "created_at": question.created_at,
            })

        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "verification_status": user.verification_status,
            "date_joined": user.date_joined,
            "last_login": user.last_login,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "questions": questions_data,
        }

        print(f"✅ Profile loaded with {len(questions_data)} questions")
        return UserProfileSchema.model_validate(user_data)
    except Exception as e:
        print(f"❌ Error in profile endpoint: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve profile: {str(e)}"
        )


@router.put(
    "/profile/",
    response_model=UserProfileSchema,
    summary="Update user profile",
    responses={
        200: {"description": "Profile updated successfully"},
        400: {"description": "Invalid input or duplicate email/username"},
        401: {"description": "Not authenticated"},
    }
)
async def update_profile(
    data: UserUpdateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile information.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    - If changing username/email: must provide current password
    
    **Fields:**
    - username: New username (optional)
    - email: New email (optional)
    - current_password: Required if changing username or email
    
    **Response:**
    - 200: Updated profile
    - 400: Validation failed (duplicate email/username, wrong password)
    """
    # Check if username or email is being changed
    username_changed = data.username and data.username != current_user.username
    email_changed = data.email and data.email != current_user.email
    
    # If changing username or email, require password verification
    if (username_changed or email_changed) and not data.current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please enter your current password to save changes"
        )
    
    # Verify current password if needed
    if (username_changed or email_changed):
        if not verify_password(data.current_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password"
            )
    
    # Check for duplicate username
    if username_changed:
        if db.query(User).filter(
            User.username == data.username,
            User.id != current_user.id
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is already taken"
            )
        current_user.username = data.username
    
    # Check for duplicate email
    if email_changed:
        if db.query(User).filter(
            User.email == data.email,
            User.id != current_user.id
        ).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email is already in use"
            )
        current_user.email = data.email
    
    # Update timestamp
    current_user.updated_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(current_user)
        return UserProfileSchema.from_orm(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error updating profile"
        )


# ============================================================================
# User Verification Endpoints
# ============================================================================

@router.get(
    "/verify/",
    response_model=dict,
    summary="Check verification status",
    responses={
        200: {"description": "Verification status retrieved"},
        401: {"description": "Not authenticated"},
    }
)
async def check_verification_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check the current user's verification status.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    
    **Response:**
    - verification_status: Current status (unverified, pending, verified, rejected)
    - verification_request: Details of verification request if exists
    """
    verification = db.query(VerificationRequest).filter(
        VerificationRequest.user_id == current_user.id
    ).first()
    
    if verification:
        return {
            "verification_status": current_user.verification_status,
            "verification_request": VerificationRequestSchema.from_orm(verification),
        }
    else:
        return {
            "verification_status": current_user.verification_status,
            "verification_request": None,
        }


@router.post(
    "/verify/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Submit verification image",
    responses={
        201: {"description": "Verification request submitted"},
        400: {"description": "User already verified or request pending"},
        401: {"description": "Not authenticated"},
        422: {"description": "No file provided"},
    }
)
async def submit_verification(
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(None),
    id_card_image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Submit an ID verification image.
    
    **Requirements:**
    - Valid JWT token in Authorization header
    - Image file (jpeg, png, jpg, gif, webp)
    - User must not be already verified
    
    **Response:**
    - 201: Verification request submitted successfully
    - 400: User already verified or request already pending
    - 422: Invalid file type or no file provided
    """
    # Check verification status
    if current_user.verification_status == "verified":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already verified"
        )
    
    if current_user.verification_status == "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your verification request is already under review"
        )
    
    # Validate file type and extension
    allowed_mimetypes = {
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".doc", ".docx"}

    # Frontend sends the file under the field name `id_card_image`.
    upload_file = id_card_image or file
    if upload_file is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No file provided"
        )

    filename = upload_file.filename or "upload"
    _, ext = os.path.splitext(filename.lower())

    if upload_file.content_type not in allowed_mimetypes or ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only image (jpg/png/gif/webp), PDF, and DOC/DOCX files are allowed"
        )

    # Enforce maximum upload size (5 MiB)
    MAX_FILE_SIZE = 5 * 1024 * 1024
    contents = await upload_file.read()
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No file provided or file is empty"
        )
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Uploaded file is too large (max 5 MiB)"
        )
    
    try:
        # Check if Supabase is configured
        if is_supabase_configured():
            # Upload to Supabase
            file_url = await upload_to_supabase(
                file_content=contents,
                filename=filename,
                content_type=upload_file.content_type,
                folder=f"user_{current_user.id}"
            )
            image_path = file_url
        else:
            # Fallback to local file storage
            media_dir = os.path.join(settings.MEDIA_ROOT, "verification_images")
            os.makedirs(media_dir, exist_ok=True)
            
            safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(filename))
            timestamp = int(datetime.utcnow().timestamp())
            file_path = os.path.join(media_dir, f"{current_user.id}_{timestamp}_{safe_name}")

            with open(file_path, "wb") as f:
                f.write(contents)
            image_path = file_path
        
        # Create or update verification request using SQLAlchemy
        verification = db.query(VerificationRequest).filter(
            VerificationRequest.user_id == current_user.id
        ).first()
        
        if verification:
            # Delete old file from Supabase if exists
            if is_supabase_configured() and verification.image_path:
                try:
                    await delete_from_supabase(verification.image_path)
                except Exception:
                    pass  # Ignore deletion errors
            
            # Update existing verification request
            verification.image_path = image_path
            verification.status = "pending"
            verification.submitted_at = datetime.utcnow()
        else:
            # Create new verification request
            verification = VerificationRequest(
                user_id=current_user.id,
                image_path=image_path,
                status="pending",
            )
            db.add(verification)
        
        # Update user verification status to pending
        current_user.verification_status = "pending"
        
        db.commit()
        db.refresh(verification)

        process_verification_request.delay(current_user.id, verification.id)
        
        return {
            "message": "Verification request submitted successfully",
            "submitted_at": verification.submitted_at,
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error submitting verification: {str(e)}"
        )


# ============================================================================
# Public User Endpoints
# ============================================================================

@router.get(
    "/{user_id}/",
    response_model=UserPublicSchema,
    summary="Get public user information",
    responses={
        200: {"description": "User found"},
        404: {"description": "User not found"},
    }
)
async def get_user_public(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Get public information about a user.
    
    **Public fields:**
    - id: User ID
    - username: Username
    - verification_status: Verification status
    
    **Parameters:**
    - user_id: The user's ID
    """
    cache_key = f"user:public:{user_id}"
    cached = await get_cached_json(cache_key)
    if cached is not None:
        return cached

    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    response = UserPublicSchema.from_orm(user).dict()
    await set_cached_json(cache_key, response, settings.CACHE_TTL_USER_PUBLIC)
    return response

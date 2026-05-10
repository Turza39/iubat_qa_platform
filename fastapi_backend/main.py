from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routes import answers_router, questions_router, users_router, votes_router
from models import User, Question, Answer, Vote, Tag, VerificationRequest
from config import settings
import os

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="IUBAT QA Platform API",
    description="FastAPI backend for IUBAT QA Platform",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create media and static directories if they don't exist
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
os.makedirs(settings.STATIC_ROOT, exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STATIC_ROOT), name="static")

# Mount media files
app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")

# Include routers
app.include_router(users_router)
app.include_router(answers_router)
app.include_router(questions_router)
app.include_router(votes_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "IUBAT QA Platform API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "timezone": settings.TIMEZONE
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

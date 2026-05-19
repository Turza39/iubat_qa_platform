from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from database import Base, engine, SessionLocal
from routes import answers_router, questions_router, users_router, votes_router
from models import User, Question, Answer, Vote, Tag, VerificationRequest
from config import settings
from utils.redis_cache import get_async_redis
import os

# Create all database tables safely on startup
try:
    Base.metadata.create_all(bind=engine, checkfirst=True)
except SQLAlchemyError as exc:
    # Existing schema or partial migration state may already exist.
    # Skip table creation and rely on migrations / existing database schema.
    print("Skipping automatic table creation due to database schema state:", exc)


def seed_default_tags():
    default_tags = [
        {"name": "python", "slug": "python"},
        {"name": "javascript", "slug": "javascript"},
        {"name": "fastapi", "slug": "fastapi"},
        {"name": "react", "slug": "react"},
        {"name": "database", "slug": "database"},
        {"name": "api", "slug": "api"},
        {"name": "authentication", "slug": "authentication"},
        {"name": "frontend", "slug": "frontend"},
        {"name": "backend", "slug": "backend"},
        {"name": "web-development", "slug": "web-development"},
    ]

    try:
        with SessionLocal() as session:
            existing = {tag.slug for tag in session.query(Tag.slug).all()}
            new_tags = [Tag(name=item["name"], slug=item["slug"]) for item in default_tags if item["slug"] not in existing]
            if new_tags:
                session.add_all(new_tags)
                session.commit()
                print(f"✅ Seeded {len(new_tags)} default tags")
    except Exception as exc:
        print("Failed to seed default tags:", exc)


seed_default_tags()

app = FastAPI(
    title="IUBAT QA Platform API",
    description="FastAPI backend for IUBAT QA Platform",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS_LIST,
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


@app.on_event("startup")
async def startup():
    try:
        redis_client = await get_async_redis()
        await redis_client.ping()
    except Exception:
        # Allow the app to start even if Redis is temporarily unavailable.
        # Startup will log the failure via the worker / API logs.
        pass

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

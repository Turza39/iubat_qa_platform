from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import SessionLocal
from routes import answers_router, questions_router, users_router, votes_router
from models import Tag
from config import settings
from utils.redis_cache import get_async_redis
from utils.rate_limit import RateLimitMiddleware
import os


# =========================
# SEED FUNCTION (SAFE VERSION)
# =========================
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
            existing = {
                row[0] for row in session.query(Tag.slug).all()
            }

            new_tags = [
                Tag(name=t["name"], slug=t["slug"])
                for t in default_tags
                if t["slug"] not in existing
            ]

            if new_tags:
                session.add_all(new_tags)
                session.commit()
                print(f"✅ Seeded {len(new_tags)} default tags")

    except Exception as exc:
        print("⚠️ Tag seeding skipped:", exc)


# =========================
# FASTAPI APP
# =========================
app = FastAPI(
    title="IUBAT QA Platform API",
    description="FastAPI backend for IUBAT QA Platform",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
app.add_middleware(RateLimitMiddleware)

# Media folder
# os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
# app.mount("/media", StaticFiles(directory=settings.MEDIA_ROOT), name="media")


# =========================
# STARTUP EVENT
# =========================
@app.on_event("startup")
async def startup():
    # Redis health check (non-blocking)
    try:
        redis_client = await get_async_redis()
        await redis_client.ping()
    except Exception:
        print("⚠️ Redis not available at startup (continuing anyway)")


# =========================
# ROUTES
# =========================
app.include_router(users_router)
app.include_router(answers_router)
app.include_router(questions_router)
app.include_router(votes_router)


# =========================
# ROOT
# =========================
@app.get("/")
async def root():
    return {
        "message": "IUBAT QA Platform API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "managed_by_alembic",
        "timezone": settings.TIMEZONE
    }


# =========================
# DEV RUN
# =========================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
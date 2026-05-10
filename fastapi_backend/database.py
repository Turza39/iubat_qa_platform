from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Construct database URL based on configuration
database_url = settings.DATABASE_URL

# Create engine with appropriate parameters
if "sqlite" in database_url:
    # SQLite-specific parameters
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False}
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        database_url,
        pool_size=30,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using them
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Database session dependency for FastAPI.
    
    Usage:
        @app.get("/items/")
        async def read_items(db: Session = Depends(get_db)):
            items = db.query(Item).all()
            return items
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


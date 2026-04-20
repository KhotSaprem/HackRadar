import os
import hashlib
from datetime import datetime
from typing import AsyncGenerator
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

# Base class for SQLAlchemy models
Base = declarative_base()


class Hackathon(Base):
    """Hackathon model for storing hackathon data."""
    __tablename__ = "hackathons"
    
    id = Column(String, primary_key=True)  # MD5 hash of source + URL
    title = Column(Text, nullable=False)
    source = Column(Text, nullable=False, index=True)
    url = Column(Text, nullable=False)
    image_url = Column(Text)
    description = Column(Text)
    prize_pool = Column(Text)
    location = Column(Text)
    mode = Column(Text)  # online|offline|hybrid
    tags = Column(Text)  # JSON array stored as string
    team_size_min = Column(Integer)
    team_size_max = Column(Integer)
    registration_deadline = Column(DateTime)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String, default="upcoming", index=True)  # upcoming|ongoing|past
    scraped_at = Column(DateTime, default=func.now())


class PlannerItem(Base):
    """Planner item model for user scheduling."""
    __tablename__ = "planner"
    
    id = Column(String, primary_key=True)
    hackathon_id = Column(String, nullable=False)  # References hackathons.id
    session_id = Column(String, nullable=False)  # localStorage UUID
    title = Column(Text, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    description = Column(Text)
    type = Column(String)  # idea|build|submit|sleep|review|meeting
    color = Column(String)
    created_at = Column(DateTime, default=func.now())


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # UUID
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    is_admin = Column(Integer, default=0)   # 1 for admin, 0 for regular user
    created_at = Column(DateTime, default=func.now())
    last_login = Column(DateTime)


# Database configuration
def get_database_url() -> str:
    """Get database URL based on environment."""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Fix postgres:// to postgresql+asyncpg://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif database_url.startswith("postgresql://"):
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        
        # Remove unsupported parameters for asyncpg
        import re
        # Remove sslmode, channel_binding, and other unsupported params
        database_url = re.sub(r'[?&]sslmode=[^&]*', '', database_url)
        database_url = re.sub(r'[?&]channel_binding=[^&]*', '', database_url)
        # Clean up any trailing ? or &
        database_url = re.sub(r'[?&]$', '', database_url)
        
        return database_url
    else:
        # Development SQLite database
        return "sqlite+aiosqlite:///./hackradar.db"


# Create async engine
def create_engine_with_config():
    """Create engine with proper configuration."""
    db_url = get_database_url()
    
    # Configure engine based on database type
    if db_url.startswith("postgresql"):
        # PostgreSQL with asyncpg - SSL is handled via connect_args
        return create_async_engine(
            db_url,
            echo=False,
            future=True,
            connect_args={
                "ssl": "require"  # Enable SSL for production databases
            }
        )
    else:
        # SQLite
        return create_async_engine(
            db_url,
            echo=False,
            future=True
        )


engine = create_engine_with_config()

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_database():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session for dependency injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def generate_hackathon_id(source: str, url: str) -> str:
    """Generate unique hackathon ID using MD5 hash of source + URL."""
    combined = f"{source}:{url}"
    return hashlib.md5(combined.encode()).hexdigest()


def compute_hackathon_status(start_date: datetime, end_date: datetime) -> str:
    """Compute hackathon status based on current date."""
    now = datetime.utcnow()
    
    if now < start_date:
        return "upcoming"
    elif start_date <= now <= end_date:
        return "ongoing"
    else:
        return "past"
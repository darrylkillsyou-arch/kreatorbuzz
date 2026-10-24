"""Database connection and session configuration supporting SQLite and Supabase / PostgreSQL."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

raw_db_url = settings.DATABASE_URL or "sqlite:///./maccall.db"

# Format PostgreSQL url for SQLAlchemy with psycopg2 driver compatibility
if raw_db_url.startswith("postgres://"):
    db_url = raw_db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif raw_db_url.startswith("postgresql://") and not raw_db_url.startswith("postgresql+"):
    db_url = raw_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
else:
    db_url = raw_db_url

# Serverless runtime safety (e.g., Vercel Lambda where root filesystem is read-only)
if db_url.startswith("sqlite") and os.environ.get("VERCEL") and "/tmp" not in db_url:
    db_url = "sqlite:////tmp/maccall.db"

engine_kwargs = {
    "echo": False,
}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL / Neon / Supabase serverless production configuration
    from sqlalchemy.pool import NullPool
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(db_url, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for obtaining database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

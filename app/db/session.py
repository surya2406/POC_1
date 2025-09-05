from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.settings import get_settings

settings = get_settings()

DATABASE_URL = settings.DB_URL
print("DATABASE URL:", DATABASE_URL)

Base = declarative_base()

# Create synchronous engine
sync_engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

def get_engine():
    """Return the synchronous engine."""
    return sync_engine

def dispose_engine():
    """Dispose of the engine to close all connections."""
    sync_engine.dispose()

# Singleton sessionmaker
_sync_sessionmaker = None

def get_sync_sessionmaker():
    """Return a singleton sync sessionmaker bound to the sync engine."""
    global _sync_sessionmaker
    if _sync_sessionmaker is None:
        _sync_sessionmaker = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=sync_engine,
            class_=Session
        )
    return _sync_sessionmaker

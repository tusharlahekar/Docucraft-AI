import logging
import socket
from typing import Generator
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings, BASE_DIR

logger = logging.getLogger(__name__)

Base = declarative_base()

def is_database_reachable(url: str) -> bool:
    """Probes host/port with a 0.2s socket timeout to immediately detect PostgreSQL availability."""
    if not url or "sqlite" in url:
        return True
    try:
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        if host == "localhost":
            host = "127.0.0.1"
        port = parsed.port or 5432
        with socket.create_connection((host, port), timeout=0.2):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

clean_postgres_url = settings.DATABASE_URL.replace("+asyncpg", "")
clean_sqlite_url = f"sqlite:///{BASE_DIR / 'platform.db'}"

if is_database_reachable(clean_postgres_url) and "postgres" in clean_postgres_url:
    target_url = clean_postgres_url
    connect_args = {}
else:
    target_url = clean_sqlite_url
    connect_args = {"check_same_thread": False}

active_engine = create_engine(
    target_url,
    echo=False,
    future=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=active_engine
)

def init_db():
    """Initializes all table schemas on startup with automatic fallback if PostgreSQL errors."""
    global active_engine, SessionLocal
    import backend.app.models.entities
    try:
        Base.metadata.create_all(bind=active_engine)
        logger.info(f"Database schemas verified successfully using {active_engine.url.drivername}.")
    except Exception as exc:
        logger.warning(f"Primary database connection failed ({exc}). Switching to SQLite fallback engine...")
        fallback_url = clean_sqlite_url
        active_engine = create_engine(
            fallback_url,
            echo=False,
            future=True,
            connect_args={"check_same_thread": False}
        )
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=active_engine
        )
        Base.metadata.create_all(bind=active_engine)
        logger.info("Database schemas initialized successfully using SQLite fallback.")

def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

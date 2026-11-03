import logging
import socket
from typing import Generator
from urllib.parse import urlparse
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from backend.app.core.config import settings

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

# Convert asyncpg scheme to psycopg2 for synchronous engine if present
clean_postgres_url = settings.DATABASE_URL.replace("+asyncpg", "")
clean_sqlite_url = settings.SQLITE_FALLBACK_URL.replace("+aiosqlite", "")

if is_database_reachable(clean_postgres_url):
    logger.info("PostgreSQL host is reachable. Using PostgreSQL engine.")
    target_url = clean_postgres_url
    connect_args = {}
else:
    logger.info("PostgreSQL not active locally. Utilizing instant SQLite engine fallback.")
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
    """Initializes all table schemas on startup."""
    import backend.app.models.entities  # Ensure models are registered on Base.metadata
    Base.metadata.create_all(bind=active_engine)
    logger.info(f"Database schemas verified successfully using {active_engine.url.drivername}.")

def get_db() -> Generator[Session, None, None]:
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

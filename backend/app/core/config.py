import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise AI Chatbot & Document Generation Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # Security
    SECRET_KEY: str = "antigravity_master_secret_key_change_in_production_9f82b7c61d5e"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/document_ai")
    SQLITE_FALLBACK_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'platform.db'}"
    
    # Local LLM (Ollama)
    ENABLE_OLLAMA: bool = os.getenv("ENABLE_OLLAMA", "false").lower() in ("true", "1", "yes")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:latest")
    OLLAMA_TIMEOUT_SECONDS: int = 60
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = str(BASE_DIR / "chroma_data")
    CHROMA_COLLECTION_NAME: str = "document_rag_collection"
    
    # Storage
    STORAGE_DIR: str = str(BASE_DIR / "storage")
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    GENERATED_DIR: str = str(BASE_DIR / "storage" / "generated")
    MAX_UPLOAD_SIZE_MB: int = 50
    
    # Web Research
    SEARCH_ENGINE: str = "duckduckgo"
    MAX_SEARCH_RESULTS: int = 5
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure storage directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.GENERATED_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

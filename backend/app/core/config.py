import os
import json
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings

# Root directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "ExamForge"
    API_V1_STR: str = "/api/v1"
    PORT: int = 8000
    HOST: str = "127.0.0.1"
    ENVIRONMENT: str = "development"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, tuple)):
            return list(v)
        return []
    
    # Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR / 'data' / 'examforge.db'}"
    
    # Storage
    STORAGE_UPLOADS_DIR: Path = BASE_DIR / "storage" / "uploads"
    STORAGE_EXPORTS_DIR: Path = BASE_DIR / "storage" / "exports"
    MAX_UPLOAD_SIZE_MB: int = 15

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if v and v.startswith("sqlite:///./"):
            rel_path = v.replace("sqlite:///./", "")
            return f"sqlite:///{BASE_DIR / rel_path}"
        return v or f"sqlite:///{BASE_DIR / 'data' / 'examforge.db'}"

    @field_validator("STORAGE_UPLOADS_DIR", "STORAGE_EXPORTS_DIR", mode="before")
    @classmethod
    def assemble_storage_path(cls, v: Union[str, Path]) -> Path:
        if isinstance(v, str):
            if v.startswith("./"):
                return BASE_DIR / v[2:]
            return Path(v)
        return v
    
    class Config:
        env_file = str(BACKEND_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
settings.STORAGE_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
settings.STORAGE_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
(BASE_DIR / "data").mkdir(parents=True, exist_ok=True)

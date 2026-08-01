import os
from typing import List
from pathlib import Path


def _load_env_file() -> None:
    candidates = []
    # Prefer the backend/.env when the app is launched from backend/
    candidates.append(Path(__file__).resolve().parents[2] / ".env")
    # Also try the workspace root .env as a fallback
    candidates.append(Path(__file__).resolve().parents[3] / ".env")

    for env_path in candidates:
        if not env_path.exists():
            continue
        with open(env_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
                elif key:
                    os.environ[key] = value


_load_env_file()


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "SDSI Knowledge Base")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./sdsi.db"
    )

    OPENAI_API_KEY: str = os.getenv(
        "OPENAI_API_KEY",
        ""
    )

    ALLOWED_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
        if origin.strip()
    ]

    UPLOAD_DIR: str = os.getenv(
        "UPLOAD_DIR",
        "uploads"
    )


settings = Settings()

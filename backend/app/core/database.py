import sys
from pathlib import Path

# Allows the bundled development interpreter to load dependencies installed
# locally in backend/.deps. Standard virtual environments use site-packages.
LOCAL_DEPENDENCIES = Path(__file__).resolve().parents[2] / ".deps"
if LOCAL_DEPENDENCIES.is_dir() and str(LOCAL_DEPENDENCIES) not in sys.path:
    sys.path.insert(0, str(LOCAL_DEPENDENCIES))

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


# ============================
# Database Connection
# ============================

engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)


# ============================
# Session Database
# ============================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ============================
# Base pour les modèles
# ============================

Base = declarative_base()


# ============================
# Dependency utilisée dans FastAPI
# ============================

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

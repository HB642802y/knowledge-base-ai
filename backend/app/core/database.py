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

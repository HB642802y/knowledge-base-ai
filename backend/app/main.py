from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from sqlalchemy import inspect, text

from .api.admin import router as admin_router
from .api.auth import router as auth_router
from .api.categories import router as categories_router
from .api.chat import router as chat_router
from .api.documents import router as documents_router
from .api.forum import router as forum_router
from .api.stats import router as stats_router
from .api.users import router as users_router
from .core.config import settings
from .core.database import Base, SessionLocal, engine
from .core.security import hash_password
from . import models
from .models.user import User

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")


def ensure_document_author_columns() -> None:
    inspector = inspect(engine)
    if "documents" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("documents")}
    required_columns = {
        "uploaded_by_id": "INTEGER",
        "uploaded_by_name": "VARCHAR",
        "uploaded_by_email": "VARCHAR",
    }

    with engine.begin() as connection:
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE documents ADD COLUMN {column_name} {column_type}"))


def ensure_initial_admin() -> None:
    if not settings.INITIAL_ADMIN_PASSWORD:
        return

    email = settings.INITIAL_ADMIN_EMAIL.strip().lower()
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == email).first()
        if admin:
            admin.full_name = settings.INITIAL_ADMIN_FULL_NAME.strip() or admin.full_name
            admin.password_hash = hash_password(settings.INITIAL_ADMIN_PASSWORD)
            db.commit()
            return

        db.add(
            User(
                email=email,
                full_name=settings.INITIAL_ADMIN_FULL_NAME.strip() or "Admin SDSI",
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
            )
        )
        db.commit()
    finally:
        db.close()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_document_author_columns()
    ensure_initial_admin()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(categories_router, prefix=settings.API_V1_STR)
app.include_router(chat_router, prefix=settings.API_V1_STR)
app.include_router(forum_router, prefix=settings.API_V1_STR)
app.include_router(stats_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.get("/")
def root():
    return {"message": "SDSI knowledge base API is ready"}

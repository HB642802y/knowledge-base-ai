from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from .api.admin import router as admin_router
from .api.auth import router as auth_router
from .api.categories import router as categories_router
from .api.chat import router as chat_router
from .api.documents import router as documents_router
from .api.forum import router as forum_router
from .api.users import router as users_router
from .core.config import settings
from .core.database import Base, SessionLocal, engine
from .services.user_service import migrate_users_table, seed_users

import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)
migrate_users_table()

_db = SessionLocal()
try:
    seed_users(_db)
finally:
    _db.close()

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0")

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
app.include_router(admin_router, prefix=settings.API_V1_STR)
app.include_router(forum_router, prefix=settings.API_V1_STR)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}


@app.get("/")
def root():
    return {
        "message": "Base de connaissances — Ministère de l'Agriculture, de la Pêche Maritime, du Développement Rural et des Eaux et Forêts"
    }

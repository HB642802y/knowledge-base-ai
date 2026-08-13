from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.forum import ForumQuestion
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "documents"


@router.get("/stats")
def admin_stats(db: Session = Depends(get_db)):
    doc_count = len(
        [
            p
            for p in UPLOAD_DIR.iterdir()
            if p.is_file()
        ]
    ) if UPLOAD_DIR.exists() else 0

    return {
        "documents": doc_count,
        "users": db.query(User).count(),
        "conversations": db.query(ForumQuestion).count(),
    }

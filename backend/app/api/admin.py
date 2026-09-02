from fastapi import APIRouter, Depends, Header
from sqlalchemy import func
from sqlalchemy.orm import Session

from .users import admin_user
from ..core.database import get_db
from ..models.document import Document
from ..models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def admin_stats(
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    admin_user(x_user_email, db)

    doc_count = db.query(func.count(func.distinct(Document.title))).scalar() or 0
    user_count = db.query(User).count()

    from ..models.conversation import Conversation
    question_count = db.query(Conversation).count()
    
    return {"documents": doc_count, "users": user_count, "conversations": question_count}

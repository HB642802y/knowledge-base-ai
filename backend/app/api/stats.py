from fastapi import APIRouter, Depends, Header
from sqlalchemy import func
from sqlalchemy.orm import Session

from .users import current_user
from ..core.database import get_db
from ..models.conversation import Conversation
from ..models.document import Document
from ..models.message import Message

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/collaborator")
def collaborator_stats(
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    current_user(x_user_email, db)

    doc_count = db.query(func.count(func.distinct(Document.title))).scalar() or 0
    question_count = db.query(Conversation).count()
    comment_count = db.query(Message).filter(Message.role == "comment").count()
    passages_count = doc_count * 30
    source_rate = 87 if doc_count > 0 else 0

    return {
        "documents": doc_count,
        "passages": passages_count,
        "questions": question_count,
        "answers": comment_count,
        "source_rate": source_rate,
        "recent_documents": get_recent_documents(db),
        "recent_activity": get_recent_activity(db),
    }


def get_recent_documents(db: Session):
    documents = db.query(Document).order_by(Document.created_at.desc(), Document.id.desc()).all()
    docs = []
    seen_titles = set()
    for document in documents:
        if document.title in seen_titles:
            continue
        seen_titles.add(document.title)
        suffix = document.title.rsplit(".", 1)[-1] if "." in document.title else "DOC"
        docs.append(
            {
                "id": document.id,
                "name": document.title,
                "size": document.source,
                "type": suffix.upper(),
                "indexed": True,
                "uploaded_by_name": document.uploaded_by_name,
                "uploaded_by_email": document.uploaded_by_email,
            }
        )
        if len(docs) >= 5:
            break
    return docs


def get_recent_activity(db: Session):
    activities = []
    documents = db.query(Document).order_by(Document.created_at.desc(), Document.id.desc()).all()
    seen_titles = set()
    for document in documents:
        if document.title in seen_titles:
            continue
        seen_titles.add(document.title)
        activities.append(
            {
                "action": "upload",
                "description": f"Document ajoute : {document.title}",
                "actor": document.uploaded_by_name or "System",
                "time": "recemment",
            }
        )
        if len(activities) >= 3:
            break

    questions = db.query(Conversation).order_by(Conversation.created_at.desc(), Conversation.id.desc()).limit(2).all()
    for question in questions:
        activities.append(
            {
                "action": "question",
                "description": f"Question posee : {question.title}",
                "actor": question.author_name or "Collaborateur",
                "time": "recemment",
            }
        )

    return activities[:5]

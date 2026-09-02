from pathlib import Path
import shutil

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .users import current_user
from ..core.database import get_db
from ..models.document import Document
from ..services.document_service import sync_documents_from_disk

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "documents"
UPLOAD_DIR.mkdir(exist_ok=True)


class DocumentOut(BaseModel):
    id: int
    title: str
    source: str
    uploaded_by_name: str | None = None
    uploaded_by_email: str | None = None
    can_delete: bool = False


def serialize_document(document: Document, user: dict) -> dict:
    uploaded_by_email = (document.uploaded_by_email or "").strip().lower() or None
    user_email = (user.get("email") or "").strip().lower()
    can_delete = user.get("role") == "admin" or bool(uploaded_by_email and uploaded_by_email == user_email)
    return {
        "id": document.id,
        "title": document.title,
        "source": document.source,
        "uploaded_by_name": document.uploaded_by_name,
        "uploaded_by_email": uploaded_by_email,
        "can_delete": can_delete,
    }


@router.get("/", response_model=list[DocumentOut])
def list_documents(
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = current_user(x_user_email, db)
    sync_documents_from_disk(db)
    documents = db.query(Document).order_by(Document.created_at.desc(), Document.id.desc()).all()
    results = []
    seen_titles = set()
    for document in documents:
        if document.title in seen_titles:
            continue
        seen_titles.add(document.title)
        results.append(serialize_document(document, user))
    return results


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = current_user(x_user_email, db)
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    document = Document(
        title=file.filename,
        source="upload",
        content=None,
        uploaded_by_id=user.get("id"),
        uploaded_by_name=user.get("full_name"),
        uploaded_by_email=user.get("email"),
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        from app.rag.skills_agent import SkillsAgent

        skills_agent = SkillsAgent()
        skills_agent.add_document(str(file_path))
        return {
            "id": document.id,
            "filename": file.filename,
            "title": document.title,
            "source": document.source,
            "uploaded_by_name": document.uploaded_by_name,
            "uploaded_by_email": document.uploaded_by_email,
            "status": "uploaded_and_indexed",
        }
    except Exception as exc:
        print(f"Erreur lors de l'indexation RAG: {exc}")
        return {
            "id": document.id,
            "filename": file.filename,
            "title": document.title,
            "source": document.source,
            "uploaded_by_name": document.uploaded_by_name,
            "uploaded_by_email": document.uploaded_by_email,
            "status": "uploaded_not_indexed",
            "error": str(exc),
        }


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = current_user(x_user_email, db)
    document = db.get(Document, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable.")

    user_email = (user.get("email") or "").strip().lower()
    owner_email = (document.uploaded_by_email or "").strip().lower()
    if user.get("role") != "admin" and owner_email != user_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous pouvez supprimer uniquement les documents que vous avez ajoutes.",
        )

    same_title_count = db.query(Document).filter(Document.title == document.title).count()
    file_path = UPLOAD_DIR / document.title
    if same_title_count <= 1 and file_path.exists() and file_path.is_file():
        file_path.unlink()

    db.delete(document)
    db.commit()

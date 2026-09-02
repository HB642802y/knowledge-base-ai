from pathlib import Path
from typing import List

from sqlalchemy.orm import Session

from ..models.document import Document
from ..schemas.document import DocumentCreate


DOCUMENTS_DIR = Path(__file__).resolve().parents[3] / "documents"


def sync_documents_from_disk(db: Session) -> None:
    """Persist files that exist on disk but are missing from the documents table."""
    if not DOCUMENTS_DIR.exists():
        return

    existing_titles = {
        title
        for (title,) in db.query(Document.title).filter(Document.source == "upload").all()
    }

    changed = False
    for file_path in sorted(DOCUMENTS_DIR.iterdir(), key=lambda path: path.stat().st_mtime):
        if not file_path.is_file() or file_path.name in existing_titles:
            continue
        db.add(
            Document(
                title=file_path.name,
                source="upload",
                content=None,
                uploaded_by_name="System",
                uploaded_by_email="system",
            )
        )
        existing_titles.add(file_path.name)
        changed = True

    if changed:
        db.commit()


class DocumentService:
    def __init__(self, storage_dir: str = "uploads"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._documents: List[dict] = []

    def list_documents(self) -> List[dict]:
        return self._documents

    def add_document(self, payload: DocumentCreate) -> dict:
        document = {"id": len(self._documents) + 1, **payload.model_dump()}
        self._documents.append(document)
        return document

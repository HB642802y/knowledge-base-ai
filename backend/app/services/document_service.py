from pathlib import Path
from typing import List

from ..schemas.document import DocumentCreate


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

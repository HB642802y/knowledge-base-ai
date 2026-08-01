from pydantic import BaseModel


class DocumentCreate(BaseModel):
    title: str
    source: str
    content: str | None = None


class DocumentOut(DocumentCreate):
    id: int

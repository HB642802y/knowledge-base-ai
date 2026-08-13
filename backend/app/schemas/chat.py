from pydantic import BaseModel
from typing import List


class ChatRequest(BaseModel):
    question: str


class SourceDocument(BaseModel):
    filename: str


class ChatResponse(BaseModel):
    """Trois réponses : documents + forum + assistant IA."""

    document_answer: str
    document_sources: List[SourceDocument] = []
    forum_answer: str
    forum_sources: List[SourceDocument] = []
    ai_answer: str
    ai_sources: List[SourceDocument] = []
    # Compat
    answer: str = ""
    sources: List[SourceDocument] = []

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from ..core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    # title contient la question posée par l'utilisateur.
    title = Column(String, nullable=False)
    # Auteur de la question : admin ou collaborateur connecté.
    author_id = Column(Integer, nullable=True)
    author_name = Column(String, nullable=True)
    # Réponse générée automatiquement par l'agent IA/RAG.
    ai_answer = Column(Text, nullable=True)
    # Sources utilisées par l'agent IA, enregistrées au format JSON.
    ai_sources = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

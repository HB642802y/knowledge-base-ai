from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from ..core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    # Chaque message est rattaché à une question stockée dans la table conversations.
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    # role="comment" représente une réponse/commentaire ajouté par un admin ou collaborateur.
    role = Column(String, nullable=False)
    # Texte de la réponse humaine publiée sous la question.
    content = Column(String, nullable=False)
    # Auteur de la réponse ; nullable pour garder les anciens messages compatibles.
    author_id = Column(Integer, nullable=True)
    author_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

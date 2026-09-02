from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from ..core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author_id = Column(Integer, nullable=True)
    author_name = Column(String, nullable=True)
    ai_answer = Column(Text, nullable=True)
    ai_sources = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

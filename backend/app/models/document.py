from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from ..core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    uploaded_by_id = Column(Integer, nullable=True)
    uploaded_by_name = Column(String, nullable=True)
    uploaded_by_email = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class ForumQuestion(Base):
    __tablename__ = "forum_questions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=True)
    author_name = Column(String(200), nullable=False)
    author_email = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    answers = relationship(
        "ForumAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="ForumAnswer.created_at",
    )


class ForumAnswer(Base):
    __tablename__ = "forum_answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("forum_questions.id"), nullable=False, index=True)
    body = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=True)
    author_name = Column(String(200), nullable=False)
    author_email = Column(String(200), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("ForumQuestion", back_populates="answers")

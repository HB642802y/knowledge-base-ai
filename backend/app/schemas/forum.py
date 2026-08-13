from datetime import datetime

from pydantic import BaseModel, Field


class ForumAuthor(BaseModel):
    id: int | None = None
    full_name: str
    email: str


class ForumQuestionCreate(BaseModel):
    title: str = Field(min_length=3, max_length=300)
    body: str = Field(min_length=3)
    author: ForumAuthor


class ForumAnswerCreate(BaseModel):
    body: str = Field(min_length=1)
    author: ForumAuthor


class ForumAnswerOut(BaseModel):
    id: int
    question_id: int
    body: str
    author_name: str
    author_email: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ForumQuestionOut(BaseModel):
    id: int
    title: str
    body: str
    author_name: str
    author_email: str
    created_at: datetime | None = None
    answers_count: int = 0

    class Config:
        from_attributes = True


class ForumQuestionDetail(ForumQuestionOut):
    answers: list[ForumAnswerOut] = []

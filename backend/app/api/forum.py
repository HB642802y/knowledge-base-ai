from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.user import User as DbUser

router = APIRouter(prefix="/forum", tags=["forum"])

# In-memory storage for demo purposes
questions_db = []
answers_db = []
question_id_counter = 1
answer_id_counter = 1


class Author(BaseModel):
    id: int
    full_name: str
    email: str


class QuestionCreate(BaseModel):
    title: str
    body: str
    author: Author


class AnswerCreate(BaseModel):
    body: str
    author: Author


class QuestionOut(BaseModel):
    id: int
    title: str
    body: str
    author_name: str
    created_at: str
    answers_count: int


class AnswerOut(BaseModel):
    id: int
    body: str
    author_name: str
    created_at: str


class QuestionDetailOut(BaseModel):
    id: int
    title: str
    body: str
    author_name: str
    created_at: str
    answers: List[AnswerOut]


def verify_author(author: Author, db: Session) -> bool:
    """Verify that the author is a valid user created by admin."""
    user = db.query(DbUser).filter(DbUser.email == author.email.lower()).first()
    if not user:
        return False
    return user.id == author.id and user.full_name == author.full_name


@router.get("/questions", response_model=List[QuestionOut])
def list_questions():
    """List all questions (public access)."""
    questions = []
    for q in questions_db:
        answers_count = len([a for a in answers_db if a["question_id"] == q["id"]])
        questions.append({
            "id": q["id"],
            "title": q["title"],
            "body": q["body"],
            "author_name": q["author_name"],
            "created_at": q["created_at"],
            "answers_count": answers_count
        })
    return questions


@router.get("/questions/{question_id}", response_model=QuestionDetailOut)
def get_question(question_id: int):
    """Get a specific question with its answers (public access)."""
    question = next((q for q in questions_db if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    answers = []
    for a in answers_db:
        if a["question_id"] == question_id:
            answers.append({
                "id": a["id"],
                "body": a["body"],
                "author_name": a["author_name"],
                "created_at": a["created_at"]
            })
    
    return {
        "id": question["id"],
        "title": question["title"],
        "body": question["body"],
        "author_name": question["author_name"],
        "created_at": question["created_at"],
        "answers": answers
    }


@router.post("/questions", response_model=QuestionOut)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    """Create a new question (requires valid user)."""
    if not verify_author(question.author, db):
        raise HTTPException(status_code=401, detail="Invalid user credentials")
    
    global question_id_counter
    new_question = {
        "id": question_id_counter,
        "title": question.title,
        "body": question.body,
        "author_name": question.author.full_name,
        "created_at": str(question_id_counter),  # Simplified for demo
    }
    questions_db.append(new_question)
    question_id_counter += 1
    
    return {
        "id": new_question["id"],
        "title": new_question["title"],
        "body": new_question["body"],
        "author_name": new_question["author_name"],
        "created_at": new_question["created_at"],
        "answers_count": 0
    }


@router.post("/questions/{question_id}/answers", response_model=AnswerOut)
def create_answer(question_id: int, answer: AnswerCreate, db: Session = Depends(get_db)):
    """Create an answer to a question (requires valid user)."""
    if not verify_author(answer.author, db):
        raise HTTPException(status_code=401, detail="Invalid user credentials")
    
    question = next((q for q in questions_db if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    global answer_id_counter
    new_answer = {
        "id": answer_id_counter,
        "question_id": question_id,
        "body": answer.body,
        "author_name": answer.author.full_name,
        "created_at": str(answer_id_counter),  # Simplified for demo
    }
    answers_db.append(new_answer)
    answer_id_counter += 1
    
    return {
        "id": new_answer["id"],
        "body": new_answer["body"],
        "author_name": new_answer["author_name"],
        "created_at": new_answer["created_at"]
    }


@router.delete("/questions/{question_id}")
def delete_question(question_id: int):
    """Delete a question (admin only - simplified for demo)."""
    question = next((q for q in questions_db if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Remove question and its answers
    questions_db[:] = [q for q in questions_db if q["id"] != question_id]
    answers_db[:] = [a for a in answers_db if a["question_id"] != question_id]
    
    return {"message": "Question deleted"}


@router.delete("/answers/{answer_id}")
def delete_answer(answer_id: int):
    """Delete an answer (admin only - simplified for demo)."""
    answer = next((a for a in answers_db if a["id"] == answer_id), None)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    answers_db[:] = [a for a in answers_db if a["id"] != answer_id]
    
    return {"message": "Answer deleted"}

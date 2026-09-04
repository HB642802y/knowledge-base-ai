import json

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.users import current_user
from app.core.database import get_db
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
service = ChatService()


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


def date_to_string(value):
    return value.isoformat() if value else None


def serialize_question(conversation: Conversation, db: Session, user: dict | None = None) -> dict:
    # Récupère les réponses humaines liées à cette question.
    comments = (
        db.query(Message)
        .filter(Message.conversation_id == conversation.id, Message.role == "comment")
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )
    try:
        sources = json.loads(conversation.ai_sources or "[]")
    except json.JSONDecodeError:
        sources = []

    return {
        "id": conversation.id,
        "question": conversation.title,
        "author_name": conversation.author_name,
        "author_id": conversation.author_id,
        "created_at": date_to_string(conversation.created_at),
        "ai_answer": conversation.ai_answer,
        "sources": sources,
        "can_delete": bool(user and conversation.author_id == user["id"]),
        "comments": [
            {
                "id": comment.id,
                "body": comment.content,
                "author_name": comment.author_name,
                "author_id": comment.author_id,
                "created_at": date_to_string(comment.created_at),
            }
            for comment in comments
        ],
    }


@router.post("/", response_model=ChatResponse)
def chat(payload: ChatRequest):
    """Legacy endpoint: return an IA answer without publishing it."""
    return service.ask(payload.question)


@router.get("/questions")
def list_questions(x_user_email: str | None = Header(default=None), db: Session = Depends(get_db)):
    user = None
    if x_user_email:
        user = current_user(x_user_email, db)
    conversations = db.query(Conversation).order_by(Conversation.created_at.desc(), Conversation.id.desc()).all()
    return [serialize_question(conversation, db, user) for conversation in conversations]


@router.post("/questions", status_code=status.HTTP_201_CREATED)
def create_question(
    payload: ChatRequest,
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = current_user(x_user_email, db)
    question_text = payload.question.strip()
    if not question_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="La question est obligatoire.")

    # Envoie la question au pipeline IA/RAG puis stocke la réponse dans la conversation.
    response = service.ask(question_text)
    conversation = Conversation(
        title=question_text,
        author_id=user["id"],
        author_name=user["full_name"],
        ai_answer=response.answer,
        ai_sources=json.dumps([source.model_dump() for source in response.sources]),
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return serialize_question(conversation, db, user)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    question_id: int,
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = current_user(x_user_email, db)
    question = db.get(Conversation, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question introuvable.")
    if question.author_id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seul l'auteur de la question peut la supprimer.",
        )

    db.query(Message).filter(Message.conversation_id == question.id).delete(synchronize_session=False)
    db.delete(question)
    db.commit()


@router.post("/questions/{question_id}/comments", status_code=status.HTTP_201_CREATED)
def create_comment(
    question_id: int,
    payload: CommentCreate,
    x_user_email: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    user = current_user(x_user_email, db)
    question = db.get(Conversation, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question introuvable.")
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Le commentaire est obligatoire.")

    # Ajoute une réponse humaine sous la question existante.
    comment = Message(
        conversation_id=question.id,
        role="comment",
        content=body,
        author_id=user["id"],
        author_name=user["full_name"],
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "body": comment.content,
        "author_name": comment.author_name,
        "author_id": comment.author_id,
        "created_at": date_to_string(comment.created_at),
    }

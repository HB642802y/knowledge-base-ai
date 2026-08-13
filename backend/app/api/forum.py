from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.models.forum import ForumAnswer, ForumQuestion
from app.schemas.forum import (
    ForumAnswerCreate,
    ForumAnswerOut,
    ForumQuestionCreate,
    ForumQuestionDetail,
    ForumQuestionOut,
)

router = APIRouter(prefix="/forum", tags=["forum"])


def _index_forum_pair(question: ForumQuestion, answer: ForumAnswer) -> None:
    """Indexe la paire question/réponse dans le RAG (best-effort)."""
    try:
        from app.rag.skills_agent import SkillsAgent
        from app.core.config import settings

        agent = SkillsAgent(openai_api_key=settings.OPENAI_API_KEY)
        if not agent.is_healthy():
            return

        text = (
            f"Question forum : {question.title}\n"
            f"{question.body}\n\n"
            f"Réponse de {answer.author_name} :\n{answer.body}"
        )
        agent.add_text(
            text=text,
            doc_id=f"forum_q{question.id}_a{answer.id}",
            metadata={
                "source": f"forum-question-{question.id}",
                "filename": f"Forum — {question.title[:80]}",
                "type": "forum",
            },
        )
    except Exception as exc:
        print(f"Indexation forum RAG ignorée : {exc}")


@router.get("/questions", response_model=list[ForumQuestionOut])
def list_questions(db: Session = Depends(get_db)):
    rows = (
        db.query(ForumQuestion)
        .options(joinedload(ForumQuestion.answers))
        .order_by(ForumQuestion.created_at.desc())
        .all()
    )
    return [
        ForumQuestionOut(
            id=q.id,
            title=q.title,
            body=q.body,
            author_name=q.author_name,
            author_email=q.author_email,
            created_at=q.created_at,
            answers_count=len(q.answers),
        )
        for q in rows
    ]


@router.get("/questions/{question_id}", response_model=ForumQuestionDetail)
def get_question(question_id: int, db: Session = Depends(get_db)):
    q = (
        db.query(ForumQuestion)
        .options(joinedload(ForumQuestion.answers))
        .filter(ForumQuestion.id == question_id)
        .first()
    )
    if not q:
        raise HTTPException(status_code=404, detail="Question introuvable")

    return ForumQuestionDetail(
        id=q.id,
        title=q.title,
        body=q.body,
        author_name=q.author_name,
        author_email=q.author_email,
        created_at=q.created_at,
        answers_count=len(q.answers),
        answers=[ForumAnswerOut.model_validate(a) for a in q.answers],
    )


@router.post("/questions", response_model=ForumQuestionOut, status_code=201)
def create_question(payload: ForumQuestionCreate, db: Session = Depends(get_db)):
    q = ForumQuestion(
        title=payload.title.strip(),
        body=payload.body.strip(),
        author_id=payload.author.id,
        author_name=payload.author.full_name.strip(),
        author_email=payload.author.email.strip(),
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return ForumQuestionOut(
        id=q.id,
        title=q.title,
        body=q.body,
        author_name=q.author_name,
        author_email=q.author_email,
        created_at=q.created_at,
        answers_count=0,
    )


@router.post(
    "/questions/{question_id}/answers",
    response_model=ForumAnswerOut,
    status_code=201,
)
def create_answer(
    question_id: int,
    payload: ForumAnswerCreate,
    db: Session = Depends(get_db),
):
    q = db.query(ForumQuestion).filter(ForumQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question introuvable")

    answer = ForumAnswer(
        question_id=q.id,
        body=payload.body.strip(),
        author_id=payload.author.id,
        author_name=payload.author.full_name.strip(),
        author_email=payload.author.email.strip(),
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    _index_forum_pair(q, answer)
    return ForumAnswerOut.model_validate(answer)


@router.delete("/questions/{question_id}", status_code=204)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    q = db.query(ForumQuestion).filter(ForumQuestion.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question introuvable")
    db.delete(q)
    db.commit()


@router.delete("/answers/{answer_id}", status_code=204)
def delete_answer(answer_id: int, db: Session = Depends(get_db)):
    a = db.query(ForumAnswer).filter(ForumAnswer.id == answer_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Réponse introuvable")
    db.delete(a)
    db.commit()

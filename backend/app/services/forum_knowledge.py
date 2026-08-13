"""Recherche locale dans le forum (SQLite) — fonctionne sans langchain / embeddings."""

from __future__ import annotations

from sqlalchemy.orm import Session, joinedload

from app.models.forum import ForumAnswer, ForumQuestion
from app.utils.text_match import similarity_score

MATCH_THRESHOLD = 0.38


class ForumKnowledgeService:
    def ask(self, question: str, db: Session) -> dict:
        rows = (
            db.query(ForumQuestion)
            .options(joinedload(ForumQuestion.answers))
            .order_by(ForumQuestion.created_at.desc())
            .all()
        )

        scored: list[tuple[float, ForumQuestion, ForumAnswer | None]] = []

        for q in rows:
            title_body = f"{q.title} {q.body}"
            title_score = similarity_score(question, q.title)
            body_score = similarity_score(question, title_body)

            if q.answers:
                for a in q.answers:
                    full = f"{title_body} {a.body}"
                    s = max(
                        title_score,
                        body_score,
                        similarity_score(question, full),
                    )
                    if s >= MATCH_THRESHOLD:
                        scored.append((s, q, a))
            else:
                s = max(title_score, body_score)
                if s >= MATCH_THRESHOLD:
                    scored.append((s, q, None))

        scored.sort(key=lambda item: item[0], reverse=True)
        top = scored[:3]

        if not top:
            return {
                "answer": (
                    "Aucune question / réponse similaire n’a encore été trouvée dans le forum. "
                    "Vous pouvez poser la question sur le forum pour que d’autres agents y répondent."
                ),
                "sources": [],
                "found": False,
                "context_text": None,
            }

        parts = []
        context_chunks = []
        sources = []
        seen = set()
        for _score_val, q, a in top:
            if a is not None:
                parts.append(
                    f"• D’après le forum (« {q.title} », réponse de {a.author_name}) :\n"
                    f"{a.body}"
                )
                context_chunks.append(
                    f"Question: {q.title}\n{q.body}\nRéponse ({a.author_name}): {a.body}"
                )
            else:
                parts.append(
                    f"• Question ouverte sur le forum (« {q.title} » par {q.author_name}) :\n"
                    f"{q.body}\n"
                    f"(Pas encore de réponse — vous pouvez y répondre dans le forum.)"
                )
                context_chunks.append(f"Question ouverte: {q.title}\n{q.body}")

            label = f"Forum — {q.title[:80]}"
            if label not in seen:
                sources.append({"filename": label})
                seen.add(label)

        answer = (
            "Échanges trouvés dans le forum collaboratif :\n\n" + "\n\n".join(parts)
        )
        return {
            "answer": answer,
            "sources": sources,
            "found": True,
            "context_text": "\n\n---\n\n".join(context_chunks),
        }

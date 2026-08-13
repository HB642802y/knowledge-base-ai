"""Appel OpenAI direct (sans sentence-transformers / Chroma)."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings


class OpenAIAnswerService:
    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or settings.OPENAI_API_KEY or "").strip()
        self.model = None
        self.error: str | None = None

        if not self.api_key:
            self.error = (
                "OPENAI_API_KEY absente. Ajoutez-la dans backend/.env puis redémarrez l'API."
            )
            return

        try:
            self.model = ChatOpenAI(
                api_key=self.api_key,
                model="gpt-4o-mini",
                temperature=0.3,
            )
        except Exception as exc:
            self.error = str(exc)
            self.model = None

    @property
    def available(self) -> bool:
        return self.model is not None

    def ask(self, question: str, forum_context: str | None = None) -> dict:
        if not self.model:
            return {
                "answer": None,
                "error": self.error or "OpenAI indisponible",
                "sources": [],
            }

        context_block = forum_context or "Aucun extrait forum pertinent."
        prompt = f"""Tu es l'assistant officiel de la base de connaissances du Ministère de l'Agriculture, de la Pêche Maritime, du Développement Rural et des Eaux et Forêts (MAPMDREF).

Réponds en français, de façon claire et professionnelle.
Tu peux t'appuyer sur les extraits du forum collaboratif ci-dessous s'ils sont pertinents, et sur tes connaissances générales administratives quand c'est utile.
Si tu n'es pas sûr, dis-le clairement.

--- Extraits forum (si disponibles) ---
{context_block}
--- Fin des extraits ---

Question de l'agent : {question}

Réponse :"""

        try:
            response = self.model.invoke([HumanMessage(content=prompt)])
            text = (response.content or "").strip()
            sources = []
            if forum_context:
                sources.append({"filename": "Contexte forum + OpenAI API"})
            else:
                sources.append({"filename": "OpenAI API"})
            return {"answer": text, "error": None, "sources": sources}
        except Exception as exc:
            err = str(exc)
            if "401" in err or "Incorrect API key" in err:
                err = "Clé API OpenAI invalide. Vérifiez OPENAI_API_KEY dans backend/.env"
            elif "429" in err or "quota" in err.lower():
                err = "Quota OpenAI dépassé. Vérifiez votre compte / facturation OpenAI."
            return {"answer": None, "error": err, "sources": []}

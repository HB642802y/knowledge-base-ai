"""Appel Groq (API compatible OpenAI) — réponse IA sans Chroma / embeddings."""

from __future__ import annotations

from app.core.config import settings


class GroqAssistant:
    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or settings.GROQ_API_KEY or "").strip()
        self.model_name = settings.GROQ_MODEL
        self.last_error: str | None = None
        self._client = None

        if not self.api_key:
            self.last_error = "GROQ_API_KEY non configurée"
            return

        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_openai import ChatOpenAI

            self._SystemMessage = SystemMessage
            self._HumanMessage = HumanMessage
            self._client = ChatOpenAI(
                api_key=self.api_key,
                base_url="https://api.groq.com/openai/v1",
                model=self.model_name,
                temperature=0.3,
            )
        except Exception as exc:
            self.last_error = str(exc)
            self._client = None

    @property
    def is_available(self) -> bool:
        return self._client is not None

    def ask(self, question: str, forum_context: str = "") -> dict:
        if not self._client:
            msg = (
                "Clé API Groq manquante. Ajoutez GROQ_API_KEY dans "
                "backend/.env puis redémarrez le serveur."
            )
            if self.last_error and "GROQ_API_KEY" not in (self.last_error or ""):
                msg = f"Assistant IA indisponible : {self.last_error}"
            return {"answer": msg, "sources": []}

        system = (
            "Tu es l'assistant officiel de la base de connaissances du "
            "Ministère de l'Agriculture, de la Pêche Maritime, du Développement "
            "Rural et des Eaux et Forêts (MAPMDREF). "
            "Réponds en français, de façon claire et professionnelle. "
            "Si un contexte forum est fourni, tu peux t'en inspirer mais précise "
            "quand une info vient du forum. Si tu n'es pas sûr, dis-le."
        )

        human = f"Question : {question}"
        if forum_context.strip():
            human += (
                "\n\nContexte issu du forum collaboratif (peut être utile) :\n"
                f"{forum_context.strip()}"
            )

        try:
            response = self._client.invoke(
                [
                    self._SystemMessage(content=system),
                    self._HumanMessage(content=human),
                ]
            )
            text = getattr(response, "content", None) or str(response)
            sources = [{"filename": f"Groq ({self.model_name})"}]
            return {"answer": text, "sources": sources}
        except Exception as exc:
            self.last_error = str(exc)
            err = str(exc)
            if "401" in err or "invalid_api_key" in err.lower():
                return {
                    "answer": "Clé API Groq invalide. Vérifiez GROQ_API_KEY dans backend/.env.",
                    "sources": [],
                }
            if "429" in err or "rate" in err.lower():
                return {
                    "answer": "Limite Groq atteinte. Réessayez dans quelques instants.",
                    "sources": [],
                }
            return {"answer": f"Erreur API Groq : {exc}", "sources": []}

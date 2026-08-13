"""Appel OpenAI direct — ne dépend pas de sentence-transformers / Chroma."""

from __future__ import annotations

from app.core.config import settings


class OpenAIAssistant:
    def __init__(self, api_key: str | None = None):
        self.api_key = (api_key or settings.OPENAI_API_KEY or "").strip()
        self.model_name = "gpt-4o-mini"
        self.last_error: str | None = None
        self._client = None

        if not self.api_key:
            self.last_error = "OPENAI_API_KEY non configurée"
            return

        try:
            from langchain_openai import ChatOpenAI
            from langchain_core.messages import SystemMessage, HumanMessage

            self._ChatOpenAI = ChatOpenAI
            self._SystemMessage = SystemMessage
            self._HumanMessage = HumanMessage
            self._client = ChatOpenAI(
                api_key=self.api_key,
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
                "Clé API OpenAI manquante. Ajoutez OPENAI_API_KEY dans "
                "backend/.env puis redémarrez le serveur."
            )
            if self.last_error and "OPENAI_API_KEY" not in (self.last_error or ""):
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
            sources = []
            if forum_context.strip():
                sources.append({"filename": "Contexte forum + modèle OpenAI"})
            else:
                sources.append({"filename": f"OpenAI ({self.model_name})"})
            return {"answer": text, "sources": sources}
        except Exception as exc:
            self.last_error = str(exc)
            err = str(exc)
            if "401" in err or "invalid_api_key" in err.lower():
                return {
                    "answer": "Clé API OpenAI invalide. Vérifiez OPENAI_API_KEY dans backend/.env.",
                    "sources": [],
                }
            if "429" in err or "quota" in err.lower():
                return {
                    "answer": "Quota OpenAI dépassé. Réessayez plus tard ou vérifiez votre compte.",
                    "sources": [],
                }
            return {"answer": f"Erreur API OpenAI : {exc}", "sources": []}

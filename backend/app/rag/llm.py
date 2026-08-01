from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model
        self.last_error: str | None = None

        self.model = (
            ChatOpenAI(api_key=self.api_key, model=self.model_name, temperature=0.7)
            if self.api_key
            else None
        )
        print("OpenAI LLM activé" if self.model else "OpenAI absent : réponse par extraits activée")

    def generate(self, prompt: str) -> str | None:
        """Generate an answer, or return None if the LLM provider is unavailable."""
        if self.model is None:
            self.last_error = "OPENAI_API_KEY non configurée"
            return None

        try:
            response = self.model.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as exc:
            self.last_error = str(exc)
            if "429" in self.last_error or "quota" in self.last_error.lower():
                print("Quota OpenAI indisponible : passage en mode réponse par extraits")
            else:
                print(f"Erreur du fournisseur LLM : {exc}")
            return None

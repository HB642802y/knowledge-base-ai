from app.core.config import settings


class LLMClient:
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model
        self.last_error: str | None = None
        self.human_message_class = None
        self.model = None

        if self.api_key:
            try:
                from langchain_core.messages import HumanMessage
                from langchain_openai import ChatOpenAI

                self.human_message_class = HumanMessage
                self.model = ChatOpenAI(api_key=self.api_key, model=self.model_name, temperature=0.7)
            except Exception as exc:
                self.last_error = str(exc)
                print(f"OpenAI indisponible : {exc}")

        print("OpenAI LLM active" if self.model else "OpenAI absent : reponse par extraits activee")

    def generate(self, prompt: str) -> str | None:
        """Generate an answer, or return None if the LLM provider is unavailable."""
        if self.model is None or self.human_message_class is None:
            self.last_error = self.last_error or "OPENAI_API_KEY non configuree"
            return None

        try:
            response = self.model.invoke([self.human_message_class(content=prompt)])
            return response.content
        except Exception as exc:
            self.last_error = str(exc)
            if "429" in self.last_error or "quota" in self.last_error.lower():
                print("Quota OpenAI indisponible : passage en mode reponse par extraits")
            else:
                print(f"Erreur du fournisseur LLM : {exc}")
            return None

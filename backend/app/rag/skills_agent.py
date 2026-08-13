from .rag_pipeline import RAGPipeline


class SkillsAgent:
    def __init__(self, openai_api_key: str = None):
        self.rag_pipeline = None
        try:
            self.rag_pipeline = RAGPipeline(openai_api_key=openai_api_key)
            self.is_available = True
        except Exception as exc:
            print(f"Erreur initialisation SkillsAgent: {exc}")
            self.is_available = False
            self.error = str(exc)

    def ask(self, question: str) -> dict:
        if not self.is_available or self.rag_pipeline is None:
            return {
                "answer": "Le skills agent est temporairement indisponible.",
                "sources": []
            }

        try:
            return self.rag_pipeline.ask(question)
        except Exception as exc:
            print(f"Erreur SkillsAgent.ask: {exc}")
            return {
                "answer": f"Erreur lors de la génération de la réponse: {exc}",
                "sources": []
            }

    def add_document(self, file_path: str) -> bool:
        if not self.is_available or self.rag_pipeline is None:
            return False

        try:
            self.rag_pipeline.add_document(file_path)
            return True
        except Exception as exc:
            print(f"Erreur SkillsAgent.add_document: {exc}")
            return False

    def add_text(self, text: str, doc_id: str, metadata: dict | None = None) -> bool:
        if not self.is_available or self.rag_pipeline is None:
            return False

        try:
            self.rag_pipeline.add_text(text=text, doc_id=doc_id, metadata=metadata)
            return True
        except Exception as exc:
            print(f"Erreur SkillsAgent.add_text: {exc}")
            return False

    def is_healthy(self) -> bool:
        return self.is_available

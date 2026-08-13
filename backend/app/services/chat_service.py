from app.schemas.chat import ChatResponse, SourceDocument
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.document_knowledge import DocumentKnowledgeService
from app.services.forum_knowledge import ForumKnowledgeService
from app.services.groq_assistant import GroqAssistant


class ChatService:
    def __init__(self):
        self.document_knowledge = DocumentKnowledgeService()
        self.forum_knowledge = ForumKnowledgeService()
        self.llm = GroqAssistant(api_key=settings.GROQ_API_KEY)
        print(
            "Groq assistant :",
            "OK" if self.llm.is_available else f"KO ({self.llm.last_error})",
        )

    def ask(self, question: str) -> ChatResponse:
        doc_result = self.document_knowledge.ask(question)
        forum_result = self._ask_forum(question)

        doc_sources = [
            SourceDocument(filename=s["filename"]) for s in doc_result.get("sources", [])
        ]
        forum_sources = [
            SourceDocument(filename=s["filename"]) for s in forum_result.get("sources", [])
        ]

        context_parts = []
        if doc_result.get("found"):
            context_parts.append(f"[Documents]\n{doc_result['answer']}")
        if forum_result.get("found"):
            context_parts.append(f"[Forum]\n{forum_result.get('context_text') or forum_result['answer']}")

        ai_result = self.llm.ask(
            question,
            forum_context="\n\n".join(context_parts),
        )
        ai_sources = [
            SourceDocument(filename=s["filename"]) for s in ai_result.get("sources", [])
        ]

        combined = (
            f"[Documents]\n{doc_result['answer']}\n\n"
            f"[Forum]\n{forum_result['answer']}\n\n"
            f"[Assistant IA]\n{ai_result.get('answer') or 'Aucune réponse IA.'}"
        )

        return ChatResponse(
            document_answer=doc_result["answer"],
            document_sources=doc_sources,
            forum_answer=forum_result["answer"],
            forum_sources=forum_sources,
            ai_answer=ai_result.get("answer") or "Aucune réponse IA.",
            ai_sources=ai_sources,
            answer=combined,
            sources=doc_sources + forum_sources + ai_sources,
        )

    def _ask_forum(self, question: str) -> dict:
        db = SessionLocal()
        try:
            return self.forum_knowledge.ask(question, db)
        except Exception as exc:
            print("Erreur forum knowledge :", exc)
            return {
                "answer": f"Impossible de consulter le forum : {exc}",
                "sources": [],
                "found": False,
            }
        finally:
            db.close()

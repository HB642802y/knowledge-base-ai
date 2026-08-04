from app.schemas.chat import ChatResponse, SourceDocument
from app.core.config import settings


class ChatService:
    def __init__(self):
        self.skills_agent = None
        try:
            from app.rag.skills_agent import SkillsAgent
            print("Chargement SkillsAgent...")
            self.skills_agent = SkillsAgent(openai_api_key=settings.OPENAI_API_KEY)
            print("SkillsAgent OK")
        except Exception as exc:
            print("ERREUR SkillsAgent :", exc)
            self.skills_agent_error = str(exc)
            self.skills_agent = None
        else:
            self.skills_agent_error = None

    def ask(self, question: str) -> ChatResponse:
        if self.skills_agent is not None:
            try:
                result = self.skills_agent.ask(question)
                sources = [SourceDocument(filename=s["filename"]) for s in result.get("sources", [])]
                return ChatResponse(answer=result["answer"], sources=sources)
            except Exception as exc:
                print("Erreur SkillsAgent ASK :", exc)
                return ChatResponse(
                    answer=f"Erreur SkillsAgent : {exc}",
                    sources=[]
                )

        return ChatResponse(
            answer="Le skills agent est temporairement indisponible.",
            sources=[]
        )

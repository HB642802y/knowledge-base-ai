from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import shutil

router = APIRouter(prefix="/documents", tags=["documents"])

# Documents storage directory
UPLOAD_DIR = Path(__file__).resolve().parents[3] / "documents"
UPLOAD_DIR.mkdir(exist_ok=True)


class DocumentOut(BaseModel):
    id: int
    title: str
    source: str


@router.get("/", response_model=list[DocumentOut])
def list_documents():
    return [{"id": 1, "title": "Guide SDSI", "source": "upload"}]


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    # Save file to disk
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Index in RAG
    try:
        from app.rag.skills_agent import SkillsAgent
        skills_agent = SkillsAgent()
        skills_agent.add_document(str(file_path))
        return {"filename": file.filename, "status": "uploaded_and_indexed"}
    except Exception as exc:
        print(f"Erreur lors de l'indexation RAG: {exc}")
        return {"filename": file.filename, "status": "uploaded_not_indexed", "error": str(exc)}

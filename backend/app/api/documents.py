from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
import shutil

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "documents"
UPLOAD_DIR.mkdir(exist_ok=True)


class DocumentOut(BaseModel):
    id: int
    title: str
    source: str


@router.get("/", response_model=list[DocumentOut])
def list_documents():
    files = sorted(
        [p for p in UPLOAD_DIR.iterdir() if p.is_file()],
        key=lambda p: p.name.lower(),
    )
    return [
        {"id": i + 1, "title": f.name, "source": "upload"}
        for i, f in enumerate(files)
    ]


@router.post("/upload")
def upload_document(file: UploadFile = File(...)):
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        from app.rag.skills_agent import SkillsAgent
        skills_agent = SkillsAgent()
        skills_agent.add_document(str(file_path))
        return {"filename": file.filename, "status": "uploaded_and_indexed"}
    except Exception as exc:
        print(f"Erreur lors de l'indexation RAG: {exc}")
        return {"filename": file.filename, "status": "uploaded_not_indexed", "error": str(exc)}

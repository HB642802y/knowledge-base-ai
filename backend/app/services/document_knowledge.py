"""Recherche dans les documents uploadés (dossier local)."""

from __future__ import annotations

from pathlib import Path

from app.utils.text_match import similarity_score

UPLOAD_DIR = Path(__file__).resolve().parents[3] / "documents"
MATCH_THRESHOLD = 0.32


def _read_file_text(path: Path) -> str:
    ext = path.suffix.lower()
    try:
        if ext == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")
        if ext == ".pdf":
            from app.utils.pdf_reader import PDFReader
            return PDFReader(path).read()
        if ext == ".docx":
            from app.utils.docx_reader import DocxReader
            return DocxReader(path).read()
        if ext in (".xlsx", ".xls"):
            from app.utils.excel_reader import ExcelReader
            return ExcelReader(path).read()
    except Exception as exc:
        print(f"Lecture document {path.name} : {exc}")
    return ""


def _chunk_text(text: str, size: int = 900, overlap: int = 200) -> list[str]:
    if not text:
        return []
    chunks = []
    step = max(size - overlap, 1)
    for i in range(0, len(text), step):
        chunk = text[i : i + size].strip()
        if chunk:
            chunks.append(chunk)
    return chunks


class DocumentKnowledgeService:
    def ask(self, question: str) -> dict:
        UPLOAD_DIR.mkdir(exist_ok=True)
        files = [
            p
            for p in UPLOAD_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in {".txt", ".pdf", ".docx", ".xlsx", ".xls"}
        ]

        if not files:
            return {
                "answer": (
                    "Aucun document n’a encore été téléversé. "
                    "Utilisez la page Upload pour ajouter des fichiers."
                ),
                "sources": [],
                "found": False,
            }

        scored: list[tuple[float, str, str]] = []

        for file_path in files:
            text = _read_file_text(file_path)
            for chunk in _chunk_text(text):
                s = similarity_score(question, chunk)
                if s >= MATCH_THRESHOLD:
                    scored.append((s, file_path.name, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:3]

        if not top:
            return {
                "answer": (
                    "Aucun extrait pertinent trouvé dans les documents téléversés "
                    "pour cette question."
                ),
                "sources": [],
                "found": False,
            }

        parts = []
        sources = []
        seen = set()
        for _s, filename, chunk in top:
            excerpt = chunk[:700] + ("…" if len(chunk) > 700 else "")
            parts.append(f"• Document « {filename} » :\n{excerpt}")
            if filename not in seen:
                sources.append({"filename": filename})
                seen.add(filename)

        return {
            "answer": "Extraits des documents officiels :\n\n" + "\n\n".join(parts),
            "sources": sources,
            "found": True,
        }

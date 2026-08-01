from pathlib import Path
from langchain_core.documents import Document

from app.utils.pdf_reader import PDFReader
from app.utils.docx_reader import DocxReader
from app.utils.excel_reader import ExcelReader


class DocumentLoader:

    def load(self, file_path: str):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {path}")

        extension = path.suffix.lower()

        if extension == ".pdf":
            text = PDFReader(path).read()

        elif extension == ".docx":
            text = DocxReader(path).read()

        elif extension in [".xlsx", ".xls"]:
            text = ExcelReader(path).read()

        elif extension == ".txt":
            text = path.read_text(encoding="utf-8")

        else:
            raise Exception(f"Format non supporté : {extension}")

        # Convert to langchain Document format
        document = Document(page_content=text, metadata={"source": str(path)})

        return [document]

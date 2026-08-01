from pathlib import Path
from docx import Document


class DocxReader:

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read(self) -> str:

        doc = Document(self.file_path)

        return "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )
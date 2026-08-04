from pathlib import Path
from pypdf import PdfReader


class PDFReader:

    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read(self) -> str:

        reader = PdfReader(self.file_path)

        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        return text
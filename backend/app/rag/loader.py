from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from .document import Document


class DocumentLoader:

    def load(self, file_path: str):

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Fichier introuvable : {path}")

        extension = path.suffix.lower()

        if extension == ".pdf":
            from app.utils.pdf_reader import PDFReader

            text = PDFReader(path).read()

        elif extension == ".docx":
            from app.utils.docx_reader import DocxReader

            text = DocxReader(path).read()

        elif extension in [".xlsx", ".xls"]:
            from app.utils.excel_reader import ExcelReader

            text = ExcelReader(path).read()

        elif extension == ".pptx":
            text = self._read_pptx(path)

        elif extension == ".txt":
            text = path.read_text(encoding="utf-8")

        else:
            raise Exception(f"Format non supporté : {extension}")

        # Convert to langchain Document format
        document = Document(page_content=text, metadata={"source": str(path)})

        return [document]

    def _read_pptx(self, path: Path) -> str:
        texts = []
        namespace = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

        with zipfile.ZipFile(path) as archive:
            slide_names = sorted(
                name
                for name in archive.namelist()
                if name.startswith("ppt/slides/slide") and name.endswith(".xml")
            )
            for slide_name in slide_names:
                root = ET.fromstring(archive.read(slide_name))
                slide_text = [
                    node.text.strip()
                    for node in root.findall(".//a:t", namespace)
                    if node.text and node.text.strip()
                ]
                if slide_text:
                    texts.append("\n".join(slide_text))

        return "\n\n".join(texts)

from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile


class DocxReader:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def read(self) -> str:
        try:
            from docx import Document

            doc = Document(self.file_path)
            return "\n".join(paragraph.text for paragraph in doc.paragraphs)
        except Exception:
            return self._read_with_stdlib()

    def _read_with_stdlib(self) -> str:
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        with zipfile.ZipFile(self.file_path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
        paragraphs = []
        for paragraph in root.findall(".//w:p", namespace):
            texts = [
                node.text
                for node in paragraph.findall(".//w:t", namespace)
                if node.text
            ]
            if texts:
                paragraphs.append("".join(texts))
        return "\n".join(paragraphs)

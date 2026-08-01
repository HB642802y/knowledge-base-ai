from typing import List


class RAGService:
    def __init__(self):
        self.documents: List[dict] = []

    def ingest(self, document: dict) -> None:
        self.documents.append(document)

    def search(self, query: str) -> List[dict]:
        return [doc for doc in self.documents if query.lower() in str(doc).lower()][:3]

from langchain_core.documents import Document


class TextSplitter:

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, documents):
        chunks = []
        for doc in documents:
            text = doc.page_content
            for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
                chunk_text = text[i:i + self.chunk_size]
                chunk = Document(
                    page_content=chunk_text,
                    metadata=doc.metadata
                )
                chunks.append(chunk)
        return chunks

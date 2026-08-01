import chromadb
from chromadb.config import Settings
from pathlib import Path


class VectorStore:
    def __init__(self, embedding_provider=None, collection_name: str = "documents"):
        self.embedding_provider = embedding_provider
        # Use persistent client for data persistence
        chroma_path = Path(__file__).resolve().parents[3] / "chroma_db"
        chroma_path.mkdir(exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(chroma_path))
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict] = None) -> None:
        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(self, embedding: list[float], top_k: int = 3) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results

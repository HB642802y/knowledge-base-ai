from .vector_store import VectorStore
from .embeddings import EmbeddingModel


class Retriever:
    def __init__(self, store: VectorStore | None = None, embedding_provider=None):
        self.store = store or VectorStore(embedding_provider)
        self.embedding_provider = embedding_provider or EmbeddingModel()

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        if self.embedding_provider is None:
            return []

        embedding = self.embedding_provider.embed(query)
        results = self.store.search(embedding, top_k=top_k)

        formatted_results = []
        if results and 'documents' in results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'text': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {}
                })

        return formatted_results

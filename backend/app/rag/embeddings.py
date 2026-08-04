from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.model = SentenceTransformer(self.model_name)

    def get_model(self):
        return self.model

    def embed(self, text: str) -> list[float]:
        embedding = self.model.encode(text)
        return embedding.tolist() if hasattr(embedding, 'tolist') else embedding.tolist()

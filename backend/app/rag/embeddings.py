import hashlib
import math


class EmbeddingModel:
    def __init__(self, dimensions: int = 384):
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self.dimensions = dimensions
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
        except Exception as exc:
            print(f"Embedding fallback active: {exc}")

    def get_model(self):
        return self.model

    def embed(self, text: str) -> list[float]:
        if self.model is not None:
            embedding = self.model.encode(text)
            return embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)

        vector = [0.0] * self.dimensions
        words = text.lower().split()
        for word in words:
            digest = hashlib.sha256(word.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
   

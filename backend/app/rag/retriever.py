import re
import unicodedata

from .embeddings import EmbeddingModel
from .vector_store import VectorStore


STOPWORDS = {
    "a",
    "ai",
    "au",
    "aux",
    "avec",
    "ce",
    "ces",
    "dans",
    "de",
    "des",
    "du",
    "elle",
    "en",
    "est",
    "et",
    "il",
    "la",
    "le",
    "les",
    "l",
    "objectif",
    "pour",
    "que",
    "quel",
    "quelle",
    "quels",
    "quelles",
    "qui",
    "un",
    "une",
}


def normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = "".join(char for char in normalized if not unicodedata.combining(char))
    return ascii_text.lower()


def tokenize(value: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9]+", normalize_text(value))
    return [word for word in words if len(word) > 1 and word not in STOPWORDS]


class Retriever:
    def __init__(self, store: VectorStore | None = None, embedding_provider=None):
        self.store = store or VectorStore(embedding_provider)
        self.embedding_provider = embedding_provider or EmbeddingModel()

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        candidates = self._load_candidates(query, top_k)
        if not candidates:
            return []

        query_terms = tokenize(query)
        scored = []
        for candidate in candidates:
            lexical_score = self._lexical_score(query, query_terms, candidate)
            vector_score = candidate.get("score", 0.0)
            scored.append((lexical_score + vector_score * 0.15, candidate))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [candidate for score, candidate in scored[:top_k] if score > 0]

    def _load_candidates(self, query: str, top_k: int) -> list[dict]:
        candidates = self._format_results(self.store.all_documents())

        if self.embedding_provider is not None:
            embedding = self.embedding_provider.embed(query)
            vector_results = self.store.search(embedding, top_k=max(top_k * 5, 20))
            candidates.extend(self._format_results(vector_results))

        unique = {}
        for candidate in candidates:
            key = (
                candidate.get("text", ""),
                str(candidate.get("metadata", {}).get("source", "")),
            )
            unique[key] = candidate
        return list(unique.values())

    def _format_results(self, results) -> list[dict]:
        formatted = []
        if not results or "documents" not in results or not results["documents"]:
            return formatted

        documents = results["documents"][0] or []
        metadatas = (results.get("metadatas") or [[]])[0] or []
        distances = (results.get("distances") or [[]])[0] or []

        for index, document in enumerate(documents):
            formatted.append(
                {
                    "text": document,
                    "metadata": metadatas[index] if index < len(metadatas) else {},
                    "score": self._distance_to_score(distances[index]) if index < len(distances) else 0.0,
                }
            )
        return formatted

    def _lexical_score(self, query: str, query_terms: list[str], candidate: dict) -> float:
        text = normalize_text(candidate.get("text", ""))
        metadata = candidate.get("metadata", {}) or {}
        source = normalize_text(str(metadata.get("source", metadata.get("filename", ""))))

        if not text:
            return 0.0

        text_tokens = set(tokenize(text))
        source_tokens = set(tokenize(source))
        score = 0.0

        for term in query_terms:
            if term in text_tokens:
                score += 4.0
            if term in source_tokens:
                score += 3.0
            if term in text:
                score += 1.0

        important_phrases = [
            "security token service",
            "certificat sts",
            "renouvellement du certificat",
            "plateforme misagri",
            "ferme sharepoint",
        ]
        combined = f"{text} {source}"
        for phrase in important_phrases:
            if phrase in normalize_text(query) and phrase in combined:
                score += 10.0

        return score

    @staticmethod
    def _distance_to_score(distance) -> float:
        try:
            return 1.0 / (1.0 + float(distance))
        except Exception:
            return 0.0

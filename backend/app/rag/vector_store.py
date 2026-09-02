import json
import math
from pathlib import Path


class VectorStore:
    def __init__(self, embedding_provider=None, collection_name: str = "documents"):
        self.embedding_provider = embedding_provider
        chroma_path = Path(__file__).resolve().parents[3] / "chroma_db"
        chroma_path.mkdir(exist_ok=True)
        self.fallback_path = chroma_path / f"{collection_name}.json"
        self.collection = None
        try:
            import chromadb

            self.client = chromadb.PersistentClient(path=str(chroma_path))
            self.collection = self.client.get_or_create_collection(name=collection_name)
        except Exception as exc:
            print(f"VectorStore fallback active: {exc}")

    def add(self, ids: list[str], texts: list[str], embeddings: list[list[float]], metadatas: list[dict] = None) -> None:
        metadatas = metadatas or [{} for _ in ids]
        if self.collection is None:
            self._fallback_upsert(ids, texts, embeddings, metadatas)
            return

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(self, embedding: list[float], top_k: int = 3) -> list[dict]:
        if self.collection is None:
            return self._fallback_search(embedding, top_k)

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )
        return results

    def all_documents(self) -> dict:
        if self.collection is None:
            items = self._read_fallback_items()
            return {
                "documents": [[item.get("document", "") for item in items]],
                "metadatas": [[item.get("metadata", {}) for item in items]],
            }

        results = self.collection.get(include=["documents", "metadatas"])
        return {
            "documents": [results.get("documents", [])],
            "metadatas": [results.get("metadatas", [])],
        }

    def prune_missing_sources(self, documents_dir: str | Path) -> int:
        documents_path = Path(documents_dir).resolve()
        valid_sources = {
            self._source_key(path)
            for path in documents_path.iterdir()
            if path.is_file()
        }

        if self.collection is not None:
            return 0

        items = self._read_fallback_items()
        kept = []
        removed_count = 0
        for item in items:
            metadata = item.get("metadata", {}) or {}
            source = metadata.get("source", "")
            if self._source_key(source) in valid_sources:
                kept.append(item)
            else:
                removed_count += 1

        if removed_count:
            self._write_fallback_items(kept)
        return removed_count

    def _read_fallback_items(self) -> list[dict]:
        if not self.fallback_path.exists():
            return []
        try:
            return json.loads(self.fallback_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _write_fallback_items(self, items: list[dict]) -> None:
        self.fallback_path.write_text(
            json.dumps(items, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _fallback_upsert(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        items_by_id = {item["id"]: item for item in self._read_fallback_items()}
        for item_id, text, vector, metadata in zip(ids, texts, embeddings, metadatas):
            items_by_id[item_id] = {
                "id": item_id,
                "document": text,
                "embedding": vector,
                "metadata": metadata,
            }
        self._write_fallback_items(list(items_by_id.values()))

    def _fallback_search(self, embedding: list[float], top_k: int) -> dict:
        scored = []
        for item in self._read_fallback_items():
            score = self._cosine_similarity(embedding, item.get("embedding", []))
            scored.append((score, item))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        selected = [item for _, item in scored[:top_k]]
        return {
            "documents": [[item.get("document", "") for item in selected]],
            "metadatas": [[item.get("metadata", {}) for item in selected]],
        }

    @staticmethod
    def _cosine_similarity(left: list[float], right: list[float]) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        dot = sum(a * b for a, b in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 0.0
        return dot / (left_norm * right_norm)

    @staticmethod
    def _source_key(source) -> str:
        try:
            path = Path(str(source))
            return path.resolve().name.lower()
        except Exception:
            return str(source).replace("\\", "/").split("/")[-1].lower()

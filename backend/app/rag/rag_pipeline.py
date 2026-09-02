import re

from .document import Document
from .embeddings import EmbeddingModel
from .llm import LLMClient
from .loader import DocumentLoader
from .prompt import PromptBuilder
from .retriever import Retriever, normalize_text, tokenize
from .text_splitter import TextSplitter
from .vector_store import VectorStore


class RAGPipeline:
    def __init__(self, openai_api_key: str = None):
        self.loader = DocumentLoader()
        self.splitter = TextSplitter()
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(self.embedding_model)
        self.retriever = Retriever(
            store=self.vector_store,
            embedding_provider=self.embedding_model,
        )
        self.prompt_builder = PromptBuilder()
        self.llm = LLMClient(api_key=openai_api_key)

    def add_document(self, file_path: str) -> None:
        documents = self.loader.load(file_path)
        chunks = self.splitter.split(documents)

        ids = []
        texts = []
        embeddings = []
        metadatas = []

        for index, chunk in enumerate(chunks):
            ids.append(f"{file_path}_{index}")
            texts.append(chunk.page_content)
            embeddings.append(self.embedding_model.embed(chunk.page_content))
            metadatas.append(chunk.metadata)

        self.vector_store.add(ids, texts, embeddings, metadatas)

    def query(self, question: str) -> str:
        results = self.retriever.retrieve(question, top_k=3)
        context = [result["text"] for result in results]
        prompt = self.prompt_builder.build(question, context)
        response = self.llm.generate(prompt)
        return response or self._retrieval_only_answer(context, question)

    def ask(self, question: str) -> dict:
        results = self.retriever.retrieve(question, top_k=3)
        context = [result["text"] for result in results]
        prompt = self.prompt_builder.build(question, context)
        answer = self.llm.generate(prompt) or self._retrieval_only_answer(context, question)
        sources = []
        seen_sources = set()
        for result in results:
            metadata = result.get("metadata", {}) or {}
            source = metadata.get("source", metadata.get("filename", "unknown"))
            filename = str(source).replace("\\", "/").split("/")[-1] if source else "unknown"
            if filename not in seen_sources:
                sources.append({"filename": filename})
                seen_sources.add(filename)
        return {"answer": answer, "sources": sources}

    @staticmethod
    def _retrieval_only_answer(context: list[str], question: str = "") -> str:
        if not context:
            return "Aucune information pertinente n'a ete trouvee dans les documents indexes pour repondre a cette question."

        excerpts = RAGPipeline._best_sentences(context, question)
        if len(excerpts) == 1:
            return f"D'apres les documents internes : {excerpts[0]}"
        return "D'apres les documents internes :\n\n- " + "\n- ".join(excerpts)

    @staticmethod
    def _best_sentences(context: list[str], question: str) -> list[str]:
        query_terms = set(tokenize(question))
        candidates = []
        for chunk in context[:5]:
            objective_match = re.search(r"Ce document d[eé]crit\b.*?(?:\.|$)", chunk, re.IGNORECASE | re.DOTALL)
            if objective_match:
                objective_sentence = " ".join(objective_match.group(0).split()).rstrip(".")
                candidates.append((100, objective_sentence))

            for sentence in RAGPipeline._split_sentences(chunk):
                clean_sentence = " ".join(sentence.split())
                if len(clean_sentence) < 25:
                    continue

                sentence_terms = set(tokenize(clean_sentence))
                score = len(query_terms & sentence_terms)
                normalized = normalize_text(clean_sentence)
                if "ce document decrit" in normalized:
                    score += 10
                if "procedure de renouvellement" in normalized:
                    score += 8
                if "security token service" in normalized or "sts" in sentence_terms:
                    score += 5
                if "misagri" in sentence_terms or "sharepoint" in sentence_terms:
                    score += 4
                candidates.append((score, clean_sentence))

        candidates.sort(key=lambda item: item[0], reverse=True)
        selected = []
        seen = set()
        for score, sentence in candidates:
            key = normalize_text(sentence[:140])
            if score <= 0 or key in seen:
                continue
            selected.append(sentence[:700])
            seen.add(key)
            if "ce document decrit" in normalize_text(sentence):
                break
            if len(selected) >= 3:
                break

        if selected:
            return selected

        return [" ".join(chunk.split())[:700] for chunk in context[:3] if chunk.strip()]

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        prepared = text.replace("\n", " ")
        parts = []
        for part in prepared.split("."):
            part = part.strip()
            if part:
                parts.append(part)
        return parts

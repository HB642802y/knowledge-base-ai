from .loader import DocumentLoader
from .text_splitter import TextSplitter
from .embeddings import EmbeddingModel
from .vector_store import VectorStore
from .retriever import Retriever
from .prompt import PromptBuilder
from .llm import LLMClient


class RAGPipeline:
    def __init__(self, openai_api_key: str = None):
        self.loader = DocumentLoader()
        self.splitter = TextSplitter()
        self.embedding_model = EmbeddingModel()
        self.vector_store = VectorStore(self.embedding_model)
        self.retriever = Retriever(
            store=self.vector_store,
            embedding_provider=self.embedding_model
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

        for i, chunk in enumerate(chunks):
            ids.append(f"{file_path}_{i}")
            texts.append(chunk.page_content)
            embeddings.append(self.embedding_model.embed(chunk.page_content))
            metadatas.append(chunk.metadata)

        self.vector_store.add(ids, texts, embeddings, metadatas)

    def query(self, question: str) -> str:
        results = self.retriever.retrieve(question, top_k=3)
        context = [result['text'] for result in results]
        prompt = self.prompt_builder.build(question, context)
        response = self.llm.generate(prompt)
        return response or self._retrieval_only_answer(context)

    @staticmethod
    def _retrieval_only_answer(context: list[str]) -> str:
        """Return transparent evidence when the LLM provider is unavailable."""
        if not context:
            return (
                "Aucune information pertinente n’a été trouvée dans les documents "
                "indexés pour répondre à cette question."
            )

        excerpts = []
        for chunk in context[:3]:
            clean_chunk = " ".join(chunk.split())
            if clean_chunk:
                excerpts.append(clean_chunk[:900])

        return (
            "Le service de génération IA est temporairement indisponible. "
            "Voici les extraits les plus pertinents des documents internes :\n\n- "
            + "\n- ".join(excerpts)
        )

    def ask(self, question: str) -> dict:
        results = self.retriever.retrieve(question, top_k=3)
        context = [result['text'] for result in results]
        prompt = self.prompt_builder.build(question, context)
        answer = self.llm.generate(prompt) or self._retrieval_only_answer(context)
        sources = []
        seen_sources = set()
        for result in results:
            metadata = result.get('metadata', {}) or {}
            source = metadata.get('source', metadata.get('filename', 'unknown'))
            filename = str(source).split('\\')[-1] if source else 'unknown'
            if filename not in seen_sources:
                sources.append({"filename": filename})
                seen_sources.add(filename)
        return {"answer": answer, "sources": sources}

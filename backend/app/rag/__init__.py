from importlib import import_module

__all__ = ["LLMClient", "DocumentLoader", "PromptBuilder", "Retriever", "TextSplitter", "VectorStore", "RAGPipeline", "SkillsAgent"]


def __getattr__(name):
    module_map = {
        "LLMClient": ".llm",
        "DocumentLoader": ".loader",
        "PromptBuilder": ".prompt",
        "Retriever": ".retriever",
        "TextSplitter": ".text_splitter",
        "VectorStore": ".vector_store",
        "RAGPipeline": ".rag_pipeline",
        "SkillsAgent": ".skills_agent",
    }
    if name in module_map:
        module = import_module(module_map[name], __name__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

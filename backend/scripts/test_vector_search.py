from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.rag.rag_pipeline import RAGPipeline

print("=== Initialisation du pipeline RAG ===")
pipeline = RAGPipeline()

print("\n=== Ajout du document test ===")
file_path = "../documents/test.txt"
pipeline.add_document(file_path)
print("Document ajouté avec succès!")

print("\n=== Test de recherche ===")
query = "Qu'est-ce que ce document?"
result = pipeline.ask(query)

print("\n=== Résultat ===")
print(f"Question: {query}")
print(f"Réponse: {result['answer']}")
print(f"Sources: {result['sources']}")

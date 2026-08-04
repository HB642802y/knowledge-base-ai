from app.rag import RAGPipeline


# Initialize pipeline (without OpenAI API key for now - will use mock response)
pipeline = RAGPipeline(openai_api_key=None)

# Add a document
file_path = "../documents/test.txt"
print(f"Adding document: {file_path}")
pipeline.add_document(file_path)
print("Document added successfully!")

# Query the system
question = "Qu'est-ce que ce document?"
print(f"\nQuery: {question}")
response = pipeline.query(question)
print(f"Response: {response}")

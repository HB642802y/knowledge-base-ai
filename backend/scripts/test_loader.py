from app.rag.loader import DocumentLoader
from app.rag.text_splitter import TextSplitter



file = "../documents/test.txt"


loader = DocumentLoader()

docs = loader.load(file)


print(
    "Pages chargées :",
    len(docs)
)


splitter = TextSplitter()

chunks = splitter.split(docs)


print(
    "Nombre de chunks :",
    len(chunks)
)


print(
    chunks[0].page_content
)

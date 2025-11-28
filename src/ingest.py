import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils import get_embedding_model

load_dotenv()
for var in ["DATABASE_URL", "PG_VECTOR_COLLECTION_NAME", "PDF_PATH"]:
  if not os.getenv(var):
    raise RuntimeError(f"Environment variable {var} is not set.")

PGVECTOR_COLLECTION = os.getenv("PG_VECTOR_COLLECTION_NAME")
PGVECTOR_URL = os.getenv("DATABASE_URL")
PDF_PATH = os.getenv("PDF_PATH")

def load_and_split_pdf_into_chunks():
  # Load PDF
  loader = PyPDFLoader(file_path=PDF_PATH)
  document = loader.load()
  
  # Split into chunks
  text_splitter = RecursiveCharacterTextSplitter(
    add_start_index=False,
    chunk_overlap=150, 
    chunk_size=1000, 
  )
  document_chunks = text_splitter.split_documents(document)
  if not document_chunks:
    raise RuntimeError("No document chunks were generated from the PDF. The file might be empty or unreadable.")
  
  # Remove empty metadata
  sanitized_chunks = [
    Document(
      page_content=doc.page_content,
      metadata={k: v for k, v in doc.metadata.items() if v not in (None, "", [], {})}
    )
    for doc in document_chunks
  ]
  return sanitized_chunks

def ingest_pdf():
  document_chunks = load_and_split_pdf_into_chunks()

  # Create custom IDs for each document chunk
  custom_ids = [f"doc-{i}" for i in range(len(document_chunks))]

  # Instantiate embeddings model
  embedding_model = get_embedding_model()

  # Create or connect to PGVector store
  pgvector_store = PGVector(
    collection_name=PGVECTOR_COLLECTION,
    connection=PGVECTOR_URL,
    embeddings=embedding_model,
    use_jsonb=True
  )

  # Add documents to the PGVector store
  pgvector_store.add_documents(documents=document_chunks, ids=custom_ids)

if __name__ == "__main__":
  ingest_pdf()
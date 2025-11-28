import os
from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_postgres import PGVector

from utils import get_embedding_model

load_dotenv()
for var in [ "DATABASE_URL", "PG_VECTOR_COLLECTION_NAME", "PDF_PATH"]:
  if not os.getenv(var):
    raise RuntimeError(f"Environment variable {var} is not set.")

PGVECTOR_COLLECTION = os.getenv("PG_VECTOR_COLLECTION_NAME")
PGVECTOR_URL = os.getenv("DATABASE_URL")

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def search_prompt(question=None):
  if not question:
    raise ValueError("A pergunta não pode ser vazia.")

  # Instantiate embeddings model
  embedding_model = get_embedding_model()
  
  # Create or connect to PGVector store
  pgvector_store = PGVector(
    collection_name=PGVECTOR_COLLECTION,
    connection=PGVECTOR_URL,
    embeddings=embedding_model,
    use_jsonb=True
  )

  # Perform similarity search
  search_results = pgvector_store.similarity_search(question, k=10)
  context_text = "\n\n".join([doc.page_content for doc in search_results])
  
  # Generate template for LLM
  template = PromptTemplate(
    input_variables=["contexto", "pergunta"],
    template=PROMPT_TEMPLATE,
  )

  # Instantiate LLM
  llm = ChatGoogleGenerativeAI(model=os.getenv("GOOGLE_GEMINI_MODEL"))

  # Create search chain
  search_chain = template | llm | StrOutputParser()
  
  # Invoke the chain with data
  result = search_chain.invoke({"contexto": context_text, "pergunta": question})
  return result

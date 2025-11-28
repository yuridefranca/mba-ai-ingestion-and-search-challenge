# Copilot Instructions - RAG System with LangChain + pgVector

## Project Overview

This is a **Retrieval-Augmented Generation (RAG)** system for semantic search over PDF documents. The architecture follows a three-stage pipeline: **ingest → store → search**, using LangChain for orchestration and PostgreSQL with pgVector for vector storage.

## Architecture & Data Flow

### 1. Ingest Pipeline (`src/ingest.py`)

-   Loads PDF → Splits into 1000-char chunks (150 overlap) → Generates embeddings → Stores in pgVector
-   **Critical**: Uses `utils.get_embedding_model()` which switches models via `MODEL_TYPE` env var
-   Chunks are sanitized (empty metadata removed) before storage to avoid serialization issues
-   Sequential IDs format: `doc-0`, `doc-1`, etc.

### 2. Search Pipeline (`src/search.py`)

-   Retrieves top 10 similar chunks → Formats context → Calls LLM with strict prompt → Returns answer
-   **Pattern**: Chain is built as `template | llm | StrOutputParser()` then invoked with data dict
-   Context assembly: `"\n\n".join([doc.page_content for doc in search_results])`

### 3. Chat Interface (`src/chat.py`)

-   Simple CLI loop calling `search_prompt()` - no conversation history maintained

## Critical Conventions

### Environment-Based Model Switching (`src/utils.py`)

```python
MODEL_TYPE=free   # Uses HuggingFace (local, no API key)
MODEL_TYPE=gemini # Uses Google Gemini embeddings
MODEL_TYPE=openai # Uses OpenAI embeddings
```

**Rule**: Both `ingest.py` and `search.py` MUST use identical embedding models. Switching models requires re-ingesting all documents.

### Code Style

-   **Indentation**: 2 spaces (configured in `.vscode/settings.json`)
-   **Imports**: Group by standard lib → third-party → local, with blank lines between
-   **Error handling**: Validate required env vars at module load with explicit `RuntimeError` messages

### PGVector Connection Pattern

```python
pgvector_store = PGVector(
  collection_name=PGVECTOR_COLLECTION,
  connection=PGVECTOR_URL,        # Note: "connection" not "connection_string"
  embeddings=embedding_model,     # Note: "embeddings" not "embedding"
  use_jsonb=True
)
```

## Developer Workflows

### Initial Setup

```bash
# 1. Start PostgreSQL with pgVector
docker compose up -d

# 2. Activate venv (packages installed in .venv/)
source .venv/bin/activate  # or just use .venv/bin/python directly

# 3. Configure environment
cp .env.example .env
# Edit .env: Set MODEL_TYPE, DATABASE_URL, PG_VECTOR_COLLECTION_NAME, PDF_PATH

# 4. Ingest document
python src/ingest.py

# 5. Run chat
python src/chat.py
```

### Common Errors & Fixes

-   **"No module named 'dotenv'"**: Using system python instead of venv - use `.venv/bin/python` or activate venv
-   **Pydantic validation error on model=None**: Missing env var (e.g., `GOOGLE_GEMINI_MODEL`)
-   **429 quota exceeded**: Switch to `MODEL_TYPE=free` in development, use paid models in production
-   **Vector dimension mismatch**: Embedding model changed - clear PGVector collection and re-ingest

### Package Management

-   Dependencies pinned in `requirements.txt` (generated via `pip freeze`)
-   Key packages: `langchain-postgres`, `langchain-huggingface`, `langchain-google-genai`, `sentence-transformers`, `torch`

## RAG-Specific Patterns

### Strict Context-Only Responses

The prompt enforces **no hallucination** by explicitly instructing:

-   Only answer from provided context
-   Default response: "Não tenho informações necessárias para responder sua pergunta."
-   Never use external knowledge or opinions

### Chain Invocation Anti-Pattern

❌ **Don't bake values into chain definition:**

```python
chain = {"contexto": context_text, "pergunta": question} | template | llm
```

This makes chain non-reusable. Each invocation requires rebuilding the chain.

✅ **Do pass values at invocation:**

```python
chain = template | llm | StrOutputParser()
result = chain.invoke({"contexto": context_text, "pergunta": question})
```

## Testing & Validation

-   No automated test suite - validate manually via `chat.py`
-   Test with questions both **in-context** (should answer from PDF) and **out-of-context** (should refuse)
-   Verify database connection: `docker exec -it postgres_rag psql -U postgres -d rag -c "SELECT COUNT(*) FROM langchain_pg_collection;"`

## Project Constraints

-   **MBA coursework project** - follows strict requirements in `Requirements.md`
-   Must use LangChain (no direct embedding API calls)
-   Must use pgVector (no alternative vector stores)
-   CLI-only interface (no web UI)

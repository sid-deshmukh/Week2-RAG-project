"""Central settings for Ask Mufasa. Secrets come from the project's .env file."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

REQUIRED_KEYS = ("OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME", "LLAMA_CLOUD_API_KEY")

# LLM + embeddings (both OpenAI, called through LangChain)
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4.1-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Pinecone. The embedding dimension is read from the index itself, so it always matches.
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "")
NAMESPACE = os.getenv("PINECONE_NAMESPACE", "toddler-book")
# One small record per uploaded PDF, so the sidebar can list sources without scanning chunks.
SOURCES_NAMESPACE = f"{NAMESPACE}-sources"

# LlamaParse tier: fast | cost_effective | agentic | agentic_plus
LLAMA_PARSE_TIER = os.getenv("LLAMA_PARSE_TIER", "cost_effective")

# Chunking. PDF pages are longer than the notebook's support docs, so chunks are larger.
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Retrieval
TOP_K = 6
HISTORY_TURNS = 6  # previous user/assistant pairs sent to the agent


def missing_keys() -> list[str]:
    return [key for key in REQUIRED_KEYS if not os.getenv(key)]

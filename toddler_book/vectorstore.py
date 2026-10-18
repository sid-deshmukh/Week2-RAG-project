"""Pinecone access: chunk storage, filtered search, and the per-PDF source registry.

Chunk vectors live in `config.NAMESPACE` with ids "<doc_id>#<chunk_index>", so all
chunks of one PDF can be listed (and deleted) by id prefix. Each PDF also gets one
record in `config.SOURCES_NAMESPACE` holding its name and stats for the sidebar.
"""

import os
from dataclasses import asdict, dataclass
from functools import lru_cache

from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

from toddler_book import config


@dataclass(frozen=True)
class Source:
    doc_id: str
    file_name: str
    num_pages: int
    num_chunks: int
    indexed_at: str


@lru_cache
def _pinecone() -> Pinecone:
    return Pinecone(api_key=os.environ["PINECONE_API_KEY"])


@lru_cache
def get_index():
    return _pinecone().Index(config.PINECONE_INDEX_NAME)


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    dimension = _pinecone().describe_index(config.PINECONE_INDEX_NAME).dimension
    return OpenAIEmbeddings(model=config.EMBEDDING_MODEL, dimensions=dimension)


@lru_cache
def get_vector_store() -> PineconeVectorStore:
    return PineconeVectorStore(index=get_index(), embedding=get_embeddings(), namespace=config.NAMESPACE)


def add_chunks(chunks: list[Document], doc_id: str) -> list[str]:
    ids = [f"{doc_id}#{chunk.metadata['chunk_index']}" for chunk in chunks]
    return get_vector_store().add_documents(chunks, ids=ids)


def search(query: str, doc_ids: list[str], k: int = config.TOP_K) -> list[tuple[Document, float]]:
    """Similarity search restricted to the given PDFs."""
    if not doc_ids:
        return []
    return get_vector_store().similarity_search_with_score(query, k=k, filter={"doc_id": {"$in": doc_ids}})


# --- source registry -------------------------------------------------------------


def register_source(source: Source) -> None:
    # Pinecone needs a non-zero vector for cosine; embedding the file name is cheap and harmless.
    vector = get_embeddings().embed_query(source.file_name)
    get_index().upsert(
        vectors=[{"id": source.doc_id, "values": vector, "metadata": asdict(source)}],
        namespace=config.SOURCES_NAMESPACE,
    )


def _to_source(metadata: dict) -> Source:
    return Source(
        doc_id=metadata["doc_id"],
        file_name=metadata["file_name"],
        num_pages=int(metadata["num_pages"]),
        num_chunks=int(metadata["num_chunks"]),
        indexed_at=metadata["indexed_at"],
    )


def get_source(doc_id: str) -> Source | None:
    record = get_index().fetch(ids=[doc_id], namespace=config.SOURCES_NAMESPACE).vectors.get(doc_id)
    return _to_source(record.metadata) if record else None


def list_sources() -> list[Source]:
    index = get_index()
    sources = []
    for id_page in index.list(namespace=config.SOURCES_NAMESPACE):
        fetched = index.fetch(ids=list(id_page), namespace=config.SOURCES_NAMESPACE).vectors
        sources.extend(_to_source(record.metadata) for record in fetched.values())
    return sorted(sources, key=lambda s: s.indexed_at)


def delete_source(doc_id: str) -> None:
    index = get_index()
    for id_page in index.list(prefix=f"{doc_id}#", namespace=config.NAMESPACE):
        index.delete(ids=list(id_page), namespace=config.NAMESPACE)
    index.delete(ids=[doc_id], namespace=config.SOURCES_NAMESPACE)

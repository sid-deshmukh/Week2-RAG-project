"""The ingestion pipeline run on every upload: parse → chunk → embed → store."""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from toddler_book import vectorstore
from toddler_book.ingestion.chunker import chunk_pages
from toddler_book.ingestion.parser import parse_pdf
from toddler_book.vectorstore import Source

ProgressFn = Callable[[str], None]


@dataclass(frozen=True)
class IngestResult:
    source: Source
    already_indexed: bool


def compute_doc_id(file_bytes: bytes) -> str:
    """Content hash, so re-uploading the same PDF (even renamed) is a no-op."""
    return hashlib.sha256(file_bytes).hexdigest()[:16]


def ingest_pdf(file_bytes: bytes, file_name: str, on_progress: ProgressFn = lambda _: None) -> IngestResult:
    doc_id = compute_doc_id(file_bytes)

    existing = vectorstore.get_source(doc_id)
    if existing:
        return IngestResult(source=existing, already_indexed=True)

    on_progress("Parsing PDF with LlamaParse…")
    pages = parse_pdf(file_bytes, file_name)

    on_progress(f"Parsed {len(pages)} pages. Chunking…")
    chunks = chunk_pages(pages, doc_id=doc_id, file_name=file_name)

    on_progress(f"Embedding {len(chunks)} chunks and storing them in Pinecone…")
    vectorstore.add_chunks(chunks, doc_id=doc_id)

    source = Source(
        doc_id=doc_id,
        file_name=file_name,
        num_pages=len(pages),
        num_chunks=len(chunks),
        indexed_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
    vectorstore.register_source(source)
    return IngestResult(source=source, already_indexed=False)

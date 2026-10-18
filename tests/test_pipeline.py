"""Pipeline tests with LlamaParse and Pinecone replaced by fakes."""

import pytest
from llama_index.core import Document as LlamaDocument

from toddler_book.ingestion import pipeline
from toddler_book.vectorstore import Source


@pytest.fixture
def fake_backends(monkeypatch):
    calls = {"parse": 0, "stored": [], "registered": []}

    def fake_parse(file_bytes, file_name):
        calls["parse"] += 1
        return [LlamaDocument(text="Hello world. " * 200, metadata={"file_name": file_name, "page": 1})]

    registry: dict[str, Source] = {}

    def register(source):
        registry[source.doc_id] = source
        calls["registered"].append(source)

    monkeypatch.setattr(pipeline, "parse_pdf", fake_parse)
    monkeypatch.setattr(pipeline.vectorstore, "get_source", registry.get)
    monkeypatch.setattr(pipeline.vectorstore, "add_chunks", lambda chunks, doc_id: calls["stored"].extend(chunks))
    monkeypatch.setattr(pipeline.vectorstore, "register_source", register)
    return calls


def test_ingest_parses_chunks_and_registers(fake_backends):
    result = pipeline.ingest_pdf(b"%PDF-fake", "notes.pdf")

    assert not result.already_indexed
    assert result.source.file_name == "notes.pdf"
    assert result.source.num_pages == 1
    assert result.source.num_chunks == len(fake_backends["stored"]) > 1
    assert fake_backends["registered"] == [result.source]


def test_reupload_of_same_bytes_is_skipped(fake_backends):
    first = pipeline.ingest_pdf(b"%PDF-fake", "notes.pdf")
    second = pipeline.ingest_pdf(b"%PDF-fake", "renamed.pdf")

    assert second.already_indexed
    assert second.source == first.source
    assert fake_backends["parse"] == 1

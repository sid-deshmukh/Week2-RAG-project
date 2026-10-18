from llama_index.core import Document as LlamaDocument

from toddler_book import config
from toddler_book.ingestion.chunker import chunk_pages


def make_page(page: int, words: int) -> LlamaDocument:
    return LlamaDocument(text=" ".join(f"word{i}" for i in range(words)), metadata={"page": page})


def test_chunks_carry_source_and_page_metadata():
    pages = [make_page(1, 50), make_page(2, 600)]
    chunks = chunk_pages(pages, doc_id="abc", file_name="book.pdf")

    assert len(chunks) > 2  # page 2 is long enough to split
    assert {c.metadata["page"] for c in chunks} == {1, 2}
    assert all(c.metadata["doc_id"] == "abc" and c.metadata["file_name"] == "book.pdf" for c in chunks)
    assert all(len(c.page_content) <= config.CHUNK_SIZE for c in chunks)


def test_chunk_index_is_unique_and_sequential():
    chunks = chunk_pages([make_page(1, 600), make_page(2, 600)], doc_id="abc", file_name="book.pdf")
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))

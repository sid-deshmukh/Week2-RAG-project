"""Split parsed pages into LangChain chunks, keeping page-level metadata on every chunk."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core import Document as LlamaDocument

from toddler_book import config


def chunk_pages(pages: list[LlamaDocument], doc_id: str, file_name: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        add_start_index=True,  # offset within the page
    )
    page_docs = [
        Document(
            page_content=page.text,
            metadata={"doc_id": doc_id, "file_name": file_name, "page": page.metadata["page"]},
        )
        for page in pages
    ]
    chunks = splitter.split_documents(page_docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    return chunks

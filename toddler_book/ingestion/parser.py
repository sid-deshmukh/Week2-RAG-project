"""PDF parsing with LlamaParse (LlamaIndex cloud parser).

Each parsed page becomes one LlamaIndex Document carrying its page number,
so every chunk downstream can be cited back to a page.
"""

import os

from llama_cloud import LlamaCloud
from llama_index.core import Document as LlamaDocument

from toddler_book import config


class ParseError(RuntimeError):
    pass


def parse_pdf(file_bytes: bytes, file_name: str) -> list[LlamaDocument]:
    client = LlamaCloud(api_key=os.environ["LLAMA_CLOUD_API_KEY"])
    result = client.parsing.parse(
        tier=config.LLAMA_PARSE_TIER,
        version="latest",
        upload_file=(file_name, file_bytes, "application/pdf"),
        expand=["markdown"],
    )

    if result.job.status != "COMPLETED":
        raise ParseError(f"LlamaParse job {result.job.status.lower()}: {result.job.error_message or 'no details'}")
    if result.markdown is None:
        raise ParseError("LlamaParse returned no markdown for this file.")

    pages = [
        LlamaDocument(
            text=page.markdown,
            metadata={"file_name": file_name, "page": page.page_number},
        )
        for page in result.markdown.pages
        if page.success and page.markdown.strip()
    ]
    if not pages:
        raise ParseError("No text could be extracted from this PDF (is it a scanned image?).")
    return pages

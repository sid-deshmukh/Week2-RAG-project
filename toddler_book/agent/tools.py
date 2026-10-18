"""Tools the agent can call. They are built per request, bound to the sources the user selected."""

from langchain_core.tools import BaseTool, tool

from toddler_book import config, vectorstore
from toddler_book.vectorstore import Source


def make_tools(sources: list[Source]) -> list[BaseTool]:
    doc_ids = [s.doc_id for s in sources]

    @tool(response_format="content_and_artifact")
    def search_sources(query: str) -> tuple[str, list[dict]]:
        """Semantic search over the user's selected PDF sources.

        Returns the most relevant passages, each labelled [file_name, p.N].
        Call it again with a different query if the results don't answer the question.

        Args:
            query: A focused search query, e.g. key terms from the user's question.
        """
        results = vectorstore.search(query, doc_ids, k=config.TOP_K)
        if not results:
            return "No relevant passages found in the selected sources.", []

        passages, citations = [], []
        for doc, score in results:
            file_name, page = doc.metadata["file_name"], int(doc.metadata["page"])
            passages.append(f"[{file_name}, p.{page}]\n{doc.page_content}")
            citations.append({"file_name": file_name, "page": page, "score": score, "text": doc.page_content})
        return "\n\n---\n\n".join(passages), citations

    @tool
    def list_sources() -> str:
        """List the PDF sources currently selected for this chat, with their page counts."""
        if not sources:
            return "No sources are selected."
        return "\n".join(f"- {s.file_name} ({s.num_pages} pages)" for s in sources)

    return [search_sources, list_sources]

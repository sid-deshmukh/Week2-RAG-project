"""The LangChain agent and a streaming wrapper the UI can consume."""

import re
from collections.abc import Callable, Iterator

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from langchain_openai import ChatOpenAI

from toddler_book import config
from toddler_book.agent.prompts import SYSTEM_PROMPT
from toddler_book.agent.tools import make_tools
from toddler_book.vectorstore import Source

BRACKET_RE = re.compile(r"\[([^\[\]]+)\]")
# One citation inside a bracket: "file.pdf, p.3" or a range "file.pdf, pp. 3-4"
CITATION_RE = re.compile(r"^\s*(.+?),\s*(?:pp?|pages?)\.?\s*(\d+)(?:\s*[-–]\s*(\d+))?\s*$", re.IGNORECASE)


def parse_citations(answer: str) -> set[tuple[str, int]]:
    """(file_name, page) pairs cited in the answer; handles ranges and "a, p.1; b, p.2" groups."""
    cited = set()
    for group in BRACKET_RE.findall(answer):
        for part in group.split(";"):
            if match := CITATION_RE.match(part):
                name, first, last = match.group(1).strip(), int(match.group(2)), int(match.group(3) or match.group(2))
                cited.update((name, page) for page in range(first, max(first, last) + 1))
    return cited


def build_agent(sources: list[Source]):
    model = ChatOpenAI(model=config.CHAT_MODEL, temperature=0)
    return create_agent(model=model, tools=make_tools(sources), system_prompt=SYSTEM_PROMPT)


class AnswerStream:
    """Iterate to get answer text tokens; afterwards `.citations` holds the retrieved passages.

    `on_search` is called with each query the agent sends to `search_sources`.
    """

    def __init__(
        self,
        question: str,
        history: list[dict],
        sources: list[Source],
        on_search: Callable[[str], None] = lambda _: None,
    ):
        self.question = question
        self.history = history[-2 * config.HISTORY_TURNS :]
        self.sources = sources
        self.on_search = on_search
        self.retrieved: list[dict] = []
        self.answer = ""

    def __iter__(self) -> Iterator[str]:
        agent = build_agent(self.sources)
        messages = [{"role": m["role"], "content": m["content"]} for m in self.history]
        messages.append({"role": "user", "content": self.question})

        for mode, data in agent.stream({"messages": messages}, stream_mode=["messages", "updates"]):
            if mode == "messages":
                chunk, meta = data
                if isinstance(chunk, AIMessageChunk) and meta.get("langgraph_node") == "model" and chunk.text:
                    self.answer += chunk.text
                    yield chunk.text
            else:  # "updates": complete messages once each node finishes
                for update in data.values():
                    for msg in (update or {}).get("messages", []):
                        if isinstance(msg, AIMessage):
                            for call in msg.tool_calls:
                                if call["name"] == "search_sources":
                                    self.on_search(call["args"].get("query", ""))
                        elif isinstance(msg, ToolMessage) and msg.artifact:
                            self.retrieved.extend(msg.artifact)

    @property
    def citations(self) -> list[dict]:
        return cited_passages(self.answer, self.retrieved)


def cited_passages(answer: str, retrieved: list[dict]) -> list[dict]:
    """Passages the answer actually cites (by file + page), deduplicated, in page order.

    An answer without citations (e.g. "I couldn't find that") gets no sources listed.
    """
    unique = list({(p["file_name"], p["page"], p["text"]): p for p in retrieved}.values())
    cited = parse_citations(answer)
    matched = [p for p in unique if (p["file_name"], p["page"]) in cited]
    return sorted(matched, key=lambda p: (p["file_name"], p["page"]))

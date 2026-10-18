# 🦁 Ask Mufasa

A NotebookLM-style app: upload PDFs, then chat with an agent that answers **only from your
sources** and cites the page each fact came from.

- **UI:** Streamlit — sidebar for sources, main pane for chat
- **Parsing:** LlamaParse (LlamaIndex cloud parser), one document per page
- **Chunking:** LangChain `RecursiveCharacterTextSplitter` (1000 chars / 200 overlap)
- **Vector DB:** Pinecone, embeddings from OpenAI `text-embedding-3-small`
- **Agent:** LangChain `create_agent` + `ChatOpenAI` (`gpt-4.1-mini`) with a `search_sources` tool

## How it works

```
Upload PDF ─► hash bytes → doc_id (skip if already indexed)
          ─► LlamaParse → markdown per page
          ─► split into chunks, each tagged {doc_id, file_name, page, chunk_index}
          ─► embed + upsert to Pinecone (ids "<doc_id>#<n>"), register source record

Question  ─► agent decides to call search_sources(query)   ← may search several times
             └─ Pinecone similarity search filtered to the ticked sources
          ─► answer streamed with inline citations [file.pdf, p.N]
          ─► cited passages shown under the answer
```

Unlike the basic notebook pipeline (always retrieve once, then generate), retrieval is a
**tool**: the agent rewrites queries, runs extra searches for broad questions, uses chat
history for follow-ups, and skips searching for small talk.

## Setup

1. Create a Pinecone **serverless index** with the **cosine** metric. Any dimension that
   `text-embedding-3-small` supports works (e.g. 512, 1024, 1536) — the app reads it from the index.
2. Copy `.env.example` to `.env` and fill in the keys.
3. Install and run:

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e . pytest
.venv/bin/streamlit run app.py
```

(or `uv sync && uv run streamlit run app.py`)

Run the tests with `.venv/bin/pytest`.

## Project layout

```
app.py                      Streamlit entry point
toddler_book/
  config.py                 models, chunking, namespaces, env loading
  vectorstore.py            Pinecone: add/search chunks, source registry, delete
  ingestion/
    parser.py               LlamaParse → LlamaIndex Documents (per page)
    chunker.py              page Documents → LangChain chunks with metadata
    pipeline.py             ingest_pdf(): parse → chunk → embed → store
  agent/
    prompts.py              grounded-answer system prompt
    tools.py                search_sources, list_sources
    agent.py                create_agent + AnswerStream (streaming + citations)
  ui/
    state.py                session state (sources, selection, chat history)
    sidebar.py              uploader + source list
    chat.py                 chat, starter prompts, citation expander
    theme.py                kid-friendly CSS, sky banner, empty-state art
.streamlit/config.toml      theme colours and fonts (Nunito + Fredoka)
tests/                      chunker, pipeline (mocked backends), citation parsing
```

## Notes

- Pinecone data lives in namespace `toddler-book` (chunks) and `toddler-book-sources` (one
  record per PDF). Override with `PINECONE_NAMESPACE`.
- Re-uploading the same file (even renamed) is detected by content hash and skipped.
- Deleting a source in the sidebar removes all of its vectors.
- If a complex or scanned PDF parses poorly, try a higher LlamaParse tier: `LLAMA_PARSE_TIER=agentic`.

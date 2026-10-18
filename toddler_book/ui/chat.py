"""Main pane: chat with the agent, with streamed answers and page citations."""

import streamlit as st

from toddler_book.agent.agent import AnswerStream
from toddler_book.ui import state, theme

STARTER_PROMPTS = [
    "✨ Summarize my books",
    "🧩 What are the main topics?",
    "📖 Explain the important words",
]
AVATARS = {"user": theme.USER_AVATAR, "assistant": theme.ASSISTANT_AVATAR}


def render_chat() -> None:
    sources = state.selected_sources()
    theme.render_hero(compact=bool(st.session_state.messages))

    if not st.session_state.sources:
        theme.render_empty_state()
        return

    if sources:
        shelf = [s.doc_id for s in st.session_state.sources]
        theme.render_source_chips([(theme.book_style(shelf.index(s.doc_id))[0], s.file_name) for s in sources])
    else:
        st.warning("Tick at least one book on your bookshelf to start chatting.", icon="📚")

    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
            st.markdown(message["content"])
            _render_citations(message.get("citations", []))

    # chat_input is pinned to the bottom wherever it's called; read it first so the
    # starter buttons can disappear as soon as a question is asked.
    prompt = st.chat_input("Ask a question about your books…", disabled=not sources) or st.session_state.pending_prompt
    st.session_state.pending_prompt = None

    if not st.session_state.messages and sources and not prompt:
        _render_starters()

    if prompt and sources:
        _answer(prompt, sources)


def _render_starters() -> None:
    st.markdown("**Not sure what to ask? Try one of these:**")
    with st.container(key="starters"):
        cols = st.columns(len(STARTER_PROMPTS))
        for col, text in zip(cols, STARTER_PROMPTS):
            if col.button(text, use_container_width=True):
                st.session_state.pending_prompt = text.split(" ", 1)[1]  # drop the emoji
                st.rerun()


def _answer(prompt: str, sources) -> None:
    history = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=theme.USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=theme.ASSISTANT_AVATAR):
        searches = st.status("🐾 Thinking…", expanded=False)
        queries: list[str] = []

        def on_search(query: str) -> None:
            queries.append(query)
            searches.update(label=f"🐾 Sniffing through your books ({len(queries)})…")
            searches.write(f"🔎 {query}")

        stream = AnswerStream(prompt, history, sources, on_search=on_search)
        try:
            answer = st.write_stream(stream)
        except Exception as exc:
            searches.update(label="Oops! Something went wrong", state="error")
            st.error(f"Couldn't generate an answer: {exc}")
            st.session_state.messages.pop()
            return
        label = f"🐾 Looked through your books {len(queries)} time(s)" if queries else "Answered without searching"
        searches.update(label=label, state="complete")
        citations = stream.citations
        _render_citations(citations)

    st.session_state.messages.append({"role": "assistant", "content": answer, "citations": citations})


def _render_citations(citations: list[dict]) -> None:
    if not citations:
        return
    with st.expander(f"📖 Where I found this ({len(citations)} passages)"):
        for c in citations:
            st.markdown(f"**{c['file_name']} · page {c['page']}**")
            st.caption(c["text"][:600] + ("…" if len(c["text"]) > 600 else ""))

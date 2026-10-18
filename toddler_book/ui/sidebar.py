"""Sidebar "bookshelf": upload PDFs (runs the ingestion pipeline) and manage sources."""

import streamlit as st

from toddler_book import vectorstore
from toddler_book.ingestion.pipeline import ingest_pdf
from toddler_book.ui import state, theme


def render_sidebar() -> None:
    while st.session_state.flash:
        message, icon = st.session_state.flash.pop(0)
        st.toast(message, icon=icon)

    with st.sidebar:
        st.title("📚 My Bookshelf")

        _render_uploader()
        st.divider()
        _render_sources()

        if st.session_state.messages:
            st.divider()
            if st.button("Start a new chat", icon=":material/refresh:", use_container_width=True):
                st.session_state.messages = []
                st.rerun()


def _render_uploader() -> None:
    files = st.file_uploader(
        "Add a book (PDF)",
        type="pdf",
        accept_multiple_files=True,
        key=f"uploader_{st.session_state.uploader_key}",
    )
    if not files:
        return

    for file in files:
        with st.status(f"🐾 Reading {file.name}…", expanded=True) as status:
            try:
                result = ingest_pdf(file.getvalue(), file.name, on_progress=status.write)
            except Exception as exc:  # surface parser / API errors in the UI
                status.update(label=f"Oops! Couldn't read {file.name}", state="error")
                st.session_state.flash.append((f"Couldn't index {file.name}: {exc}", ":material/error:"))
                continue
            state.add_source(result.source)
            if result.already_indexed:
                st.session_state.flash.append((f"{file.name} is already on your bookshelf", ":material/info:"))
            else:
                s = result.source
                msg = f"Added {s.file_name} to your bookshelf ({s.num_pages} pages)"
                st.session_state.flash.append((msg, ":material/check_circle:"))
            status.update(label=f"Done: {file.name}", state="complete", expanded=False)

    # A fresh uploader key clears the widget so the same files aren't re-processed on rerun.
    st.session_state.uploader_key += 1
    st.rerun()


def _render_sources() -> None:
    sources = st.session_state.sources
    st.subheader(f"Books ({len(sources)})")
    if not sources:
        st.caption("No books yet. Add one above!")
        return

    st.caption("Tick the books to ask about.")
    theme.render_spine_colours([s.doc_id for s in sources])
    for i, source in enumerate(sources):
        emoji, _ = theme.book_style(i)
        with st.container(key=f"book_{source.doc_id}"):
            check_col, delete_col = st.columns([0.82, 0.18], vertical_alignment="center")
            with check_col:
                st.checkbox(
                    f"{emoji} {source.file_name}",
                    key=state.selection_key(source),
                    help=f"{source.num_pages} pages · {source.num_chunks} chunks · added {source.indexed_at[:10]}",
                )
            with delete_col:
                with st.popover("", icon=":material/delete:", help="Remove book"):
                    st.write(f"Remove **{source.file_name}** from your bookshelf? This deletes it from Pinecone.")
                    if st.button("Remove", key=f"delete_{source.doc_id}", type="primary"):
                        vectorstore.delete_source(source.doc_id)
                        state.remove_source(source)
                        st.rerun()

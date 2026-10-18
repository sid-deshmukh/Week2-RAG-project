"""Streamlit session state: loaded sources, chat history, and which sources are selected."""

import streamlit as st

from toddler_book import vectorstore
from toddler_book.vectorstore import Source


def init_state() -> None:
    if "sources" not in st.session_state:
        st.session_state.sources = vectorstore.list_sources()
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("uploader_key", 0)
    st.session_state.setdefault("pending_prompt", None)
    st.session_state.setdefault("flash", [])  # toasts to show after a rerun
    for source in st.session_state.sources:
        st.session_state.setdefault(selection_key(source), True)


def selection_key(source: Source) -> str:
    return f"selected_{source.doc_id}"


def selected_sources() -> list[Source]:
    return [s for s in st.session_state.sources if st.session_state.get(selection_key(s))]


def add_source(source: Source) -> None:
    if all(s.doc_id != source.doc_id for s in st.session_state.sources):
        st.session_state.sources.append(source)
    st.session_state[selection_key(source)] = True


def remove_source(source: Source) -> None:
    st.session_state.sources = [s for s in st.session_state.sources if s.doc_id != source.doc_id]
    st.session_state.pop(selection_key(source), None)

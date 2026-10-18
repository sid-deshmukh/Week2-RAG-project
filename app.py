"""Ask Mufasa — a NotebookLM-style app for chatting with your PDFs.

Run with:  streamlit run app.py
"""

import streamlit as st

from toddler_book import config

st.set_page_config(page_title="Ask Mufasa", page_icon="🦁", layout="centered")

if missing := config.missing_keys():
    st.error(f"Missing environment variables in .env: {', '.join(missing)}")
    st.stop()

from toddler_book.ui import state, theme  # noqa: E402  (imports Pinecone/OpenAI clients; keys checked first)
from toddler_book.ui.chat import render_chat  # noqa: E402
from toddler_book.ui.sidebar import render_sidebar  # noqa: E402

theme.inject_css()
state.init_state()
render_sidebar()
render_chat()

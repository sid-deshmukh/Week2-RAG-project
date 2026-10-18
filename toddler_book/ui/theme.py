"""Kid-friendly look: custom CSS, the sky banner, and the empty-state illustration.

Colours and fonts live in .streamlit/config.toml; this file adds what the theme can't.
"""

import base64
import html

import streamlit as st

SKY = "#8FD3FF"
NAVY = "#1F3A5F"
SAND = "#F7C873"
ORANGE = "#E8772E"
GRASS = "#7CC86E"
BOOK_COLOURS = [("📘", "#2F7DE1"), ("📙", "#E8772E"), ("📗", "#4CAF6A"), ("📕", "#E0565B")]

USER_AVATAR = "🧒"
ASSISTANT_AVATAR = "🦁"

# A faint paw-print pattern for the page background (SVG, colours URL-encoded).
_PAW = (
    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='140' height='140' "
    "viewBox='0 0 140 140'><g fill='%232F7DE1' fill-opacity='0.05'>"
    "<ellipse cx='35' cy='45' rx='11' ry='9'/><circle cx='22' cy='30' r='5'/><circle cx='31' cy='24' r='5'/>"
    "<circle cx='41' cy='24' r='5'/><circle cx='49' cy='31' r='5'/>"
    "<g transform='translate(70 70) rotate(25)'><ellipse cx='35' cy='45' rx='11' ry='9'/>"
    "<circle cx='22' cy='30' r='5'/><circle cx='31' cy='24' r='5'/><circle cx='41' cy='24' r='5'/>"
    "<circle cx='49' cy='31' r='5'/></g></g></svg>"
)

_CSS = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-color: #FFF8EC;
    background-image: url("{_PAW}");
}}
[data-testid="stHeader"] {{ background: transparent; }}
[data-testid="stMainBlockContainer"] {{ max-width: 900px; padding-top: 2rem; }}

/* ---- sky banner ---- */
.tb-hero {{
    position: relative; overflow: hidden; border-radius: 28px;
    background: linear-gradient(180deg, {SKY} 0%, #CDEBFF 100%);
    padding: 1.6rem 2rem 3.4rem; margin-bottom: 1.2rem;
    box-shadow: 0 6px 0 #A9D3F5;
}}
.tb-hero.compact {{ padding: 1rem 1.6rem 2.6rem; }}
.tb-hero .tb-title {{
    font-family: Fredoka, sans-serif; color: {NAVY}; margin: 0; padding: 0;
    font-size: 2.6rem; line-height: 1.1; position: relative; z-index: 1;
}}
.tb-hero.compact .tb-title {{ font-size: 1.9rem; }}
.tb-hero p {{ color: {NAVY}; font-weight: 700; margin: .3rem 0 0; position: relative; z-index: 1; }}
.tb-hero-art {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }}

/* ---- chat bubbles ---- */
[data-testid="stChatMessage"] {{
    border-radius: 22px; padding: .9rem 1.1rem; margin-bottom: .6rem;
    background: #FFFFFF; border: 2px solid #BFDDF7; box-shadow: 0 3px 0 #BFDDF7;
}}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {{
    background: #FFE9CC; border-color: {SAND}; box-shadow: 0 3px 0 {SAND};
}}
[data-testid="stChatMessageAvatarCustom"], [data-testid="stChatMessage"] > div:first-child {{
    font-size: 1.6rem;
}}

/* ---- chat input ---- */
[data-testid="stBottom"] > div {{ background: transparent; }}
[data-testid="stChatInput"] > div {{
    border-radius: 999px; border: 3px solid {ORANGE}; background: #FFFFFF;
    box-shadow: 0 4px 0 #F2B48A;
}}

/* ---- starter question buttons ---- */
.st-key-starters button {{
    min-height: 4.2rem; border: none; font-weight: 800; color: {NAVY};
    box-shadow: 0 4px 0 rgba(31,58,95,.18); transition: transform .1s ease;
}}
.st-key-starters button:hover {{ transform: translateY(-2px); color: {NAVY}; }}
.st-key-starters [data-testid="stColumn"]:nth-child(1) button {{ background: #CDEBFF; }}
.st-key-starters [data-testid="stColumn"]:nth-child(2) button {{ background: #FFE3B8; }}
.st-key-starters [data-testid="stColumn"]:nth-child(3) button {{ background: #D7F2CF; }}

/* ---- source chips above the chat ---- */
.tb-chips {{ display: flex; flex-wrap: wrap; gap: .4rem; margin: .2rem 0 1rem; }}
.tb-chip {{
    background: #FFFFFF; border: 2px solid #BFDDF7; border-radius: 999px;
    padding: .15rem .7rem; font-size: .85rem; font-weight: 700; color: {NAVY};
}}

/* ---- sidebar: bookshelf ---- */
[data-testid="stSidebar"] h1 {{ font-size: 1.7rem; }}
[data-testid="stFileUploaderDropzone"] {{
    border: 3px dashed {ORANGE}; border-radius: 20px; background: #FFF8EC;
}}
[class*="st-key-book_"] {{
    background: #FFFFFF; border-radius: 14px; padding: .35rem .5rem .35rem .8rem;
    border-left: 8px solid #2F7DE1; box-shadow: 0 2px 0 #A9D3F5;
}}

/* ---- empty state ---- */
.tb-empty {{ text-align: center; padding: 1rem 0 2rem; }}
.tb-empty .tb-subtitle {{ font-family: Fredoka, sans-serif; font-size: 1.6rem; font-weight: 600; color: {NAVY}; margin: .4rem 0 .2rem; }}
.tb-steps {{ display: flex; gap: .8rem; justify-content: center; flex-wrap: wrap; margin-top: 1.2rem; }}
.tb-step {{
    background: #FFFFFF; border-radius: 20px; padding: .8rem 1rem; width: 200px;
    border: 2px solid #BFDDF7; box-shadow: 0 4px 0 #BFDDF7; font-weight: 700; color: {NAVY};
}}
.tb-step span {{ display: block; font-size: 1.8rem; }}
</style>
"""

# Clouds, a sun, and rolling sand/grass hills along the bottom of the banner.
_HERO_SVG = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" preserveAspectRatio="none">
  <g fill="#FFD45C">
    <circle cx="730" cy="50" r="28"/>
  </g>
  <g stroke="#FFD45C" stroke-width="5" stroke-linecap="round">
    <line x1="730" y1="8" x2="730" y2="0"/><line x1="772" y1="50" x2="790" y2="50"/>
    <line x1="760" y1="20" x2="770" y2="10"/><line x1="760" y1="80" x2="770" y2="90"/>
    <line x1="688" y1="50" x2="676" y2="50"/><line x1="700" y1="20" x2="690" y2="10"/>
  </g>
  <g fill="#FFFFFF" opacity=".9">
    <ellipse cx="520" cy="45" rx="42" ry="16"/><ellipse cx="548" cy="34" rx="26" ry="18"/>
    <ellipse cx="620" cy="110" rx="34" ry="12"/><ellipse cx="640" cy="102" rx="20" ry="13"/>
    <ellipse cx="420" cy="95" rx="28" ry="10"/>
  </g>
  <path d="M0 170 Q 120 140 250 165 T 520 160 T 800 150 V200 H0 Z" fill="{SAND}"/>
  <path d="M0 185 Q 160 160 330 182 T 650 178 T 800 172 V200 H0 Z" fill="{GRASS}"/>
</svg>
"""

_EMPTY_SVG = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="220" height="150" viewBox="0 0 220 150">
  <ellipse cx="110" cy="138" rx="80" ry="8" fill="#1F3A5F" opacity=".08"/>
  <path d="M110 40 C 80 25, 45 25, 25 35 V 125 C 45 115, 80 115, 110 130 Z" fill="#FFFFFF" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"/>
  <path d="M110 40 C 140 25, 175 25, 195 35 V 125 C 175 115, 140 115, 110 130 Z" fill="#FFFFFF" stroke="{NAVY}" stroke-width="4" stroke-linejoin="round"/>
  <g stroke="#8FD3FF" stroke-width="5" stroke-linecap="round">
    <line x1="42" y1="55" x2="92" y2="50"/><line x1="42" y1="72" x2="92" y2="67"/><line x1="42" y1="89" x2="80" y2="85"/>
  </g>
  <g stroke="{SAND}" stroke-width="5" stroke-linecap="round">
    <line x1="128" y1="50" x2="178" y2="55"/><line x1="128" y1="67" x2="178" y2="72"/><line x1="128" y1="84" x2="166" y2="88"/>
  </g>
  <path d="M110 40 V130" stroke="{NAVY}" stroke-width="4"/>
  <g fill="#FFD45C" stroke="{ORANGE}" stroke-width="2" stroke-linejoin="round">
    <path d="M40 12 l4 8 9 1 -7 6 2 9 -8 -5 -8 5 2 -9 -7 -6 9 -1 z"/>
    <path d="M178 4 l3 6 7 1 -5 5 1 7 -6 -4 -6 4 1 -7 -5 -5 7 -1 z"/>
  </g>
</svg>
"""


def _html(markup: str) -> None:
    # st.html sanitizes away <style>/<svg>, so raw HTML goes through markdown instead.
    # Blank lines would end markdown's HTML block, so drop them.
    st.markdown("\n".join(line for line in markup.splitlines() if line.strip()), unsafe_allow_html=True)


def _svg_img(svg: str, css_class: str) -> str:
    data = base64.b64encode(svg.strip().encode()).decode()
    return f'<img class="{css_class}" alt="" src="data:image/svg+xml;base64,{data}">'


def inject_css() -> None:
    _html(_CSS)


def render_hero(compact: bool = False) -> None:
    css_class = "tb-hero compact" if compact else "tb-hero"
    _html(
        f'<div class="{css_class}">{_svg_img(_HERO_SVG, "tb-hero-art")}'
        '<div class="tb-title">Ask Mufasa</div>'
        "<p>Wise answers from your books 🦁</p></div>"
    )


def render_empty_state() -> None:
    _html(
        f'<div class="tb-empty">{_svg_img(_EMPTY_SVG, "tb-empty-art")}'
        '<div class="tb-subtitle">Your bookshelf is empty!</div>'
        "<p>Add a PDF in the sidebar and we'll read it together.</p>"
        '<div class="tb-steps">'
        '<div class="tb-step"><span>📚</span>Add a PDF to your bookshelf</div>'
        '<div class="tb-step"><span>🐾</span>Wait while we read every page</div>'
        '<div class="tb-step"><span>💬</span>Ask any question about it</div>'
        "</div></div>"
    )


def render_source_chips(books: list[tuple[str, str]]) -> None:
    """Pill per selected source; `books` is [(emoji, file_name), ...]."""
    chips = "".join(f'<span class="tb-chip">{emoji} {html.escape(name)}</span>' for emoji, name in books)
    _html(f'<div class="tb-chips">{chips}</div>')


def render_spine_colours(doc_ids: list[str]) -> None:
    """Colour each bookshelf card's spine to match its book emoji."""
    rules = "".join(
        f'[data-testid="stSidebar"] .st-key-book_{doc_id} {{ border-left-color: {book_style(i)[1]}; }}'
        for i, doc_id in enumerate(doc_ids)
    )
    _html(f"<style>{rules}</style>")


def book_style(index: int) -> tuple[str, str]:
    """(emoji, spine colour) for the n-th book on the shelf."""
    return BOOK_COLOURS[index % len(BOOK_COLOURS)]

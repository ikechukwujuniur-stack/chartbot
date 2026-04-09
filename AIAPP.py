import streamlit as st
import hashlib
import json
import os
import requests

# -------------------------
# CONFIG
# -------------------------
API_URL = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

st.set_page_config(page_title="📖 Smart Dictionary AI", layout="centered")

# -------------------------
# SESSION STATE (FIXED)
# -------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dictionary"

if "username" not in st.session_state:
    st.session_state.username = "Guest"

# UI defaults
defaults = {
    "brightness": 1.0,
    "font_size": 16,
    "accent_color": "#1f77b4",
    "bg_color": "#ffffff",
    "text_color": "#000000",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------
# SIDEBAR (FIXED)
# -------------------------
st.sidebar.header("📌 Navigation")

nav_choice = st.sidebar.selectbox(
    "Go to page:",
    ["Dictionary", "Settings"],
    index=0 if st.session_state.page == "Dictionary" else 1
)

st.session_state.page = nav_choice

st.sidebar.success(f"User: {st.session_state.username}")

# -------------------------
# GLOBAL STYLE
# -------------------------
st.markdown(
    f"""
    <style>
    html, body, [class*="st"] {{
        background-color: {st.session_state.bg_color};
        color: {st.session_state.text_color};
        font-size: {st.session_state.font_size}px;
        opacity: {st.session_state.brightness};
    }}
    h1, h2, h3 {{
        color: {st.session_state.accent_color};
    }}
    div.stButton > button {{
        background-color: {st.session_state.accent_color};
        color: #ffffff;
        border-radius: 8px;
        padding: 0.5em 1em;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------
# DICTIONARY PAGE (FIXED)
# -------------------------
if st.session_state.page == "Dictionary":

    st.title("📖 Smart Dictionary AI")

    show_phonetics = st.sidebar.checkbox("Show Phonetics", True)
    play_audio = st.sidebar.checkbox("Play Pronunciation Audio", True)
    show_synonyms = st.sidebar.checkbox("Show Synonyms", True)
    show_antonyms = st.sidebar.checkbox("Show Antonyms", True)
    show_examples = st.sidebar.checkbox("Show Examples", True)

    output_style = st.sidebar.radio("Display Style", ("Detailed", "Minimal"))
    layout_option = st.sidebar.radio("Layout", ("Single Column", "Two Columns"))

    word = st.text_input("Enter a word").strip().lower()

    if word:
        try:
            response = requests.get(API_URL.format(word))
            data = response.json()

            if isinstance(data, dict):
                st.error("No definitions found.")
            else:
                entry = data[0]
                st.subheader(entry["word"].capitalize())

                if layout_option == "Two Columns":
                    col1, col2 = st.columns(2)
                else:
                    col1, col2 = st, st

                for meaning in entry.get("meanings", []):
                    pos = meaning.get("partOfSpeech", "")
                    for d in meaning.get("definitions", []):

                        if output_style == "Detailed":
                            col1.markdown(f"**({pos})** {d['definition']}")
                        else:
                            col1.write(f"- {d['definition']}")

                        if show_examples and d.get("example"):
                            col2.caption("Example: " + d["example"])

                        if show_synonyms and d.get("synonyms"):
                            col2.write("🟢 Synonyms: " + ", ".join(d["synonyms"][:10]))

                        if show_antonyms and d.get("antonyms"):
                            col2.write("🔴 Antonyms: " + ", ".join(d["antonyms"][:10]))

                if show_phonetics and entry.get("phonetics"):
                    for ph in entry["phonetics"]:
                        if ph.get("text"):
                            st.markdown(f"Phonetic: {ph['text']}")
                        if play_audio and ph.get("audio"):
                            st.audio(ph["audio"])

        except Exception as e:
            st.error(f"Error fetching data: {e}")

# -------------------------
# SETTINGS PAGE (FIXED)
# -------------------------
elif st.session_state.page == "Settings":

    st.title("⚙️ Settings")

    st.subheader("🎨 Display Settings")

    st.session_state.brightness = st.slider("Brightness", 0.5, 1.0, st.session_state.brightness)
    st.session_state.font_size = st.slider("Font Size", 12, 24, st.session_state.font_size)
    st.session_state.accent_color = st.color_picker("Accent Color", st.session_state.accent_color)
    st.session_state.bg_color = st.color_picker("Background Color", st.session_state.bg_color)
    st.session_state.text_color = st.color_picker("Text Color", st.session_state.text_color)

    st.success("Settings saved automatically ✅")

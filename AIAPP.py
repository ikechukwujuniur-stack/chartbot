import streamlit as st
import wikipedia
import re
from gtts import gTTS
import tempfile

st.title("📚 Dictionary")

# ---------------- SETTINGS ----------------

st.sidebar.title("⚙️ Settings")

background_color = st.sidebar.color_picker(
    "Background Color",
    "#0e1117"
)

heading_color = st.sidebar.color_picker(
    "Heading Color",
    "#ffffff"
)

text_color = st.sidebar.color_picker(
    "Text Color",
    "#ffffff"
)

voice_on = st.sidebar.checkbox("Enable AI Voice", value=True)

max_pages = st.sidebar.slider(
    "Pages to Search",
    1,
    10,
    3
)

# ---------------- STYLE ----------------

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {background_color};
        color: {text_color};
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {heading_color};
    }}

    p, span, label, div {{
        color: {text_color};
    }}

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- ANIMATED CIRCLES ----------------

st.markdown("""
<style>

.circle{
position:fixed;
border-radius:50%;
opacity:0.15;
animation:float 8s infinite ease-in-out;
}

.circle1{
width:200px;
height:200px;
background:#00ffff;
top:20%;
left:10%;
}

.circle2{
width:150px;
height:150px;
background:#ff00ff;
top:60%;
left:70%;
}

.circle3{
width:120px;
height:120px;
background:#ffff00;
top:40%;
left:40%;
}

@keyframes float{
0%{transform:translateY(0);}
50%{transform:translateY(-40px);}
100%{transform:translateY(0);}
}

</style>

<div class="circle circle1"></div>
<div class="circle circle2"></div>
<div class="circle circle3"></div>

""", unsafe_allow_html=True)

# ---------------- WIKIPEDIA SEARCH ----------------

def wiki_search(query, max_pages=3):

    pages = []

    try:
        summary = wikipedia.summary(query, sentences=10, auto_suggest=False)
        pages.append(summary)

    except wikipedia.DisambiguationError as e:

        for option in e.options:

            bad_words = ["song","album","film","movie","band"]

            if not any(b in option.lower() for b in bad_words):

                try:
                    summary = wikipedia.summary(option, sentences=10)
                    pages.append(summary)
                    return pages
                except:
                    continue

        summary = wikipedia.summary(e.options[0], sentences=10)
        pages.append(summary)

    except wikipedia.PageError:

        results = wikipedia.search(query, results=max_pages)

        for title in results:

            if any(x in title.lower() for x in ["song","album","film","movie"]):
                continue

            try:
                summary = wikipedia.summary(title, sentences=6)
                pages.append(summary)
                break
            except:
                continue

    return pages

# ---------------- ANSWER GENERATION ----------------

def generate_answer_locally(query, pages):

    combined_text = " ".join(pages)

    sentences = re.split(r'(?<=[.!?]) +', combined_text)

    stop_words = {
        "what","is","are","the","a","an","who","why",
        "when","where","how","does","do","did","of"
    }

    keywords = [word.lower() for word in query.split() if word.lower() not in stop_words]

    picks = [
        s for s in sentences
        if any(keyword in s.lower() for keyword in keywords)
    ]

    if not picks:
        return " ".join(sentences[:3])

    return " ".join(picks[:3])

# ---------------- USER INPUT ----------------

q = st.text_input("Ask a question:")

# ---------------- AI BUTTON ----------------

if st.button("Search and Answer") and q:

    with st.spinner("Searching Wikipedia and generating answer..."):

        pages = wiki_search(q, max_pages=max_pages)

        if not pages:

            st.error("Sorry, no relevant pages found. Try rephrasing your question.")

        else:

            answer = generate_answer_locally(q, pages)

            st.subheader("Answer")

            st.write(answer)

            # ---------------- AI VOICE ----------------

            if voice_on:

                tts = gTTS(answer)

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")

                tts.save(temp_file.name)

                st.audio(temp_file.name)

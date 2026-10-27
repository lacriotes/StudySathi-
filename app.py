import os
import re
from typing import List, Dict

import streamlit as st
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="StudySathi AI",
    page_icon="📚",
    layout="wide",
)

# ---------- Styling ----------
st.markdown("""
<style>
.block-container {max-width: 1050px; padding-top: 2rem; padding-bottom: 3rem;}
.hero {
  padding: 1.5rem 1.6rem; border-radius: 18px;
  background: linear-gradient(120deg, #14233b 0%, #176b78 100%);
  color: white; margin-bottom: 1.2rem;
}
.hero h1 {color: white; margin-bottom: .25rem;}
.hero p {color: #e5f4f5; margin-bottom: 0;}
.small-note {color: #667085; font-size: .9rem;}
.source-card {padding: .9rem 1rem; border: 1px solid #d9e2ec; border-radius: 12px; margin: .5rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>📚 StudySathi AI</h1>
  <p>Your study companion for understanding your own notes — upload, ask, review, learn.</p>
</div>
""", unsafe_allow_html=True)

st.caption("A student-built learning prototype. Answers may be incomplete or incorrect; verify important information against your course materials.")

# ---------- Helpers ----------
def extract_pdf(file) -> str:
    reader = PdfReader(file)
    pages = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception:
            text = ""
        if text.strip():
            pages.append(f"[Page {i + 1}]\n{text}")
    return "\n\n".join(pages)

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 140) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

def retrieve(question: str, chunks: List[Dict], top_k: int = 4):
    if not chunks or not question.strip():
        return []
    corpus = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
    try:
        matrix = vectorizer.fit_transform(corpus + [question])
    except ValueError:
        return []
    qvec = matrix[-1]
    scores = cosine_similarity(qvec, matrix[:-1]).ravel()
    indices = scores.argsort()[::-1][:top_k]
    return [
        {**chunks[int(i)], "score": float(scores[int(i)])}
        for i in indices if scores[int(i)] > 0
    ]

def get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", "") or os.getenv("GEMINI_API_KEY", "")
    except Exception:
        return os.getenv("GEMINI_API_KEY", "")
        
        
def generate_with_gemini(prompt: str):
    api_key = get_api_key()

    if not api_key:
        return None, "No Gemini API key configured; using retrieval-only mode."

    try:
        from google import genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text, None

    except Exception as e:
        print(f"Gemini error: {type(e).__name__}: {e}")
        return None, (
            f"AI generation unavailable ({type(e).__name__}). "
            "Showing retrieved source passages instead."
        )



def build_context(results):
    return "\n\n".join(
        f"Source: {r['source']} | {r['location']}\n{r['text']}"
        for r in results
    )

def answer_question(question, results):
    if not results or results[0]["score"] < 0.035:
        return ("I couldn't find a clearly relevant passage in the uploaded notes. "
                "Try rephrasing the question or uploading a document that covers this topic."), None
    context = build_context(results)
    prompt = f"""You are StudySathi AI, a careful study assistant.
Answer the student's question using ONLY the source excerpts below.
If the excerpts do not contain enough information, say so. Do not invent facts.
Use a clear, student-friendly explanation. End with a short 'Sources used' list naming the source and location.
Student question: {question}

Source excerpts:
{context}
"""
    generated, warning = generate_with_gemini(prompt)
    if generated:
        return generated, warning
    # A truthful fallback: show excerpts, not a fabricated AI-generated answer.
    fallback = "I couldn't generate a synthesized answer right now. Here are the closest passages I found:\n\n"
    fallback += "\n\n".join(
        f"**{r['source']} — {r['location']}** (similarity {r['score']:.2f})\n\n{r['text']}"
        for r in results[:3]
    )
    return fallback, warning

def simple_summary(text: str, max_sentences: int = 6):
    # Extractive fallback summary: rank sentences by TF-IDF importance.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 35]
    if not sentences:
        return "There isn't enough extractable text to summarize. Try a text-based PDF."
    if len(sentences) <= max_sentences:
        return "\n\n".join(f"- {s}" for s in sentences)
    try:
        vec = TfidfVectorizer(stop_words="english")
        mat = vec.fit_transform(sentences)
        weights = mat.sum(axis=1).A1
        top = sorted(range(len(sentences)), key=lambda i: weights[i], reverse=True)[:max_sentences]
        top = sorted(top)
        return "\n\n".join(f"- {sentences[i]}" for i in top)
    except ValueError:
        return "\n\n".join(f"- {s}" for s in sentences[:max_sentences])

def summarize_notes(text: str):
    prompt = f"""Create a concise study summary from the notes below.
Use headings: Main ideas, Key terms, What to remember.
Do not add facts that are not in the notes.
Notes (may be truncated):
{text[:14000]}
"""
    generated, warning = generate_with_gemini(prompt)
    return (generated, warning) if generated else (simple_summary(text), warning)

def make_flashcards(text: str):
    prompt = f"""Create 8 useful study flashcards from these notes.
Format each as:
Q: ...
A: ...
Use only information present in the notes. If there is not enough information for 8, create fewer.
Notes:
{text[:14000]}
"""
    generated, warning = generate_with_gemini(prompt)
    if generated:
        return generated, warning
    # Simple fallback: extract sentences as prompt cards.
    sentences = re.split(r"(?<=[.!?])\s+", text)
    candidates = [s.strip() for s in sentences if len(s.strip()) > 45]
    cards = []
    for i, sentence in enumerate(candidates[:8], 1):
        cards.append(f"**Card {i} — Try to explain this:**\n\n{sentence}")
    if not cards:
        return "Not enough extractable text to make flashcards.", warning
    return "\n\n".join(cards), warning

# ---------- Sidebar ----------
with st.sidebar:
    st.header("How it works")
    st.write("1. Upload text-based PDFs.")
    st.write("2. StudySathi extracts text and splits it into passages.")
    st.write("3. It retrieves relevant passages for your question.")
    st.write("4. If configured, a language model explains the answer using those passages.")
    st.divider()
    st.caption("Privacy: documents are processed in this app session. Avoid uploading confidential, personal, or copyrighted material you do not have permission to use.")
    st.caption("Scanned/image-only PDFs may need OCR and may not work in this prototype.")

# ---------- Upload ----------
uploaded_files = st.file_uploader(
    "Upload your study notes (PDF)",
    type=["pdf"],
    accept_multiple_files=True,
    help="Start with one or two text-based PDFs for best results.",
)

if "documents" not in st.session_state:
    st.session_state.documents = []
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "full_text" not in st.session_state:
    st.session_state.full_text = ""

if uploaded_files:
    docs, all_chunks, all_text = [], [], []
    with st.spinner("Reading your notes..."):
        for file in uploaded_files:
            text = extract_pdf(file)
            if not text.strip():
                st.warning(f"No selectable text found in {file.name}. It may be a scanned PDF.")
                continue
            docs.append({"name": file.name, "text": text})
            all_text.append(f"Document: {file.name}\n{text}")
            for j, chunk in enumerate(chunk_text(text)):
                all_chunks.append({
                    "source": file.name,
                    "location": f"Passage {j + 1}",
                    "text": chunk,
                })
    st.session_state.documents = docs
    st.session_state.chunks = all_chunks
    st.session_state.full_text = "\n\n".join(all_text)

if st.session_state.documents:
    st.success(f"Loaded {len(st.session_state.documents)} document(s) and created {len(st.session_state.chunks)} searchable passages.")
    tab_ask, tab_summary, tab_cards, tab_about = st.tabs(
        ["💬 Ask my notes", "📝 Summarize", "🧠 Flashcards", "ℹ️ About"]
    )

    with tab_ask:
        question = st.text_input("What do you want to understand?", placeholder="e.g. Explain supervised learning in simple terms")
        if st.button("Find answer", type="primary", use_container_width=True):
            if not question.strip():
                st.warning("Enter a question first.")
            else:
                with st.spinner("Searching your notes..."):
                    results = retrieve(question, st.session_state.chunks)
                    answer, warning = answer_question(question, results)
                st.markdown("### Answer")
                st.markdown(answer)
                if warning:
                    st.info(warning)
                if results:
                    with st.expander("Inspect retrieved passages"):
                        for r in results:
                            st.markdown(
                                f"<div class='source-card'><b>{r['source']}</b> · {r['location']} · similarity {r['score']:.2f}<br/><br/>{r['text']}</div>",
                                unsafe_allow_html=True,
                            )

    with tab_summary:
        st.write("Create a quick study summary from the uploaded notes.")
        if st.button("Summarize notes", use_container_width=True):
            with st.spinner("Preparing summary..."):
                summary, warning = summarize_notes(st.session_state.full_text)
            st.markdown(summary)
            if warning:
                st.info(warning)

    with tab_cards:
        st.write("Generate practice prompts from the uploaded notes.")
        if st.button("Make flashcards", use_container_width=True):
            with st.spinner("Creating flashcards..."):
                cards, warning = make_flashcards(st.session_state.full_text)
            st.markdown(cards)
            if warning:
                st.info(warning)

    with tab_about:
        st.markdown("""
        **What this prototype demonstrates**
        - PDF text extraction
        - Text chunking and TF-IDF retrieval
        - Optional grounded response generation through a language model
        - Extractive summarization and basic study-card fallback
        - A simple Streamlit interface

        **Known limitations**
        - TF-IDF is keyword-based; it may miss semantically related passages.
        - PDF extraction can fail on scanned documents, tables, or complex layouts.
        - Generated responses can still be wrong. Always check source material.
        - This is a prototype, not a replacement for teachers or official course materials.
        """)
else:
    st.info("Upload a text-based PDF above to begin. For a quick test, use your own short class notes.")
    st.markdown("### Demo flow")
    st.write("Upload notes → ask a question → inspect the source passages → summarize → make flashcards.")

st.divider()
st.caption("Built as an independent student project. Inspired by the general idea of accessible study tools; no third-party branding or proprietary code is used.")

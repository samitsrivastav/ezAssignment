import streamlit as st
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import askanything

# --- Load .env ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in .env file.")
    st.stop()

genai.configure(api_key=api_key)

st.set_page_config(page_title="Smart Assistant", layout="wide")
st.title("Smart Assistant")

# --- MODE SELECTION ---
mode = st.radio("Select Mode:", [
    "Document Summarization",
    "Challenge Me",
    "Ask Anything"
])

# --- Document Summarization ---
if mode == "Document Summarization":
    st.header("📄 Document Summarization")

    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"], key="summary_file")

    if uploaded_file:
        # extract text
        if uploaded_file.name.endswith(".pdf"):
            with open("temp.pdf", "wb") as f:
                f.write(uploaded_file.read())
            doc = fitz.open("temp.pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
        else:
            text = uploaded_file.read().decode("utf-8")

        with st.spinner("Generating Summary..."):
            model = genai.Genera

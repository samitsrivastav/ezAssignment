import streamlit as st
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()

st.set_page_config(page_title="Smart Assistant", layout="wide")

st.title("📄 Smart Research Assistant")

uploaded_file = st.file_uploader("Upload a PDF or TXT file", type=["pdf", "txt"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".pdf"):
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())
        text = extract_text_from_pdf("temp.pdf")
    else:  # TXT file
        text = uploaded_file.read().decode("utf-8")
    
    st.subheader("📜 Extracted Text (First 1000 characters)")
    st.write(text[:1000] + "...")

import streamlit as st
import fitz
import google.generativeai as genai
from dotenv import load_dotenv
import os

def run_ask_anything():
    # --- Load .env ---
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error("❌ GEMINI_API_KEY not found in .env file.")
        st.stop()

    genai.configure(api_key=api_key)

    st.set_page_config(page_title="Ask Anything", layout="wide")
    st.title("💬 Ask Anything")

    uploaded_file = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"], key="ask_file")

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

        st.session_state.doc_text = text  # store in session

        st.success("✅ Document uploaded & processed. You can now ask questions below.")

        question = st.text_input("Enter your question about the document:")

        if question:
            with st.spinner("Thinking..."):
                model = genai.GenerativeModel("gemini-1.5-pro")

                prompt = f"""
You are an assistant. Answer the question below based ONLY on the provided document.
If the document does not contain the answer, say: 'The document does not contain the answer.'

Document:
{text[:5000]}

Question: {question}

Answer:
                """

                response = model.generate_content(prompt)
                answer = response.text.strip()

            st.subheader("Answer:")
            st.write(answer)

if __name__ == "__main__":
    run_ask_anything()

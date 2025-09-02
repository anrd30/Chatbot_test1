from processing import extract_text
from db import build_or_load_db
from llm import answer_question
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os

PDF_FOLDER = r"C:\Users\Dell\Chatbot_test"
persist_dir = "chromaDb"

# 1️⃣ Extract text from all PDFs
pdf_files = [os.path.join(PDF_FOLDER, f) for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]
documents = []

for pdf in pdf_files:
    text = extract_text(pdf)
    documents.append(Document(page_content=text, metadata={"source": os.path.basename(pdf), "page": 1}))

# 2️⃣ Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunked_docs = splitter.split_documents(documents)

# 3️⃣ Build or load vector DB
vectordb = build_or_load_db(chunked_docs, persist_dir)

# 4️⃣ Query example
if __name__ == "__main__":
    user_query = "what is the menu on tuesday"
    response = answer_question(vectordb, user_query)
    print("Q:", user_query)
    print("A:", response)

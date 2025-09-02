from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

import os

def build_or_load_db(documents, persist_dir="chromaDb"):
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")
    
    if not os.path.exists(persist_dir) or not os.listdir(persist_dir):
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embedding_model,
            persist_directory=persist_dir
        )
        print(f"[INFO] Vector DB created with {len(documents)} chunks")
    else:
        vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding_model)
        print(f"[INFO] Loaded existing vector DB")
    
    return vectordb

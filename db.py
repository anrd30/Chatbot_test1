import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def build_or_load_db(documents=None, persist_dir="chromaDb_csv1", collection_name=None):
    """
    Build or load a Chroma vector DB using HuggingFace embeddings.
    Matches backend usage: build_or_load_db(chunked_docs, persist_dir=..., collection_name=...)
    """
    if collection_name is None:
        raise ValueError("You must provide a collection_name")

    print(f"[DEBUG] build_or_load_db: docs={'None' if documents is None else len(documents)}, persist_dir={persist_dir}, collection_name={collection_name}")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/multi-qa-MiniLM-L6-cos-v1")

    # Load if persisted DB exists and no documents provided to rebuild
    if os.path.exists(persist_dir) and len(os.listdir(persist_dir)) > 0 and documents is None:
        print(f"[INFO] Loading existing vector DB '{collection_name}' from {persist_dir}")
        vectordb = Chroma(
            persist_directory=persist_dir,
            embedding_function=embeddings,
            collection_name=collection_name,
        )
    else:
        if documents is None:
            raise ValueError("No documents provided to build the DB and no existing DB found")
        print(f"[INFO] Creating new vector DB '{collection_name}' at {persist_dir}")
        vectordb = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=persist_dir,
            collection_name=collection_name,
        )
        vectordb.persist()
        print("[INFO] Database persisted successfully")

    print(f"[DEBUG] Vector DB ready: collection='{collection_name}'")
    return vectordb

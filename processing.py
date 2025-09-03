import pandas as pd
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_csv(csv_path):
    """
    Load CSV and convert each Q&A row into a Document with metadata.
    """
    df = pd.read_csv(csv_path)
    documents = []

    for _, row in df.iterrows():
        question = str(row['question']).strip()
        answer = str(row['answer']).strip()
        if question and answer:
            doc = Document(
                page_content=answer,
                metadata={"question": question}
            )
            documents.append(doc)

    return documents

def split_documents(documents, chunk_size=500, chunk_overlap=50):
    """
    Split long answers into chunks if needed.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(documents)

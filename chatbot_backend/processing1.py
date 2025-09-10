import pandas as pd
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ==========================
# Load CSV into Documents
# ==========================
def load_csv(csv_path: str):
    print(f"[DEBUG] Loading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)
    # Normalize headers to lowercase to tolerate 'Category, Question, Answer'
    df.columns = [str(c).strip().lower() for c in df.columns]
    print(f"[DEBUG] Detected columns: {list(df.columns)}")

    documents = []
    for i, row in df.iterrows():
        # Expect lowercase: category, question, answer (after normalization above)
        question = str(row.get("question", "")).strip()
        answer = str(row.get("answer", "")).strip()
        category = str(row.get("category", "General")).strip()

        if not question or not answer:
            continue  # skip incomplete rows

        # Q&A style content
        content = f"Q: {question}\nA: {answer}"

        # Metadata: keep category + row index
        metadata = {
            "row": i,
            "source": csv_path,
            "category": category,
            "question": question,
            "answer": answer
        }

        doc = Document(page_content=content, metadata=metadata)
        documents.append(doc)

    print(f"[DEBUG] Loaded {len(documents)} Q&A documents with categories")
    return documents

# ==========================
# Split only long answers
# ==========================
def split_documents(documents, chunk_size=500, chunk_overlap=50):
    print(f"[DEBUG] Splitting {len(documents)} documents into chunks (if needed)...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = []
    for doc in documents:
        if len(doc.page_content) > chunk_size:
            chunks.extend(text_splitter.split_documents([doc]))
        else:
            chunks.append(doc)  # short docs remain whole

    print(f"[DEBUG] Created {len(chunks)} chunks total")
    return chunks

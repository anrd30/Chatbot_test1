import pandas as pd
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# ==========================
# Load CSV into Documents
# ==========================
def load_csv(csv_path: str):
    print(f"[DEBUG] Loading CSV from: {csv_path}")
    df = pd.read_csv(csv_path)

    documents = []
    for i, row in df.iterrows():
        # Convert row into readable text (excluding NaN)
        content_parts = []
        for col in df.columns:
            val = row[col]
            if pd.notna(val):
                content_parts.append(f"{col}: {val}")
        content = " ".join(content_parts)

        # Build metadata dictionary with all non-null fields
        metadata = {"row": i, "source": csv_path}
        for col in df.columns:
            if pd.notna(row[col]):
                metadata[col] = row[col]

        # Create Document
        doc = Document(
            page_content=content,
            metadata=metadata
        )
        documents.append(doc)

    print(f"[DEBUG] Loaded {len(documents)} documents with full metadata")
    return documents

# ==========================
# Split Documents into Chunks
# ==========================
def split_documents(documents, chunk_size=1000, chunk_overlap=100):
    print(f"[DEBUG] Splitting {len(documents)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    chunks = text_splitter.split_documents(documents)
    print(f"[DEBUG] Created {len(chunks)} chunks total")
    return chunks

# ==========================
# Run as a Test
# ==========================
'''if __name__ == "__main__":
    CSV_PATH = "DATA_05_09_2025 - Sheet1.csv"

    # Load CSV
    docs = load_csv(CSV_PATH)
    print(f"Loaded {len(docs)} documents")

    # Print first 3 docs with metadata
    for i, doc in enumerate(docs[:3], 1):
        print(f"\n--- Document {i} ---")
        print(doc.page_content[:500])  # only show first 500 chars
        print(doc.metadata)

    # Split documents
    chunks = split_documents(docs)
    print(f"\nTotal chunks after splitting: {len(chunks)}")'''

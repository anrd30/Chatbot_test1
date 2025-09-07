from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Path where your Chroma DB is persisted
CHROMA_DIR = "chromaDb_csv1"
COLLECTION_NAME = "iitrpr_faq"  # adjust if different

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load Chroma collection
db = Chroma(
    persist_directory=CHROMA_DIR,
    embedding_function=embeddings,
    collection_name=COLLECTION_NAME
)

def word_in_chroma_vector(word, top_k=10, literal_only=False):
    """
    Search Chroma DB with embeddings.
    
    Args:
        word (str): The query word/phrase.
        top_k (int): Number of vector results to return.
        literal_only (bool): 
            - True → return only results containing the literal word.
            - False → return all semantic matches.
    """
    query_vector = embeddings.embed_query(word)
    results = db.similarity_search_by_vector(query_vector, k=top_k)

    matches = []
    for i, doc in enumerate(results, 1):
        if not literal_only or word.lower() in doc.page_content.lower():
            matches.append(f"--- Match {i} ---\n{doc.page_content}")

    return matches


# Example usage
word = "Sudarshan"

print(f"\n=== Semantic Vector Search for '{word}' ===")
semantic_matches = word_in_chroma_vector(word, top_k=5, literal_only=False)
print("\n".join(semantic_matches) if semantic_matches else "No semantic matches found.")

print(f"\n=== Literal Vector Search for '{word}' ===")
literal_matches = word_in_chroma_vector(word, top_k=5, literal_only=True)
print("\n".join(literal_matches) if literal_matches else f"No literal matches found for '{word}'.")

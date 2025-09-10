from .processing import load_csv, split_documents
from .db import build_or_load_db
from .llm import answer_question


CSV_PATH = "../data/DATA_FAQ_EXPANDED.csv"
documents = load_csv(CSV_PATH)


chunked_docs = split_documents(documents, chunk_size=500, chunk_overlap=50)


persist_dir = "../chromaDb_csv1"
vectordb = build_or_load_db(chunked_docs, persist_dir=persist_dir)


if __name__ == "__main__":
    print("IIT Ropar Chatbot ready! Type 'exit' to quit.\n")
    while True:
        user_query = input("Ask me anything about IIT Ropar: ")
        if user_query.lower() == 'exit':
            break
        response = answer_question(vectordb, user_query)
        print("A:", response)
        print("-" * 80)

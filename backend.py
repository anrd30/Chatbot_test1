from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from processing1 import load_csv, split_documents
from db import build_or_load_db
from llm import answer_question
import os
import traceback

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173",
                    "http://localhost:5174", "http://127.0.0.1:5174"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# --- Load CSV and build vector DB once on startup ---
CSV_PATH = r"C:\Users\Dell\Chatbot_test2\DATA_05_09_2025 - Sheet1.csv"
PERSIST_DIR = "chromaDb_csv1"

if not os.path.exists(PERSIST_DIR):
    os.makedirs(PERSIST_DIR)

# Load and process documents
print("Loading documents...")
documents = load_csv(CSV_PATH)
print(f"Loaded {len(documents)} documents from CSV")

# Split documents into chunks with better settings
print("Splitting documents into chunks...")
chunked_docs = split_documents(documents, chunk_size=1000, chunk_overlap=200)
print(f"Split into {len(chunked_docs)} chunks")

# Debug: Print sample chunks
print("\nSample chunks:")
for i, doc in enumerate(chunked_docs[:3]):
    print(f"\nChunk {i+1} (length: {len(doc.page_content)}):")
    print(f"Content: {doc.page_content[:200]}...")
    print(f"Metadata: {doc.metadata}")

# Build or load the vector database
COLLECTION_NAME = "iitrpr_faq"
print("\nBuilding/loading vector database...")
vectordb = build_or_load_db(chunked_docs, persist_dir=PERSIST_DIR, collection_name=COLLECTION_NAME)

print("Backend ready. Vector DB loaded.")

'''test_query = "Who is Dr. Sudarshan?"
print("\n--- Backend Test ---")
print(f"Query: {test_query}")
answer = answer_question(vectordb, test_query)
print(f"Answer: {answer}\n")'''


# --- API Endpoint ---
@app.route("/chat", methods=["POST", "OPTIONS"])
@cross_origin()
def chat():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response
        
    try:
        print("\n=== Request Headers ===")
        for header, value in request.headers.items():
            print(f"{header}: {value}")
            
        if not request.is_json:
            print("Request is not JSON")
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        print(f"\n=== Request Data ===\n{data}")
        
        user_message = data.get("message")
        if not user_message:
            return jsonify({"reply": "No message received"}), 400
        
        print(f"\n[DEBUG] Processing message: {user_message}")
        reply = answer_question(vectordb, user_message)
        print(f"[DEBUG] Generated reply: {reply[:200]}")
        
        response = jsonify({"reply": reply})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    
    except Exception as e:
        # Log the error
        print(f"[ERROR] Exception in /chat endpoint: {e}")
        traceback.print_exc()
        return jsonify({"reply": "I encountered an error while processing your request."}), 500
if __name__ == "__main__":
    # Run with single process (no reloader) so logs are consistent
    app.run(port=5000, debug=True, use_reloader=False)



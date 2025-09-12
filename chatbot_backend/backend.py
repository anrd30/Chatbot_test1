from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin
from .processing1 import load_csv, split_documents
from .db import build_or_load_db
from .llm import answer_question
from langchain_community.retrievers import BM25Retriever
import os
import traceback
import speech_recognition as sr

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173",
                    "http://localhost:5174", "http://127.0.0.1:5174"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# API Key for authentication
API_KEY = os.getenv('API_KEY', 'your_api_key_here')

# --- Load CSV and build vector DB once on startup ---
CSV_PATH = r"C:\Users\aniru\Chatbot_test1-1\data\DATA_FAQ_EXPANDED.csv"
PERSIST_DIR = r"C:\Users\aniru\Chatbot_test1-1\chromaDb_expanded"

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

# Create sparse BM25 retriever for hybrid retrieval
print("Creating BM25 retriever for hybrid retrieval...")
bm25_retriever = BM25Retriever.from_documents(chunked_docs)

print("Backend ready. Vector DB loaded.")

def speech_to_text(audio_file):
    """Convert audio file to text using Google Speech Recognition."""
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"STT service error: {e}"

# --- API Endpoints ---

@app.route("/stt", methods=["POST", "OPTIONS"])
@cross_origin()
def stt():
    if request.method == "OPTIONS":
        response = make_response()
        return response
        
    try:
        audio_file = request.files.get("audio")
        if not audio_file:
            return jsonify({"error": "No audio file provided"}), 400
        
        text = speech_to_text(audio_file)
        return jsonify({"text": text})
    
    except Exception as e:
        print(f"[ERROR] STT failed: {e}")
        return jsonify({"error": "STT processing failed"}), 500

@app.route("/chat", methods=["POST", "OPTIONS"])
@cross_origin()
def chat():
    if request.method == "OPTIONS":
        response = make_response()
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
        
        user_message = data.get("question")
        if not user_message:
            return jsonify({"answer": "No message received"}), 400
        
        # Greeting detection
        greeting_words = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how are you", "what's up", "greetings", "good day"]
        if any(word in user_message.lower() for word in greeting_words):
            return jsonify({"answer": "Hello! I'm the IIT Ropar chatbot. How can I help you today?"})
        
        print(f"\n[DEBUG] Processing message: {user_message}")
        try:
            reply = answer_question(vectordb, user_message, bm25_retriever=bm25_retriever)
            print(f"[DEBUG] Generated reply: {reply[:200]}")
        except Exception as e:
            print(f"[ERROR] Failed to generate answer: {e}")
            reply = "I'm sorry, I encountered an error while processing your request. Please try again."
        
        response = jsonify({"answer": reply})
        return response
    
    except Exception as e:
        # Log the error
        print(f"[ERROR] Exception in /chat endpoint: {e}")
        traceback.print_exc()
        return jsonify({"answer": "I encountered an error while processing your request."}), 500
if __name__ == "__main__":
    # Run with single process (no reloader) so logs are consistent
    app.run(port=5000, debug=True, use_reloader=False)



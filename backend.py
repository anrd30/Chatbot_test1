from flask import Flask, request, jsonify
from flask_cors import CORS
from processing import load_csv, split_documents
from db import build_or_load_db
from llm import answer_question
import os

app = Flask(__name__)
CORS(app)

# --- Load CSV and build vector DB once on startup ---
CSV_PATH = r"C:\Users\Dell\Chatbot_test\iitrpr_qa - Sheet1.csv"
PERSIST_DIR = "chromaDb_csv"

if not os.path.exists(PERSIST_DIR):
    os.makedirs(PERSIST_DIR)

documents = load_csv(CSV_PATH)
chunked_docs = split_documents(documents, chunk_size=500, chunk_overlap=50)
vectordb = build_or_load_db(chunked_docs, persist_dir=PERSIST_DIR)

print("Backend ready. Vector DB loaded.")

# --- API Endpoint ---
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")
    reply = answer_question(vectordb, user_message)
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(port=5000)

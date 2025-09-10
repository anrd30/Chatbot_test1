from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from urllib.parse import parse_qs, urlparse

# Add parent directory to path to import your modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import build_or_load_db
from llm import answer_question

# Initialize the vector database
PERSIST_DIR = "chromaDb_csv1"
COLLECTION_NAME = "iitrpr_faq"

# This will be initialized on first request
vectordb = None

def init_db():
    global vectordb
    if vectordb is None:
        print("Initializing vector database...")
        vectordb = build_or_load_db(None, PERSIST_DIR, COLLECTION_NAME)
        print("Vector database initialized")

class handler(BaseHTTPRequestHandler):

    # ---- GET /api/chat?question=... ----
    def do_GET(self):
        if self.path.startswith("/api/chat"):
            query = urlparse(self.path).query
            params = parse_qs(query)
            question = params.get('question', [''])[0]

            if not question:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Question parameter is required'
                }).encode())
                return

            try:
                init_db()
                answer = answer_question(vectordb, question)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'question': question,
                    'answer': answer
                }).encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.w

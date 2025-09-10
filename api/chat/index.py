import json
import os
import sys

# Add parent directory to path to import your modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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

def make_response(status_code, body, headers=None):
    # Define CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': 'http://localhost:5173',  # Explicitly allow frontend origin
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
        'Access-Control-Allow-Credentials': 'true',
        'Access-Control-Max-Age': '86400',  # 24 hours
        'Content-Type': 'application/json'
    }

    # Merge with any additional headers
    if headers:
        cors_headers.update(headers)

    return {
        'statusCode': status_code,
        'headers': cors_headers,
        'body': json.dumps(body) if isinstance(body, dict) else body
    }

def handler(event, context):
    print("Received event:", json.dumps(event, indent=2))

    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'http://localhost:5173',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }

    try:
        # Initialize DB
        init_db()

        # Get request method and headers
        method = event.get('httpMethod', '').upper()

        # Handle POST requests
        if method == 'POST':
            try:
                # Parse request body
                body = event.get('body', '{}')
                try:
                    data = json.loads(body) if isinstance(body, str) else body

                    question = data.get('question', '').strip()
                    if not question:
                        return make_response(400, {'error': 'Question is required'})

                    # Get answer from RAG pipeline
                    answer = answer_question(vectordb, question)
                    return make_response(200, {
                        'question': question,
                        'answer': answer
                    })

                except json.JSONDecodeError as e:
                    print(f'JSON decode error: {str(e)}')
                    return make_response(400, {
                        'error': 'Invalid JSON in request body',
                        'details': str(e)
                    })

            except Exception as e:
                print(f'Error processing request: {str(e)}')
                return make_response(500, {
                    'error': 'Internal server error',
                    'message': str(e)
                })

        # Handle unsupported methods
        return make_response(405, {
            'error': 'Method Not Allowed',
            'allowed_methods': ['POST', 'OPTIONS']
        })

    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return make_response(500, {
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        })

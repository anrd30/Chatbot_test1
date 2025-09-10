import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

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

def handler(event, context):
    # Initialize DB
    init_db()
    
    # Get request method and headers
    method = event.get('httpMethod', '').upper()
    headers = event.get('headers', {})
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({})
        }
    
    # Handle POST requests
    if method == 'POST':
        try:
            # Parse request body
            body = event.get('body', '{}')
            if isinstance(body, str):
                try:
                    data = json.loads(body)
                except json.JSONDecodeError:
                    data = {}
            else:
                data = body
                
            question = data.get('question', '')
            
            if not question:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Question is required'})
                }
            
            # Get answer from RAG pipeline
            answer = answer_question(vectordb, question)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true'
                },
                'body': json.dumps({
                    'question': question,
                    'answer': answer
                })
            }
            
        except json.JSONDecodeError as e:
            print(f'JSON decode error: {str(e)}')
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true'
                },
                'body': json.dumps({'error': 'Invalid JSON in request body', 'details': str(e)})
            }
        except Exception as e:
            print(f'Error processing request: {str(e)}')
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': 'true'
                },
                'body': json.dumps({'error': 'Internal server error', 'message': str(e)})
            }
    
    # Handle unsupported methods
    return {
        'statusCode': 405,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Credentials': 'true',
            'Allow': 'POST, OPTIONS'
        },
        'body': json.dumps({'error': 'Method Not Allowed', 'allowed_methods': ['POST', 'OPTIONS']})
    }

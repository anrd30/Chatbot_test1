IIT Ropar Info Chatbot

A chatbot that answers questions about IIT Ropar using a CSV-based question-answer dataset and vector embeddings.

Features

Answers questions using a custom CSV knowledge base.

Uses vector embeddings (OllamaEmbeddings + Chroma) for semantic search.

Concise, factual answers — no reasoning or guessing outside the provided context.

Easy to extend: add new Q&A pairs to the CSV.

Project Structure
Chatbot_test/
│
├─ main.py           # Main script to run chatbot
├─ processing.py     # CSV loading & text processing
├─ llm.py            # LLM interface & answer logic
├─ db.py             # Vector database creation/loading
├─ requirements.txt  # Python dependencies
└─ (CSV file)        # Optional local Q&A CSV (not pushed to repo)

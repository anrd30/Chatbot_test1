# IIT Ropar Info Chatbot

A chatbot that answers questions about **IIT Ropar** using a **CSV-based Q&A dataset** and **vector embeddings**.

---

## Features

- Answers questions using a **custom CSV knowledge base**.
- Uses **vector embeddings** (OllamaEmbeddings + Chroma) for semantic search.
- Provides **concise, factual answers** — no reasoning or guessing outside the provided context.
- **Easy to extend**: just add new Q&A pairs to the CSV.

---

## Project Structure

Chatbot_test/
├── main.py # Main script to run chatbot (CLI version)
├── processing.py # CSV loading & text processing
├── llm.py # LLM interface & answer logic
├── db.py # Vector database creation/loading
├── requirements.txt # Python dependencies
└── (CSV file) # Optional local Q&A CSV (not pushed to repo)

yaml
Copy code

---

## Prerequisites

- Python 3.9+
- Install dependencies:

```bash
pip install -r requirements.txt
Running the Chatbot (CLI)
bash
Copy code
python main.py
The chatbot will prompt you:

vbnet
Copy code
Ask me anything about IIT Ropar:
Type a question and press Enter to get an answer.

Type exit to quit.

Adding New Data
To extend the chatbot, add new Q&A pairs to your CSV.

Ensure the CSV is in the same format as the existing one.

The vector database will automatically index the new data when you reload.

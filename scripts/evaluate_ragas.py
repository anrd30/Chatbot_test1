"""
RAGAS evaluation script for your IIT Ropar RAG pipeline (Ollama-only).

Requirements:
  pip install ragas datasets pandas langchain-ollama

Make sure Ollama is installed and you have pulled a model, e.g.:
  ollama pull phi3

Usage example:
  ollama pull phi3
  python scripts/evaluate_ragas.py --eval-file scripts/sample_eval.jsonl --persist-dir chromaDb_csv1 --collection iitrpr_faq
"""

import os
import sys
import json
import argparse
import pandas as pd
from datasets import Dataset

# Ensure project root is on sys.path so local imports work when running from scripts/
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(THIS_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---- your pipeline pieces (should exist in project root) ----
from processing1 import load_csv, split_documents
from db import build_or_load_db
from llm import debug_retrieve, answer_question

# ---- RAGAS ----
from ragas import evaluate
from ragas.metrics import context_precision, context_recall
# Judge metrics (classes) will be constructed below if LLM is available
# from ragas.metrics import Faithfulness, AnswerRelevancy  # imported later when LLM exists


def load_eval_jsonl(path: str) -> list[dict]:
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            q = obj.get("question", "").strip()
            gt = obj.get("ground_truth", [])
            if isinstance(gt, str):
                gt = [gt]
            items.append({"question": q, "ground_truth": gt})
    return items


def ensure_vector_db(csv_path: str | None, persist_dir: str, collection: str):
    """Build or load the vector database similarly to your backend code."""
    docs = None
    if csv_path:
        print(f"[RAGAS] Loading CSV for ingestion: {csv_path}")
        raw_docs = load_csv(csv_path)
        docs = split_documents(raw_docs, chunk_size=1000, chunk_overlap=200)
        print(f"[RAGAS] Prepared {len(docs)} chunks")
    print(f"[RAGAS] Building/loading vectordb: persist_dir={persist_dir}, collection={collection}")
    vectordb = build_or_load_db(docs, persist_dir=persist_dir, collection_name=collection)
    return vectordb


def run_evaluation(vectordb, eval_items: list[dict], out_path: str | None = None, ollama_model: str = "phi3"):
    rows = []
    print(f"[RAGAS] Preparing evaluation dataset with {len(eval_items)} items")

    for i, item in enumerate(eval_items, 1):
        q = item["question"]
        gts = item.get("ground_truth", []) or []
        # Use debug_retrieve to extract exact contexts the system will see
        dbg = debug_retrieve(vectordb, q, top_k=5)
        contexts = []
        if isinstance(dbg, dict) and dbg.get("selected"):
            for sel in dbg["selected"]:
                snippet = sel.get("snippet") or ""
                if snippet:
                    contexts.append(snippet)

        # Get model answer using the normal pipeline path
        answer = answer_question(vectordb, q)
        # RAGAS expects a list of ground-truth strings in column `ground_truth`
        reference = gts[0] if gts else ""
        rows.append({
            "question": q,
            "answer": answer,
            "contexts": contexts,
            "ground_truth": [reference],  # IMPORTANT: list[str]
        })
        print(f"[RAGAS] [{i}/{len(eval_items)}] q='{q[:60]}...' | ctx={len(contexts)}")

    df = pd.DataFrame(rows)

    # convert empty strings to empty list for ground_truth to be safe
    df["ground_truth"] = df["ground_truth"].apply(lambda x: x if isinstance(x, list) else [x])

    ds = Dataset.from_pandas(df, preserve_index=False)

    # -------- LLM / Ollama setup (Ollama-only) ----------
    metrics = []
    llm = None
    try:
        from langchain_ollama import ChatOllama
        # Use the supplied model name (default "phi3"); change to "llama3" if you prefer
        llm = ChatOllama(model=ollama_model, temperature=0)
        print(f"[RAGAS] Using Ollama model: {ollama_model}")
    except ModuleNotFoundError:
        print("[RAGAS] ERROR: langchain_ollama not installed. Install with `pip install langchain-ollama`")
        print("[RAGAS] Falling back to context-only metrics (no judge LLM).")

    if llm:
        try:
            from ragas.metrics import Faithfulness, AnswerRelevancy
            metrics.extend([
                Faithfulness(llm=llm),
                AnswerRelevancy(llm=llm),
            ])
        except Exception as e:
            # If ragas API differs, notify and fallback to context metrics
            print(f"[RAGAS] WARNING: could not construct judge metrics: {e}")
            print("[RAGAS] Falling back to context-only metrics.")
            metrics = []

    # Always include context metrics
    metrics.extend([context_precision, context_recall])

    print(f"[RAGAS] Running evaluation with metrics: {[getattr(m, 'name', str(m)) for m in metrics]}")
    ds_small = ds.select(range(4))
    results = evaluate(ds_small, metrics=metrics)
    print("\n[RAGAS] Results:")
    print(results)

    if out_path:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump({"results": results}, f, indent=2)
        print(f"[RAGAS] Saved results to {out_path}")

    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default=None, help="Path to the CSV to (re)build the vector DB from.")
    ap.add_argument("--persist-dir", type=str, default="chromaDb_csv1", help="Chroma persist directory")
    ap.add_argument("--collection", type=str, default="iitrpr_faq", help="Chroma collection name")
    ap.add_argument("--eval-file", type=str, required=True, help="JSONL with question and ground_truth list")
    ap.add_argument("--out", type=str, default="scripts/ragas_results.json", help="Where to store JSON results")
    ap.add_argument("--ollama-model", type=str, default="phi:latest", help="Ollama model to use (phi3, llama3, etc.)")
    args = ap.parse_args()

    vectordb = ensure_vector_db(args.csv, args.persist_dir, args.collection)
    eval_items = load_eval_jsonl(args.eval_file)
    run_evaluation(vectordb, eval_items, out_path=args.out, ollama_model=args.ollama_model)


if __name__ == "__main__":
    main()

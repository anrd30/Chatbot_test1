from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import json
import re

# Prompt template for CSV Q&A
template = """
You are a helpful assistant for IIT Ropar-specific information. Answer the user’s question only using the information in the context provided.
You are allowed to reframe the questions so as to get an asnwer but the final answer should be in the context provided.
Rules:
All context provided directly refers to IIT Ropar. So when I say "Is there a hospital?", it means "Is there a hospital in IIT Ropar."
Answer directly and concisely, in 1–4 lines.Do not create puzzles, hypothetical scenarios, reasoning chains, or explanations.
If the answer is not in the context, respond exactly: "I’m sorry, I don’t have information on that."
If a question is not related to IIT Ropar, respond exactly: "I’m sorry, I can only answer questions related to IIT Ropar."
Never hallucinate; answer only the asked question.
If the question is about the mess menu, list exact meals: breakfast, lunch, and dinner.


Context:
{context}

Question:
{question}

Answer:
"""

prompt_template = ChatPromptTemplate.from_template(template)
# Using llama3 for better understanding and response generation
llm = OllamaLLM(model="phi:latest", temperature=0.1, max_tokens=2000)

def generate_paraphrases_with_llm(query: str, n: int = 3) -> list:
    """Use the LLM to produce a few short, diverse paraphrases for higher-recall retrieval.
    Returns a list of strings. Falls back gracefully on parsing errors.
    """
    prompt = (
        "Generate "
        f"{n} diverse paraphrases for the following question about IIT Ropar. "
        "Keep each under 12 words, concise, and do not answer it. "
        "Return ONLY a JSON array of strings.\n\n"
        f"Question: {query}"
    )
    try:
        raw = llm.invoke(prompt)
        # Try parse as JSON array
        paras = json.loads(raw)
        if isinstance(paras, list):
            cleaned = []
            seen = set()
            for p in paras[: n * 2]:  # cap
                if not isinstance(p, str):
                    continue
                s = re.sub(r"\s+", " ", p).strip()
                if s and s.lower() not in seen:
                    seen.add(s.lower())
                    cleaned.append(s)
            return cleaned[:n]
    except Exception:
        pass

    # Fallback: try to split lines / bullets
    try:
        lines = [re.sub(r"^[-*\d\.\)\s]+", "", ln).strip() for ln in raw.splitlines()]
        lines = [ln for ln in lines if ln]
        uniq = []
        seen = set()
        for ln in lines:
            s = re.sub(r"\s+", " ", ln)
            if s and s.lower() not in seen:
                seen.add(s.lower())
                uniq.append(s)
        return uniq[:n] if uniq else []
    except Exception:
        return []

def normalize_name(name):
    """Normalize name variations for better matching."""
    return ''.join(c.lower() for c in name if c.isalnum())

def answer_question(vectordb, query, top_k=5, use_mmr=True):
    """
    Retrieves relevant context from ChromaDB and queries the LLM with a strict prompt.
    """

    try:
        # 1️⃣ Build LLM-based multi-query variants to improve recall
        variants = [query]
        try:
            llm_variants = generate_paraphrases_with_llm(query, n=3)
            variants.extend(llm_variants)
        except Exception:
            pass
        # Always include a simple anchored variant
        variants.append(f"{query} IIT Ropar")

        # 2️⃣ Retrieve with MMR for each variant (high fetch_k), then union
        candidate_docs = []
        for v in variants:
            try:
                docs_v = vectordb.max_marginal_relevance_search(v, k=top_k, fetch_k=100)
            except Exception:
                docs_v = vectordb.similarity_search(v, k=top_k)
            candidate_docs.extend(docs_v)

        print(f"\n[RETRIEVE] collected {len(candidate_docs)} docs across {len(variants)} variants")

        # 3️⃣ Deduplicate by a stable key: email or question (name) or first 100 chars
        seen = set()
        deduped = []
        for d in candidate_docs:
            meta = getattr(d, 'metadata', {}) or {}
            email_key = str(meta.get('email') or '').strip().lower()
            name_key = str(meta.get('question') or meta.get('name') or '').strip().lower()
            key = email_key or name_key or (d.page_content[:100].lower() if d.page_content else '')
            if key and key not in seen:
                seen.add(key)
                deduped.append(d)

        # Keep only top_k after union+dedup for final context
        results = deduped[:top_k]
        print(f"[RETRIEVE] deduplicated to {len(results)} docs (top_k={top_k})")

        if not results:
            return "I’m sorry, I don’t have information on that."
        for i, r in enumerate(results):
            print(f"\n[Result {i+1}]")
            print(r.page_content[:300])
        

        # 2️⃣ Build clean context (answers only, no redundant Q/A labels)
        context = "\n\n".join(doc.page_content for doc in results)

        # 3️⃣ Format with your strict IIT Ropar prompt template
        prompt_text = prompt_template.format_prompt(
            context=context,
            question=query
        ).to_string()

        # 4️⃣ Debug what’s going to LLM
        print("\n=== FINAL PROMPT SENT TO LLM ===")
        print(prompt_text[:2000])  # print first 2000 chars only to avoid flooding console

        # 5️⃣ Call Llama3
        response = llm.invoke(prompt_text)

        # 6️⃣ Return clean answer
        return response.strip()

    except Exception as e:
        print(f"Error in answer_question: {e}")
        return "I encountered an error while processing your request."

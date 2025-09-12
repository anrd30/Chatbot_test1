from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import json
import re
from typing import Optional, List
from sentence_transformers import CrossEncoder

# Prompt template for CSV Q&A
template = """
You are a helpful assistant for IIT Ropar-specific information. First, check if the question is related to IIT Ropar. If not, respond exactly: "I’m sorry, I can only answer questions related to IIT Ropar." Do not provide information on topics outside IIT Ropar.

If the question is related to IIT Ropar, always answer based on the provided context. Do not say 'I don't have information' or 'sorry' if the context contains relevant details. Use the context to provide a direct answer.

Context:
{context}

Question:
{question}

Answer:
"""

prompt_template = ChatPromptTemplate.from_template(template)
# Using mistral for better understanding and response generation
llm = OllamaLLM(model="mistral:7b-instruct-q4_K_M", temperature=0.3, max_tokens=2000)

def qoqa_rewrite(query: str, n: int = 3) -> dict:
    """QOQA-style query optimization: produce one canonical rewrite and n alignment-oriented queries.
    Returns {"canonical": str, "queries": [str,...]} with robust fallbacks.
    """
    rewriter = OllamaLLM(model="mistral:7b-instruct-q4_K_M", temperature=0.0, max_tokens=400)
    base = query.strip()
    canonical, queries = None, []

    def _attempt_once() -> dict | None:
        prompt = (
            
    "You are a query optimizer for IIT Ropar’s knowledge base.\n"
    "Your task: rewrite the user’s question into a canonical form and "
    "produce multiple search-friendly variants.\n\n"
    "Return ONLY a JSON object of the form:\n"
    "{"
    "  \"canonical\": string,"  
    "  \"queries\": [string, string, string]"
    "}\n\n"
    "Rules:\n"
    "- canonical: 2 concise rewrites that makes the user’s intent explicit "
    "using terms found in IIT Ropar FAQs, official departments, roles, or facilities.\n"
    "- queries: exactly {n} distinct rewrites optimized for retrieval. Use synonyms, abbreviations, and role/department name variants. "
    "Examples: HoD ↔ Head of Department, CSE ↔ Computer Science, Mess ↔ Hostel Mess, Sports Complex ↔ Gym.\n"
    "- Each query must stay under 16 words.\n"
    "- Do not generate answers, explanations, or filler text.\n"
    "- If user question is ambiguous, generate variants that cover multiple likely intents.\n\n"
    # Adaptive rules based on keywords
    + ("- For hostel-related queries, generate variants like 'What amenities does X hostel offer?' or 'What facilities are available in X hostel?'\n" if "hostel" in base.lower() else "")
    + ("- For doctor/medical queries, generate variants like 'What is Dr. X's specialization?' or 'What services does Dr. X provide?'\n" if any(word in base.lower() for word in ["doctor", "dr.", "medical", "hospital"]) else "")
    + ("- For admission-related queries, generate variants like 'What are the admission requirements for X?' or 'How to apply for X program?'\n" if "admission" in base.lower() else "")
    + ("- For facility-related queries, generate variants like 'What is available at X facility?' or 'How to access X?'\n" if any(word in base.lower() for word in ["facility", "sports", "gym", "library", "mess"]) else "")
    + ("- For staff/admin queries, generate variants like 'What is the role of X?' or 'Who handles X?'\n" if any(word in base.lower() for word in ["staff", "admin", "warden", "council"]) else "")
    + ("- For course-related queries, generate variants like 'What topics are covered in X course?' or 'What is taught in X subject?'\n" if any(word in base.lower() for word in ["course", "subject", "curriculum", "syllabus"]) else "")
    + ("- For research-related queries, generate variants like 'What are the research interests of X?' or 'What projects does X work on?'\n" if "research" in base.lower() else "")
    + ("- For event-related queries, generate variants like 'What is happening at X event?' or 'When is X scheduled?'\n" if any(word in base.lower() for word in ["event", "festival", "seminar", "workshop"]) else "")
    + ("- For transport-related queries, generate variants like 'How to reach X via transport?' or 'What transport options are for X?'\n" if any(word in base.lower() for word in ["transport", "bus", "train", "airport"]) else "")
    + ("- For department-related queries, generate variants like 'What does X department do?' or 'Who is in X department?'\n" if any(word in base.lower() for word in ["department", "cse", "ece", "mechanical"]) else "")
    + f"\nUser question: {base}\n"
)

        
        raw_local = rewriter.invoke(prompt)
        try:
            data = json.loads(raw_local)
            if not isinstance(data, dict):
                return None
            can = data.get("canonical")
            qs = data.get("queries")
            if not isinstance(can, str) or not isinstance(qs, list) or len(qs) < 1:
                return None
            # Clean and enforce distinctness
            can = re.sub(r"\s+", " ", can).strip()
            out_qs, seenq = [], set()
            for q in qs:
                if isinstance(q, str):
                    s = re.sub(r"\s+", " ", q).strip()
                    if s and s.lower() not in seenq:
                        seenq.add(s.lower())
                        out_qs.append(s)
            if len(out_qs) == 0:
                return None
            # Truncate or pad to exactly n entries
            out_qs = out_qs[:n]
            return {"canonical": can or base, "queries": out_qs}
        except Exception:
            return None

    def _name_tokens(text: str) -> list[str]:
        toks = re.findall(r"[A-Za-z][A-Za-z\.]+", text)
        # keep capitalized tokens or those >= 4 chars that look like names
        out = []
        for t in toks:
            if t.lower() in {"what","does","prof","prof.","dr","dr.","teach","teaches","course","courses","subject","subjects","at","iit","ropar","iitrpr"}:
                continue
            if (t[0].isupper() and len(t) >= 3) or len(t) >= 5:
                out.append(t.strip('.'))
        return out[:3]

    def _valid_query(q: str, names: list[str]) -> bool:
        words = q.strip().split()
        if len(words) < 4 or len(words) > 18:
            return False
        # must include at least one name/entity token from the question if present
        if names and not any(n.lower() in q.lower() for n in names):
            return False
        # must include an intent verb
        intent = ["teach","teaches","teaching","courses","subjects","interests","research"]
        if not any(iv in q.lower() for iv in intent):
            return False
        return True

    names = _name_tokens(base)

    # Try up to 2 deterministic attempts
    for _ in range(2):
        res = _attempt_once()
        if res:
            canonical, queries = res["canonical"], res["queries"]
            # validate queries
            queries = [q for q in queries if _valid_query(q, names)]
            break

    # Fallback if parsing/formatting failed
    if not canonical:
        canonical = base
    if not queries:
        # Synthesize alignment-oriented queries using names and intent verbs
        if names:
            nm = " ".join(names[:2])
            candidates = [
                f"What courses does {nm} teach at IIT Ropar?",
                f"What subjects does {nm} teach in Computer Science?",
                f"What are {nm}'s research interests at IIT Ropar?",
            ]
        else:
            candidates = [
                f"{base} at IIT Ropar",
                base.replace("What does", "What courses does").replace("what does", "what courses does"),
                base.replace("teach", "teach at IIT Ropar"),
            ]
        seen = {canonical.lower()}
        queries = []
        for v in candidates:
            s = re.sub(r"\s+", " ", v).strip()
            if s and s.lower() not in seen and _valid_query(s, names):
                seen.add(s.lower())
                queries.append(s)
            if len(queries) >= n:
                break

    print(f"[QOQA] canonical: {canonical} | queries: {queries}")
    return {"canonical": canonical, "queries": queries}

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

def hyde_generate(query: str) -> str:
    """HyDE: Generate a hypothetical answer/passage for the query to use for retrieval.
    Keep it short and factual in tone. Fail open to empty string.
    """
    try:
        prompt = (
            "You are writing a concise passage that would answer the user's question about IIT Ropar.\n"
            "Do NOT include disclaimers or sources. 3-5 sentences, factual tone.\n\n"
            f"Question: {query}\n\n"
            "Passage:"
        )
        text = llm.invoke(prompt)
        # sanitize newlines and trim
        return re.sub(r"\s+", " ", text).strip()
    except Exception:
        return ""

def normalize_name(name):
    """Normalize name variations for better matching."""
    return ''.join(c.lower() for c in name if c.isalnum())

# --- Generic intent/entity signals and filtering ---
INTENTS = {
    "leadership": {"hod", "head", "head of", "chair", "chairperson", "runs", "leads", "in charge"},
    "teaching": {"teach", "teaches", "teaching", "course", "courses", "subject", "subjects", "syllabus"},
    "research": {"interest", "interests", "research", "areas"},
    "contact": {"email", "phone", "contact", "room"},
    "hostel": {"hostel", "warden", "mess", "executive", "council"},
    "guest": {"guest house", "booking", "category a", "category b", "b-1", "b-2"},
    "courses": {"courses", "syllabus", "syllabi", "syllabus of", "syllabus for","subjects"},
    "mess": {"mess", "mess menu", "mess menu of", "mess menu for"},
    

}

DEPARTMENTS = {
    "cse", "computer science", "computer science & engineering",
    "civil", "ece", "eee", "mechanical", "chemical", "dbme",
    "saide",
}

COURSE_CODE_RE = re.compile(r"\b[A-Z]{2}\d{3}\b")

def _extract_names(text: str) -> list[str]:
    toks = re.findall(r"[A-Za-z][A-Za-z\.]+", text)
    out = []
    skip = {"what","who","is","the","of","and","at","for","in","to","a","an","on","with","about",
            "prof","prof.","dr","dr.","iit","ropar","iitrpr"}
    for t in toks:
        tl = t.lower().strip('.')
        if tl in skip:
            continue
        if (t[0].isupper() and len(t) >= 3) or len(t) >= 5:
            out.append(t.strip('.'))
    return out[:3]

def _extract_signals(query: str) -> dict:
    ql = query.lower()
    intents_hit = set()
    for k, toks in INTENTS.items():
        if any(tok in ql for tok in toks):
            intents_hit.add(k)
    dept_hits = {d for d in DEPARTMENTS if d in ql}
    has_course_code = bool(COURSE_CODE_RE.search(query))
    names = _extract_names(query)
    return {
        "intents": intents_hit,
        "dept_hits": dept_hits,
        "has_course_code": has_course_code,
        "names": names,
    }

def _haystack_for_doc(d) -> str:
    meta = getattr(d, 'metadata', {}) or {}
    return " ".join([
        (d.page_content or ''),
        str(meta.get('question') or ''),
        str(meta.get('answer') or ''),
        str(meta.get('category') or ''),
    ]).lower()

def _passes_generic_filter(d, signals: dict) -> bool:
    hay = _haystack_for_doc(d)
    # If we have any intent, require at least one matching token from that union
    if signals["intents"]:
        intent_union = set().union(*(INTENTS[k] for k in signals["intents"]))
        if not any(tok in hay for tok in intent_union):
            return False
    # If we have explicit entity/domain (dept, course code, names), require at least one
    entity_hit = False
    if signals["dept_hits"] and any(d in hay for d in DEPARTMENTS):
        entity_hit = True
    if signals["has_course_code"] and COURSE_CODE_RE.search(hay):
        entity_hit = True
    if signals["names"] and any(n.lower() in hay for n in signals["names"]):
        entity_hit = True
    # If no entity cues were present in query, don't block on entity match
    want_entity = bool(signals["dept_hits"] or signals["has_course_code"] or signals["names"])
    if want_entity and not entity_hit:
        return False
    return True

def answer_question(vectordb, query, top_k=20, use_mmr=True, bm25_retriever: Optional[object] = None, use_hyde: bool = True):
    """
    Retrieves relevant context from ChromaDB and queries the LLM with a strict prompt.
    """

    try:
        # 1️⃣ Simplified query processing (removed QOQA for speed)
        canonical = query.strip()
        variants = [canonical]
        if "iit ropar" not in canonical.lower():
            variants.append(f"{canonical} IIT Ropar")

        # 3️⃣ Retrieve (Dense: E5) with MMR for each variant (high fetch_k), then union
        candidate_docs = []
        for v in variants:
            q_dense = v
            try:
                docs_v = vectordb.max_marginal_relevance_search(q_dense, k=top_k, fetch_k=120)
            except Exception:
                docs_v = vectordb.similarity_search(q_dense, k=top_k)
            candidate_docs.extend(docs_v)

        # Dense retrieval using HyDE passage as query (commented out)
        # if hyde_passage:
        #     try:
        #         docs_h = vectordb.max_marginal_relevance_search(hyde_passage, k=top_k, fetch_k=120)
        #     except Exception:
        #         docs_h = vectordb.similarity_search(hyde_passage, k=top_k)
        #     candidate_docs.extend(docs_h)

        # 4️⃣ (Optional) Sparse BM25 retrieval for hybrid
        if bm25_retriever is not None:
            try:
                bm25_docs_q = bm25_retriever.get_relevant_documents(canonical) or []
            except Exception:
                bm25_docs_q = []
            candidate_docs.extend(bm25_docs_q[: top_k])
            # if hyde_passage:
            #     try:
            #         bm25_docs_h = bm25_retriever.get_relevant_documents(hyde_passage) or []
            #     except Exception:
            #         bm25_docs_h = []
            #     candidate_docs.extend(bm25_docs_h[: top_k])

        print(f"\n[RETRIEVE] collected {len(candidate_docs)} docs (dense only) across {len(variants)} variants")

        # Rerank with cross-encoder for better accuracy
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        query_doc_pairs = [(canonical, doc.page_content) for doc in candidate_docs]
        scores = cross_encoder.predict(query_doc_pairs)
        # Sort with stable key to avoid Document comparison errors
        sorted_pairs = sorted(zip(scores, candidate_docs), key=lambda x: (-x[0], id(x[1])))
        ranked_docs = [doc for _, doc in sorted_pairs]
        candidate_docs = ranked_docs[:top_k]

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

        # 4️⃣ Generic pre-LLM filter using intent/entity signals (safe fallback)
        signals = _extract_signals(canonical)
        filtered = [d for d in deduped if _passes_generic_filter(d, signals)]
        chosen = filtered if filtered else deduped

        # Keep only top_k after filter
        results = chosen[:top_k]
        print(f"[RETRIEVE] dedup={len(deduped)} filtered={len(filtered)} -> using {len(results)} (top_k={top_k})")

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
        '''print("\n=== FINAL PROMPT SENT TO LLM ===")
        print(prompt_text[:2000])  # print first 2000 chars only to avoid flooding console'''

        # 5️⃣ Call Llama3
        response = llm.invoke(prompt_text)

        # 6️⃣ Return clean answer
        return response.strip()

    except Exception as e:
        print(f"Error in answer_question: {e}")
        return "I encountered an error while processing your request."


def debug_retrieve(vectordb, query, top_k=5):
    """Diagnostics for retrieval: returns canonical, queries, candidates, filter decisions, and final prompt (truncated)."""
    info = {"query": query, "canonical": None, "queries": [], "candidates": [], "filtered": [], "selected": [], "final_prompt": None}
    try:
        qo = qoqa_rewrite(query, n=3)
        canonical = qo.get("canonical", query.strip())
        variants = [canonical] + qo.get("queries", [])
        if "iit ropar" not in canonical.lower():
            variants.append(f"{canonical} IIT Ropar")
        info["canonical"], info["queries"] = canonical, variants

        # retrieve
        candidate_docs = []
        for v in variants:
            try:
                docs_v = vectordb.max_marginal_relevance_search(v, k=top_k, fetch_k=120)
            except Exception:
                docs_v = vectordb.similarity_search(v, k=top_k)
            candidate_docs.extend(docs_v)

        # dedup
        seen = set(); deduped = []
        for d in candidate_docs:
            meta = getattr(d, 'metadata', {}) or {}
            email_key = str(meta.get('email') or '').strip().lower()
            name_key = str(meta.get('question') or meta.get('name') or '').strip().lower()
            key = email_key or name_key or (d.page_content[:100].lower() if d.page_content else '')
            if key and key not in seen:
                seen.add(key); deduped.append(d)

        # filter decisions
        signals = _extract_signals(canonical)
        for d in deduped:
            passed = _passes_generic_filter(d, signals)
            info["candidates"].append({
                "passed": passed,
                "snippet": (d.page_content or '')[:300],
                "metadata": getattr(d, 'metadata', {}) or {}
            })
        filtered = [d for d in deduped if _passes_generic_filter(d, signals)]
        chosen = filtered if filtered else deduped
        selected = chosen[:top_k]
        info["filtered"] = [bool(_passes_generic_filter(d, signals)) for d in deduped]
        info["selected"] = [{"snippet": (d.page_content or '')[:300], "metadata": getattr(d, 'metadata', {}) or {}} for d in selected]

        context = "\n\n".join(doc.page_content for doc in selected)
        prompt_text = prompt_template.format_prompt(context=context, question=query).to_string()
        info["final_prompt"] = prompt_text[:2000]
        return info
    except Exception as e:
        info["error"] = str(e)
        return info

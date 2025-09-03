from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Prompt template for CSV Q&A
template = """You are a helpful assistant for IIT Ropar-specific information. Answer the user’s question only using the information in the context provided.

Rules:

Use only the context provided; do NOT assume or add information.
All context provided directly refers to IIT Ropar. So when I say "Is there a hospital?", it means "Is there a hospital in IIT Ropar."
Answer directly and concisely, in 1–4 lines.

Do not create puzzles, hypothetical scenarios, reasoning chains, or explanations.

If the question is about the mess menu, list exact meals: breakfast, lunch, and dinner.

If the answer is not in the context, respond exactly: "I’m sorry, I don’t have information on that."
If the question is not in the context, respond exactly: "I’m sorry, I don’t have information on that."
Never hallucinate; answer only the asked question.

Example:
Q: “Is there a medical facility on campus?”
A: “Yes, IIT Ropar has a campus health center providing medical services to students, staff, and faculty.”

Context:
{context}

Question:
{question}

Answer:
"""

prompt_template = ChatPromptTemplate.from_template(template)
llm = OllamaLLM(model="phi", temperature=0.2)

def answer_question(vectordb, query, top_k=3, category=None):
    """
    Retrieve top-k relevant documents and answer the query.
    If category is provided, filter documents by category metadata.
    """
    if category:
        # Filter search by category metadata
        retrieved = vectordb.similarity_search(
            query,
            k=top_k,
            filter={"category": category}
        )
    else:
        retrieved = vectordb.similarity_search(query, k=top_k)

    if not retrieved:
        return "I’m sorry, I don’t have information on that."

    context = "\n\n".join([
        f"Question: {doc.metadata['question']}\n"
        f"Answer: {doc.page_content}\n"
        f"Category: {doc.metadata.get('category', 'General')}"
        for doc in retrieved
    ])

    prompt_text = prompt_template.format_prompt(
        context=context,
        question=query
    ).to_string()

    return llm.invoke(prompt_text)

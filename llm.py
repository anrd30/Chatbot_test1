from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

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
# Using llama3 for better understanding and response generation
llm = OllamaLLM(model="phi:latest", temperature=0.3, max_tokens=1024)

def normalize_name(name):
    """Normalize name variations for better matching."""
    return ''.join(c.lower() for c in name if c.isalnum())

def answer_question(vectordb, query, top_k=5, use_mmr=True):
    """
    Retrieves relevant context from ChromaDB and queries the LLM with a strict prompt.
    """

    try:
        # 1️⃣ Retrieve documents
        results = vectordb.similarity_search(query, k=top_k)
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

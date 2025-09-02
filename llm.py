from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template = """You are a helpful assistant for college-specific information. Answer the user's question ONLY using the information in the context below.

Guidelines:
1. Use only the context provided; do NOT assume or provide information not in the context.
2. If the answer is not in the context, politely respond:
   "I’m sorry, I don’t have information on that."
3. Provide concise, clear, and relevant answers.
4. Organize your answer with bullet points or numbered lists if needed.

Context:
{context}

Question:
{question}

Answer:
"""

prompt_template = ChatPromptTemplate.from_template(template)
llm = OllamaLLM(model="phi:2")

def answer_question(vectordb, query, top_k=3):
    retrieved = vectordb.similarity_search(query, k=top_k)
    context = "\n\n".join([
        f"Source: {doc.metadata['source']} (Page {doc.metadata['page']})\n{doc.page_content}"
        for doc in retrieved
    ])
    prompt_text = prompt_template.format_prompt(context=context, question=query).to_string()
    return llm(prompt_text)

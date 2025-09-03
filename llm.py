from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Prompt template for CSV Q&A
template = """You are a helpful assistant for IIT Ropar-specific information. Answer the user's question ONLY using the information in the context below.

Guidelines:
1. Use only the context provided; do NOT assume or provide information not in the context.
2. If the answer is not in the context, respond with:
   "I’m sorry, I don’t have information on that."
3. Provide **direct and concise answers**, without reasoning steps or extra elaboration.
4. If the question is about a mess menu, list the exact meals (breakfast, lunch, dinner)  with break fast lumch and dinner mentioned clearly.
5.DONT CREATE ALL PUZZLE NONSENE AND HALLUCINATE FOR EACH QUESTION IF THERE'S A SIMPLE ANSWER OUTPUT THAT
6.OTHERWISE SAY IDK . IF YOU SAY IDK ITS A GOOD THING 
7. NEVER HALLUCINATE UR ASNweR SHOULD BE IN 4 LINES MAX. IF STOP GOING TO PUZZLES AGAIN AND AGAIN . I WANT A STRICT FUNDAMENTAL CONCISE ONLY RELEVANT TO TEXT ANSWER
Context:
{context}

Question:
{question}

Answer:
"""

prompt_template = ChatPromptTemplate.from_template(template)
llm = OllamaLLM(model="phi")

def answer_question(vectordb, query, top_k=3):
    """
    Retrieve top-k relevant documents and answer the query.
    """
    retrieved = vectordb.similarity_search(query, k=top_k)
    context = "\n\n".join([
        f"Question: {doc.metadata['question']}\nAnswer: {doc.page_content}"
        for doc in retrieved
    ])
    prompt_text = prompt_template.format_prompt(context=context, question=query).to_string()
    return llm(prompt_text)

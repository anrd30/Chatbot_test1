import pandas as pd
import json
from langchain_ollama.llms import OllamaLLM

# Choose Ollama model: "mistral:7b-instruct" (better quality, slower) OR "phi:latest" (faster)
llm = OllamaLLM(model="mistral:7b-instruct", temperature=0.4, max_tokens=300)

def generate_paraphrases(question: str, n: int = 4):
    """
    Generate n paraphrases for a given question using Ollama.
    Returns a list of unique paraphrases.
    """
    prompt = f"""
    Generate {n} different paraphrases of the following question about IIT Ropar.
    - Each paraphrase must mean the SAME thing but sound different.
    - Keep them short (<12 words).
    - Preserve names, departments, and entities exactly as they are.
    - Return ONLY a JSON list of strings, no explanations.
    EX: INPUT CSV
    category,question,answer
Department,Who is the HOD of CSE?,Dr. Nitin Auluck
Facilities,Is there a hospital?,Yes, there is a health center
OUTPUT_CSV
category,question,answer
Department,Who is the HOD of CSE?,Dr. Nitin Auluck
Department,Who runs the CSE department?,Dr. Nitin Auluck
Department,Who is heading Computer Science at IIT Ropar?,Dr. Nitin Auluck
Department,Which professor is HoD of Computer Science?,Dr. Nitin Auluck
Department,Who leads the Department of CSE?,Dr. Nitin Auluck
Facilities,Is there a hospital?,Yes, there is a health center
Facilities,Does IIT Ropar have a hospital?,Yes, there is a health center
Facilities,Is medical care available on campus?,Yes, there is a health center
Facilities,Is there a health facility at IIT Ropar?,Yes, there is a health center
Facilities,Does the campus have a clinic?,Yes, there is a health center

    Question: {question}
    """
    try:
        raw = llm.invoke(prompt).strip()
        paras = json.loads(raw)  # Parse JSON
        if isinstance(paras, list):
            cleaned = []
            seen = set()
            for p in paras:
                if isinstance(p, str):
                    s = p.strip()
                    if s and s.lower() not in seen:
                        seen.add(s.lower())
                        cleaned.append(s)
            return cleaned[:n]
    except Exception as e:
        print(f"[WARN] Failed to parse paraphrases for '{question}': {e}")
    return [question]  # fallback

# === Main Script ===
input_csv = r"C:\Users\Dell\Chatbot_test2\DATA_05_09_2025 - Sheet1.csv"        # your input CSV with category, question, answer
output_csv = r"DATA_FAQ_EXPANDED.csv"

df = pd.read_csv(input_csv)
expanded_rows = []

for _, row in df.iterrows():
    category, question, answer = row["Category"], row["Question"], row["Answer"]
    
    # Generate 4 variants
    variants = generate_paraphrases(question, n=4)
    
    # Save original + variants with category intact
    for q in [question] + variants:
        expanded_rows.append({"category": category, "question": q, "answer": answer})

df_expanded = pd.DataFrame(expanded_rows)
df_expanded.to_csv(output_csv, index=False)

print(f"✅ Expanded dataset saved to {output_csv} with {len(df_expanded)} rows")

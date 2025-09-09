import csv
import json
from pathlib import Path

CSV_PATH = Path(r"C:\Users\Dell\Chatbot_test2\DATA_05_09_2025 - Sheet1.csv")
OUT_PATH = Path(r"C:\Users\Dell\Chatbot_test2\frontend_new\public\testing\redteam_questions.json")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# Simple helpers

def norm_header(h: str) -> str:
    return (h or "").strip().lower()


def make_questions_from_row(cat: str, q: str, a: str) -> list[str]:
    cat_l = (cat or "").lower()
    q_l = (q or "").lower()
    res = []

    # Leadership / HoD / Head variants
    if any(tok in q_l for tok in ["hod", "head", "who runs", "head of"]):
        base = q
        res.extend([
            base,
            base.replace("Who is", "Who is the").replace("who is", "who is the"),
            base.replace("head", "head of the department"),
            base.replace("HoD", "Head of Department"),
            base.replace("department", "dept"),
        ])

    # Teaching / Courses / Syllabus
    if any(tok in q_l for tok in ["course", "courses", "subject", "syllabus", "teach", "teaches"]):
        res.extend([
            q,
            q.replace("What is", "What are"),
            q.replace("courses", "subjects").replace("course", "courses"),
        ])

    # Research interests
    if any(tok in q_l for tok in ["interest", "interests", "research"]):
        res.extend([
            q,
            q.replace("What are", "What is"),
            q.replace("research interests", "research areas"),
        ])

    # Hostel / Mess governance
    if "mess" in q_l or "hostel" in q_l or "warden" in q_l or "executive council" in q_l:
        res.extend([
            q,
            q.replace("Who", "Who all"),
            q.replace("How", "Explain how"),
        ])

    # Guest House
    if "guest house" in q_l or "booking" in q_l:
        res.extend([
            q,
            q.replace("Who approves", "Who is responsible for approving"),
            q.replace("How far", "Up to how many days in advance"),
        ])

    # SAIDE / unit programs
    if "saide" in q_l:
        res.extend([
            q,
            q.replace("What programs", "List the academic programs"),
            q.replace("vision", "What is the vision statement of SAIDE"),
            q.replace("mission", "What is the mission of SAIDE"),
        ])

    # Course codes
    if any(cc in q for cc in ["CS", "CH", "CY", "EE", "ME"]):
        res.extend([
            q,
            q.replace("What", "Explain what"),
            q.replace(",", " "),
        ])

    # Generic variants
    if not res:
        res = [q, q + " at IIT Ropar"]

    # Dedup and normalize
    seen = set()
    out = []
    for item in res:
        s = " ".join((item or "").split()).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out[:4]


def main():
    with open(CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        # Normalize headers
        fieldnames = [norm_header(h) for h in reader.fieldnames or []]
        rows = []
        for raw in reader:
            row = {norm_header(k): (v or "").strip() for k, v in raw.items()}
            rows.append(row)

    questions = []
    for r in rows:
        cat = r.get("category", "")
        q = r.get("question", "")
        a = r.get("answer", "")
        if not q or not a:
            continue
        qs = make_questions_from_row(cat, q, a)
        for qq in qs:
            questions.append({
                "category": cat,
                "source_question": q,
                "generated_question": qq,
            })

    # Balance and cap ~200
    # Sample evenly by category
    by_cat = {}
    for item in questions:
        by_cat.setdefault(item["category"], []).append(item)
    balanced = []
    per_cat = max(1, 200 // max(1, len(by_cat)))
    for cat, items in by_cat.items():
        balanced.extend(items[:per_cat])
    # If under 200, top up with remaining
    if len(balanced) < 200:
        extra = [x for x in questions if x not in balanced]
        balanced.extend(extra[: 200 - len(balanced)])

    OUT_PATH.write_text(json.dumps({"count": len(balanced), "items": balanced}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {len(balanced)} questions to {OUT_PATH}")


if __name__ == "__main__":
    main()

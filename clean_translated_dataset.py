import json
from pathlib import Path

INPUT_FILE = Path("dataset/merged/all_problems_translated_vi.json")
OUTPUT_FILE = Path("dataset/processed/clean_problems_vi.json")

def is_valid_problem(p, seen_ids):
    pid = p.get("id")
    if not pid or pid in seen_ids:
        return False
    keywords = p.get("keywords")
    if not isinstance(keywords, list) or not keywords:
        return False
    text = p.get("problem_text_vi")
    if not isinstance(text, str) or len(text.strip()) < 30:
        return False
    return True

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        problems = json.load(f)

    cleaned = []
    seen_ids = set()
    for p in problems:
        if is_valid_problem(p, seen_ids):
            seen_ids.add(p["id"])
            cleaned.append(p)

    print(f"Giữ lại {len(cleaned)}/{len(problems)} bài hợp lệ.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    print(f"Đã lưu dữ liệu sạch vào: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
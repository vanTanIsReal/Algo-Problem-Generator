import json
import os
import re
from deep_translator import GoogleTranslator

# 1. TỪ ĐIỂN CHUYÊN NGÀNH (DOMAIN DICTIONARY)
# Bạn có thể bổ sung thêm các tag hay gặp trên Codeforces vào đây
TECH_DICT = {
    "brute force": "vét cạn",
    "dynamic programming": "quy hoạch động",
    "dp": "quy hoạch động",
    "greedy": "thuật toán tham lam",
    "graphs": "đồ thị",
    "trees": "cây",
    "binary search": "tìm kiếm nhị phân",
    "two pointers": "hai con trỏ",
    "data structures": "cấu trúc dữ liệu",
    "math": "toán học",
    "geometry": "hình học",
    "bitmasks": "mặt nạ bit",
    "sortings": "thuật toán sắp xếp",
    "shortest paths": "đường đi ngắn nhất",
    "dfs and similar": "tìm kiếm theo chiều sâu",
    "dsu": "cấu trúc tập hợp rời rạc",
    "string suffix structures": "cấu trúc hậu tố chuỗi",
    "divide and conquer": "chia để trị"
}

def clean_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def translate_keyword(kw, translator):
    """Hàm xử lý dịch keyword thông minh"""
    kw_lower = kw.lower().strip()
    # Nếu có trong từ điển chuyên ngành -> Lấy luôn
    if kw_lower in TECH_DICT:
        return TECH_DICT[kw_lower]
    # Nếu không có -> Nhờ Google dịch
    return translator.translate(kw)

def process_and_translate_dataset(input_file="dataset/raw/codeforces_raw.json", output_file="dataset/processed/train.json"):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[!] Không tìm thấy file {input_file}.")
        return

    translator = GoogleTranslator(source='en', target='vi')
    processed_data = []
    
    print(f"Bắt đầu làm sạch và dịch với TỪ ĐIỂN CHUYÊN NGÀNH...\n" + "="*50)
    
    for i, item in enumerate(data):
        try:
            # Dùng hàm dịch thông minh cho danh sách keywords
            translated_keywords = [translate_keyword(kw, translator) for kw in item['keywords']]
            
            clean_text = clean_html_tags(item['problem_text'])
            translated_text = translator.translate(clean_text[:4000])
            
            processed_data.append({
                "id": item['id'],
                "keywords": translated_keywords,
                "problem_text": translated_text
            })
            
            print(f"[{i+1}/{len(data)}] Đã dịch xong bài: {item['id']}")
            
        except Exception as e:
            print(f"[!] Lỗi ở bài {item['id']}: {e}")
            continue

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=4)
        
    print("Hoàn tất dịch thuật an toàn!")

if __name__ == "__main__":
    process_and_translate_dataset()
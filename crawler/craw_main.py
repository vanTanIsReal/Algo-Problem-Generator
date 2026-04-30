import requests
from bs4 import BeautifulSoup
import json
import os
import time

# Đảm bảo thư mục lưu dữ liệu thô tồn tại
os.makedirs("dataset/raw", exist_ok=True)

def get_problem_description(contest_id, index):
    """
    Hàm này vào thẳng URL của từng bài để bóc tách phần mô tả (tránh lấy cả input/output rác)
    """
    url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
    try:
        # Giả lập header trình duyệt để không bị chặn
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Codeforces bọc toàn bộ đề trong class 'problem-statement'
        statement = soup.find('div', class_='problem-statement')
        if not statement:
            return None
        
        # Phần mô tả luôn nằm ngay sau phần 'header' và trước 'input-specification'
        header = statement.find('div', class_='header')
        description_text = ""
        
        if header:
            for sibling in header.next_siblings:
                if sibling.name == 'div' and sibling.get('class') and 'input-specification' in sibling.get('class'):
                    break # Gặp phần "Input" thì dừng, ta chỉ cần mô tả đề
                if sibling.name == 'div' or sibling.name == 'p':
                    description_text += sibling.get_text(separator=' ', strip=True) + " "
                    
        return description_text.strip()
    except Exception as e:
        print(f"[!] Lỗi khi cào {url}: {e}")
        return None

def crawl_dataset(limit=50):
    """
    Hàm chính điều phối việc cào dữ liệu
    """
    print("1. Đang gọi Codeforces API để lấy danh sách bài và Keywords (Tags)...")
    api_url = "https://codeforces.com/api/problemset.problems"
    res = requests.get(api_url).json()
    
    if res['status'] != 'OK':
        print("[!] Lỗi gọi API Codeforces")
        return
    
    problems = res['result']['problems']
    dataset = []
    
    print(f"2. Bắt đầu cào chi tiết {limit} bài đầu tiên...\n" + "="*50)
    
    for i, prob in enumerate(problems[:limit]):
        contest_id = prob.get('contestId')
        index = prob.get('index')
        tags = prob.get('tags', []) # Đây chính là Keyword cho model của bạn
        
        if not contest_id or not tags:
            continue
            
        print(f"[{i+1}/{limit}] Cào bài {contest_id}{index} | Keywords: {tags}")
        description = get_problem_description(contest_id, index)
        
        if description and len(description) > 50: # Bỏ qua các bài có mô tả quá ngắn hoặc lỗi
            dataset.append({
                "id": f"CF_{contest_id}_{index}",
                "keywords": tags,
                "problem_text": description
            })
        
        # LƯU Ý SỐNG CÒN: Nghỉ 1 giây để không bị máy chủ Codeforces ban IP
        time.sleep(1)
        
    # Lưu file JSON
    output_path = "dataset/raw/codeforces_raw.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
        
    print("="*50)
    print(f"Hoàn thành! Đã lưu thành công {len(dataset)} bài vào: {output_path}")

if __name__ == "__main__":
    # Test thử 20 bài trước để xem dữ liệu có sạch không
    # Nếu ổn định, bạn có thể tăng limit lên 1000 hoặc 5000 để tạo dataset lớn
    crawl_dataset(limit=5000)
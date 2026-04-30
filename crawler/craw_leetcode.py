import requests
import json
import os
import time

# Đảm bảo thư mục lưu dữ liệu thô tồn tại
os.makedirs("dataset/raw", exist_ok=True)

# URL API của LeetCode
LEETCODE_URL = "https://leetcode.com/graphql"

def get_leetcode_problems_list(limit=50):
    """
    Bước 1: Lấy danh sách tên định danh (titleSlug) của các bài toán
    """
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: $categorySlug
        limit: $limit
        skip: $skip
        filters: $filters
      ) {
        total: totalNum
        questions: data {
          titleSlug
        }
      }
    }
    """
    variables = {
        "categorySlug": "",
        "skip": 0,
        "limit": limit,
        "filters": {}
    }
    
    print(f"1. Đang lấy danh sách {limit} bài toán từ LeetCode...")
    response = requests.post(LEETCODE_URL, json={"query": query, "variables": variables})
    
    if response.status_code == 200:
        data = response.json()
        return [q['titleSlug'] for q in data['data']['problemsetQuestionList']['questions']]
    else:
        print("[!] Lỗi khi lấy danh sách bài toán:", response.status_code)
        return []

def get_problem_details(title_slug):
    """
    Bước 2: Lấy chi tiết đề bài (Content) và Từ khóa (Tags) bằng titleSlug
    """
    query = """
    query questionData($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionId
        title
        content
        topicTags {
          name
        }
      }
    }
    """
    variables = {"titleSlug": title_slug}
    
    # Header để đánh lừa LeetCode rằng đây là trình duyệt thật
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    
    response = requests.post(LEETCODE_URL, json={"query": query, "variables": variables}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        question = data['data']['question']
        
        # Lấy danh sách tags
        tags = [tag['name'] for tag in question.get('topicTags', [])]
        content = question.get('content', '')
        
        return tags, content
    return [], ""

def crawl_leetcode_dataset(limit=20):
    """
    Hàm chính điều phối
    """
    slugs = get_leetcode_problems_list(limit)
    if not slugs:
        return
        
    dataset = []
    print(f"2. Bắt đầu cào chi tiết {len(slugs)} bài...\n" + "="*50)
    
    for i, slug in enumerate(slugs):
        print(f"[{i+1}/{len(slugs)}] Đang xử lý: {slug}")
        tags, content = get_problem_details(slug)
        
        if content and tags:
            dataset.append({
                "id": f"LC_{slug}",
                "keywords": tags,
                "problem_text": content # Lưu ý: Đây vẫn là HTML, file clean_data.py sẽ xử lý sau
            })
            
        # NGHỈ GIẢI LAO ĐỂ KHÔNG BỊ BAN IP
        time.sleep(2) 
        
    # Lưu ra file
    output_path = "dataset/raw/leetcode_raw.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
        
    print("="*50)
    print(f"Hoàn thành! Đã lưu thành công {len(dataset)} bài vào: {output_path}")

if __name__ == "__main__":
    # Test thử 20 bài trước
    crawl_leetcode_dataset(limit=20)
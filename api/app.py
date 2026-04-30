from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Khởi tạo ứng dụng FastAPI
app = FastAPI(
    title="AI Programming Judge Pipeline",
    description="Hệ thống tự động sinh đề bài, giải code và chấm điểm",
    version="1.0.0"
)

# ==========================================
# 1. Định nghĩa cấu trúc dữ liệu (Schemas)
# ==========================================
class KeywordRequest(BaseModel):
    keywords: List[str]

class ProblemRequest(BaseModel):
    problem_text: str

class JudgeRequest(BaseModel):
    source_code: str
    test_cases: List[dict] # Ví dụ: [{"input": "2 3", "output": "5"}]

# ==========================================
# 2. Các Endpoints (Đường dẫn API)
# ==========================================

@app.get("/")
async def root():
    return {"message": "Hệ thống AI Pipeline đã sẵn sàng hoạt động!"}

@app.post("/generate-problem")
async def generate_problem(req: KeywordRequest):
    """
    Module 1: Nhận keyword và gọi model sinh ra đề bài lập trình
    """
    # TODO: Import và gọi model tan_former.py tại đây
    
    # Code fake nghiệm thu tạm thời
    fake_problem = f"Cho các từ khóa {', '.join(req.keywords)}, hãy viết một thuật toán tối ưu..."
    
    return {
        "status": "success",
        "keywords_received": req.keywords,
        "problem_statement": fake_problem
    }

@app.post("/solve-code")
async def solve_code(req: ProblemRequest):
    """
    Module 2: Nhận văn bản đề bài và sinh ra mã nguồn (Python/C++)
    """
    # TODO: Gọi model Code Generation (ví dụ CodeT5) tại đây
    
    fake_code = "def solve():\n    # TODO: Implement logic\n    pass\n\nif __name__ == '__main__':\n    solve()"
    
    return {
        "status": "success",
        "source_code": fake_code
    }

@app.post("/judge")
async def run_judge(req: JudgeRequest):
    """
    Module 3: Ném mã nguồn vào Docker Sandbox để chạy test case
    """
    # TODO: Viết logic gọi Docker SDK và thực thi code
    
    return {
        "status": "judged",
        "verdict": "Accepted", # hoặc "Wrong Answer", "Time Limit Exceeded"
        "pass_rate": "100%"
    }
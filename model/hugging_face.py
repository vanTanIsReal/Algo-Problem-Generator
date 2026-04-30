from transformers import AutoTokenizer, AutoModel
import torch

def test_huggingface_embedding():
    # Tên model bạn muốn dùng
    model_name = "vinai/phobert-base-v2" # Hoặc chọn 1 trong 3 cái trên"
    # Hoặc nếu data tiếng Anh, thử dùng: model_name = "sentence-transformers/all-MiniLM-L6-v2"
    
    print(f"Đang tải {model_name} về máy...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    embedding_model = AutoModel.from_pretrained(model_name)
    
    # Giả sử đây là input keyword bạn truyền vào
    keywords = "Graph Shortest Path Dijkstra"
    
    # Bước 1: Tokenizer băm chữ thành số
    inputs = tokenizer(keywords, return_tensors="pt", padding=True, truncation=True)
    
    # Bước 2: Model biến số thành Vector ma trận (Embedding)
    with torch.no_grad(): # Tắt tính đạo hàm để chạy cho nhanh lúc test
        outputs = embedding_model(**inputs)
    
    # Lấy vector đại diện (thường là token [CLS] ở vị trí đầu tiên)
    embeddings = outputs.last_hidden_state
    
    print("Kích thước ma trận (Batch, Số Token, Số Chiều Vector):", embeddings.shape)
    return embeddings

if __name__ == "__main__":
    test_huggingface_embedding()
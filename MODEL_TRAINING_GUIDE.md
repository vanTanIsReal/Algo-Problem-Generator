# Hướng dẫn Xây dựng Mô hình Sinh Đề Bài

## 📋 Tổng Quan

Dự án tự động sinh đề bài dựa trên từ khóa (keywords) đã được xây dựng hoàn chỉnh với các bước chính:

### Quy trình Hoàn chỉnh:

```
Crawl dữ liệu → Merge → Dịch → Lọc sạch → Chia train/valid/test → Huấn luyện → Sinh đề
```

---

## 🔄 Các Bước Đã Thực Hiện

### 1. ✅ Lọc Dữ liệu Lỗi (Clean Data)
**File**: `clean_translated_dataset.py`

```bash
python clean_translated_dataset.py
```

**Kết quả**: 
- Đầu vào: 8,341 bài toán
- Đầu ra: 4,771 bài hợp lệ
- Tiêu chí lọc:
  - ID phải tồn tại, không trùng
  - Keywords là list không rỗng
  - problem_text_vi có độ dài > 30 ký tự

---

### 2. ✅ Chia Bộ Dữ liệu (Dataset Split)
**File**: `split_dataset.py`

```bash
python split_dataset.py
```

**Kết quả**:
- Train: 3,816 bài (80%)
- Valid: 477 bài (10%)
- Test: 478 bài (10%)

**Lưu vào**:
- `dataset/processed/train.json`
- `dataset/processed/valid.json`
- `dataset/processed/test.json`

---

### 3. 📊 Phân Tích Dữ liệu (Dataset Analysis)
**File**: `train/eval.py`

```bash
python train/eval.py
```

**Thống kê chính**:
- **Từ khóa**: 38 loại
- **Trung bình keywords/bài**: 3.55
- **Trung bình độ dài mô tả**: 989 ký tự

**Top 10 Từ Khóa**:
1. greedy (205)
2. math (200)
3. constructive algorithms (139)
4. dp (120)
5. implementation (118)
6. brute force (108)
7. data structures (106)
8. binary search (69)
9. sortings (61)
10. combinatorics (59)

---

### 4. 🤖 Huấn Luyện Mô hình (Model Training)

#### **Phương án 1: Mô hình Đơn Giản (Simple Model)**
**File**: `train/train_simple.py`

Sử dụng phương pháp TF-IDF kết hợp tìm kiếm các bài toán có keyword tương tự.

```bash
python train/train_simple.py
```

**Đặc điểm**:
- Không cần PyTorch/Transformers
- Nhanh chóng, phù hợp để test
- Kết quả chấp nhận được cho baseline

**Checkpoint**: `checkpoint/simple_tfidf_model/model.pkl`

---

#### **Phương án 2: Mô hình Transformer (Advanced)**
**File**: `train/train.py`

Sử dụng T5 (Text-to-Text Transfer Transformer) từ Hugging Face.

**Yêu cầu cài đặt**:
```bash
pip install torch transformers accelerate datasets
```

**Chạy training**:
```bash
python train/train.py
```

**Checkpoint**: `checkpoint/t5_problem_generator/`

---

### 5. 🎯 Sinh Đề từ Keywords (Inference)

#### **Dùng Mô hình Đơn giản**:
**File**: `train/infer_simple.py`

```bash
python train/infer_simple.py
```

**Kết quả**: `dataset/processed/generated_problems_simple.json`

**Ví dụ Đầu ra**:
```
Keywords: ['math', 'recursion']
Generated: Kamilka has a flock of n sheep, the i-th of which has a beauty 
level of a_i. All a_i are distinct...

Keywords: ['binary search', 'divide and conquer']
Generated: Boboniu defines BN-string as a string s of characters 'B' and 'N'...
```

#### **Dùng Mô hình Transformer** (sau khi cài PyTorch):
**File**: `train/infer.py`

```bash
python train/infer.py
```

---

## 📁 Cấu Trúc File/Folder

```
dataset/
├── processed/
│   ├── clean_problems_vi.json        # Dữ liệu sạch
│   ├── train.json                     # Tập huấn luyện
│   ├── valid.json                     # Tập validation
│   ├── test.json                      # Tập kiểm tra
│   └── generated_problems_simple.json # Đề sinh ra

checkpoint/
├── simple_tfidf_model/
│   └── model.pkl                      # Mô hình đơn giản
└── t5_problem_generator/              # Mô hình Transformer (nếu huấn luyện)

train/
├── train.py          # Huấn luyện với Transformers
├── train_simple.py   # Huấn luyện mô hình đơn giản
├── infer.py          # Sinh đề với Transformers
├── infer_simple.py   # Sinh đề với mô hình đơn giản
└── eval.py           # Đánh giá mô hình
```

---

## 🚀 Để Bắt Đầu Từ Đầu

Nếu bạn chạy từ đầu (từ crawl data), hãy làm theo các bước:

```bash
# 1. Crawl dữ liệu
python crawler/craw_main.py

# 2. Merge các khối dữ liệu
python merge_datasets.py

# 3. Dịch sang Tiếng Việt
python translate_dataset.py

# 4. Lọc dữ liệu lỗi
python clean_translated_dataset.py

# 5. Chia train/valid/test
python split_dataset.py

# 6. Phân tích dữ liệu
python train/eval.py

# 7. Huấn luyện mô hình (chọn một)
python train/train_simple.py      # Mô hình đơn giản
# hoặc
python train/train.py              # Mô hình Transformer

# 8. Sinh đề
python train/infer_simple.py       # Dùng mô hình đơn giản
# hoặc
python train/infer.py              # Dùng mô hình Transformer
```

---

## 📊 Kết Quả Hiện Tại

✅ **Hoàn thành**:
- ✔ Lọc dữ liệu sạch (4,771 bài)
- ✔ Chia bộ dữ liệu (train/valid/test)
- ✔ Phân tích thống kê
- ✔ Huấn luyện mô hình đơn giản
- ✔ Sinh đề từ keywords

📈 **Tiếp theo (Optional)**:
- [ ] Huấn luyện mô hình Transformer (cần cài PyTorch)
- [ ] Cải thiện chất lượng sinh đề
- [ ] Xây dựng API để phục vụ
- [ ] Đánh giá BLEU/ROUGE scores

---

## 💡 Ghi Chú

1. **Mô hình Đơn giản** phù hợp cho:
   - Testing nhanh chóng
   - Baseline so sánh
   - Môi trường không có GPU

2. **Mô hình Transformer** phù hợp cho:
   - Sinh đề chất lượng cao hơn
   - Học các pattern phức tạp
   - Cần cài đặt: `pip install torch transformers`

3. **Cải thiện hiệu năng**:
   - Thêm dữ liệu huấn luyện
   - Tune hyperparameters
   - Sử dụng mô hình lớn hơn (T5-base, T5-large)

---

## 📞 Support

Để chạy các bước cụ thể hoặc cải thiện mô hình, hãy yêu cầu!

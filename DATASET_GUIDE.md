# Dataset Merge & Translation Guide

## Project Overview
Combined **Codeforces crawled data** with **Hugging Face LeetCode dataset** and translated to Vietnamese.

## What Was Done

### 1. ✅ Data Download & Merge
- **Codeforces Data**: 4,792 problems (crawled from your raw data)
- **Hugging Face LeetCode Data**: 3,549 problems from `Alishohadaee/leetcode-problems-dataset`
- **Total Merged**: 8,341 problems
- **Output File**: `dataset/merged/all_problems_merged.json`

### 2. 🔄 Vietnamese Translation (In Progress)
- **Process**: Translating all problem texts to Vietnamese using Google Translate
- **Status**: Currently processing ~8,341 problems
- **Output File**: `dataset/merged/all_problems_translated_vi.json`

## Data Structure

Each problem entry contains:
```json
{
  "id": "CF_2226_G",                    // Problem ID
  "keywords": ["strings", "trees"],     // Problem keywords/topics
  "problem_text": "Original English...", // English problem description
  "problem_text_vi": "Bản dịch tiếng Việt..." // Vietnamese translation (if available)
}
```

## File Locations

```
dataset/
├── raw/
│   └── codeforces_raw.json      (4,792 Codeforces problems)
├── hf_leetcode/                 (Downloaded Hugging Face dataset)
│   └── leetcode_problems.json   (3,549 LeetCode problems)
└── merged/
    ├── all_problems_merged.json (8,341 merged problems)
    └── all_problems_translated_vi.json (Translated - in progress)
```

## How to Use the Data

### 1. Load the Merged Dataset
```python
import json

with open('dataset/merged/all_problems_merged.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

print(f"Total problems: {len(problems)}")
for problem in problems[:3]:
    print(f"ID: {problem['id']}")
    print(f"Keywords: {problem['keywords']}")
    print(f"Text: {problem['problem_text'][:100]}...")
```

### 2. Access Vietnamese Translations (when available)
```python
import json

with open('dataset/merged/all_problems_translated_vi.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

for problem in problems:
    if 'problem_text_vi' in problem and problem['problem_text_vi']:
        print(f"[{problem['id']}] {problem['problem_text_vi'][:100]}...")
```

### 3. Filter by Keywords
```python
import json

with open('dataset/merged/all_problems_merged.json', 'r', encoding='utf-8') as f:
    problems = json.load(f)

# Find all graph problems
graph_problems = [p for p in problems if 'graphs' in p.get('keywords', [])]
print(f"Found {len(graph_problems)} graph problems")
```

## Next Steps

### Option 1: Model Training
Use the merged dataset to train your LeetCode/Codeforces problem model:
- Input: `problem_text` or `problem_text_vi`
- Output: Problem solutions or classifications

### Option 2: Analysis
- Analyze problem distribution by keywords
- Compare Codeforces vs LeetCode problem types
- Generate statistics on problem difficulty/topics

### Option 3: Web Application
- Create a search interface for the combined dataset
- Provide Vietnamese translations for users
- Generate practice recommendations

## Translation Details

- **Language**: English → Vietnamese
- **Translator**: Google Translate (via deep-translator library)
- **Processing**: Batch of 10 problems with 1s delay between batches
- **Coverage**: All problem texts with maximum 5000 characters each

## Performance Notes

- **Total Size**: ~46MB (includes both English and Vietnamese texts)
- **Processing Time**: ~14 minutes for full translation of 8,341 problems
- **API Rate Limiting**: 1 second delay between batches to be respectful to Google's API

## Files Generated

1. `merge_datasets.py` - Script to download and merge datasets
2. `translate_dataset.py` - Script to translate merged dataset to Vietnamese
3. `dataset/merged/all_problems_merged.json` - Combined English dataset
4. `dataset/merged/all_problems_translated_vi.json` - Combined dataset with Vietnamese translations

## Troubleshooting

### Translation Takes Too Long
- Reduce `BATCH_SIZE` in `translate_dataset.py` to process faster
- Increase `SLEEP_TIME` if you hit rate limits

### Memory Issues
- Process data in chunks instead of loading all at once
- Use streaming JSON reader for very large files

### Translation Accuracy
- Some problems contain mathematical notation that may not translate perfectly
- Review translated texts manually if using for production

## Statistics

```
Total Combined Dataset: 8,341 problems
├── Codeforces: 4,792 problems (57.4%)
└── LeetCode: 3,549 problems (42.6%)

Keywords Distribution: (varies by problem source)
Example topics: graphs, trees, strings, math, DP, greedy, arrays, etc.
```

## Credits

- **Dataset Sources**:
  - Codeforces: Your crawled data
  - LeetCode: [Alishohadaee/leetcode-problems-dataset](https://huggingface.co/datasets/Alishohadaee/leetcode-problems-dataset)

- **Tools Used**:
  - `huggingface_hub`: For downloading HF datasets
  - `deep_translator`: For Vietnamese translations
  - `json`: For data serialization

---

**Status**: ✅ Data download and merge complete | 🔄 Translation in progress
**Last Updated**: May 3, 2026

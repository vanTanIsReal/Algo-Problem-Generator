#!/usr/bin/env python3
"""
Script to download Hugging Face leetcode dataset and merge with crawled data.
"""

import json
import os
from pathlib import Path
from huggingface_hub import snapshot_download, list_repo_files

# Configuration
HF_DATASET_ID = "Alishohadaee/leetcode-problems-dataset"
DATASET_DIR = Path("dataset")
OUTPUT_DIR = DATASET_DIR / "merged"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"📥 Downloading Hugging Face dataset: {HF_DATASET_ID}")

try:
    # Download the dataset
    repo_path = snapshot_download(
        repo_id=HF_DATASET_ID,
        repo_type="dataset",
        local_dir=DATASET_DIR / "hf_leetcode",
        force_download=False
    )
    print(f"✅ Dataset downloaded to: {repo_path}")
except Exception as e:
    print(f"❌ Error downloading dataset: {e}")
    exit(1)

# Load existing crawled data
crawled_data = []
raw_file = DATASET_DIR / "raw" / "codeforces_raw.json"
if raw_file.exists():
    try:
        with open(raw_file, 'r', encoding='utf-8') as f:
            crawled_data = json.load(f)
        print(f"✅ Loaded {len(crawled_data)} crawled problems from codeforces")
    except Exception as e:
        print(f"⚠️  Error loading crawled data: {e}")

# Load Hugging Face dataset
hf_data = []
hf_dir = DATASET_DIR / "hf_leetcode"

# Try to find JSON/JSONL/Parquet files
for file in hf_dir.rglob("*"):
    if file.suffix in ['.json', '.jsonl']:
        try:
            print(f"📖 Reading: {file.name}")
            with open(file, 'r', encoding='utf-8') as f:
                if file.suffix == '.jsonl':
                    for line in f:
                        if line.strip():
                            hf_data.append(json.loads(line))
                else:
                    content = json.load(f)
                    if isinstance(content, list):
                        hf_data.extend(content)
                    else:
                        hf_data.append(content)
            print(f"   ✅ Loaded {len(hf_data)} records so far")
        except Exception as e:
            print(f"   ⚠️  Error reading {file.name}: {e}")

print(f"\n📊 Data summary:")
print(f"   - Crawled (Codeforces): {len(crawled_data)} problems")
print(f"   - Hugging Face (LeetCode): {len(hf_data)} problems")

# Merge datasets
merged_data = crawled_data + hf_data
print(f"   - Total merged: {len(merged_data)} problems")

# Save merged data
output_file = OUTPUT_DIR / "all_problems_merged.json"
try:
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Merged dataset saved to: {output_file}")
except Exception as e:
    print(f"❌ Error saving merged data: {e}")
    exit(1)

# Also save individual splits if they exist in HF dataset
print(f"\n📂 Checking for dataset splits...")
split_files = {
    'train': DATASET_DIR / "hf_leetcode" / "train-*.parquet",
    'test': DATASET_DIR / "hf_leetcode" / "test-*.parquet",
    'validation': DATASET_DIR / "hf_leetcode" / "validation-*.parquet"
}

for split_name, pattern in split_files.items():
    parquet_files = list(Path("dataset/hf_leetcode").glob(f"{split_name}-*.parquet"))
    if parquet_files:
        print(f"   - Found {split_name} split: {len(parquet_files)} file(s)")
        print(f"     Note: Parquet files require 'pyarrow' library to read")

print(f"\n🎉 Done! Merged data is ready for processing.")
print(f"   Next steps:")
print(f"   1. Install translation library: pip install google-cloud-translate")
print(f"   2. Run translation script to translate the merged data")

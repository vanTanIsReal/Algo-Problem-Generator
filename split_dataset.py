#!/usr/bin/env python3
"""
Script to split cleaned dataset into train/valid/test sets.
"""

import json
import random
from pathlib import Path

INPUT_FILE = Path("dataset/processed/clean_problems_vi.json")
TRAIN_FILE = Path("dataset/processed/train.json")
VALID_FILE = Path("dataset/processed/valid.json")
TEST_FILE = Path("dataset/processed/test.json")

# Configuration
TRAIN_RATIO = 0.8
VALID_RATIO = 0.1
TEST_RATIO = 0.1
RANDOM_SEED = 42

def main():
    print(f"📖 Loading dataset from: {INPUT_FILE}")
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        problems = json.load(f)
    
    print(f"✅ Loaded {len(problems)} problems")
    
    # Shuffle data with fixed seed
    random.seed(RANDOM_SEED)
    random.shuffle(problems)
    
    # Calculate split indices
    total = len(problems)
    train_size = int(total * TRAIN_RATIO)
    valid_size = int(total * VALID_RATIO)
    
    # Split data
    train = problems[:train_size]
    valid = problems[train_size:train_size + valid_size]
    test = problems[train_size + valid_size:]
    
    print(f"\n📊 Dataset split:")
    print(f"   Train: {len(train)} problems ({len(train)/len(problems)*100:.1f}%)")
    print(f"   Valid: {len(valid)} problems ({len(valid)/len(problems)*100:.1f}%)")
    print(f"   Test:  {len(test)} problems ({len(test)/len(problems)*100:.1f}%)")
    
    # Save files
    print(f"\n💾 Saving split datasets...")
    
    for data, path in [(train, TRAIN_FILE), (valid, VALID_FILE), (test, TEST_FILE)]:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   ✅ Saved {len(data)} problems to {path}")
    
    print(f"\n🎉 Dataset split complete!")

if __name__ == "__main__":
    main()

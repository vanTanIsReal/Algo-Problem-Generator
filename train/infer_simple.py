#!/usr/bin/env python3
"""
Generate problems using trained simple model.
"""

import json
import pickle
from pathlib import Path

CHECKPOINT_DIR = Path("checkpoint/simple_tfidf_model")
OUTPUT_FILE = Path("dataset/processed/generated_problems_simple.json")


def load_model(model_path):
    """Load trained model."""
    model_file = model_path / "model.pkl"
    
    if not model_file.exists():
        print(f"❌ Model not found at {model_file}")
        print("   Train the model first: python train/train_simple.py")
        return None
    
    with open(model_file, 'rb') as f:
        model_data = pickle.load(f)
    
    print(f"✅ Model loaded from {model_path}")
    return model_data


def generate_problems(model_data, keywords_list):
    """Generate problems for given keywords."""
    keyword_to_problems = model_data["keyword_to_problems"]
    generated = []
    
    for keywords in keywords_list:
        # Find matching problems
        matching_problems = []
        
        for kw in keywords:
            kw_lower = kw.lower().strip()
            if kw_lower in keyword_to_problems:
                matching_problems.extend(keyword_to_problems[kw_lower])
        
        if matching_problems:
            # Get first matching problem's text
            problem_text = matching_problems[0].get("text", "")[:500]
        else:
            problem_text = f"Problem related to: {', '.join(keywords)}"
        
        generated.append({
            "keywords": keywords,
            "generated_problem_vi": problem_text
        })
    
    return generated


def main():
    print("=" * 60)
    print("Problem Generation (Simple Model)")
    print("=" * 60)
    
    # Load model
    model_data = load_model(CHECKPOINT_DIR)
    if not model_data:
        return
    
    # Test keywords
    test_keywords = [
        ["dynamic programming", "array"],
        ["graph", "BFS"],
        ["string", "sorting"],
        ["math", "recursion"],
        ["binary search", "divide and conquer"],
        ["greedy", "optimization"],
        ["implementation", "constructive algorithms"],
        ["data structures", "queue"],
    ]
    
    print(f"\n🔄 Generating {len(test_keywords)} problems...\n")
    
    generated = generate_problems(model_data, test_keywords)
    
    for item in generated:
        keywords = item["keywords"]
        text = item["generated_problem_vi"][:150]
        print(f"Keywords: {keywords}")
        print(f"Generated: {text}...\n")
    
    # Save results
    print(f"\n💾 Saving generated problems...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(generated, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated problems saved to {OUTPUT_FILE}")
    
    print(f"\n📊 Summary:")
    print(f"   - Generated: {len(generated)} problems")
    print(f"   - Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

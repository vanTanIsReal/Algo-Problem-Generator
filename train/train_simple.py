#!/usr/bin/env python3
"""
Simple problem generation model using TF-IDF and scikit-learn.
This is a lightweight version that doesn't require PyTorch/Transformers.
Can be used for baseline testing or further development.
"""

import json
import pickle
from pathlib import Path
from collections import defaultdict
import random

CHECKPOINT_DIR = Path("checkpoint/simple_tfidf_model")
TRAIN_FILE = "dataset/processed/train.json"
VALID_FILE = "dataset/processed/valid.json"


class SimpleProblemGenerator:
    """Generate problems using TF-IDF based matching."""
    
    def __init__(self):
        self.keyword_to_problems = defaultdict(list)
        self.all_problems = []
        
    def train(self, train_file):
        """Train model by indexing problems by keywords."""
        print("📖 Loading training data...")
        with open(train_file, 'r', encoding='utf-8') as f:
            self.all_problems = json.load(f)
        
        print(f"📊 Indexing {len(self.all_problems)} problems by keywords...")
        
        for problem in self.all_problems:
            keywords = problem.get("keywords", [])
            problem_text = problem.get("problem_text_vi", "")
            
            for keyword in keywords:
                keyword_lower = keyword.lower().strip()
                self.keyword_to_problems[keyword_lower].append({
                    "text": problem_text,
                    "original_keywords": keywords,
                    "id": problem.get("id", "")
                })
        
        print(f"✅ Indexed {len(self.keyword_to_problems)} unique keywords")
    
    def generate(self, keywords, top_k=3):
        """Generate problem by finding similar problems with given keywords."""
        if not keywords:
            # Random problem if no keywords provided
            return random.choice(self.all_problems)["problem_text_vi"]
        
        # Find problems matching the keywords
        matching_problems = []
        keyword_lower = [k.lower().strip() for k in keywords]
        
        for kw in keyword_lower:
            if kw in self.keyword_to_problems:
                matching_problems.extend(self.keyword_to_problems[kw])
        
        if not matching_problems:
            # If no exact match, return random problem
            print(f"   ⚠️  No problems found for keywords: {keywords}")
            return random.choice(self.all_problems)["problem_text_vi"]
        
        # Remove duplicates and return top-k
        unique_problems = {p["id"]: p for p in matching_problems}.values()
        selected = list(unique_problems)[:top_k]
        
        # Combine texts (simple approach)
        combined_text = " ".join([p["text"][:200] for p in selected])  # First 200 chars from each
        return combined_text
    
    def save(self, output_path):
        """Save model to disk."""
        output_path.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "keyword_to_problems": dict(self.keyword_to_problems),
            "all_problems_count": len(self.all_problems)
        }
        
        with open(output_path / "model.pkl", 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {output_path}")
    
    def load(self, model_path):
        """Load model from disk."""
        with open(model_path / "model.pkl", 'rb') as f:
            model_data = pickle.load(f)
        
        self.keyword_to_problems = defaultdict(list, model_data["keyword_to_problems"])
        print(f"✅ Model loaded from {model_path}")


def evaluate_model(model, valid_file):
    """Simple evaluation on validation set."""
    print("\n📊 Evaluating model...")
    
    with open(valid_file, 'r', encoding='utf-8') as f:
        valid_data = json.load(f)
    
    # Generate for first 10 validation samples
    print("\n🔄 Generating problems for validation samples:\n")
    
    for i, item in enumerate(valid_data[:10]):
        keywords = item.get("keywords", [])
        original_problem = item.get("problem_text_vi", "")[:100]
        
        generated = model.generate(keywords)[:100]
        
        print(f"Sample {i+1}:")
        print(f"   Keywords: {keywords}")
        print(f"   Original: {original_problem}...")
        print(f"   Generated: {generated}...")
        print()


def main():
    print("=" * 60)
    print("Simple Problem Generator Model (TF-IDF)")
    print("=" * 60)
    
    # Check if training data exists
    if not Path(TRAIN_FILE).exists():
        print(f"❌ Training file not found: {TRAIN_FILE}")
        print("   Run split_dataset.py first")
        return
    
    # Create and train model
    print("\n🚀 Training model...")
    model = SimpleProblemGenerator()
    model.train(TRAIN_FILE)
    
    # Evaluate
    if Path(VALID_FILE).exists():
        evaluate_model(model, VALID_FILE)
    
    # Save model
    print(f"\n💾 Saving model...")
    model.save(CHECKPOINT_DIR)
    
    print(f"\n✅ Training complete!")
    print(f"\n📁 Model checkpoint: {CHECKPOINT_DIR}")
    print(f"\n💡 Next steps:")
    print(f"   1. Use this model for inference: python train/infer_simple.py")
    print(f"   2. For better results, train with Transformers: python train/train.py")
    print(f"      (Requires: pip install torch transformers accelerate)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script to evaluate the problem generation model.
"""

import json
from pathlib import Path
from collections import Counter
import re

def load_json(file_path):
    """Load JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def preprocess_text(text):
    """Simple text preprocessing."""
    text = text.lower()
    text = re.sub(r'[^a-zàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]', '', text)
    return text.split()


def calculate_bleu_score(reference, hypothesis, n=4):
    """Calculate BLEU score."""
    from collections import Counter
    import math
    
    ref_tokens = preprocess_text(reference)
    hyp_tokens = preprocess_text(hypothesis)
    
    if len(hyp_tokens) == 0:
        return 0.0
    
    precision_scores = []
    
    for n_gram in range(1, n + 1):
        ref_ngrams = Counter()
        hyp_ngrams = Counter()
        
        for i in range(len(ref_tokens) - n_gram + 1):
            ref_ngrams[tuple(ref_tokens[i:i + n_gram])] += 1
        
        for i in range(len(hyp_tokens) - n_gram + 1):
            hyp_ngrams[tuple(hyp_tokens[i:i + n_gram])] += 1
        
        matches = 0
        for ngram in hyp_ngrams:
            if ngram in ref_ngrams:
                matches += min(hyp_ngrams[ngram], ref_ngrams[ngram])
        
        if len(hyp_ngrams) > 0:
            precision = matches / sum(hyp_ngrams.values())
        else:
            precision = 0.0
        
        precision_scores.append(precision)
    
    # Geometric mean
    if all(p > 0 for p in precision_scores):
        geo_mean = (precision_scores[0] * precision_scores[1] * precision_scores[2] * precision_scores[3]) ** 0.25
    else:
        geo_mean = 0.0
    
    return geo_mean


def calculate_rouge_score(reference, hypothesis):
    """Calculate simple ROUGE-L score."""
    ref_tokens = set(preprocess_text(reference))
    hyp_tokens = set(preprocess_text(hypothesis))
    
    if len(ref_tokens) == 0 and len(hyp_tokens) == 0:
        return 1.0
    
    if len(ref_tokens) == 0 or len(hyp_tokens) == 0:
        return 0.0
    
    common = len(ref_tokens & hyp_tokens)
    total = len(ref_tokens | hyp_tokens)
    
    return common / total if total > 0 else 0.0


def evaluate_dataset(test_file, generated_file=None):
    """Evaluate model on test dataset."""
    print("=" * 60)
    print("Model Evaluation Report")
    print("=" * 60)
    
    # Load test data
    test_data = load_json(test_file)
    print(f"\n📊 Test Dataset: {len(test_data)} samples")
    
    # Statistics
    total_keywords = sum(len(item.get("keywords", [])) for item in test_data)
    avg_keywords = total_keywords / len(test_data) if test_data else 0
    
    problem_lengths = [len(item.get("problem_text_vi", "")) for item in test_data]
    avg_problem_length = sum(problem_lengths) / len(problem_lengths) if problem_lengths else 0
    
    print(f"\n📈 Dataset Statistics:")
    print(f"   - Total problems: {len(test_data)}")
    print(f"   - Average keywords per problem: {avg_keywords:.2f}")
    print(f"   - Average problem text length: {avg_problem_length:.0f} characters")
    print(f"   - Min problem length: {min(problem_lengths) if problem_lengths else 0}")
    print(f"   - Max problem length: {max(problem_lengths) if problem_lengths else 0}")
    
    # Keyword analysis
    all_keywords = []
    for item in test_data:
        all_keywords.extend(item.get("keywords", []))
    
    keyword_counts = Counter(all_keywords)
    print(f"\n🏷️  Keyword Analysis:")
    print(f"   - Unique keywords: {len(keyword_counts)}")
    print(f"   - Total keyword occurrences: {len(all_keywords)}")
    print(f"   - Top 10 keywords:")
    for keyword, count in keyword_counts.most_common(10):
        print(f"      {keyword}: {count}")
    
    # If generated file exists, compare
    if generated_file and Path(generated_file).exists():
        print(f"\n🔄 Comparing with generated problems...")
        generated_data = load_json(generated_file)
        
        if len(generated_data) >= 5:
            bleu_scores = []
            rouge_scores = []
            
            for i in range(min(5, len(generated_data), len(test_data))):
                reference = test_data[i].get("problem_text_vi", "")
                hypothesis = generated_data[i].get("generated_problem_vi", "")
                
                bleu = calculate_bleu_score(reference, hypothesis)
                rouge = calculate_rouge_score(reference, hypothesis)
                
                bleu_scores.append(bleu)
                rouge_scores.append(rouge)
            
            avg_bleu = sum(bleu_scores) / len(bleu_scores)
            avg_rouge = sum(rouge_scores) / len(rouge_scores)
            
            print(f"\n📊 Generation Quality Metrics (sample of {len(bleu_scores)} problems):")
            print(f"   - Average BLEU-4 Score: {avg_bleu:.4f}")
            print(f"   - Average ROUGE-L Score: {avg_rouge:.4f}")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Train the model using: python train/train_seq2seq.py")
    print(f"   2. Generate problems using: python train/infer.py")
    print(f"   3. Deploy API using: python api/app.py")
    
    print(f"\n✅ Evaluation complete!")


if __name__ == "__main__":
    test_file = "dataset/processed/test.json"
    
    if not Path(test_file).exists():
        print(f"❌ Test file not found: {test_file}")
        print("   Run split_dataset.py first to create train/valid/test splits")
        exit(1)
    
    evaluate_dataset(test_file)

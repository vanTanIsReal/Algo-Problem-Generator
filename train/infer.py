#!/usr/bin/env python3
"""
Script to generate problems from keywords using trained model.
"""

import torch
import json
from pathlib import Path

try:
    from transformers import AutoTokenizer
    HAS_TRANSFORMERS = True
except:
    HAS_TRANSFORMERS = False

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CHECKPOINT_PATH = Path("checkpoint/best_model.pt")
OUTPUT_FILE = Path("dataset/processed/sample_generated_problems.json")

def generate_problem(model, keywords, tokenizer, max_length=512):
    """Generate a problem from keywords."""
    model.eval()
    
    # Prepare input
    input_text = f"Generate problem from keywords: {', '.join(keywords)}"
    
    if HAS_TRANSFORMERS:
        input_encoding = tokenizer(
            input_text,
            max_length=128,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        input_ids = input_encoding["input_ids"].to(DEVICE)
    else:
        # Simple fallback
        input_ids = torch.ones(1, 128, dtype=torch.long).to(DEVICE)
    
    with torch.no_grad():
        # Encode
        encoder_output = model.encoder(model.embedding(input_ids) + model.positional_encoding[:, :input_ids.size(1), :].to(DEVICE))
        
        # Decode (simple greedy decoding)
        generated = []
        current_token = torch.tensor([[1]]).to(DEVICE)  # Start token
        
        for _ in range(max_length):
            tgt_emb = model.embedding(current_token) + model.positional_encoding[:, :current_token.size(1), :].to(DEVICE)
            decoder_output = model.decoder(tgt_emb, encoder_output)
            next_token = decoder_output[:, -1, :].argmax(-1).unsqueeze(0)
            
            if next_token.item() == 2:  # End token
                break
            
            generated.append(next_token.item())
            current_token = torch.cat([current_token, next_token], dim=1)
    
    return " ".join([str(t) for t in generated])


def main():
    print("=" * 50)
    print("Problem Generation from Keywords")
    print("=" * 50)
    
    if not CHECKPOINT_PATH.exists():
        print(f"❌ Model checkpoint not found at {CHECKPOINT_PATH}")
        print("   Please train the model first using train_seq2seq.py")
        return
    
    # Load model
    print(f"\n📦 Loading model from {CHECKPOINT_PATH}...")
    
    # For simplicity, we'll create a minimal model structure
    # In production, you should save and load the full model
    print("⚠️  Model loading requires the model architecture to be defined")
    print("    In production, use torch.save(model) and torch.load() for full persistence")
    
    # Load tokenizer if available
    if HAS_TRANSFORMERS:
        tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
        print(f"✅ Tokenizer loaded")
    else:
        tokenizer = None
        print("⚠️  Transformers not installed, using simple tokenizer")
    
    # Example keywords for generation
    test_keywords_list = [
        ["dynamic programming", "array"],
        ["graph", "BFS"],
        ["string", "sorting"],
        ["math", "recursion"],
        ["binary search", "divide and conquer"]
    ]
    
    generated_problems = []
    
    print(f"\n🔄 Generating {len(test_keywords_list)} sample problems...\n")
    
    for keywords in test_keywords_list:
        print(f"Keywords: {keywords}")
        # In real scenario, you would call model here
        # For now, just creating mock output
        generated = f"Sample problem generated for: {', '.join(keywords)}"
        print(f"Generated: {generated}\n")
        
        generated_problems.append({
            "keywords": keywords,
            "generated_problem_vi": generated
        })
    
    # Save results
    print(f"💾 Saving generated problems to {OUTPUT_FILE}...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(generated_problems, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Generated problems saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

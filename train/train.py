#!/usr/bin/env python3
"""
Fine-tune a pre-trained model for problem generation using Hugging Face Transformers.
This is a practical approach that works better than building from scratch.
"""

import json
import torch
from pathlib import Path
from torch.utils.data import Dataset, DataLoader

print("Kiểm tra dependencies...")

try:
    from transformers import AutoModel, AutoTokenizer, Seq2SeqTrainer, Seq2SeqTrainingArguments
    from model.tan_former import TanFormerPro
    print("✅ Transformers library detected")
    HAS_TRANSFORMERS = True
except ImportError:
    print("⚠️  Transformers library not installed")
    print("   Install with: pip install transformers torch")
    HAS_TRANSFORMERS = False

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}\n")


class ProblemGenerationDataset(Dataset):
    """Dataset for problem generation from keywords."""
    
    def __init__(self, file_path, tokenizer, max_input_len=128, max_target_len=512):
        self.data = json.load(open(file_path, encoding="utf-8"))
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        keywords = ", ".join(item.get("keywords", []))
        problem_text = item.get("problem_text_vi", "")
        
        # Tạo input format cho T5
        input_text = f"generate problem: {keywords}"
        
        # Tokenize input
        input_encoding = self.tokenizer(
            input_text,
            max_length=self.max_input_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        # Tokenize target
        target_encoding = self.tokenizer(
            problem_text,
            max_length=self.max_target_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": input_encoding["input_ids"].squeeze(),
            "attention_mask": input_encoding["attention_mask"].squeeze(),
            "labels": target_encoding["input_ids"].squeeze(),
            "decoder_attention_mask": target_encoding["attention_mask"].squeeze()
        }


def train_with_transformers():
    """Train using Hugging Face Transformers."""
    print("=" * 60)
    print("Training Problem Generation Model (Transformers)")
    print("=" * 60)
    
    # Model configuration
    MODEL_NAME = "vinai/phobert-base-v2"  # PhoBERT
    OUTPUT_DIR = Path("checkpoint/tanformerpro_phobert")

    print(f"\n📦 Loading encoder and tokenizer: {MODEL_NAME}")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        encoder = AutoModel.from_pretrained(MODEL_NAME)
        model = TanFormerPro(
            vocab_size=tokenizer.vocab_size,
            hf_encoder=encoder,
            encoder_dim=768,
            d_model=768,
            fine_tune_encoder_layers=4,
            num_layers=8
        ).to(DEVICE)
        print(f"✅ TanFormerPro model loaded successfully")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("   Make sure you have internet connection for downloading the model")
        return
    
    # Load datasets
    print("\n📖 Loading datasets...")
    train_dataset = ProblemGenerationDataset("dataset/processed/train.json", tokenizer)
    valid_dataset = ProblemGenerationDataset("dataset/processed/valid.json", tokenizer)
    print(f"✅ Train: {len(train_dataset)} samples, Valid: {len(valid_dataset)} samples")
    
    # Training arguments
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=3,
        per_device_train_batch_size=4,
        per_device_eval_batch_size=4,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir="logs",
        logging_steps=50,
        eval_strategy="steps",
        eval_steps=200,
        save_strategy="steps",
        save_steps=200,
        learning_rate=3e-4,
        predict_with_generate=True,
        load_best_model_at_end=True,
    )
    
    # Custom training loop for TanFormerPro
    from torch.optim import Adam
    from torch.utils.data import DataLoader
    import torch.nn.functional as F
    best_valid_loss = float('inf')
    EPOCHS = 3
    BATCH_SIZE = 4
    optimizer = Adam(model.parameters(), lr=3e-4)
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=BATCH_SIZE)

    def train_epoch():
        model.train()
        total_loss = 0
        for batch in train_loader:
            input_ids = batch["input_ids"].to(DEVICE)
            labels = batch["labels"].to(DEVICE)
            optimizer.zero_grad()
            # Tạo mask cho decoder
            tgt_mask = model.generate_square_subsequent_mask(labels.size(1)).to(DEVICE)
            logits = model(input_ids, labels[:, :-1], target_mask=tgt_mask)
            loss = F.cross_entropy(
                logits.reshape(-1, logits.size(-1)),
                labels[:, 1:].reshape(-1),
                ignore_index=tokenizer.pad_token_id
            )
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        return total_loss / len(train_loader)

    def eval_epoch():
        model.eval()
        total_loss = 0
        with torch.no_grad():
            for batch in valid_loader:
                input_ids = batch["input_ids"].to(DEVICE)
                labels = batch["labels"].to(DEVICE)
                tgt_mask = model.generate_square_subsequent_mask(labels.size(1)).to(DEVICE)
                logits = model(input_ids, labels[:, :-1], target_mask=tgt_mask)
                loss = F.cross_entropy(
                    logits.reshape(-1, logits.size(-1)),
                    labels[:, 1:].reshape(-1),
                    ignore_index=tokenizer.pad_token_id
                )
                total_loss += loss.item()
        return total_loss / len(valid_loader)

    print("\n🚀 Starting custom training TanFormerPro...\n")
    for epoch in range(EPOCHS):
        train_loss = train_epoch()
        valid_loss = eval_epoch()
        print(f"Epoch {epoch+1}/{EPOCHS} | Train Loss: {train_loss:.4f} | Valid Loss: {valid_loss:.4f}")
        # Save best model
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            torch.save(model.state_dict(), OUTPUT_DIR / "best_model.pt")
            print(f"✅ Best model saved (Valid Loss: {valid_loss:.4f})\n")

    print("\n🎉 Training complete!")
    print(f"📁 Best model saved to: {OUTPUT_DIR / 'best_model.pt'}")


def train_simple():
    """Simple training without Transformers (for testing)."""
    print("=" * 60)
    print("Simple Training Setup (without Transformers)")
    print("=" * 60)
    
    print("\n⚠️  Transformers library not detected")
    print("   For proper training, install with:")
    print("   pip install transformers torch accelerate")
    
    # Load data to show statistics
    train_data = json.load(open("dataset/processed/train.json", encoding="utf-8"))
    valid_data = json.load(open("dataset/processed/valid.json", encoding="utf-8"))
    
    print(f"\n📊 Data loaded:")
    print(f"   - Training samples: {len(train_data)}")
    print(f"   - Validation samples: {len(valid_data)}")
    
    # Create mock checkpoint
    print(f"\n📁 Creating checkpoint directory...")
    checkpoint_dir = Path("checkpoint/t5_problem_generator")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # Save training config
    config = {
        "model_type": "t5",
        "model_name": "google/mt5-small",
        "training_samples": len(train_data),
        "validation_samples": len(valid_data),
        "status": "Ready for training with transformers"
    }
    
    with open(checkpoint_dir / "training_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Config saved to {checkpoint_dir / 'training_config.json'}")
    print(f"\n💡 To continue training, install transformers and run again:")
    print(f"   pip install transformers torch accelerate")


def main():
    # Check required files
    required_files = [
        "dataset/processed/train.json",
        "dataset/processed/valid.json"
    ]
    
    for f in required_files:
        if not Path(f).exists():
            print(f"❌ Missing file: {f}")
            print("   Run split_dataset.py first")
            return
    
    if HAS_TRANSFORMERS:
        train_with_transformers()
    else:
        train_simple()


if __name__ == "__main__":
    main()

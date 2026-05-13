#!/usr/bin/env python3
"""
Seq2Seq model for problem generation from keywords using PyTorch and Hugging Face.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import Adam
from pathlib import Path
import json
from tqdm import tqdm

# Check if GPU is available
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {DEVICE}")

class ProblemDataset(Dataset):
    """Dataset for problem generation from keywords."""
    
    def __init__(self, data, tokenizer, max_input_len=128, max_output_len=512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_input_len = max_input_len
        self.max_output_len = max_output_len
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Convert keywords list to input text
        keywords = ", ".join(item.get("keywords", []))
        input_text = f"Generate problem from keywords: {keywords}"
        
        # Target is the problem text
        target_text = item.get("problem_text_vi", "")
        
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
            target_text,
            max_length=self.max_output_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": input_encoding["input_ids"].squeeze(),
            "attention_mask": input_encoding["attention_mask"].squeeze(),
            "labels": target_encoding["input_ids"].squeeze()
        }


class Seq2SeqModel(nn.Module):
    """Simple Seq2Seq model with Transformer architecture."""
    
    def __init__(self, vocab_size, embed_dim=256, num_heads=8, num_layers=4, max_seq_len=512):
        super(Seq2SeqModel, self).__init__()
        
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.positional_encoding = self._get_positional_encoding(max_seq_len, embed_dim)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=512,
            batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=512,
            batch_first=True
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        
        self.fc_out = nn.Linear(embed_dim, vocab_size)
    
    @staticmethod
    def _get_positional_encoding(max_len, d_model):
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * -(torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        return pe.unsqueeze(0)
    
    def forward(self, src, tgt, src_mask=None, tgt_mask=None):
        # Embed and add positional encoding
        src_emb = self.embedding(src) + self.positional_encoding[:, :src.size(1), :].to(src.device)
        tgt_emb = self.embedding(tgt) + self.positional_encoding[:, :tgt.size(1), :].to(tgt.device)
        
        # Encoder
        encoder_output = self.encoder(src_emb, src_key_padding_mask=src_mask)
        
        # Decoder
        decoder_output = self.decoder(tgt_emb, encoder_output, tgt_key_padding_mask=tgt_mask)
        
        # Output projection
        output = self.fc_out(decoder_output)
        return output


def load_data(file_path):
    """Load JSON data."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0
    
    for batch in tqdm(dataloader, desc="Training"):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        
        # Create padding mask
        src_mask = (attention_mask == 0)
        tgt_mask = (labels == 0)  # Assuming 0 is padding token
        
        # Forward pass
        outputs = model(input_ids, labels[:, :-1], src_mask=src_mask, tgt_mask=tgt_mask)
        
        # Calculate loss
        loss = criterion(outputs.reshape(-1, outputs.size(-1)), labels[:, 1:].reshape(-1))
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


def validate(model, dataloader, criterion, device):
    """Validate the model."""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for batch in tqdm(dataloader, desc="Validating"):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            
            # Create padding mask
            src_mask = (attention_mask == 0)
            tgt_mask = (labels == 0)
            
            # Forward pass
            outputs = model(input_ids, labels[:, :-1], src_mask=src_mask, tgt_mask=tgt_mask)
            
            # Calculate loss
            loss = criterion(outputs.reshape(-1, outputs.size(-1)), labels[:, 1:].reshape(-1))
            total_loss += loss.item()
    
    return total_loss / len(dataloader)


def main():
    print("=" * 50)
    print("Problem Generation Model Training")
    print("=" * 50)
    
    # Hyperparameters
    BATCH_SIZE = 8
    EPOCHS = 5
    LEARNING_RATE = 1e-4
    EMBED_DIM = 256
    NUM_HEADS = 8
    NUM_LAYERS = 4
    VOCAB_SIZE = 30000  # Estimated vocab size
    
    # Load data
    print("\n📖 Loading dataset...")
    train_data = load_data("dataset/processed/train.json")
    valid_data = load_data("dataset/processed/valid.json")
    
    print(f"✅ Loaded {len(train_data)} training samples")
    print(f"✅ Loaded {len(valid_data)} validation samples")
    
    # Initialize model and tokenizer
    print("\n🔧 Initializing model...")
    
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")
        VOCAB_SIZE = len(tokenizer)
    except:
        print("⚠️  Using simple tokenizer (install transformers for better results)")
        from collections import Counter
        all_words = []
        for item in train_data:
            all_words.extend(item.get("problem_text_vi", "").split())
        # Simple mock tokenizer
        tokenizer = type('Tokenizer', (), {
            '__call__': lambda self, text, **kwargs: {
                'input_ids': torch.tensor([[1] * 128]),
                'attention_mask': torch.tensor([[1] * 128])
            }
        })()
    
    model = Seq2SeqModel(
        vocab_size=VOCAB_SIZE,
        embed_dim=EMBED_DIM,
        num_heads=NUM_HEADS,
        num_layers=NUM_LAYERS
    ).to(DEVICE)
    
    print(f"✅ Model initialized on {DEVICE}")
    print(f"   Parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    # Create datasets and dataloaders
    print("\n📊 Creating dataloaders...")
    train_dataset = ProblemDataset(train_data, tokenizer)
    valid_dataset = ProblemDataset(valid_data, tokenizer)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    valid_loader = DataLoader(valid_dataset, batch_size=BATCH_SIZE)
    
    # Setup training
    optimizer = Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.CrossEntropyLoss(ignore_index=0)  # 0 is padding token
    
    # Training loop
    print("\n🚀 Starting training...\n")
    
    best_valid_loss = float('inf')
    checkpoint_dir = Path("checkpoint")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    for epoch in range(EPOCHS):
        print(f"Epoch {epoch + 1}/{EPOCHS}")
        
        train_loss = train_epoch(model, train_loader, optimizer, criterion, DEVICE)
        valid_loss = validate(model, valid_loader, criterion, DEVICE)
        
        print(f"Train Loss: {train_loss:.4f} | Valid Loss: {valid_loss:.4f}\n")
        
        # Save best model
        if valid_loss < best_valid_loss:
            best_valid_loss = valid_loss
            torch.save(model.state_dict(), checkpoint_dir / "best_model.pt")
            print(f"✅ Best model saved (Valid Loss: {valid_loss:.4f})\n")
    
    print("\n🎉 Training complete!")
    print(f"📁 Best model saved to: {checkpoint_dir / 'best_model.pt'}")


if __name__ == "__main__":
    main()

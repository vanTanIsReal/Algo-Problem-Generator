import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    # (Giữ nguyên như phiên bản trước)
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:, :x.size(1)]
        return self.dropout(x)

class TanFormerPro(nn.Module):
    def __init__(self, vocab_size, hf_encoder, encoder_dim=768, d_model=768, n_heads=12, num_layers=6, dropout=0.1, fine_tune_encoder_layers=2):
        super(TanFormerPro, self).__init__()
        
        self.d_model = d_model
        self.encoder = hf_encoder
        
        # ==========================================
        # 1. ENCODER TỐI ƯU HÓA CHO COLAB
        # ==========================================
        # Đóng băng toàn bộ trước
        for param in self.encoder.parameters():
            param.requires_grad = False 
            
        # MỞ KHÓA vài lớp cuối cùng (nếu dùng mô hình họ BERT/RoBERTa)
        # Giúp embedding hiểu từ khóa IT tốt hơn
        if hasattr(self.encoder, 'encoder') and hasattr(self.encoder.encoder, 'layer'):
            total_layers = len(self.encoder.encoder.layer)
            for i in range(total_layers - fine_tune_encoder_layers, total_layers):
                for param in self.encoder.encoder.layer[i].parameters():
                    param.requires_grad = True

        # Tối ưu Bridge: Nếu d_model bằng encoder_dim (768 == 768), ta bỏ qua Linear cho đỡ nặng
        self.use_bridge = (encoder_dim != d_model)
        if self.use_bridge:
            self.bridge = nn.Linear(encoder_dim, d_model)
        
        # ==========================================
        # 2. DECODER CHUẨN MỰC (Base Scale)
        # ==========================================
        self.decoder_embedding = nn.Embedding(vocab_size, d_model)
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=d_model, 
            nhead=n_heads, 
            dim_feedforward=d_model * 4, # Thường là 3072
            dropout=dropout,
            batch_first=True 
        )
        self.transformer_decoder = nn.TransformerDecoder(decoder_layer, num_layers=num_layers)
        
        # ==========================================
        # 3. LỚP ĐẦU RA (Tying Weights - Kỹ thuật cao cấp)
        # ==========================================
        self.fc_out = nn.Linear(d_model, vocab_size)
        
        # BÍ QUYẾT TỐI ƯU CỦA GPT: Dùng chung trọng số giữa lớp nhúng từ và lớp dự đoán từ
        # Giúp giảm hàng chục triệu tham số mà model vẫn thông minh
        self.fc_out.weight = self.decoder_embedding.weight

    def generate_square_subsequent_mask(self, sz):
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

    def forward(self, keywords_tensor, target_seq, target_mask=None):
        # Lưu ý: Không dùng torch.no_grad() ở đây nữa vì ta đang train 2 lớp cuối của Encoder
        encoder_output = self.encoder(keywords_tensor).last_hidden_state
        
        if self.use_bridge:
            memory = self.bridge(encoder_output)
        else:
            memory = encoder_output # Chạy thẳng luồng 768 chiều
        
        tgt_emb = self.decoder_embedding(target_seq) * math.sqrt(self.d_model)
        tgt_emb = self.pos_encoder(tgt_emb)
        
        output = self.transformer_decoder(tgt=tgt_emb, memory=memory, tgt_mask=target_mask)
        logits = self.fc_out(output)
        
        return logits
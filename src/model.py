#========================================================
# LSTMオートエンコーダモデル定義
#========================================================
from __future__ import annotations

import torch
import torch.nn as nn

class LSTMAutoEncoder(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self.encoder = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            batch_first=True,
        )
        self.decoder = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=input_dim,
            batch_first=True,
        )
        self.output_layer = nn.Linear(input_dim, input_dim)

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        _, (hidden, _) = self.encoder(x)
        return hidden[-1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        hidden_vec = self.encode(x)
        decoder_input = hidden_vec.unsqueeze(0).repeat(x.size(1), 1, 1).permute(1, 0, 2)
        decoder_output, _ = self.decoder(decoder_input)
        return self.output_layer(decoder_output)


def build_model(input_dim: int, hidden_dim: int = 10) -> LSTMAutoEncoder:
    return LSTMAutoEncoder(input_dim=input_dim, hidden_dim=hidden_dim)


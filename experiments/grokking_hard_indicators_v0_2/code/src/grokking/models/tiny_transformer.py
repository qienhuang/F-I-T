from __future__ import annotations

import torch
from torch import nn


class TinyTransformer(nn.Module):
    def __init__(
        self,
        *,
        vocab_size: int,
        d_model: int,
        n_heads: int,
        n_layers: int,
        dropout: float,
        n_classes: int,
    ) -> None:
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.pos = nn.Parameter(torch.zeros(1, 2, d_model))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            dim_feedforward=4 * d_model,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(d_model)
        self.unembed = nn.Linear(d_model, n_classes, bias=False)

        self._init_weights()

    def _init_weights(self) -> None:
        nn.init.normal_(self.embed.weight, mean=0.0, std=0.02)
        nn.init.zeros_(self.pos)
        nn.init.normal_(self.unembed.weight, mean=0.0, std=0.02)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x) + self.pos
        h = self.encoder(h)
        h = self.norm(h)
        h = h.mean(dim=1)
        return self.unembed(h)


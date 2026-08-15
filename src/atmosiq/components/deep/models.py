import math

import torch
from torch import nn


class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x):
        return x + self.pe[:, : x.size(1)]


class _SequenceHead(nn.Module):
    def __init__(self, d_model, hidden, out_dim, dropout):
        super().__init__()
        self.head = nn.Sequential(
            nn.LayerNorm(d_model), nn.Linear(d_model, hidden), nn.GELU(),
            nn.Dropout(dropout), nn.Linear(hidden, out_dim),
        )

    def forward(self, x):
        return self.head(x[:, -1])


class LSTMModel(nn.Module):
    def __init__(self, in_dim, d_model=64, layers=2, out_dim=1, dropout=0.1):
        super().__init__()
        self.proj = nn.Linear(in_dim, d_model)
        self.rnn = nn.LSTM(d_model, d_model, num_layers=layers, batch_first=True, dropout=dropout)
        self.head = _SequenceHead(d_model, d_model, out_dim, dropout)

    def forward(self, x):
        return self.head(self.rnn(self.proj(x))[0])


class GRUModel(nn.Module):
    def __init__(self, in_dim, d_model=64, layers=2, out_dim=1, dropout=0.1):
        super().__init__()
        self.proj = nn.Linear(in_dim, d_model)
        self.rnn = nn.GRU(d_model, d_model, num_layers=layers, batch_first=True, dropout=dropout)
        self.head = _SequenceHead(d_model, d_model, out_dim, dropout)

    def forward(self, x):
        return self.head(self.rnn(self.proj(x))[0])


class TCNBlock(nn.Module):
    def __init__(self, channels, kernel, dilation, dropout):
        super().__init__()
        padding = (kernel - 1) * dilation
        self.conv1 = nn.utils.parametrizations.weight_norm(nn.Conv1d(channels, channels, kernel, padding=padding, dilation=dilation))
        self.conv2 = nn.utils.parametrizations.weight_norm(nn.Conv1d(channels, channels, kernel, padding=padding, dilation=dilation))
        self.drop = nn.Dropout(dropout)
        self.act = nn.GELU()
        self.chop = padding

    def forward(self, x):
        out = self.act(self.drop(self.act(self.drop(self.conv1(x)[:, :, self.chop:]))))
        out = self.conv2(out)[:, :, self.chop:]
        return self.drop(out) + x


class TCNModel(nn.Module):
    def __init__(self, in_dim, d_model=64, levels=4, kernel=3, out_dim=1, dropout=0.1):
        super().__init__()
        self.proj = nn.Linear(in_dim, d_model)
        self.blocks = nn.Sequential(*[TCNBlock(d_model, kernel, 2 ** i, dropout) for i in range(levels)])
        self.head = _SequenceHead(d_model, d_model, out_dim, dropout)

    def forward(self, x):
        h = self.proj(x).transpose(1, 2)
        return self.head(self.blocks(h).transpose(1, 2))


class WeatherTransformer(nn.Module):
    def __init__(self, in_dim, d_model=64, n_heads=4, layers=2, ffn_dim=128, out_dim=1, dropout=0.1, context_length=48):
        super().__init__()
        if d_model % n_heads != 0:
            raise ValueError(f"d_model {d_model} must be divisible by n_heads {n_heads}")
        self.proj = nn.Linear(in_dim, d_model)
        self.pos = PositionalEncoding(d_model, context_length + 1)
        encoder_layer = nn.TransformerEncoderLayer(d_model, n_heads, ffn_dim, dropout, batch_first=True, norm_first=True)
        self.encoder = nn.TransformerEncoder(encoder_layer, layers)
        self.head = _SequenceHead(d_model, ffn_dim, out_dim, dropout)

    def forward(self, x):
        h = self.pos(self.proj(x))
        return self.head(self.encoder(h))


def build_model(name, in_dim, cfg):
    if name == "lstm":
        return LSTMModel(in_dim, cfg.get("d_model", 64), cfg.get("layers", 2), dropout=cfg.get("dropout", 0.1))
    if name == "gru":
        return GRUModel(in_dim, cfg.get("d_model", 64), cfg.get("layers", 2), dropout=cfg.get("dropout", 0.1))
    if name == "tcn":
        return TCNModel(in_dim, cfg.get("d_model", 64), cfg.get("levels", 4), dropout=cfg.get("dropout", 0.1))
    if name == "transformer":
        return WeatherTransformer(in_dim, cfg.get("d_model", 64), cfg.get("heads", 4), cfg.get("layers", 2), cfg.get("ffn_dim", 128), dropout=cfg.get("dropout", 0.1), context_length=cfg.get("context_length", 48))
    raise ValueError(f"Unknown deep model {name}")

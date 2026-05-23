from __future__ import annotations

import argparse
import logging
import pickle
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim

from src.dataset import (
    FEATURE_COLUMNS,
    create_sequences,
    extract_normal_period,
    load_turbofan_data,
    scale_features,
    split_by_unit,
)
from src.model import build_model


logger = logging.getLogger(__name__)


def train_model(
    data_path: str | Path = "data/raw/train_FD001.txt",
    model_path: str | Path = "models/anomaly_api_model.pt",
    scaler_path: str | Path = "models/scaler.pkl",
    seq_len: int = 10,
    hidden_dim: int = 10,
    normal_ratio: float = 0.5,
    train_unit_count: int = 80,
    num_epochs: int = 50,
    learning_rate: float = 0.001,
    feature_cols: list[str] | None = None,
) -> dict[str, float]:
    feature_cols = feature_cols or FEATURE_COLUMNS
    data = load_turbofan_data(data_path)
    train_df, _ = split_by_unit(data, train_unit_count=train_unit_count)
    train_scaled, _, scaler = scale_features(train_df, feature_cols=feature_cols)
    normal_train_df = extract_normal_period(train_scaled, normal_ratio=normal_ratio)

    train_seq = create_sequences(normal_train_df, seq_len=seq_len, feature_cols=feature_cols)
    if len(train_seq) == 0:
        raise ValueError("No training sequences were created. Check seq_len and input data.")

    train_tensor = torch.tensor(train_seq, dtype=torch.float32)
    model = build_model(input_dim=len(feature_cols), hidden_dim=hidden_dim)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    last_loss = 0.0
    for epoch in range(num_epochs):
        model.train()
        reconstructed = model(train_tensor)
        optimizer.zero_grad()
        loss = criterion(reconstructed, train_tensor)
        loss.backward()
        optimizer.step()
        last_loss = float(loss.item())

        if epoch % 10 == 0 or epoch == num_epochs - 1:
            logger.info("Epoch %s/%s, Loss: %.4f", epoch + 1, num_epochs, last_loss)

    model_path = Path(model_path)
    scaler_path = Path(scaler_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    scaler_path.parent.mkdir(parents=True, exist_ok=True)

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "feature_cols": feature_cols,
            "seq_len": seq_len,
            "hidden_dim": hidden_dim,
        },
        model_path,
    )
    with scaler_path.open("wb") as f:
        pickle.dump(scaler, f)

    return {"loss": last_loss, "train_sequences": float(len(train_seq))}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the turbofan anomaly model.")
    parser.add_argument("--data-path", default="data/raw/train_FD001.txt")
    parser.add_argument("--model-path", default="models/anomaly_api_model.pt")
    parser.add_argument("--scaler-path", default="models/scaler.pkl")
    parser.add_argument("--seq-len", type=int, default=10)
    parser.add_argument("--hidden-dim", type=int, default=10)
    parser.add_argument("--normal-ratio", type=float, default=0.5)
    parser.add_argument("--train-unit-count", type=int, default=80)
    parser.add_argument("--num-epochs", type=int, default=50)
    parser.add_argument("--learning-rate", type=float, default=0.001)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    args = parse_args()
    metrics = train_model(**vars(args))
    logger.info("Training finished: %s", metrics)


if __name__ == "__main__":
    main()


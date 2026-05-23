from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import yaml

from src.dataset import FEATURE_COLUMNS, add_cycle_norm, create_sequences
from src.metrics import reconstruction_error
from src.model import build_model


CONFIG_PATH = Path("config/config.yaml")
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)
     
DEFAULT_MODEL_PATH = Path(CONFIG["model"]["path"])
DEFAULT_SCALER_PATH = Path(CONFIG["model"]["scaler_path"])


def load_artifacts(
    model_path: str | Path = DEFAULT_MODEL_PATH,
    scaler_path: str | Path = DEFAULT_SCALER_PATH,
    device: str = "cpu",
):
    checkpoint = torch.load(model_path, map_location=device)
    feature_cols = checkpoint.get("feature_cols", FEATURE_COLUMNS)
    hidden_dim = checkpoint.get("hidden_dim", 10)

    model = build_model(input_dim=len(feature_cols), hidden_dim=hidden_dim)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    with Path(scaler_path).open("rb") as f:
        scaler = pickle.load(f)

    return model, scaler, feature_cols


def evaluate_with_cycle(
    model: torch.nn.Module,
    data: pd.DataFrame,
    seq_len: int,
    feature_cols: list[str] | None = None,
) -> pd.DataFrame:
    feature_cols = feature_cols or FEATURE_COLUMNS
    data = data.sort_values(["unit_number", "time_in_cycles"])
    rows = []

    for unit_id in data["unit_number"].unique():
        unit_df = data[data["unit_number"] == unit_id].sort_values("time_in_cycles")
        unit_seq = create_sequences(unit_df, seq_len=seq_len, feature_cols=feature_cols)

        if len(unit_seq) == 0:
            continue

        unit_tensor = torch.tensor(unit_seq, dtype=torch.float32)
        errors = reconstruction_error(model, unit_tensor).numpy()

        result = pd.DataFrame(
            {
                "unit_number": unit_id,
                "time_in_cycles": unit_df["time_in_cycles"].values[seq_len - 1 :],
                "cycle": unit_df["time_in_cycles"].values[seq_len - 1 :],
                "cycle_norm": unit_df["cycle_norm"].values[seq_len - 1 :],
                "error": errors,
            }
        )

        with torch.no_grad():
            reconstructed = model(unit_tensor)
            sensor_error = ((unit_tensor - reconstructed) ** 2).mean(dim=1)

        for i, col in enumerate(feature_cols):
            result[f"sensor_error_{col}"] = sensor_error[:, i].cpu().numpy()

        rows.append(result)

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def extract_latent_with_cycle(
    model: torch.nn.Module,
    data: pd.DataFrame,
    seq_len: int,
    feature_cols: list[str] | None = None,
) -> pd.DataFrame:
    feature_cols = feature_cols or FEATURE_COLUMNS
    data = data.sort_values(["unit_number", "time_in_cycles"])
    rows = []

    model.eval()
    with torch.no_grad():
        for unit_id in data["unit_number"].unique():
            unit_df = data[data["unit_number"] == unit_id].sort_values("time_in_cycles")
            unit_seq = create_sequences(unit_df, seq_len=seq_len, feature_cols=feature_cols)

            if len(unit_seq) == 0:
                continue

            unit_tensor = torch.tensor(unit_seq, dtype=torch.float32)
            latent = model.encode(unit_tensor).numpy()
            meta = pd.DataFrame(
                {
                    "unit_number": unit_id,
                    "cycle": unit_df["time_in_cycles"].values[seq_len - 1 :],
                    "cycle_norm": unit_df["cycle_norm"].values[seq_len - 1 :],
                }
            )
            latent_df = pd.DataFrame(latent, columns=[f"z{i}" for i in range(latent.shape[1])])
            rows.append(pd.concat([meta.reset_index(drop=True), latent_df], axis=1))

    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True)


def predict_anomaly(
    sequence: pd.DataFrame,
    model: torch.nn.Module,
    scaler,
    seq_len: int = 10,
    feature_cols: list[str] | None = None,
    rolling_window: int = 10,
    threshold: float = 0.8,
    consecutive_window: int = 5,
) -> pd.DataFrame:
    feature_cols = feature_cols or FEATURE_COLUMNS
    data = sequence.copy()

    if "cycle_norm" not in data.columns:
        data = add_cycle_norm(data)

    data = data.sort_values(["unit_number", "time_in_cycles"]).reset_index(drop=True)
    data[feature_cols] = scaler.transform(data[feature_cols])

    result = evaluate_with_cycle(
        model,
        data,
        seq_len=seq_len,
        feature_cols=feature_cols,
    )
    if result.empty:
        return result

    result["rolling_error"] = result.groupby("unit_number")["error"].transform(
        lambda x: x.rolling(window=rolling_window, min_periods=1).mean()
    )
    result["alert"] = result["rolling_error"] > threshold

    alert_group = result.groupby("unit_number")["alert"].transform(
        lambda x: (x != x.shift()).cumsum()
    )
    result["consecutive"] = (
        result["alert"]
        .astype(int)
        .groupby([result["unit_number"], alert_group])
        .cumsum()
    )
    result["final_alert"] = result["consecutive"] >= consecutive_window

    return result.replace([np.inf, -np.inf], np.nan).fillna(0)

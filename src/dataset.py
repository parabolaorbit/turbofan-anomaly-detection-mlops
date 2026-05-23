from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


OPERATION_COLUMNS = [f"ope_setting{i}" for i in range(1, 4)]
FEATURE_COLUMNS = [f"sensor_ms{i}" for i in range(1, 22)]
BASE_COLUMNS = ["unit_number", "time_in_cycles", *OPERATION_COLUMNS, *FEATURE_COLUMNS]


def load_turbofan_data(path: str | Path) -> pd.DataFrame:
    """Load NASA turbofan text data and add a normalized cycle column."""
    data = pd.read_csv(path, sep=r"\s+", header=None)
    data.columns = BASE_COLUMNS
    return add_cycle_norm(data)


def add_cycle_norm(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data["cycle_norm"] = data.groupby("unit_number")["time_in_cycles"].transform(
        lambda x: x / x.max()
    )
    return data


def split_by_unit(
    data: pd.DataFrame,
    train_unit_count: int = 80,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    units = data["unit_number"].unique()
    train_units = units[:train_unit_count]
    test_units = units[train_unit_count:]
    return (
        data[data["unit_number"].isin(train_units)].copy(),
        data[data["unit_number"].isin(test_units)].copy(),
    )


def scale_features(
    train_data: pd.DataFrame,
    test_data: pd.DataFrame | None = None,
    feature_cols: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame | None, StandardScaler]:
    feature_cols = feature_cols or FEATURE_COLUMNS
    scaler = StandardScaler()

    train_scaled = train_data.copy()
    train_scaled[feature_cols] = scaler.fit_transform(train_data[feature_cols])

    test_scaled = None
    if test_data is not None:
        test_scaled = test_data.copy()
        test_scaled[feature_cols] = scaler.transform(test_data[feature_cols])

    return train_scaled, test_scaled, scaler


def extract_normal_period(data: pd.DataFrame, normal_ratio: float = 0.5) -> pd.DataFrame:
    normal_rows = []
    for unit_id in data["unit_number"].unique():
        unit_df = data[data["unit_number"] == unit_id].sort_values("time_in_cycles")
        cutoff = int(len(unit_df) * normal_ratio)
        normal_rows.append(unit_df.iloc[:cutoff])
    return pd.concat(normal_rows, ignore_index=True)


def create_sequences(
    data: pd.DataFrame,
    seq_len: int,
    feature_cols: list[str] | None = None,
) -> np.ndarray:
    feature_cols = feature_cols or FEATURE_COLUMNS
    sequences = []

    for unit_id in data["unit_number"].unique():
        unit_df = data[data["unit_number"] == unit_id].sort_values("time_in_cycles")
        values = unit_df[feature_cols].values
        for i in range(len(unit_df) - seq_len + 1):
            sequences.append(values[i : i + seq_len])

    return np.array(sequences)


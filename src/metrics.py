#========================================================
# Grafana表示に必要な評価指標の計算用の関数群
#========================================================
from __future__ import annotations

import numpy as np
import pandas as pd
import torch


def reconstruction_error(model: torch.nn.Module, x: torch.Tensor) -> torch.Tensor:
    """再構成誤差を計算する"""
    model.eval()
    with torch.no_grad():
        reconstructed = model(x)
        return ((x - reconstructed) ** 2).mean(dim=(1, 2))


def sensor_reconstruction_error(model: torch.nn.Module, x: torch.Tensor) -> torch.Tensor:
    """センサーごとの再構成誤差を計算する"""
    model.eval()
    with torch.no_grad():
        reconstructed = model(x)
        return ((x - reconstructed) ** 2).mean(dim=(0, 1))


def threshold_counts(result: pd.DataFrame, threshold: float) -> tuple[int, int]:
    """閾値を超えたアラートの数を計算する"""
    phase = np.where(result["cycle_norm"] < 0.5, "normal", "degradation")
    normal_alerts = ((phase == "normal") & (result["error"] > threshold)).sum()
    degradation_alerts = ((phase == "degradation") & (result["error"] > threshold)).sum()
    return int(normal_alerts), int(degradation_alerts)


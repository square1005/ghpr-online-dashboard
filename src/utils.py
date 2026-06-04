"""Shared utilities for GHPR Engine."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
COT_RAW_DIR = RAW_DIR / "cot"
GOLD_RAW_DIR = RAW_DIR / "gold_price"
OI_RAW_DIR = RAW_DIR / "oi"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_MASTER_WEEKLY = PROCESSED_DIR / "ghpr_master_weekly.csv"


def ensure_project_dirs() -> None:
    """Create GHPR data/output directories if they do not already exist."""
    for path in [
        COT_RAW_DIR,
        GOLD_RAW_DIR,
        OI_RAW_DIR,
        PROCESSED_DIR,
        PROJECT_ROOT / "outputs" / "charts",
        PROJECT_ROOT / "outputs" / "reports",
    ]:
        path.mkdir(parents=True, exist_ok=True)


def rolling_zscore(series: pd.Series, window: int = 156, min_periods: int = 52) -> pd.Series:
    mean = series.rolling(window=window, min_periods=min_periods).mean()
    std = series.rolling(window=window, min_periods=min_periods).std()
    return (series - mean) / std.replace(0, pd.NA)


def rolling_percentile(series: pd.Series, window: int = 156, min_periods: int = 52) -> pd.Series:
    def percentile(values) -> float:
        clean = pd.Series(values).dropna()
        if clean.empty:
            return float("nan")
        current = clean.iloc[-1]
        return float((clean <= current).mean())

    return series.rolling(window=window, min_periods=min_periods).apply(percentile, raw=False)

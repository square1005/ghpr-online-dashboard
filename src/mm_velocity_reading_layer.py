"""GHPR v0.6.4 MM velocity reading layer.

This module turns the v0.6.2/v0.6.3 velocity-window research into a
dashboard-readable definition layer. It is historical structure research only
and does not create execution logic or market instructions.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STRUCTURE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_structure_lifecycle_dataset.csv"
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"

READING_DATASET_PATH = PROCESSED_DIR / "mm_velocity_reading_layer.csv"
READING_REPORT_PATH = REPORTS_DIR / "mm_velocity_reading_layer.md"

FEATURE_GROUPS = ["long", "short", "net"]
REQUIRED_WINDOWS = [2, 4, 8, 26]
NEAR_ZERO_THRESHOLD = 0.03
ROLLING_WINDOW = 156
ROLLING_MIN_PERIODS = 20

SOURCE_COLUMNS = [
    "date",
    "gold_close",
    "mm_long_percentile_156w",
    "mm_short_percentile_156w",
    "mm_net_percentile_156w",
    "mm_structure_state",
]

OUTPUT_COLUMNS = [
    "date",
    "gold_close",
    "long_baseline_8w",
    "long_candidate_26w",
    "long_baseline_candidate_delta",
    "short_baseline_8w",
    "short_candidate_2w",
    "short_candidate_4w",
    "short_candidate_fast_avg",
    "short_baseline_candidate_delta",
    "net_baseline_8w",
    "net_candidate_26w",
    "net_baseline_candidate_delta",
    "long_alignment_status",
    "short_alignment_status",
    "net_alignment_status",
    "overall_velocity_reading",
    "mm_structure_state",
]


def scalar_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def fmt_value(value: object, digits: int = 2) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{number * 100:.{digits}f} pct points"


def fmt_price(value: object) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{number:,.2f}"


def rolling_percentile_prior(values: pd.Series, window: int = ROLLING_WINDOW) -> pd.Series:
    result: list[float] = []
    numeric = pd.to_numeric(values, errors="coerce")
    for index, value in enumerate(numeric):
        if pd.isna(value):
            result.append(np.nan)
            continue
        start = max(0, index - window)
        prior = numeric.iloc[start:index].dropna()
        if len(prior) < ROLLING_MIN_PERIODS:
            result.append(np.nan)
            continue
        result.append(float((prior <= value).mean()))
    return pd.Series(result, index=values.index)


def load_source_dataset() -> pd.DataFrame:
    if STRUCTURE_DATASET_PATH.exists():
        data = pd.read_csv(STRUCTURE_DATASET_PATH)
    elif MASTER_PATH.exists():
        data = pd.read_csv(MASTER_PATH)
        required = ["mm_long", "mm_short", "mm_net_percentile_156w"]
        missing = [column for column in required if column not in data.columns]
        if missing:
            raise ValueError("Missing fallback master columns: " + ", ".join(missing))
        data["mm_long_percentile_156w"] = rolling_percentile_prior(data["mm_long"])
        data["mm_short_percentile_156w"] = rolling_percentile_prior(data["mm_short"])
        data["mm_structure_state"] = "N/A"
    else:
        raise FileNotFoundError(
            f"Missing source dataset: {STRUCTURE_DATASET_PATH} and fallback {MASTER_PATH}"
        )

    if "mm_structure_state" not in data.columns:
        data["mm_structure_state"] = "N/A"

    missing = [column for column in SOURCE_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required source columns: " + ", ".join(missing))

    data = data.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for column in data.columns:
        if column not in {"date", "mm_structure_state"}:
            data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return data


def velocity_column(group: str, window: int) -> str:
    return f"mm_{group}_velocity_{window}w"


def percentile_column(group: str) -> str:
    return f"mm_{group}_percentile_156w"


def ensure_velocity_columns(data: pd.DataFrame) -> pd.DataFrame:
    out = data.copy()
    for group in FEATURE_GROUPS:
        source = percentile_column(group)
        if source not in out.columns:
            raise ValueError(f"Missing percentile column: {source}")
        for window in REQUIRED_WINDOWS:
            target = velocity_column(group, window)
            if target not in out.columns:
                out[target] = out[source] - out[source].shift(window)
            else:
                out[target] = pd.to_numeric(out[target], errors="coerce")
    return out


def alignment_status(baseline: object, candidate: object) -> str:
    base = scalar_float(baseline)
    cand = scalar_float(candidate)
    if base is None or cand is None:
        return "MIXED_OR_UNCLEAR"
    if abs(base) < NEAR_ZERO_THRESHOLD and abs(cand) < NEAR_ZERO_THRESHOLD:
        return "BOTH_NEAR_ZERO"
    if base > 0 and cand > 0:
        return "SAME_DIRECTION_POSITIVE"
    if base < 0 and cand < 0:
        return "SAME_DIRECTION_NEGATIVE"
    if base > 0 and cand < 0:
        return "BASELINE_POSITIVE_CANDIDATE_NEGATIVE"
    if base < 0 and cand > 0:
        return "BASELINE_NEGATIVE_CANDIDATE_POSITIVE"
    return "MIXED_OR_UNCLEAR"


def is_near_zero(value: object) -> bool:
    number = scalar_float(value)
    return number is None or abs(number) < NEAR_ZERO_THRESHOLD


def overall_velocity_reading(row: pd.Series) -> str:
    long_8w = scalar_float(row.get("long_baseline_8w"))
    long_26w = scalar_float(row.get("long_candidate_26w"))
    short_fast = scalar_float(row.get("short_candidate_fast_avg"))
    net_8w = scalar_float(row.get("net_baseline_8w"))
    net_26w = scalar_float(row.get("net_candidate_26w"))

    if any(value is None for value in [long_8w, long_26w, short_fast, net_8w, net_26w]):
        return "MIXED_STRUCTURE"
    if long_26w > 0 and net_26w > 0:
        return "MEDIUM_TERM_PARTICIPATION_BUILDING"
    if long_26w < 0 and net_26w < 0:
        return "MEDIUM_TERM_STRUCTURE_WEAKENING"
    if abs(short_fast) >= NEAR_ZERO_THRESHOLD and is_near_zero(long_26w) and is_near_zero(net_26w):
        return "SHORT_TERM_ONLY_REACTION"
    if (long_8w > 0 or net_8w > 0) and (long_26w <= 0 or net_26w <= 0):
        return "SHORT_TERM_RECOVERY_MEDIUM_TERM_UNCONFIRMED"
    return "MIXED_STRUCTURE"


def build_reading_dataset(source: pd.DataFrame) -> pd.DataFrame:
    data = ensure_velocity_columns(source)
    out = data[["date", "gold_close", "mm_structure_state"]].copy()
    out["long_baseline_8w"] = data["mm_long_velocity_8w"]
    out["long_candidate_26w"] = data["mm_long_velocity_26w"]
    out["long_baseline_candidate_delta"] = out["long_baseline_8w"] - out["long_candidate_26w"]
    out["short_baseline_8w"] = data["mm_short_velocity_8w"]
    out["short_candidate_2w"] = data["mm_short_velocity_2w"]
    out["short_candidate_4w"] = data["mm_short_velocity_4w"]
    out["short_candidate_fast_avg"] = out[["short_candidate_2w", "short_candidate_4w"]].mean(axis=1)
    out["short_baseline_candidate_delta"] = out["short_baseline_8w"] - out["short_candidate_fast_avg"]
    out["net_baseline_8w"] = data["mm_net_velocity_8w"]
    out["net_candidate_26w"] = data["mm_net_velocity_26w"]
    out["net_baseline_candidate_delta"] = out["net_baseline_8w"] - out["net_candidate_26w"]
    out["long_alignment_status"] = out.apply(
        lambda row: alignment_status(row["long_baseline_8w"], row["long_candidate_26w"]),
        axis=1,
    )
    out["short_alignment_status"] = out.apply(
        lambda row: alignment_status(row["short_baseline_8w"], row["short_candidate_fast_avg"]),
        axis=1,
    )
    out["net_alignment_status"] = out.apply(
        lambda row: alignment_status(row["net_baseline_8w"], row["net_candidate_26w"]),
        axis=1,
    )
    out["overall_velocity_reading"] = out.apply(overall_velocity_reading, axis=1)
    return out[OUTPUT_COLUMNS]


def latest_valid_row(reading: pd.DataFrame) -> pd.Series:
    data = reading.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"]).sort_values("date")
    if data.empty:
        raise ValueError("Reading dataset has no valid date rows.")
    return data.iloc[-1]


def reading_counts(reading: pd.DataFrame) -> pd.Series:
    if "overall_velocity_reading" not in reading.columns:
        return pd.Series(dtype=int)
    return reading["overall_velocity_reading"].value_counts(dropna=False)


def latest_table(row: pd.Series) -> str:
    fields: list[tuple[str, Any]] = [
        ("date", pd.Timestamp(row["date"]).strftime("%Y-%m-%d")),
        ("gold_close", fmt_price(row.get("gold_close"))),
        ("long_baseline_8w", fmt_value(row.get("long_baseline_8w"))),
        ("long_candidate_26w", fmt_value(row.get("long_candidate_26w"))),
        ("long_alignment_status", row.get("long_alignment_status", "N/A")),
        ("short_baseline_8w", fmt_value(row.get("short_baseline_8w"))),
        ("short_candidate_2w", fmt_value(row.get("short_candidate_2w"))),
        ("short_candidate_4w", fmt_value(row.get("short_candidate_4w"))),
        ("short_candidate_fast_avg", fmt_value(row.get("short_candidate_fast_avg"))),
        ("short_alignment_status", row.get("short_alignment_status", "N/A")),
        ("net_baseline_8w", fmt_value(row.get("net_baseline_8w"))),
        ("net_candidate_26w", fmt_value(row.get("net_candidate_26w"))),
        ("net_alignment_status", row.get("net_alignment_status", "N/A")),
        ("overall_velocity_reading", row.get("overall_velocity_reading", "N/A")),
    ]
    lines = ["| Field | Value |", "|---|---|"]
    lines.extend(f"| {name} | `{value}` |" for name, value in fields)
    return "\n".join(lines)


def render_report(reading: pd.DataFrame) -> str:
    latest = latest_valid_row(reading)
    counts = reading_counts(reading)
    count_lines = ["| Reading | Count |", "|---|---:|"]
    count_lines.extend(f"| {name} | {int(value)} |" for name, value in counts.items())

    return "\n".join(
        [
            "# GHPR v0.6.4 MM Velocity Reading Layer",
            "",
            "Historical structure research only. Not a trading signal. Not financial advice.",
            "",
            "## 1. What Is This Reading Layer?",
            "",
            "This layer compares the current 8W dashboard baseline with the research-candidate velocity windows from the v0.6.2 window discovery and v0.6.3 review layer. It is designed to make the velocity definition readable without replacing the existing dashboard baseline.",
            "",
            "## 2. Why Compare 8W Baseline And Candidate Windows?",
            "",
            "8W remains the continuity baseline because GHPR already uses it for the MM Structure Lifecycle page. Candidate windows can capture different historical rhythms: Long and Net may behave more like medium-term cycles, while Short can react faster. The comparison shows whether the baseline and candidate windows are aligned or diverging.",
            "",
            "## 3. Long 8W vs 26W",
            "",
            "Long 8W is the current swing baseline. Long 26W is the research candidate for medium-term position-building or reduction. When both point in the same direction, the short swing and medium-term Long readings are aligned. When they diverge, the current swing move may not yet be confirmed by the medium-term Long cycle.",
            "",
            "## 4. Short 8W vs 2W / 4W",
            "",
            "Short 2W / 4W is the research candidate for faster short-side stress or covering windows. The `short_candidate_fast_avg` field averages 2W and 4W to reduce single-window noise while preserving short-term sensitivity.",
            "",
            "## 5. Net 8W vs 26W",
            "",
            "Net 8W is the current swing baseline. Net 26W is the research candidate because Net behavior often resembles the broader Long-side cycle. Comparing the two helps identify whether the current Net swing is also visible in the medium-term structure.",
            "",
            "## 6. Latest Reading Snapshot",
            "",
            latest_table(latest),
            "",
            "## 7. Overall Reading Distribution",
            "",
            "\n".join(count_lines),
            "",
            "## 8. Are Long / Short / Net Aligned?",
            "",
            f"- Long alignment: `{latest.get('long_alignment_status', 'N/A')}`.",
            f"- Short alignment: `{latest.get('short_alignment_status', 'N/A')}`.",
            f"- Net alignment: `{latest.get('net_alignment_status', 'N/A')}`.",
            f"- Overall reading: `{latest.get('overall_velocity_reading', 'N/A')}`.",
            "",
            "## 9. Should GHPR Replace 8W Now?",
            "",
            "No formal replacement is made in v0.6.4. The dashboard should keep the 8W continuity baseline while displaying the candidate windows as historical research context. A later version can decide whether a formal definition change improves readability and stability.",
            "",
            "## Research Limit",
            "",
            "This report only describes historical velocity-window structure. It does not forecast price, does not rank actions, does not connect to execution systems, and does not provide financial advice.",
            "",
        ]
    )


def build_and_export() -> tuple[pd.DataFrame, str]:
    source = load_source_dataset()
    reading = build_reading_dataset(source)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reading.to_csv(READING_DATASET_PATH, index=False)
    report = render_report(reading)
    READING_REPORT_PATH.write_text(report, encoding="utf-8")
    return reading, report


def main() -> int:
    reading, _ = build_and_export()
    latest = latest_valid_row(reading)
    print(f"Wrote velocity reading layer dataset: {READING_DATASET_PATH}")
    print(f"Wrote velocity reading layer report: {READING_REPORT_PATH}")
    print(f"Rows: {len(reading)}")
    print(f"Latest date: {pd.Timestamp(latest['date']).strftime('%Y-%m-%d')}")
    print("Scope: historical structure research only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

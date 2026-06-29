"""GHPR v0.6.8 MM weekly change layer.

This module computes one-week changes in Managed Money long, short, and net
positioning from the GHPR master weekly dataset. It is Historical COT Weekly
Change Research only and does not create execution logic or market
instructions.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"

WEEKLY_CHANGE_DATASET_PATH = PROCESSED_DIR / "mm_weekly_change_dataset.csv"
WEEKLY_CHANGE_REPORT_PATH = REPORTS_DIR / "mm_weekly_change_summary.md"

REQUIRED_COLUMNS = [
    "date",
    "gold_close",
    "mm_long",
    "mm_short",
    "mm_net",
    "mm_net_percentile_156w",
]

OUTPUT_COLUMNS = [
    "date",
    "gold_close",
    "gold_normalized_index",
    "mm_long",
    "mm_short",
    "mm_net",
    "mm_net_percentile_156w",
    "mm_long_change_1w",
    "mm_short_change_1w",
    "mm_net_change_1w",
    "mm_long_change_pct_1w",
    "mm_short_change_pct_1w",
    "mm_net_change_pct_1w",
    "weekly_structure_state",
    "net_weekly_state",
    "weekly_change_state",
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


def fmt_int(value: object) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{int(round(number)):,}"


def fmt_pct(value: object) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{number * 100:.2f}%"


def load_master_dataset(path: Path = MASTER_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Master weekly dataset not found: {path}")
    data = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required master columns: " + ", ".join(missing))

    data = data.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for column in REQUIRED_COLUMNS:
        if column != "date":
            data[column] = pd.to_numeric(data[column], errors="coerce")
    data = data.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return data


def classify_weekly_structure(row: pd.Series) -> str:
    long_change = scalar_float(row.get("mm_long_change_1w"))
    short_change = scalar_float(row.get("mm_short_change_1w"))
    if long_change is None or short_change is None:
        return "NEUTRAL"
    if long_change > 0 and short_change < 0:
        return "LONG_BUILDING_SHORT_COVERING"
    if long_change > 0 and short_change > 0:
        return "LONG_BUILDING_SHORT_BUILDING"
    if long_change < 0 and short_change < 0:
        return "LONG_LIQUIDATION_SHORT_COVERING"
    if long_change < 0 and short_change > 0:
        return "LONG_LIQUIDATION_SHORT_BUILDING"
    return "NEUTRAL"


def classify_net_state(value: object) -> str:
    net_change = scalar_float(value)
    if net_change is None:
        return "NEUTRAL"
    if net_change > 0:
        return "NET_UP"
    if net_change < 0:
        return "NET_DOWN"
    return "NEUTRAL"


def build_weekly_change_dataset(master: pd.DataFrame) -> pd.DataFrame:
    data = master[REQUIRED_COLUMNS].copy()
    data["gold_normalized_index"] = data["gold_close"] / data["gold_close"].dropna().iloc[0] * 100

    data["mm_long_change_1w"] = data["mm_long"] - data["mm_long"].shift(1)
    data["mm_short_change_1w"] = data["mm_short"] - data["mm_short"].shift(1)
    data["mm_net_change_1w"] = data["mm_net"] - data["mm_net"].shift(1)

    data["mm_long_change_pct_1w"] = data["mm_long_change_1w"] / data["mm_long"].shift(1)
    data["mm_short_change_pct_1w"] = data["mm_short_change_1w"] / data["mm_short"].shift(1)
    data["mm_net_change_pct_1w"] = data["mm_net_change_1w"] / data["mm_net"].shift(1).abs()

    data["weekly_structure_state"] = data.apply(classify_weekly_structure, axis=1)
    data["net_weekly_state"] = data["mm_net_change_1w"].apply(classify_net_state)
    data["weekly_change_state"] = data["weekly_structure_state"]
    neutral_mask = data["weekly_change_state"].eq("NEUTRAL") & ~data["net_weekly_state"].eq("NEUTRAL")
    data.loc[neutral_mask, "weekly_change_state"] = data.loc[neutral_mask, "net_weekly_state"]
    return data[OUTPUT_COLUMNS]


def latest_row(data: pd.DataFrame) -> pd.Series | None:
    if data.empty:
        return None
    return data.dropna(subset=["date"]).sort_values("date").iloc[-1]


def render_summary(data: pd.DataFrame) -> str:
    latest = latest_row(data)
    previous = data.dropna(subset=["date"]).sort_values("date").iloc[-2] if len(data) >= 2 else None
    period_start = data["date"].min().strftime("%Y-%m-%d") if not data.empty else "N/A"
    period_end = data["date"].max().strftime("%Y-%m-%d") if not data.empty else "N/A"

    if latest is None:
        latest_lines = ["- Latest row: `N/A`"]
    else:
        latest_lines = [
            f"- Latest date: `{latest['date'].strftime('%Y-%m-%d')}`",
            f"- Previous date: `{previous['date'].strftime('%Y-%m-%d') if previous is not None else 'N/A'}`",
            f"- MM Long: `{fmt_int(latest.get('mm_long'))}`",
            f"- MM Short: `{fmt_int(latest.get('mm_short'))}`",
            f"- MM Net: `{fmt_int(latest.get('mm_net'))}`",
            f"- Long 1W change: `{fmt_int(latest.get('mm_long_change_1w'))}` ({fmt_pct(latest.get('mm_long_change_pct_1w'))})",
            f"- Short 1W change: `{fmt_int(latest.get('mm_short_change_1w'))}` ({fmt_pct(latest.get('mm_short_change_pct_1w'))})",
            f"- Net 1W change: `{fmt_int(latest.get('mm_net_change_1w'))}` ({fmt_pct(latest.get('mm_net_change_pct_1w'))})",
            f"- Weekly structure state: `{latest.get('weekly_change_state', 'N/A')}`",
        ]

    state_counts = (
        data["weekly_change_state"].fillna("N/A").value_counts(dropna=False).rename_axis("state").reset_index(name="count")
        if "weekly_change_state" in data.columns
        else pd.DataFrame(columns=["state", "count"])
    )
    state_lines = ["| State | Count |", "| --- | ---: |"]
    for _, row in state_counts.iterrows():
        state_lines.append(f"| `{row['state']}` | {int(row['count'])} |")

    lines = [
        "# MM Weekly Change Summary",
        "",
        "Historical COT Weekly Change Research only. Not a trading signal. Not financial advice.",
        "",
        "## Dataset",
        "",
        f"- Source: `data/processed/ghpr_master_weekly.csv`",
        f"- Output: `data/processed/mm_weekly_change_dataset.csv`",
        f"- Data period: `{period_start}` to `{period_end}`",
        f"- Rows: `{len(data):,}`",
        "",
        "## Latest Weekly Change",
        "",
        *latest_lines,
        "",
        "## Classification Rules",
        "",
        "- `LONG_BUILDING_SHORT_COVERING`: long change > 0 and short change < 0.",
        "- `LONG_BUILDING_SHORT_BUILDING`: long change > 0 and short change > 0.",
        "- `LONG_LIQUIDATION_SHORT_COVERING`: long change < 0 and short change < 0.",
        "- `LONG_LIQUIDATION_SHORT_BUILDING`: long change < 0 and short change > 0.",
        "- `NET_UP`: net change > 0 when long/short structure is neutral.",
        "- `NET_DOWN`: net change < 0 when long/short structure is neutral.",
        "- `NEUTRAL`: other cases or insufficient prior-week data.",
        "",
        "## State Counts",
        "",
        *state_lines,
        "",
        "## Interpretation Limit",
        "",
        "This layer shows the latest COT report versus the prior report. It is a weekly positioning-change lens, not a forecast and not an execution rule.",
    ]
    return "\n".join(lines) + "\n"


def write_outputs(
    dataset: pd.DataFrame,
    dataset_path: Path = WEEKLY_CHANGE_DATASET_PATH,
    report_path: Path = WEEKLY_CHANGE_REPORT_PATH,
) -> None:
    dataset_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    output = dataset.copy()
    output["date"] = output["date"].dt.strftime("%Y-%m-%d")
    output.to_csv(dataset_path, index=False)
    report_path.write_text(render_summary(dataset), encoding="utf-8")


def main() -> int:
    master = load_master_dataset()
    dataset = build_weekly_change_dataset(master)
    write_outputs(dataset)
    latest = latest_row(dataset)
    print(f"Wrote weekly change dataset: {WEEKLY_CHANGE_DATASET_PATH}")
    print(f"Wrote weekly change summary: {WEEKLY_CHANGE_REPORT_PATH}")
    print(f"Latest date: {latest['date'].strftime('%Y-%m-%d') if latest is not None else 'N/A'}")
    print("Scope: Historical COT Weekly Change Research only. Not a trading signal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

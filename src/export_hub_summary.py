"""Export a compact GHPR summary JSON for the online hub.

The export is historical statistics / research reference only. It does not
create trade execution logic or market instructions.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
HSE_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_report.csv"
HSE_STATS_PATH = PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_stats.csv"
MM_LIFECYCLE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_lifecycle_dataset.csv"
MM_LIFECYCLE_LEAD_LAG_PATH = PROJECT_ROOT / "outputs" / "reports" / "mm_lifecycle_lead_lag.csv"
MM_STRUCTURE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_structure_lifecycle_dataset.csv"
HUB_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "ghpr_summary_for_hub.json"
DASHBOARD_URL = "https://square1005.github.io/ghpr-online-dashboard/"


MASTER_REQUIRED_COLUMNS = [
    "date",
    "gold_close",
    "mm_net_percentile_156w",
    "producer_net_percentile_156w",
    "oi_percentile_156w",
]


def percent_points(value: object) -> float | None:
    number = scalar_float(value)
    if number is None:
        return None
    return number * 100 if abs(number) <= 1 else number


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


def json_value(value: object, digits: int | None = None) -> Any:
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (int, str, bool)):
        return value
    number = scalar_float(value)
    if number is not None:
        return round(number, digits) if digits is not None else number
    return str(value)


def latest_valid_master_row(master: pd.DataFrame) -> pd.Series:
    missing = [column for column in MASTER_REQUIRED_COLUMNS if column not in master.columns]
    if missing:
        raise ValueError("Missing master columns: " + ", ".join(missing))
    data = master.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date", "gold_close"]).sort_values("date")
    if data.empty:
        raise ValueError("Master dataset has no valid date/gold_close rows.")
    return data.iloc[-1]


def mm_state_from_percentile(value: object) -> str:
    percentile = percent_points(value)
    if percentile is None:
        return "N/A"
    if percentile < 20:
        return "MM_EXTREME_LOW"
    if percentile < 40:
        return "MM_LOW"
    if percentile < 60:
        return "MM_NEUTRAL"
    if percentile < 80:
        return "MM_HIGH"
    return "MM_EXTREME_HIGH"


def market_state(mm_value: object, oi_value: object) -> str:
    mm = percent_points(mm_value)
    oi = percent_points(oi_value)
    if mm is None:
        return "N/A"
    if mm >= 80 and oi is not None and oi >= 60:
        return "Expansion / Momentum"
    if mm >= 80 and (oi is None or oi < 60):
        return "Euphoria / Thin Momentum"
    if 60 <= mm < 80:
        return "Healthy High Positioning"
    if 40 <= mm < 60:
        return "Neutral / Transition"
    if 20 <= mm < 40:
        return "Accumulation / Weak Positioning"
    return "Extreme Low / Potential Reset"


def top20_stats_row(stats: pd.DataFrame) -> pd.Series | None:
    if stats.empty or "group" not in stats.columns:
        return None
    matches = stats[stats["group"].astype(str).str.lower().eq("top 20")]
    if matches.empty:
        return None
    return matches.iloc[0]


def top20_similarity_average(report: pd.DataFrame) -> float | None:
    if report.empty or "similarity_score" not in report.columns:
        return None
    values = pd.to_numeric(report.head(20)["similarity_score"], errors="coerce").dropna()
    if values.empty:
        return None
    return float(values.mean())


def same_return_direction(left: object, right: object) -> bool:
    left_number = scalar_float(left)
    right_number = scalar_float(right)
    if left_number is None or right_number is None:
        return False
    return (left_number > 0 and right_number > 0) or (left_number < 0 and right_number < 0)


def build_confidence(report: pd.DataFrame, stats: pd.DataFrame) -> str:
    row = top20_stats_row(stats)
    if row is None:
        return "Low"
    case_count = scalar_float(row.get("case_count"))
    win_rate_8w = scalar_float(row.get("win_rate_8w"))
    median_return_8w = scalar_float(row.get("median_return_8w"))
    avg_return_8w = scalar_float(row.get("avg_return_8w"))
    avg_similarity_score = top20_similarity_average(report)
    direction_consistent = same_return_direction(median_return_8w, avg_return_8w)

    if case_count is None or case_count < 10:
        return "Low"
    if case_count >= 20 and direction_consistent:
        if (
            win_rate_8w is not None
            and (win_rate_8w >= 0.75 or win_rate_8w <= 0.25)
            and avg_similarity_score is not None
            and avg_similarity_score >= 85
        ):
            return "High"
        if win_rate_8w is not None and (win_rate_8w >= 0.65 or win_rate_8w <= 0.35):
            return "Medium"
    return "Low"


def build_historical_tendency(row: pd.Series | None) -> str:
    if row is None:
        return "N/A"
    median_8w = scalar_float(row.get("median_return_8w"))
    win_rate_8w = scalar_float(row.get("win_rate_8w"))
    if median_8w is None or win_rate_8w is None:
        return "historical_sample_mixed"
    if median_8w > 0 and win_rate_8w >= 0.55:
        return "historical_sample_positive"
    if median_8w < 0 and win_rate_8w <= 0.45:
        return "historical_sample_negative"
    return "historical_sample_mixed"


def build_data_health(
    master: pd.DataFrame,
    latest: pd.Series,
    report: pd.DataFrame,
    stats: pd.DataFrame,
) -> dict[str, Any]:
    missing_master_columns = [
        column for column in MASTER_REQUIRED_COLUMNS if column not in master.columns
    ]
    missing_files = [
        str(path.relative_to(PROJECT_ROOT))
        for path in [MASTER_PATH, HSE_REPORT_PATH, HSE_STATS_PATH]
        if not path.exists()
    ]
    latest_date = pd.to_datetime(latest.get("date"), errors="coerce")
    hse_current_date = None
    if not report.empty and "current_date" in report.columns:
        hse_current_date = pd.to_datetime(report["current_date"].iloc[0], errors="coerce")
    current_date_matches_hse = (
        bool(pd.notna(latest_date) and pd.notna(hse_current_date) and latest_date == hse_current_date)
        if hse_current_date is not None
        else None
    )

    warnings = []
    if missing_files:
        warnings.append("missing_files")
    if missing_master_columns:
        warnings.append("missing_master_columns")
    if current_date_matches_hse is False:
        warnings.append("hse_current_date_mismatch")
    if report.empty:
        warnings.append("historical_similarity_report_empty")
    if stats.empty:
        warnings.append("historical_similarity_stats_empty")

    status = "ok" if not warnings else "warning"
    return {
        "status": status,
        "warnings": warnings,
        "master_rows": int(len(master)),
        "historical_similarity_cases": int(len(report)),
        "historical_similarity_stats_rows": int(len(stats)),
        "missing_master_columns": missing_master_columns,
        "missing_files": missing_files,
        "current_date_matches_hse": current_date_matches_hse,
        "gold_price_source": json_value(latest.get("gold_price_source")),
        "scope": "historical statistics / research reference only",
    }


def read_csv_or_empty(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def latest_lifecycle_row(lifecycle: pd.DataFrame) -> pd.Series | None:
    required = ["date", "mm_lifecycle_state", "mm_velocity_8w", "mm_acceleration_8w"]
    if lifecycle.empty or any(column not in lifecycle.columns for column in required):
        return None
    data = lifecycle.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"]).sort_values("date")
    if data.empty:
        return None
    return data.iloc[-1]


def latest_structure_row(structure: pd.DataFrame) -> pd.Series | None:
    required = [
        "date",
        "mm_long_percentile_156w",
        "mm_short_percentile_156w",
        "mm_net_percentile_156w",
        "mm_long_velocity_8w",
        "mm_short_velocity_8w",
        "mm_net_velocity_8w",
        "mm_structure_state",
    ]
    if structure.empty or any(column not in structure.columns for column in required):
        return None
    data = structure.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"]).sort_values("date")
    if data.empty:
        return None
    return data.iloc[-1]


def build_structure_note(row: pd.Series | None) -> str | None:
    if row is None:
        return None
    state = json_value(row.get("mm_structure_state"))
    contribution = json_value(row.get("mm_structure_contribution_state"))
    long_velocity = scalar_float(row.get("mm_long_velocity_8w"))
    short_velocity = scalar_float(row.get("mm_short_velocity_8w"))
    net_velocity = scalar_float(row.get("mm_net_velocity_8w"))
    if state is None:
        return None
    parts = [f"Current MM structure state: {state}"]
    if contribution:
        parts.append(f"contribution: {contribution}")
    if all(value is not None for value in [long_velocity, short_velocity, net_velocity]):
        parts.append(
            "8W velocities long/short/net: "
            f"{long_velocity:.4f}/{short_velocity:.4f}/{net_velocity:.4f}"
        )
    parts.append("historical structure research only")
    return "; ".join(parts)


def build_lifecycle_lead_lag_note(lead_lag: pd.DataFrame) -> str | None:
    required = ["mm_feature", "lag_weeks", "rank_correlation", "interpretation"]
    if lead_lag.empty or any(column not in lead_lag.columns for column in required):
        return None
    data = lead_lag.copy()
    data["rank_correlation"] = pd.to_numeric(data["rank_correlation"], errors="coerce")
    data["lag_weeks"] = pd.to_numeric(data["lag_weeks"], errors="coerce")
    positive_lag = data[data["lag_weeks"] > 0].dropna(subset=["rank_correlation"])
    if positive_lag.empty:
        return "No positive-lag lifecycle relationship available."
    top = positive_lag.assign(abs_rank=positive_lag["rank_correlation"].abs()).sort_values(
        "abs_rank", ascending=False
    ).iloc[0]
    return (
        f"{top['mm_feature']} at +{int(top['lag_weeks'])}W has rank correlation "
        f"{top['rank_correlation']:.3f}; historical lifecycle research only."
    )


def build_hub_summary() -> dict[str, Any]:
    master = read_csv_or_empty(MASTER_PATH)
    if master.empty:
        raise ValueError(f"Missing or empty master dataset: {MASTER_PATH}")
    latest = latest_valid_master_row(master)
    report = read_csv_or_empty(HSE_REPORT_PATH)
    stats = read_csv_or_empty(HSE_STATS_PATH)
    lifecycle = read_csv_or_empty(MM_LIFECYCLE_DATASET_PATH)
    lifecycle_lead_lag = read_csv_or_empty(MM_LIFECYCLE_LEAD_LAG_PATH)
    structure = read_csv_or_empty(MM_STRUCTURE_DATASET_PATH)
    top20 = top20_stats_row(stats)
    latest_lifecycle = latest_lifecycle_row(lifecycle)
    latest_structure = latest_structure_row(structure)

    mm_percentile = percent_points(latest.get("mm_net_percentile_156w"))
    producer_percentile = percent_points(latest.get("producer_net_percentile_156w"))
    oi_percentile = percent_points(latest.get("oi_percentile_156w"))

    summary = {
        "date": json_value(latest.get("date")),
        "gold_close": json_value(latest.get("gold_close"), 4),
        "mm_percentile": json_value(mm_percentile, 4),
        "producer_percentile": json_value(producer_percentile, 4),
        "oi_percentile": json_value(oi_percentile, 4),
        "mm_state": mm_state_from_percentile(mm_percentile),
        "market_state": market_state(mm_percentile, oi_percentile),
        "historical_tendency": build_historical_tendency(top20),
        "confidence": build_confidence(report, stats),
        "top20_median_return_1w": json_value(None if top20 is None else top20.get("median_return_1w"), 6),
        "top20_median_return_2w": json_value(None if top20 is None else top20.get("median_return_2w"), 6),
        "top20_median_return_4w": json_value(None if top20 is None else top20.get("median_return_4w"), 6),
        "top20_median_return_8w": json_value(None if top20 is None else top20.get("median_return_8w"), 6),
        "top20_win_rate_8w": json_value(None if top20 is None else top20.get("win_rate_8w"), 6),
        "data_health": build_data_health(master, latest, report, stats),
        "last_update_time": datetime.now(timezone.utc).isoformat(),
        "dashboard_url": DASHBOARD_URL,
        "mm_lifecycle_state": json_value(
            None if latest_lifecycle is None else latest_lifecycle.get("mm_lifecycle_state")
        ),
        "mm_velocity_8w": json_value(
            None if latest_lifecycle is None else latest_lifecycle.get("mm_velocity_8w"), 6
        ),
        "mm_acceleration_8w": json_value(
            None if latest_lifecycle is None else latest_lifecycle.get("mm_acceleration_8w"), 6
        ),
        "mm_lead_lag_note": build_lifecycle_lead_lag_note(lifecycle_lead_lag),
        "mm_long_percentile": json_value(
            None if latest_structure is None else percent_points(latest_structure.get("mm_long_percentile_156w")),
            4,
        ),
        "mm_short_percentile": json_value(
            None if latest_structure is None else percent_points(latest_structure.get("mm_short_percentile_156w")),
            4,
        ),
        "mm_net_percentile": json_value(
            None if latest_structure is None else percent_points(latest_structure.get("mm_net_percentile_156w")),
            4,
        ),
        "mm_long_velocity_8w": json_value(
            None if latest_structure is None else latest_structure.get("mm_long_velocity_8w"), 6
        ),
        "mm_short_velocity_8w": json_value(
            None if latest_structure is None else latest_structure.get("mm_short_velocity_8w"), 6
        ),
        "mm_net_velocity_8w": json_value(
            None if latest_structure is None else latest_structure.get("mm_net_velocity_8w"), 6
        ),
        "mm_structure_state": json_value(
            None if latest_structure is None else latest_structure.get("mm_structure_state")
        ),
        "mm_structure_note": build_structure_note(latest_structure),
    }
    return summary


def export_hub_summary(output_path: Path = HUB_SUMMARY_PATH) -> dict[str, Any]:
    summary = build_hub_summary()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    summary = export_hub_summary()
    print(f"Wrote hub summary: {HUB_SUMMARY_PATH}")
    print(f"Summary date: {summary['date']}")
    print("Scope: historical statistics / research reference only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

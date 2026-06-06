"""GHPR v0.5-B MM lifecycle and lead-lag research.

This module is historical statistics / research reference only. It does not
create execution logic, market instructions, or broker/API integrations.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

LIFECYCLE_DATASET_PATH = PROCESSED_DIR / "mm_lifecycle_dataset.csv"
SUMMARY_MD_PATH = REPORTS_DIR / "mm_lifecycle_summary.md"
LEAD_LAG_PATH = REPORTS_DIR / "mm_lifecycle_lead_lag.csv"
STATE_ANALYSIS_PATH = REPORTS_DIR / "mm_lifecycle_state_analysis.csv"
TRAJECTORY_SIMILARITY_PATH = REPORTS_DIR / "mm_trajectory_similarity.csv"

GOLD_VS_MM_CHART = CHARTS_DIR / "gold_vs_mm_lifecycle.png"
VELOCITY_ACCELERATION_CHART = CHARTS_DIR / "mm_velocity_acceleration.png"
LEAD_LAG_CHART = CHARTS_DIR / "mm_lead_lag_correlation.png"
STATE_OUTCOMES_CHART = CHARTS_DIR / "mm_lifecycle_state_outcomes.png"
TRAJECTORY_CHART = CHARTS_DIR / "mm_trajectory_similarity_cases.png"

REQUIRED_COLUMNS = [
    "date",
    "gold_close",
    "mm_net",
    "mm_net_percentile_156w",
    "gold_return_1w",
    "gold_return_2w",
    "gold_return_4w",
    "gold_return_8w",
]
HORIZONS = [1, 2, 4, 8]
VELOCITY_WINDOWS = [4, 8, 12, 26]
ACCELERATION_WINDOWS = [4, 8]
TRAJECTORY_WINDOWS = [4, 8, 12, 26]
LAGS = [-8, -4, -2, 0, 2, 4, 8]
EXCLUDE_RECENT_WEEKS = 52
STATE_ORDER = [
    "MM_RESET",
    "MM_ACCUMULATION",
    "MM_EXPANSION",
    "MM_CROWDED_EXPANSION",
    "MM_DISTRIBUTION",
    "MM_NEUTRAL",
]
STATE_COLORS = {
    "MM_RESET": "#ef4444",
    "MM_ACCUMULATION": "#22c55e",
    "MM_EXPANSION": "#2563eb",
    "MM_CROWDED_EXPANSION": "#9333ea",
    "MM_DISTRIBUTION": "#f97316",
    "MM_NEUTRAL": "#64748b",
}


@dataclass(frozen=True)
class ResearchBundle:
    dataset: pd.DataFrame
    state_analysis: pd.DataFrame
    lead_lag: pd.DataFrame
    trajectory_similarity: pd.DataFrame


def as_number(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def fmt_number(value: object, digits: int = 4) -> str:
    number = as_number(value)
    if number is None:
        return "N/A"
    return f"{number:.{digits}f}"


def fmt_pct(value: object, digits: int = 2) -> str:
    number = as_number(value)
    if number is None:
        return "N/A"
    return f"{number * 100:.{digits}f}%"


def load_master() -> pd.DataFrame:
    if not MASTER_PATH.exists():
        raise FileNotFoundError(f"Missing master dataset: {MASTER_PATH}")
    master = pd.read_csv(MASTER_PATH)
    missing = [column for column in REQUIRED_COLUMNS if column not in master.columns]
    if missing:
        raise ValueError("Missing required master columns: " + ", ".join(missing))
    master = master.copy()
    master["date"] = pd.to_datetime(master["date"], errors="coerce")
    master = master.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return master


def lifecycle_state(row: pd.Series) -> str:
    percentile = as_number(row.get("mm_percentile"))
    velocity_8w = as_number(row.get("mm_velocity_8w"))
    if percentile is None or velocity_8w is None:
        return "MM_NEUTRAL"
    if percentile < 0.30 and velocity_8w < 0:
        return "MM_RESET"
    if percentile < 0.40 and velocity_8w > 0:
        return "MM_ACCUMULATION"
    if percentile >= 0.80 and velocity_8w > 0:
        return "MM_CROWDED_EXPANSION"
    if 0.40 <= percentile < 0.80 and velocity_8w > 0:
        return "MM_EXPANSION"
    if velocity_8w < 0:
        return "MM_DISTRIBUTION"
    return "MM_NEUTRAL"


def build_lifecycle_dataset(master: pd.DataFrame) -> pd.DataFrame:
    columns = REQUIRED_COLUMNS.copy()
    data = master[columns].copy()
    data["mm_percentile"] = pd.to_numeric(data["mm_net_percentile_156w"], errors="coerce")
    data["mm_percentile_pct"] = data["mm_percentile"] * 100

    for window in VELOCITY_WINDOWS:
        data[f"mm_velocity_{window}w"] = data["mm_percentile"] - data["mm_percentile"].shift(window)

    for window in ACCELERATION_WINDOWS:
        data[f"mm_acceleration_{window}w"] = (
            data[f"mm_velocity_{window}w"] - data[f"mm_velocity_{window}w"].shift(window)
        )

    for window in VELOCITY_WINDOWS:
        data[f"gold_return_{window}w_trailing"] = (
            pd.to_numeric(data["gold_close"], errors="coerce")
            / pd.to_numeric(data["gold_close"], errors="coerce").shift(window)
            - 1
        )

    data["gold_velocity_4w"] = data["gold_return_4w_trailing"]
    data["gold_velocity_8w"] = data["gold_return_8w_trailing"]
    data["mm_lifecycle_state"] = data.apply(lifecycle_state, axis=1)
    return data


def state_analysis(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for state in STATE_ORDER:
        group = data[data["mm_lifecycle_state"] == state]
        row: dict[str, object] = {"mm_lifecycle_state": state, "count": int(len(group))}
        for horizon in HORIZONS:
            values = pd.to_numeric(group[f"gold_return_{horizon}w"], errors="coerce").dropna()
            row[f"avg_forward_return_{horizon}w"] = np.nan if values.empty else float(values.mean())
            row[f"median_forward_return_{horizon}w"] = np.nan if values.empty else float(values.median())
            row[f"win_rate_{horizon}w"] = np.nan if values.empty else float((values > 0).mean())
        values_8w = pd.to_numeric(group["gold_return_8w"], errors="coerce").dropna()
        row["best_return_8w"] = np.nan if values_8w.empty else float(values_8w.max())
        row["worst_return_8w"] = np.nan if values_8w.empty else float(values_8w.min())
        rows.append(row)
    return pd.DataFrame(rows)


def corr_pair(left: pd.Series, right: pd.Series, method: str = "pearson") -> float:
    frame = pd.concat([left, right], axis=1).dropna()
    if len(frame) < 5:
        return np.nan
    if frame.iloc[:, 0].nunique() < 2 or frame.iloc[:, 1].nunique() < 2:
        return np.nan
    return float(frame.iloc[:, 0].corr(frame.iloc[:, 1], method=method))


def lead_lag_interpretation(lag_weeks: int, rank_correlation: object) -> str:
    corr = as_number(rank_correlation)
    if corr is None or abs(corr) < 0.10:
        return "weak_or_no_clear_historical_relationship"
    direction = "positive" if corr > 0 else "negative"
    if lag_weeks > 0:
        return f"mm_feature_leads_gold_{lag_weeks}w_{direction}_historical_alignment"
    if lag_weeks < 0:
        return f"gold_or_later_mm_alignment_{abs(lag_weeks)}w_{direction}_historical_alignment"
    return f"same_week_{direction}_historical_alignment"


def lead_lag_analysis(data: pd.DataFrame) -> pd.DataFrame:
    features = [
        "mm_velocity_4w",
        "mm_velocity_8w",
        "mm_velocity_12w",
        "mm_velocity_26w",
        "mm_acceleration_4w",
        "mm_acceleration_8w",
    ]
    rows: list[dict[str, object]] = []
    for feature in features:
        for horizon in HORIZONS:
            return_col = f"gold_return_{horizon}w"
            for lag in LAGS:
                shifted_feature = data[feature].shift(lag)
                valid = pd.concat([shifted_feature, data[return_col]], axis=1).dropna()
                correlation = corr_pair(shifted_feature, data[return_col], "pearson")
                rank_correlation = corr_pair(shifted_feature, data[return_col], "spearman")
                rows.append(
                    {
                        "mm_feature": feature,
                        "gold_horizon": f"{horizon}W",
                        "lag_weeks": lag,
                        "correlation": correlation,
                        "rank_correlation": rank_correlation,
                        "sample_count": int(len(valid)),
                        "interpretation": lead_lag_interpretation(lag, rank_correlation),
                    }
                )
    return pd.DataFrame(rows)


def normalized_distance_score(current_path: np.ndarray, historical_path: np.ndarray) -> float:
    euclidean = float(np.linalg.norm(current_path - historical_path) / math.sqrt(len(current_path)))
    if np.std(current_path) == 0 or np.std(historical_path) == 0:
        corr_distance = 0.5
    else:
        corr = float(np.corrcoef(current_path, historical_path)[0, 1])
        corr_distance = (1 - corr) / 2
    combined = min(2.0, euclidean + corr_distance)
    return max(0.0, min(100.0, 100.0 * (1 - combined / 2.0)))


def json_path(values: Iterable[float]) -> str:
    return json.dumps([round(float(value) * 100, 4) for value in values], ensure_ascii=False)


def trajectory_similarity(data: pd.DataFrame) -> pd.DataFrame:
    valid = data.dropna(subset=["date", "mm_percentile"]).sort_values("date").reset_index(drop=True)
    if valid.empty:
        return pd.DataFrame()
    current_date = valid["date"].iloc[-1]
    cutoff = current_date - pd.Timedelta(weeks=EXCLUDE_RECENT_WEEKS)
    rows: list[dict[str, object]] = []

    for window in TRAJECTORY_WINDOWS:
        path_length = window + 1
        if len(valid) < path_length:
            continue
        current_slice = valid.iloc[-path_length:]
        current_path = current_slice["mm_percentile"].to_numpy(dtype=float)
        if np.isnan(current_path).any():
            continue
        for end_idx in range(window, len(valid)):
            historical_slice = valid.iloc[end_idx - window : end_idx + 1]
            end_date = historical_slice["date"].iloc[-1]
            if end_date > cutoff:
                continue
            historical_path = historical_slice["mm_percentile"].to_numpy(dtype=float)
            if len(historical_path) != path_length or np.isnan(historical_path).any():
                continue
            score = normalized_distance_score(current_path, historical_path)
            end_row = historical_slice.iloc[-1]
            rows.append(
                {
                    "window": f"{window}W",
                    "historical_start_date": historical_slice["date"].iloc[0].strftime("%Y-%m-%d"),
                    "historical_end_date": end_date.strftime("%Y-%m-%d"),
                    "similarity_score": score,
                    "current_path": json_path(current_path),
                    "historical_path": json_path(historical_path),
                    "historical_gold_return_1w": end_row.get("gold_return_1w"),
                    "historical_gold_return_2w": end_row.get("gold_return_2w"),
                    "historical_gold_return_4w": end_row.get("gold_return_4w"),
                    "historical_gold_return_8w": end_row.get("gold_return_8w"),
                }
            )

    if not rows:
        return pd.DataFrame()
    result = pd.DataFrame(rows)
    return (
        result.sort_values(["window", "similarity_score"], ascending=[True, False])
        .groupby("window", as_index=False, group_keys=False)
        .head(20)
        .reset_index(drop=True)
    )


def output_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def write_charts(bundle: ResearchBundle) -> None:
    data = bundle.dataset.copy()
    state_frame = bundle.state_analysis.copy()
    lead_lag = bundle.lead_lag.copy()
    trajectories = bundle.trajectory_similarity.copy()
    plt.style.use("seaborn-v0_8-whitegrid")

    chart_data = data.dropna(subset=["date", "gold_close"]).copy()
    if not chart_data.empty:
        chart_data["gold_index"] = chart_data["gold_close"] / chart_data["gold_close"].iloc[0] * 100
        fig, ax1 = plt.subplots(figsize=(14, 7))
        ax1.plot(chart_data["date"], chart_data["gold_index"], color="#111827", label="Gold normalized index")
        ax1.set_ylabel("Gold index")
        ax2 = ax1.twinx()
        ax2.plot(chart_data["date"], chart_data["mm_percentile"] * 100, color="#2563eb", label="MM Percentile")
        ax2.plot(
            chart_data["date"],
            chart_data["mm_velocity_8w"] * 100,
            color="#f97316",
            label="MM Velocity 8W",
            alpha=0.8,
        )
        for state, color in STATE_COLORS.items():
            sample = chart_data[chart_data["mm_lifecycle_state"] == state]
            if not sample.empty:
                ax2.scatter(
                    sample["date"],
                    sample["mm_percentile"] * 100,
                    s=12,
                    alpha=0.45,
                    color=color,
                    label=state,
                )
        ax2.set_ylabel("MM percentile / velocity (pct points)")
        ax1.set_title("Gold vs MM Lifecycle")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=8, ncols=2, loc="upper left")
        fig.tight_layout()
        fig.savefig(GOLD_VS_MM_CHART, dpi=170)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(chart_data["date"], chart_data["mm_percentile"] * 100, label="MM Percentile", color="#2563eb")
        ax.plot(chart_data["date"], chart_data["mm_velocity_8w"] * 100, label="MM Velocity 8W", color="#f97316")
        ax.plot(
            chart_data["date"],
            chart_data["mm_acceleration_8w"] * 100,
            label="MM Acceleration 8W",
            color="#16a34a",
        )
        ax.axhline(0, color="#111827", linewidth=1)
        ax.set_title("MM Velocity And Acceleration")
        ax.set_ylabel("Percentile points")
        ax.legend()
        fig.tight_layout()
        fig.savefig(VELOCITY_ACCELERATION_CHART, dpi=170)
        plt.close(fig)

    lead_feature = lead_lag[lead_lag["mm_feature"] == "mm_velocity_8w"].copy()
    if not lead_feature.empty:
        fig, ax = plt.subplots(figsize=(11, 6))
        for horizon, group in lead_feature.groupby("gold_horizon", sort=False):
            ordered = group.sort_values("lag_weeks")
            ax.plot(ordered["lag_weeks"], ordered["correlation"], marker="o", label=f"{horizon} corr")
            ax.plot(
                ordered["lag_weeks"],
                ordered["rank_correlation"],
                marker="x",
                linestyle="--",
                alpha=0.75,
                label=f"{horizon} rank",
            )
        ax.axhline(0, color="#111827", linewidth=1)
        ax.set_title("MM Velocity 8W Lead-Lag Correlation")
        ax.set_xlabel("Lag weeks (positive = MM feature earlier)")
        ax.set_ylabel("Correlation")
        ax.legend(fontsize=8, ncols=2)
        fig.tight_layout()
        fig.savefig(LEAD_LAG_CHART, dpi=170)
        plt.close(fig)

    if not state_frame.empty:
        plot_frame = state_frame.melt(
            id_vars=["mm_lifecycle_state"],
            value_vars=[f"median_forward_return_{horizon}w" for horizon in HORIZONS],
            var_name="horizon",
            value_name="median_forward_return",
        )
        plot_frame["horizon"] = plot_frame["horizon"].str.extract(r"(\d+w)", expand=False).str.upper()
        pivot = plot_frame.pivot_table(
            index="mm_lifecycle_state",
            columns="horizon",
            values="median_forward_return",
            aggfunc="mean",
        ).reindex(STATE_ORDER)
        fig, ax = plt.subplots(figsize=(12, 6))
        (pivot * 100).plot(kind="bar", ax=ax)
        ax.axhline(0, color="#111827", linewidth=1)
        ax.set_title("MM Lifecycle State Historical Outcomes")
        ax.set_ylabel("Median following return (%)")
        ax.set_xlabel("MM lifecycle state")
        ax.legend(title="Horizon")
        fig.tight_layout()
        fig.savefig(STATE_OUTCOMES_CHART, dpi=170)
        plt.close(fig)

    if not trajectories.empty:
        window = "8W" if "8W" in set(trajectories["window"]) else trajectories["window"].iloc[0]
        top = trajectories[trajectories["window"] == window].head(5).copy()
        current_path = json.loads(top.iloc[0]["current_path"]) if not top.empty else []
        fig, ax = plt.subplots(figsize=(11, 6))
        offsets = list(range(-len(current_path) + 1, 1))
        if current_path:
            ax.plot(offsets, current_path, color="#111827", linewidth=2.5, label="Current MM trajectory")
        for _, row in top.iterrows():
            path = json.loads(row["historical_path"])
            path_offsets = list(range(-len(path) + 1, 1))
            ax.plot(
                path_offsets,
                path,
                alpha=0.55,
                linewidth=1.4,
                label=f"{row['historical_end_date']} ({row['similarity_score']:.1f})",
            )
        ax.set_title("Top Similar Historical MM Trajectories")
        ax.set_xlabel("Normalized week index")
        ax.set_ylabel("MM percentile")
        ax.set_ylim(0, 100)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(TRAJECTORY_CHART, dpi=170)
        plt.close(fig)


def best_rows(frame: pd.DataFrame, count: int = 5) -> pd.DataFrame:
    if frame.empty:
        return frame
    result = frame.copy()
    result["abs_rank_correlation"] = result["rank_correlation"].abs()
    return result.sort_values("abs_rank_correlation", ascending=False).head(count)


def strongest_velocity_window(lead_lag: pd.DataFrame) -> str:
    velocity_rows = lead_lag[lead_lag["mm_feature"].str.startswith("mm_velocity")].copy()
    if velocity_rows.empty:
        return "N/A"
    summary = (
        velocity_rows.assign(abs_rank=lambda frame: frame["rank_correlation"].abs())
        .groupby("mm_feature", as_index=False)["abs_rank"]
        .mean()
        .sort_values("abs_rank", ascending=False)
    )
    if summary.empty:
        return "N/A"
    row = summary.iloc[0]
    return f"{row['mm_feature']} average absolute rank correlation {row['abs_rank']:.3f}"


def trajectory_outcome_summary(trajectories: pd.DataFrame, window: str = "8W") -> pd.Series | None:
    if trajectories.empty:
        return None
    sample = trajectories[trajectories["window"] == window].head(20)
    if sample.empty:
        sample = trajectories.head(20)
    metrics: dict[str, object] = {"window": window, "case_count": int(len(sample))}
    for horizon in HORIZONS:
        col = f"historical_gold_return_{horizon}w"
        values = pd.to_numeric(sample[col], errors="coerce").dropna()
        metrics[f"avg_return_{horizon}w"] = np.nan if values.empty else float(values.mean())
        metrics[f"median_return_{horizon}w"] = np.nan if values.empty else float(values.median())
        metrics[f"win_rate_{horizon}w"] = np.nan if values.empty else float((values > 0).mean())
    return pd.Series(metrics)


def state_takeaway(state_frame: pd.DataFrame) -> str:
    if state_frame.empty:
        return "N/A"
    frame = state_frame.copy()
    frame["abs_median_8w"] = pd.to_numeric(frame["median_forward_return_8w"], errors="coerce").abs()
    frame = frame.sort_values("abs_median_8w", ascending=False)
    if frame.empty or pd.isna(frame.iloc[0]["abs_median_8w"]):
        return "N/A"
    row = frame.iloc[0]
    return (
        f"{row['mm_lifecycle_state']} has the largest absolute 8W median following return "
        f"({fmt_pct(row['median_forward_return_8w'])}) in this sample."
    )


def write_summary(bundle: ResearchBundle) -> None:
    data = bundle.dataset
    latest = data.dropna(subset=["date"]).iloc[-1]
    lead_lag = bundle.lead_lag
    state_frame = bundle.state_analysis
    trajectories = bundle.trajectory_similarity
    top_lead = best_rows(lead_lag, 8)
    trajectory_summary = trajectory_outcome_summary(trajectories, "8W")
    top_trajectories = (
        trajectories[trajectories["window"] == "8W"].head(10)
        if not trajectories.empty and "8W" in set(trajectories["window"])
        else trajectories.head(10)
    )
    positive_lag = best_rows(lead_lag[lead_lag["lag_weeks"] > 0], 1)
    lag_take = (
        "The strongest positive-lag row suggests MM lifecycle features have some historical lead-lag context, "
        "but it should be treated as sample evidence rather than a forecast."
        if not positive_lag.empty and abs(float(positive_lag.iloc[0]["rank_correlation"])) >= 0.10
        else "Positive-lag tests do not show a strong standalone lead relationship in this sample."
    )

    lines = [
        "# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery",
        "",
        "This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.",
        "",
        "## Executive Summary",
        "",
        f"- Data period: `{data['date'].min().strftime('%Y-%m-%d')}` to `{data['date'].max().strftime('%Y-%m-%d')}`.",
        f"- Latest date: `{latest['date'].strftime('%Y-%m-%d')}`.",
        f"- Latest MM percentile: `{fmt_pct(latest['mm_percentile'])}`.",
        f"- Latest MM lifecycle state: `{latest['mm_lifecycle_state']}`.",
        f"- Latest MM velocity 8W: `{fmt_pct(latest['mm_velocity_8w'])}`.",
        f"- Latest MM acceleration 8W: `{fmt_pct(latest['mm_acceleration_8w'])}`.",
        f"- Strongest velocity window summary: `{strongest_velocity_window(lead_lag)}`.",
        f"- State outcome note: {state_takeaway(state_frame)}",
        f"- Lead-lag note: {lag_take}",
        "",
        "## Required Research Questions",
        "",
        "### 1. What does the current MM percentile lifecycle mean?",
        "",
        "MM lifecycle treats `mm_net_percentile_156w` as a positioning phase variable. A low percentile with rising velocity is different from a low percentile still falling; a high percentile with rising velocity is different from a high percentile already rolling over.",
        "",
        "### 2. What is MM Velocity?",
        "",
        "MM Velocity measures the change in MM percentile over a trailing window. For example, `mm_velocity_8w = mm_percentile - mm_percentile.shift(8)`. Positive values mean MM positioning moved higher versus eight weeks earlier; negative values mean positioning moved lower.",
        "",
        "### 3. What is MM Acceleration?",
        "",
        "MM Acceleration measures whether velocity itself is increasing or fading. `mm_acceleration_8w = mm_velocity_8w - mm_velocity_8w.shift(8)`. It helps separate steady accumulation from a faster or slower positioning move.",
        "",
        "### 4. Does MM lead gold, does gold lead MM, or is the relationship mixed?",
        "",
        lag_take,
        "",
        "### 5. Which MM velocity window has the most information?",
        "",
        strongest_velocity_window(lead_lag),
        "",
        "### 6. Which MM Lifecycle State has the strongest historical sample tendency?",
        "",
        state_takeaway(state_frame),
        "",
        "### 7. What does the current MM Lifecycle State mean?",
        "",
        f"The latest state is `{latest['mm_lifecycle_state']}`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.",
        "",
        "### 8. What does the current MM Velocity imply?",
        "",
        f"Latest 8W velocity is `{fmt_pct(latest['mm_velocity_8w'])}`. It describes recent positioning movement only; it does not independently determine market direction.",
        "",
        "### 9. What does the current MM Acceleration imply?",
        "",
        f"Latest 8W acceleration is `{fmt_pct(latest['mm_acceleration_8w'])}`. It describes whether the positioning movement is speeding up or slowing down.",
        "",
        "### 10. Which historical MM trajectories are most similar now?",
        "",
    ]

    if top_trajectories.empty:
        lines.append("N/A: no valid trajectory matches were available after the recent-window exclusion.")
    else:
        lines.extend(
            [
                top_trajectories[
                    [
                        "window",
                        "historical_start_date",
                        "historical_end_date",
                        "similarity_score",
                        "historical_gold_return_1w",
                        "historical_gold_return_2w",
                        "historical_gold_return_4w",
                        "historical_gold_return_8w",
                    ]
                ].to_markdown(index=False),
            ]
        )

    lines.extend(
        [
            "",
            "### 11. What happened after the most similar historical trajectories?",
            "",
        ]
    )
    if trajectory_summary is None:
        lines.append("N/A: no trajectory outcome summary is available.")
    else:
        for horizon in HORIZONS:
            lines.append(
                f"- {horizon}W: avg `{fmt_pct(trajectory_summary.get(f'avg_return_{horizon}w'))}`, "
                f"median `{fmt_pct(trajectory_summary.get(f'median_return_{horizon}w'))}`, "
                f"win rate `{fmt_pct(trajectory_summary.get(f'win_rate_{horizon}w'))}`."
            )

    lines.extend(
        [
            "",
            "### 12. Should this replace MM Percentile in the Dashboard?",
            "",
            "No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.",
            "",
            "### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?",
            "",
            "Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.",
            "",
            "## MM Lifecycle State Analysis",
            "",
            state_frame.to_markdown(index=False),
            "",
            "## Strongest Lead-Lag Rows",
            "",
            top_lead.to_markdown(index=False),
            "",
            "## Method Notes",
            "",
            "- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.",
            "- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.",
            "- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.",
            "- All outputs are historical statistics / research reference only.",
        ]
    )
    SUMMARY_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(bundle: ResearchBundle) -> None:
    output_dirs()
    bundle.dataset.to_csv(LIFECYCLE_DATASET_PATH, index=False)
    bundle.state_analysis.to_csv(STATE_ANALYSIS_PATH, index=False)
    bundle.lead_lag.to_csv(LEAD_LAG_PATH, index=False)
    bundle.trajectory_similarity.to_csv(TRAJECTORY_SIMILARITY_PATH, index=False)
    write_charts(bundle)
    write_summary(bundle)


def run_research() -> ResearchBundle:
    master = load_master()
    data = build_lifecycle_dataset(master)
    bundle = ResearchBundle(
        dataset=data,
        state_analysis=state_analysis(data),
        lead_lag=lead_lag_analysis(data),
        trajectory_similarity=trajectory_similarity(data),
    )
    write_outputs(bundle)
    return bundle


def main() -> int:
    bundle = run_research()
    print(f"Wrote MM lifecycle dataset: {LIFECYCLE_DATASET_PATH}")
    print(f"Wrote MM lifecycle summary: {SUMMARY_MD_PATH}")
    print(f"Rows: {len(bundle.dataset)}")
    print("Scope: historical statistics / research reference only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

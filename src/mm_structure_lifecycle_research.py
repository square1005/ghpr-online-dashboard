"""GHPR v0.6 MM long/short/net structure lifecycle research.

This module is historical structure research only. It does not create
execution logic, market instructions, broker/API integrations, or account use.
"""

from __future__ import annotations

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

DATASET_PATH = PROCESSED_DIR / "mm_structure_lifecycle_dataset.csv"
SUMMARY_MD_PATH = REPORTS_DIR / "mm_structure_lifecycle_summary.md"
LEAD_LAG_PATH = REPORTS_DIR / "mm_structure_lead_lag.csv"
STATE_ANALYSIS_PATH = REPORTS_DIR / "mm_structure_state_analysis.csv"
CONTRIBUTION_ANALYSIS_PATH = REPORTS_DIR / "mm_structure_contribution_analysis.csv"

GOLD_STRUCTURE_CHART = CHARTS_DIR / "gold_vs_mm_long_short_net.png"
PERCENTILES_CHART = CHARTS_DIR / "mm_long_short_net_percentiles.png"
VELOCITY_CHART = CHARTS_DIR / "mm_structure_velocity.png"
LEAD_LAG_CHART = CHARTS_DIR / "mm_structure_lead_lag_correlation.png"
STATE_OUTCOMES_CHART = CHARTS_DIR / "mm_structure_state_outcomes.png"

REQUIRED_COLUMNS = [
    "date",
    "gold_close",
    "mm_long",
    "mm_short",
    "mm_net",
    "mm_net_percentile_156w",
    "gold_return_1w",
    "gold_return_2w",
    "gold_return_4w",
    "gold_return_8w",
]
HORIZONS = [1, 2, 4, 8]
VELOCITY_WINDOWS = [4, 8, 12]
LAGS = [-8, -4, -2, 0, 2, 4, 8]
ROLLING_WINDOW = 156
ROLLING_MIN_PERIODS = 20

STRUCTURE_STATE_ORDER = [
    "MM_STRUCTURE_ACCUMULATION",
    "MM_STRUCTURE_SHORT_COVERING_RALLY",
    "MM_STRUCTURE_LONG_LIQUIDATION",
    "MM_STRUCTURE_SHORT_BUILDING",
    "MM_STRUCTURE_CROWDED_LONG",
    "MM_STRUCTURE_LOW_PARTICIPATION",
    "MM_STRUCTURE_NEUTRAL",
]
CONTRIBUTION_STATE_ORDER = [
    "LONG_BUILDING",
    "SHORT_COVERING",
    "LONG_LIQUIDATION",
    "SHORT_BUILDING",
    "MIXED_LONG_AND_SHORT_UP",
    "MIXED_LONG_AND_SHORT_DOWN",
    "NEUTRAL_STRUCTURE",
]
STRUCTURE_COLORS = {
    "MM_STRUCTURE_ACCUMULATION": "#16a34a",
    "MM_STRUCTURE_SHORT_COVERING_RALLY": "#0ea5e9",
    "MM_STRUCTURE_LONG_LIQUIDATION": "#ef4444",
    "MM_STRUCTURE_SHORT_BUILDING": "#f97316",
    "MM_STRUCTURE_CROWDED_LONG": "#9333ea",
    "MM_STRUCTURE_LOW_PARTICIPATION": "#64748b",
    "MM_STRUCTURE_NEUTRAL": "#94a3b8",
}


@dataclass(frozen=True)
class StructureResearchBundle:
    dataset: pd.DataFrame
    lead_lag: pd.DataFrame
    state_analysis: pd.DataFrame
    contribution_analysis: pd.DataFrame


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


def fmt_number(value: object, digits: int = 2) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{number:,.{digits}f}"


def fmt_pct(value: object, digits: int = 2) -> str:
    number = scalar_float(value)
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
    for column in REQUIRED_COLUMNS:
        if column != "date":
            master[column] = pd.to_numeric(master[column], errors="coerce")
    master = master.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return master


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


def contribution_state(row: pd.Series) -> str:
    long_change = scalar_float(row.get("mm_long_change_8w"))
    short_change = scalar_float(row.get("mm_short_change_8w"))
    if long_change is None or short_change is None:
        return "NEUTRAL_STRUCTURE"
    if long_change > 0 and short_change < 0:
        return "LONG_BUILDING" if abs(long_change) >= abs(short_change) else "SHORT_COVERING"
    if long_change < 0 and short_change > 0:
        return "LONG_LIQUIDATION" if abs(long_change) >= abs(short_change) else "SHORT_BUILDING"
    if long_change > 0 and short_change == 0:
        return "LONG_BUILDING"
    if long_change == 0 and short_change < 0:
        return "SHORT_COVERING"
    if long_change < 0 and short_change == 0:
        return "LONG_LIQUIDATION"
    if long_change == 0 and short_change > 0:
        return "SHORT_BUILDING"
    if long_change > 0 and short_change > 0:
        return "MIXED_LONG_AND_SHORT_UP"
    if long_change < 0 and short_change < 0:
        return "MIXED_LONG_AND_SHORT_DOWN"
    return "NEUTRAL_STRUCTURE"


def structure_state(row: pd.Series) -> str:
    long_pct = scalar_float(row.get("mm_long_percentile_156w"))
    short_pct = scalar_float(row.get("mm_short_percentile_156w"))
    net_pct = scalar_float(row.get("mm_net_percentile_156w"))
    long_velocity = scalar_float(row.get("mm_long_velocity_8w"))
    short_velocity = scalar_float(row.get("mm_short_velocity_8w"))
    net_velocity = scalar_float(row.get("mm_net_velocity_8w"))
    if any(value is None for value in [long_pct, short_pct, net_pct, long_velocity, short_velocity, net_velocity]):
        return "MM_STRUCTURE_NEUTRAL"
    if long_pct >= 0.80 and net_pct >= 0.80:
        return "MM_STRUCTURE_CROWDED_LONG"
    if long_pct < 0.40 and short_pct < 0.40:
        return "MM_STRUCTURE_LOW_PARTICIPATION"
    if long_velocity > 0 and short_velocity <= 0 and net_velocity > 0:
        return "MM_STRUCTURE_ACCUMULATION"
    if short_velocity < 0 and net_velocity > 0:
        return "MM_STRUCTURE_SHORT_COVERING_RALLY"
    if long_velocity < 0 and net_velocity < 0:
        return "MM_STRUCTURE_LONG_LIQUIDATION"
    if short_velocity > 0 and net_velocity < 0:
        return "MM_STRUCTURE_SHORT_BUILDING"
    return "MM_STRUCTURE_NEUTRAL"


def build_structure_dataset(master: pd.DataFrame) -> pd.DataFrame:
    data = master[REQUIRED_COLUMNS].copy()
    data["mm_long_percentile_156w"] = rolling_percentile_prior(data["mm_long"])
    data["mm_short_percentile_156w"] = rolling_percentile_prior(data["mm_short"])
    data["mm_net_percentile_156w"] = pd.to_numeric(data["mm_net_percentile_156w"], errors="coerce")

    for prefix in ["long", "short", "net"]:
        source = f"mm_{prefix}_percentile_156w"
        for window in VELOCITY_WINDOWS:
            data[f"mm_{prefix}_velocity_{window}w"] = data[source] - data[source].shift(window)
        data[f"mm_{prefix}_acceleration_8w"] = (
            data[f"mm_{prefix}_velocity_8w"] - data[f"mm_{prefix}_velocity_8w"].shift(8)
        )

    data["mm_long_change_8w"] = data["mm_long"] - data["mm_long"].shift(8)
    data["mm_short_change_8w"] = data["mm_short"] - data["mm_short"].shift(8)
    data["mm_net_change_8w"] = data["mm_net"] - data["mm_net"].shift(8)
    data["mm_net_change_8w_from_components"] = data["mm_long_change_8w"] - data["mm_short_change_8w"]
    data["mm_net_change_8w_reconciliation_error"] = (
        data["mm_net_change_8w"] - data["mm_net_change_8w_from_components"]
    )
    data["mm_structure_contribution_state"] = data.apply(contribution_state, axis=1)
    data["mm_structure_state"] = data.apply(structure_state, axis=1)
    return data


def outcome_analysis(data: pd.DataFrame, group_column: str, order: list[str]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for state in order:
        group = data[data[group_column] == state]
        row: dict[str, object] = {group_column: state, "count": int(len(group))}
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
    corr = scalar_float(rank_correlation)
    if corr is None or abs(corr) < 0.10:
        return "weak_historical_structure_relationship"
    direction = "positive" if corr > 0 else "negative"
    if lag_weeks > 0:
        return f"mm_structure_feature_leads_gold_{lag_weeks}w_{direction}_historical_alignment"
    if lag_weeks < 0:
        return f"mm_structure_feature_lags_or_confirms_gold_{abs(lag_weeks)}w_{direction}_historical_alignment"
    return f"same_week_{direction}_historical_alignment"


def lead_lag_analysis(data: pd.DataFrame) -> pd.DataFrame:
    features = [
        "mm_long_velocity_4w",
        "mm_long_velocity_8w",
        "mm_long_velocity_12w",
        "mm_short_velocity_4w",
        "mm_short_velocity_8w",
        "mm_short_velocity_12w",
        "mm_net_velocity_4w",
        "mm_net_velocity_8w",
        "mm_net_velocity_12w",
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


def output_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def write_charts(bundle: StructureResearchBundle) -> None:
    data = bundle.dataset.copy()
    lead_lag = bundle.lead_lag.copy()
    state_analysis = bundle.state_analysis.copy()
    plt.style.use("seaborn-v0_8-whitegrid")

    chart_data = data.dropna(subset=["date", "gold_close"]).copy()
    if not chart_data.empty:
        chart_data["gold_index"] = chart_data["gold_close"] / chart_data["gold_close"].iloc[0] * 100

        fig, ax1 = plt.subplots(figsize=(14, 7))
        ax1.plot(chart_data["date"], chart_data["gold_index"], color="#111827", label="Gold normalized index")
        ax1.set_ylabel("Gold normalized index")
        ax2 = ax1.twinx()
        ax2.plot(chart_data["date"], chart_data["mm_long_percentile_156w"] * 100, color="#16a34a", label="MM Long Percentile")
        ax2.plot(chart_data["date"], chart_data["mm_short_percentile_156w"] * 100, color="#ef4444", label="MM Short Percentile")
        ax2.plot(chart_data["date"], chart_data["mm_net_percentile_156w"] * 100, color="#2563eb", label="MM Net Percentile")
        ax2.set_ylabel("MM percentile")
        ax2.set_ylim(0, 100)
        ax1.set_title("Gold vs MM Long / Short / Net Structure")
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, loc="upper left")
        fig.tight_layout()
        fig.savefig(GOLD_STRUCTURE_CHART, dpi=170)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(chart_data["date"], chart_data["mm_long_percentile_156w"] * 100, label="MM Long Percentile", color="#16a34a")
        ax.plot(chart_data["date"], chart_data["mm_short_percentile_156w"] * 100, label="MM Short Percentile", color="#ef4444")
        ax.plot(chart_data["date"], chart_data["mm_net_percentile_156w"] * 100, label="MM Net Percentile", color="#2563eb")
        ax.set_title("MM Long / Short / Net Percentiles")
        ax.set_ylabel("Percentile")
        ax.set_ylim(0, 100)
        ax.legend()
        fig.tight_layout()
        fig.savefig(PERCENTILES_CHART, dpi=170)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(14, 6))
        ax.plot(chart_data["date"], chart_data["mm_long_velocity_8w"] * 100, label="Long velocity 8W", color="#16a34a")
        ax.plot(chart_data["date"], chart_data["mm_short_velocity_8w"] * 100, label="Short velocity 8W", color="#ef4444")
        ax.plot(chart_data["date"], chart_data["mm_net_velocity_8w"] * 100, label="Net velocity 8W", color="#2563eb")
        ax.axhline(0, color="#111827", linewidth=1)
        ax.set_title("MM Structure Velocity")
        ax.set_ylabel("Percentile points")
        ax.legend()
        fig.tight_layout()
        fig.savefig(VELOCITY_CHART, dpi=170)
        plt.close(fig)

    lead_subset = lead_lag[
        lead_lag["mm_feature"].isin(["mm_long_velocity_8w", "mm_short_velocity_8w", "mm_net_velocity_8w"])
        & lead_lag["gold_horizon"].isin(["4W", "8W"])
    ].copy()
    if not lead_subset.empty:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        for ax, horizon in zip(axes, ["4W", "8W"]):
            horizon_frame = lead_subset[lead_subset["gold_horizon"] == horizon]
            for feature, group in horizon_frame.groupby("mm_feature", sort=False):
                ordered = group.sort_values("lag_weeks")
                label = feature.replace("mm_", "").replace("_", " ")
                ax.plot(ordered["lag_weeks"], ordered["rank_correlation"], marker="o", label=label)
            ax.axhline(0, color="#111827", linewidth=1)
            ax.set_title(f"Gold {horizon} following return")
            ax.set_xlabel("Lag weeks")
        axes[0].set_ylabel("Rank correlation")
        axes[1].legend(fontsize=8)
        fig.suptitle("MM Structure Lead-Lag Rank Correlation")
        fig.tight_layout()
        fig.savefig(LEAD_LAG_CHART, dpi=170)
        plt.close(fig)

    if not state_analysis.empty:
        plot_frame = state_analysis.melt(
            id_vars=["mm_structure_state"],
            value_vars=[f"median_forward_return_{horizon}w" for horizon in HORIZONS],
            var_name="horizon",
            value_name="median_forward_return",
        )
        plot_frame["horizon"] = plot_frame["horizon"].str.extract(r"(\d+w)", expand=False).str.upper()
        pivot = plot_frame.pivot_table(
            index="mm_structure_state",
            columns="horizon",
            values="median_forward_return",
            aggfunc="mean",
        ).reindex(STRUCTURE_STATE_ORDER)
        fig, ax = plt.subplots(figsize=(14, 7))
        (pivot * 100).plot(kind="bar", ax=ax)
        ax.axhline(0, color="#111827", linewidth=1)
        ax.set_title("MM Structure State Historical Outcomes")
        ax.set_ylabel("Median following return (%)")
        ax.set_xlabel("MM structure state")
        ax.legend(title="Horizon")
        fig.tight_layout()
        fig.savefig(STATE_OUTCOMES_CHART, dpi=170)
        plt.close(fig)


def strongest_rows(frame: pd.DataFrame, count: int = 8) -> pd.DataFrame:
    if frame.empty:
        return frame
    return (
        frame.assign(abs_rank_correlation=frame["rank_correlation"].abs())
        .sort_values("abs_rank_correlation", ascending=False)
        .head(count)
    )


def strongest_feature_note(lead_lag: pd.DataFrame, feature_prefix: str) -> str:
    subset = lead_lag[lead_lag["mm_feature"].str.startswith(feature_prefix)].copy()
    if subset.empty:
        return "N/A"
    row = strongest_rows(subset, 1).iloc[0]
    return (
        f"{row['mm_feature']} vs {row['gold_horizon']} at lag {int(row['lag_weeks'])}W "
        f"has rank correlation {row['rank_correlation']:.3f}."
    )


def state_takeaway(state_analysis: pd.DataFrame) -> str:
    if state_analysis.empty:
        return "N/A"
    frame = state_analysis.copy()
    frame["abs_median_8w"] = pd.to_numeric(frame["median_forward_return_8w"], errors="coerce").abs()
    frame = frame.sort_values("abs_median_8w", ascending=False)
    if frame.empty or pd.isna(frame.iloc[0]["abs_median_8w"]):
        return "N/A"
    row = frame.iloc[0]
    return (
        f"{row['mm_structure_state']} has the largest absolute 8W median following return "
        f"({fmt_pct(row['median_forward_return_8w'])}) in this sample."
    )


def contribution_takeaway(contribution_analysis: pd.DataFrame) -> str:
    if contribution_analysis.empty:
        return "N/A"
    frame = contribution_analysis.copy()
    frame["abs_median_8w"] = pd.to_numeric(frame["median_forward_return_8w"], errors="coerce").abs()
    frame = frame.sort_values("abs_median_8w", ascending=False)
    if frame.empty or pd.isna(frame.iloc[0]["abs_median_8w"]):
        return "N/A"
    row = frame.iloc[0]
    return (
        f"{row['mm_structure_contribution_state']} has the largest absolute 8W median following return "
        f"({fmt_pct(row['median_forward_return_8w'])}) in this sample."
    )


def write_summary(bundle: StructureResearchBundle) -> None:
    data = bundle.dataset
    latest = data.dropna(subset=["date"]).iloc[-1]
    top_lead = strongest_rows(bundle.lead_lag, 10)
    lines = [
        "# GHPR v0.6 MM Long / Short Structure Lifecycle Research",
        "",
        "Historical structure research only. Not a trading signal. Not financial advice.",
        "",
        "## Executive Summary",
        "",
        f"- Data period: `{data['date'].min().strftime('%Y-%m-%d')}` to `{data['date'].max().strftime('%Y-%m-%d')}`.",
        f"- Latest date: `{latest['date'].strftime('%Y-%m-%d')}`.",
        f"- Latest MM Long / Short / Net: `{fmt_number(latest['mm_long'], 0)}` / `{fmt_number(latest['mm_short'], 0)}` / `{fmt_number(latest['mm_net'], 0)}`.",
        f"- Latest MM Long / Short / Net percentile: `{fmt_pct(latest['mm_long_percentile_156w'])}` / `{fmt_pct(latest['mm_short_percentile_156w'])}` / `{fmt_pct(latest['mm_net_percentile_156w'])}`.",
        f"- Latest Long / Short / Net velocity 8W: `{fmt_pct(latest['mm_long_velocity_8w'])}` / `{fmt_pct(latest['mm_short_velocity_8w'])}` / `{fmt_pct(latest['mm_net_velocity_8w'])}`.",
        f"- Latest structure state: `{latest['mm_structure_state']}`.",
        f"- Latest contribution state: `{latest['mm_structure_contribution_state']}`.",
        f"- Structure state note: {state_takeaway(bundle.state_analysis)}",
        f"- Contribution note: {contribution_takeaway(bundle.contribution_analysis)}",
        "",
        "## Required Research Questions",
        "",
        "### 1. Why is MM Net alone incomplete?",
        "",
        "MM Net equals MM Long minus MM Short. A rising net position can come from new long exposure, short reduction, or both. A falling net position can come from long liquidation, short building, or both. The structure layer separates those paths.",
        "",
        "### 2. What do MM Long / Short / Net each represent?",
        "",
        "MM Long describes long-side exposure, MM Short describes short-side exposure, and MM Net summarizes their difference. The three series can move together or diverge, so Net should be read with its component structure.",
        "",
        "### 3. When Net rises, is it driven by Long building or Short covering?",
        "",
        f"Latest 8W changes: Long `{fmt_number(latest['mm_long_change_8w'], 0)}`, Short `{fmt_number(latest['mm_short_change_8w'], 0)}`, Net `{fmt_number(latest['mm_net_change_8w'], 0)}`. Latest contribution label is `{latest['mm_structure_contribution_state']}`.",
        "",
        "### 4. When Net falls, is it driven by Long liquidation or Short building?",
        "",
        "The contribution analysis table separates long-side reduction from short-side increase. This distinction matters because both can produce lower Net while describing different participation behavior.",
        "",
        "### 5. Which has more information: Long Velocity, Short Velocity, or Net Velocity?",
        "",
        f"- Long: {strongest_feature_note(bundle.lead_lag, 'mm_long')}",
        f"- Short: {strongest_feature_note(bundle.lead_lag, 'mm_short')}",
        f"- Net: {strongest_feature_note(bundle.lead_lag, 'mm_net')}",
        "",
        "### 6. Does Long lead Gold?",
        "",
        strongest_feature_note(bundle.lead_lag, "mm_long"),
        "",
        "### 7. Does Short lead Gold?",
        "",
        strongest_feature_note(bundle.lead_lag, "mm_short"),
        "",
        "### 8. Is Net mainly a Long or Short outcome?",
        "",
        "Net is a component outcome. The current 8W reconciliation confirms `mm_net_change_8w = mm_long_change_8w - mm_short_change_8w`, with any residual shown in `mm_net_change_8w_reconciliation_error`.",
        "",
        "### 9. What is the current MM Structure State?",
        "",
        f"The current MM Structure State is `{latest['mm_structure_state']}`. This is a historical structure label, not a market instruction.",
        "",
        "### 10. What do the current structure fields mean?",
        "",
        f"- MM Long Percentile: `{fmt_pct(latest['mm_long_percentile_156w'])}`.",
        f"- MM Short Percentile: `{fmt_pct(latest['mm_short_percentile_156w'])}`.",
        f"- MM Net Percentile: `{fmt_pct(latest['mm_net_percentile_156w'])}`.",
        f"- Long Velocity 8W: `{fmt_pct(latest['mm_long_velocity_8w'])}`.",
        f"- Short Velocity 8W: `{fmt_pct(latest['mm_short_velocity_8w'])}`.",
        f"- Net Velocity 8W: `{fmt_pct(latest['mm_net_velocity_8w'])}`.",
        "",
        "### 11. Should GHPR Dashboard v0.6 add Long / Short / Net structure?",
        "",
        "Yes, as a research layer. It improves explainability of the existing MM Net signal by showing whether long-side or short-side positioning is driving the structure.",
        "",
        "### 12. Should Producer / OI lifecycle be added next?",
        "",
        "Potentially, but this v0.6 module intentionally stays MM-only. Producer and OI lifecycle research should be separate modules so their definitions do not blur the MM structure study.",
        "",
        "### 13. Current research conclusion",
        "",
        "MM structure adds useful decomposition around MM Net. The dashboard should display it as historical structure research, with the existing MM Net percentile preserved as the current core positioning reference.",
        "",
        "## MM Structure State Analysis",
        "",
        bundle.state_analysis.to_markdown(index=False),
        "",
        "## MM Structure Contribution Analysis",
        "",
        bundle.contribution_analysis.to_markdown(index=False),
        "",
        "## Strongest Lead-Lag Rows",
        "",
        top_lead.to_markdown(index=False),
        "",
        "## Method Notes",
        "",
        "- MM Long and MM Short percentiles use prior-only rolling 156-week windows with a 20-observation minimum.",
        "- MM Net percentile uses the existing `mm_net_percentile_156w` from the master weekly dataset.",
        "- Positive lag means the MM feature is shifted earlier against gold following returns.",
        "- All outputs are historical structure research only.",
    ]
    SUMMARY_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(bundle: StructureResearchBundle) -> None:
    output_dirs()
    bundle.dataset.to_csv(DATASET_PATH, index=False)
    bundle.lead_lag.to_csv(LEAD_LAG_PATH, index=False)
    bundle.state_analysis.to_csv(STATE_ANALYSIS_PATH, index=False)
    bundle.contribution_analysis.to_csv(CONTRIBUTION_ANALYSIS_PATH, index=False)
    write_charts(bundle)
    write_summary(bundle)


def run_research() -> StructureResearchBundle:
    master = load_master()
    data = build_structure_dataset(master)
    bundle = StructureResearchBundle(
        dataset=data,
        lead_lag=lead_lag_analysis(data),
        state_analysis=outcome_analysis(data, "mm_structure_state", STRUCTURE_STATE_ORDER),
        contribution_analysis=outcome_analysis(
            data,
            "mm_structure_contribution_state",
            CONTRIBUTION_STATE_ORDER,
        ),
    )
    write_outputs(bundle)
    return bundle


def main() -> int:
    bundle = run_research()
    print(f"Wrote MM structure lifecycle dataset: {DATASET_PATH}")
    print(f"Wrote MM structure lifecycle summary: {SUMMARY_MD_PATH}")
    print(f"Rows: {len(bundle.dataset)}")
    print("Scope: historical structure research only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""GHPR v0.6.2 MM velocity window discovery.

Historical structure research only. This module compares MM Long / Short / Net
velocity windows and does not create execution logic or market instructions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STRUCTURE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_structure_lifecycle_dataset.csv"
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

WINDOW_DATASET_PATH = PROCESSED_DIR / "mm_velocity_window_dataset.csv"
SCORECARD_PATH = REPORTS_DIR / "mm_velocity_window_scorecard.csv"
BUCKET_ANALYSIS_PATH = REPORTS_DIR / "mm_velocity_window_bucket_analysis.csv"
TRAIN_TEST_PATH = REPORTS_DIR / "mm_velocity_window_train_test.csv"
SUMMARY_MD_PATH = REPORTS_DIR / "mm_velocity_window_summary.md"

SCORECARD_CHART = CHARTS_DIR / "mm_velocity_window_scorecard.png"
LONG_WINDOWS_CHART = CHARTS_DIR / "mm_long_velocity_windows.png"
SHORT_WINDOWS_CHART = CHARTS_DIR / "mm_short_velocity_windows.png"
NET_WINDOWS_CHART = CHARTS_DIR / "mm_net_velocity_windows.png"
FORWARD_8W_CHART = CHARTS_DIR / "mm_velocity_window_forward_8w.png"
LEAD_LAG_CHART = CHARTS_DIR / "mm_velocity_window_lead_lag.png"

FEATURE_GROUPS = ["long", "short", "net"]
WINDOWS = [2, 4, 8, 12, 26]
HORIZONS = [1, 2, 4, 8]
LAGS = [-8, -4, -2, 0, 2, 4, 8]
RETURN_COLUMNS = [f"gold_return_{horizon}w" for horizon in HORIZONS]
REQUIRED_COLUMNS = [
    "date",
    "gold_close",
    "mm_long",
    "mm_short",
    "mm_net",
    "mm_long_percentile_156w",
    "mm_short_percentile_156w",
    "mm_net_percentile_156w",
    *RETURN_COLUMNS,
]
BUCKET_LABELS = ["<= -40", "-40 to -20", "-20 to 0", "0 to 20", "20 to 40", ">= 40"]
TRAIN_START = pd.Timestamp("2009-09-01")
TRAIN_END = pd.Timestamp("2018-12-31")
TEST_START = pd.Timestamp("2019-01-01")
ROLLING_WINDOW = 156
ROLLING_MIN_PERIODS = 20


@dataclass(frozen=True)
class DiscoveryBundle:
    dataset: pd.DataFrame
    scorecard: pd.DataFrame
    bucket_analysis: pd.DataFrame
    train_test: pd.DataFrame
    lead_lag: pd.DataFrame


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


def fmt_pct(value: object, digits: int = 2) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{number * 100:.{digits}f}%"


def fmt_num(value: object, digits: int = 3) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{number:.{digits}f}"


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
        data["mm_long_percentile_156w"] = rolling_percentile_prior(data["mm_long"])
        data["mm_short_percentile_156w"] = rolling_percentile_prior(data["mm_short"])
    else:
        raise FileNotFoundError(
            f"Missing source dataset: {STRUCTURE_DATASET_PATH} and fallback {MASTER_PATH}"
        )

    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    data = data[REQUIRED_COLUMNS].copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for column in data.columns:
        if column != "date":
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return data.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def feature_column(group: str, window: int) -> str:
    return f"mm_{group}_velocity_{window}w"


def percentile_column(group: str) -> str:
    return f"mm_{group}_percentile_156w"


def build_velocity_dataset(source: pd.DataFrame) -> pd.DataFrame:
    data = source.copy()
    for group in FEATURE_GROUPS:
        source_column = percentile_column(group)
        for window in WINDOWS:
            data[feature_column(group, window)] = data[source_column] - data[source_column].shift(window)
    return data


def corr_pair(left: pd.Series, right: pd.Series, method: str = "pearson") -> float:
    frame = pd.concat([left, right], axis=1).dropna()
    if len(frame) < 5:
        return np.nan
    if frame.iloc[:, 0].nunique() < 2 or frame.iloc[:, 1].nunique() < 2:
        return np.nan
    return float(frame.iloc[:, 0].corr(frame.iloc[:, 1], method=method))


def high_low_spread(data: pd.DataFrame, feature_name: str, return_col: str) -> float:
    valid = data[[feature_name, return_col]].dropna().copy()
    if len(valid) < 20:
        return np.nan
    low_threshold = valid[feature_name].quantile(0.20)
    high_threshold = valid[feature_name].quantile(0.80)
    low = valid.loc[valid[feature_name] <= low_threshold, return_col].dropna()
    high = valid.loc[valid[feature_name] >= high_threshold, return_col].dropna()
    if low.empty or high.empty:
        return np.nan
    return float(high.median() - low.median())


def normalize_rank(series: pd.Series, higher_is_better: bool = True) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().sum() == 0:
        return pd.Series(50.0, index=series.index)
    ranks = numeric.rank(pct=True, ascending=not higher_is_better).fillna(0.5) * 100
    return ranks


def stability_metrics(data: pd.DataFrame, feature_name: str) -> dict[str, float | int]:
    values = pd.to_numeric(data[feature_name], errors="coerce")
    weekly_change = values.diff().abs().dropna()
    if weekly_change.empty:
        return {
            "weekly_change_avg": np.nan,
            "weekly_change_median": np.nan,
            "weekly_change_std": np.nan,
            "extreme_jump_count": 0,
        }
    return {
        "weekly_change_avg": float(weekly_change.mean()),
        "weekly_change_median": float(weekly_change.median()),
        "weekly_change_std": float(weekly_change.std(ddof=0)),
        "extreme_jump_count": int((weekly_change > 0.30).sum()),
    }


def information_scorecard(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for group in FEATURE_GROUPS:
        for window in WINDOWS:
            feature_name = feature_column(group, window)
            stability = stability_metrics(data, feature_name)
            for horizon in HORIZONS:
                return_col = f"gold_return_{horizon}w"
                valid = data[[feature_name, return_col]].dropna()
                correlation = corr_pair(data[feature_name], data[return_col], "pearson")
                rank_correlation = corr_pair(data[feature_name], data[return_col], "spearman")
                rows.append(
                    {
                        "feature_group": group,
                        "window": f"{window}W",
                        "window_weeks": window,
                        "feature_name": feature_name,
                        "horizon": f"{horizon}W",
                        "correlation": correlation,
                        "rank_correlation": rank_correlation,
                        "absolute_rank_correlation": np.nan
                        if pd.isna(rank_correlation)
                        else abs(rank_correlation),
                        "high_low_spread": high_low_spread(data, feature_name, return_col),
                        "sample_count": int(len(valid)),
                        **stability,
                    }
                )
    scorecard = pd.DataFrame(rows)
    scorecard["stability_raw_score"] = (
        0.55 * normalize_rank(scorecard["weekly_change_avg"], higher_is_better=False)
        + 0.30 * normalize_rank(scorecard["weekly_change_std"], higher_is_better=False)
        + 0.15 * normalize_rank(scorecard["extreme_jump_count"], higher_is_better=False)
    )
    scorecard["stability_score"] = scorecard["stability_raw_score"]
    scorecard["information_score"] = (
        0.65 * normalize_rank(scorecard["absolute_rank_correlation"], higher_is_better=True)
        + 0.35 * normalize_rank(scorecard["high_low_spread"].abs(), higher_is_better=True)
    )
    scorecard["interpretability_score"] = scorecard["window_weeks"].map(
        {2: 55.0, 4: 85.0, 8: 95.0, 12: 90.0, 26: 65.0}
    )
    return scorecard


def train_test_analysis(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    train = data[(data["date"] >= TRAIN_START) & (data["date"] <= TRAIN_END)]
    test = data[data["date"] >= TEST_START]
    for group in FEATURE_GROUPS:
        for window in WINDOWS:
            feature_name = feature_column(group, window)
            for horizon in HORIZONS:
                return_col = f"gold_return_{horizon}w"
                train_rank = corr_pair(train[feature_name], train[return_col], "spearman")
                test_rank = corr_pair(test[feature_name], test[return_col], "spearman")
                train_spread = high_low_spread(train, feature_name, return_col)
                test_spread = high_low_spread(test, feature_name, return_col)
                if pd.isna(train_rank) or pd.isna(test_rank):
                    consistency = False
                elif train_rank == 0 or test_rank == 0:
                    consistency = True
                else:
                    consistency = (train_rank > 0 and test_rank > 0) or (train_rank < 0 and test_rank < 0)
                rows.append(
                    {
                        "feature_group": group,
                        "window": f"{window}W",
                        "window_weeks": window,
                        "feature_name": feature_name,
                        "horizon": f"{horizon}W",
                        "train_rank_corr": train_rank,
                        "test_rank_corr": test_rank,
                        "train_high_low_spread": train_spread,
                        "test_high_low_spread": test_spread,
                        "direction_consistency": bool(consistency),
                    }
                )
    return pd.DataFrame(rows)


def add_final_scores(scorecard: pd.DataFrame, train_test: pd.DataFrame) -> pd.DataFrame:
    merged = scorecard.merge(
        train_test,
        on=["feature_group", "window", "window_weeks", "feature_name", "horizon"],
        how="left",
    )
    merged["train_test_score"] = merged["direction_consistency"].map(lambda value: 100.0 if bool(value) else 0.0)
    merged["total_score"] = (
        0.40 * merged["information_score"]
        + 0.25 * merged["stability_score"]
        + 0.25 * merged["train_test_score"]
        + 0.10 * merged["interpretability_score"]
    )
    merged["recommended"] = False
    for group, rows in merged.groupby("feature_group"):
        long_horizon = rows[rows["horizon"].isin(["4W", "8W"])]
        ranking = (
            long_horizon.groupby("window", as_index=False)["total_score"]
            .mean()
            .sort_values("total_score", ascending=False)
        )
        if not ranking.empty:
            best_window = ranking.iloc[0]["window"]
            merged.loc[
                (merged["feature_group"] == group) & (merged["window"] == best_window),
                "recommended",
            ] = True
    merged["reason"] = merged.apply(score_reason, axis=1)
    output_order = [
        "feature_group",
        "window",
        "feature_name",
        "horizon",
        "correlation",
        "rank_correlation",
        "absolute_rank_correlation",
        "high_low_spread",
        "sample_count",
        "weekly_change_avg",
        "weekly_change_median",
        "weekly_change_std",
        "extreme_jump_count",
        "stability_score",
        "train_rank_corr",
        "test_rank_corr",
        "train_high_low_spread",
        "test_high_low_spread",
        "direction_consistency",
        "information_score",
        "train_test_score",
        "interpretability_score",
        "total_score",
        "recommended",
        "reason",
    ]
    return merged[output_order].sort_values(
        ["feature_group", "horizon", "total_score"],
        ascending=[True, True, False],
    )


def score_reason(row: pd.Series) -> str:
    window = int(str(row["window"]).replace("W", ""))
    parts = []
    if window == 2:
        parts.append("short-term window; higher noise risk")
    elif window == 4:
        parts.append("short-term velocity candidate")
    elif window == 8:
        parts.append("current swing velocity baseline")
    elif window == 12:
        parts.append("medium swing velocity candidate")
    elif window == 26:
        parts.append("medium-term window; slower response")
    if bool(row.get("direction_consistency")):
        parts.append("train/test direction is consistent")
    else:
        parts.append("train/test direction is not consistent")
    parts.append("historical structure research only")
    return "; ".join(parts)


def assign_velocity_bucket(values: pd.Series) -> pd.Series:
    points = pd.to_numeric(values, errors="coerce") * 100
    return pd.cut(
        points,
        bins=[-np.inf, -40, -20, 0, 20, 40, np.inf],
        labels=BUCKET_LABELS,
        right=False,
    )


def bucket_analysis(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for group in FEATURE_GROUPS:
        for window in WINDOWS:
            feature_name = feature_column(group, window)
            frame = data[[feature_name, *RETURN_COLUMNS]].copy()
            frame["bucket"] = assign_velocity_bucket(frame[feature_name])
            for bucket in BUCKET_LABELS:
                sample = frame[frame["bucket"] == bucket]
                row: dict[str, object] = {
                    "feature_group": group,
                    "window": f"{window}W",
                    "feature_name": feature_name,
                    "bucket": bucket,
                    "count": int(len(sample)),
                }
                for horizon in HORIZONS:
                    values = sample[f"gold_return_{horizon}w"].dropna()
                    row[f"avg_forward_return_{horizon}w"] = np.nan if values.empty else float(values.mean())
                    row[f"median_forward_return_{horizon}w"] = np.nan if values.empty else float(values.median())
                    row[f"win_rate_{horizon}w"] = np.nan if values.empty else float((values > 0).mean())
                values_8w = sample["gold_return_8w"].dropna()
                row["best_return_8w"] = np.nan if values_8w.empty else float(values_8w.max())
                row["worst_return_8w"] = np.nan if values_8w.empty else float(values_8w.min())
                rows.append(row)
    return pd.DataFrame(rows)


def recommended_windows(scorecard: pd.DataFrame) -> pd.DataFrame:
    long_horizon = scorecard[scorecard["horizon"].isin(["4W", "8W"])].copy()
    return (
        long_horizon.groupby(["feature_group", "window"], as_index=False)
        .agg(
            avg_total_score=("total_score", "mean"),
            avg_information_score=("information_score", "mean"),
            avg_stability_score=("stability_score", "mean"),
            avg_train_test_score=("train_test_score", "mean"),
        )
        .sort_values(["feature_group", "avg_total_score"], ascending=[True, False])
    )


def lead_lag_analysis(data: pd.DataFrame, scorecard: pd.DataFrame) -> pd.DataFrame:
    rec = recommended_windows(scorecard).groupby("feature_group", as_index=False).head(1)
    rows: list[dict[str, object]] = []
    for _, rec_row in rec.iterrows():
        group = rec_row["feature_group"]
        window = int(str(rec_row["window"]).replace("W", ""))
        feature_name = feature_column(str(group), window)
        for horizon in [4, 8]:
            return_col = f"gold_return_{horizon}w"
            for lag in LAGS:
                shifted = data[feature_name].shift(lag)
                valid = pd.concat([shifted, data[return_col]], axis=1).dropna()
                corr = corr_pair(shifted, data[return_col], "pearson")
                rank = corr_pair(shifted, data[return_col], "spearman")
                rows.append(
                    {
                        "feature_group": group,
                        "recommended_window": f"{window}W",
                        "feature_name": feature_name,
                        "gold_horizon": f"{horizon}W",
                        "lag_weeks": lag,
                        "correlation": corr,
                        "rank_correlation": rank,
                        "sample_count": int(len(valid)),
                    }
                )
    return pd.DataFrame(rows)


def write_outputs(bundle: DiscoveryBundle) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    bundle.dataset.to_csv(WINDOW_DATASET_PATH, index=False)
    bundle.scorecard.to_csv(SCORECARD_PATH, index=False)
    bundle.bucket_analysis.to_csv(BUCKET_ANALYSIS_PATH, index=False)
    bundle.train_test.to_csv(TRAIN_TEST_PATH, index=False)
    write_charts(bundle)
    write_summary(bundle)


def plot_velocity_windows(data: pd.DataFrame, group: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 6))
    for window in WINDOWS:
        column = feature_column(group, window)
        ax.plot(data["date"], data[column] * 100, label=f"{window}W", linewidth=1.2)
    ax.axhline(0, color="#111827", linewidth=1)
    ax.set_title(f"MM {group.title()} Velocity Windows")
    ax.set_ylabel("Percentile point change")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


def write_charts(bundle: DiscoveryBundle) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    scorecard = bundle.scorecard.copy()

    summary = (
        scorecard[scorecard["horizon"].isin(["4W", "8W"])]
        .groupby(["feature_group", "window"], as_index=False)["total_score"]
        .mean()
    )
    fig, ax = plt.subplots(figsize=(12, 6))
    for group, frame in summary.groupby("feature_group", sort=False):
        ordered = frame.sort_values("window", key=lambda s: s.str.replace("W", "").astype(int))
        ax.plot(ordered["window"], ordered["total_score"], marker="o", label=group.title())
    ax.set_title("MM Velocity Window Total Score")
    ax.set_ylabel("Average total score (4W/8W horizons)")
    ax.set_xlabel("Window")
    ax.legend()
    fig.tight_layout()
    fig.savefig(SCORECARD_CHART, dpi=170)
    plt.close(fig)

    plot_velocity_windows(bundle.dataset, "long", LONG_WINDOWS_CHART)
    plot_velocity_windows(bundle.dataset, "short", SHORT_WINDOWS_CHART)
    plot_velocity_windows(bundle.dataset, "net", NET_WINDOWS_CHART)

    eight = scorecard[scorecard["horizon"] == "8W"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for ax, metric, title in [
        (axes[0], "rank_correlation", "Rank correlation vs 8W following return"),
        (axes[1], "high_low_spread", "High-low median spread vs 8W following return"),
    ]:
        for group, frame in eight.groupby("feature_group", sort=False):
            ordered = frame.sort_values("window", key=lambda s: s.str.replace("W", "").astype(int))
            ax.plot(ordered["window"], ordered[metric], marker="o", label=group.title())
        ax.axhline(0, color="#111827", linewidth=1)
        ax.set_title(title)
        ax.set_xlabel("Window")
    axes[0].set_ylabel("Value")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(FORWARD_8W_CHART, dpi=170)
    plt.close(fig)

    if not bundle.lead_lag.empty:
        fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
        for ax, horizon in zip(axes, ["4W", "8W"]):
            sample = bundle.lead_lag[bundle.lead_lag["gold_horizon"] == horizon]
            for group, frame in sample.groupby("feature_group", sort=False):
                ordered = frame.sort_values("lag_weeks")
                label = f"{group.title()} {ordered['recommended_window'].iloc[0]}"
                ax.plot(ordered["lag_weeks"], ordered["rank_correlation"], marker="o", label=label)
            ax.axhline(0, color="#111827", linewidth=1)
            ax.set_title(f"Gold {horizon} following return")
            ax.set_xlabel("Lag weeks")
        axes[0].set_ylabel("Rank correlation")
        axes[1].legend(fontsize=8)
        fig.suptitle("MM Velocity Window Lead-Lag")
        fig.tight_layout()
        fig.savefig(LEAD_LAG_CHART, dpi=170)
        plt.close(fig)


def best_window_for_group(scorecard: pd.DataFrame, group: str) -> pd.Series | None:
    rec = recommended_windows(scorecard)
    rows = rec[rec["feature_group"] == group]
    if rows.empty:
        return None
    return rows.iloc[0]


def best_for_horizon(scorecard: pd.DataFrame, horizon: str) -> pd.Series | None:
    rows = (
        scorecard[scorecard["horizon"] == horizon]
        .groupby(["feature_group", "window"], as_index=False)
        .agg(avg_information_score=("information_score", "mean"), avg_total_score=("total_score", "mean"))
        .sort_values("avg_information_score", ascending=False)
    )
    if rows.empty:
        return None
    return rows.iloc[0]


def most_stable_window(scorecard: pd.DataFrame) -> pd.Series | None:
    rows = (
        scorecard.groupby(["feature_group", "window"], as_index=False)
        .agg(avg_stability_score=("stability_score", "mean"), weekly_change_avg=("weekly_change_avg", "mean"))
        .sort_values("avg_stability_score", ascending=False)
    )
    if rows.empty:
        return None
    return rows.iloc[0]


def write_summary(bundle: DiscoveryBundle) -> None:
    scorecard = bundle.scorecard
    rec = recommended_windows(scorecard)
    long_best = best_window_for_group(scorecard, "long")
    short_best = best_window_for_group(scorecard, "short")
    net_best = best_window_for_group(scorecard, "net")
    stable = most_stable_window(scorecard)
    best_4w = best_for_horizon(scorecard, "4W")
    best_8w = best_for_horizon(scorecard, "8W")
    eight_score = (
        rec[rec["window"] == "8W"]["avg_total_score"].mean()
        if not rec[rec["window"] == "8W"].empty
        else np.nan
    )
    best_overall = rec.sort_values("avg_total_score", ascending=False).iloc[0]
    keep_8w = pd.notna(eight_score) and eight_score >= best_overall["avg_total_score"] * 0.90

    lines = [
        "# GHPR v0.6.2 MM Velocity Window Discovery",
        "",
        "Historical structure research only. Not a trading signal. Not financial advice.",
        "",
        "## Executive Summary",
        "",
        f"- Data period: `{bundle.dataset['date'].min().strftime('%Y-%m-%d')}` to `{bundle.dataset['date'].max().strftime('%Y-%m-%d')}`.",
        f"- Best Long velocity window: `{long_best['window'] if long_best is not None else 'N/A'}`.",
        f"- Best Short velocity window: `{short_best['window'] if short_best is not None else 'N/A'}`.",
        f"- Best Net velocity window: `{net_best['window'] if net_best is not None else 'N/A'}`.",
        f"- Most stable feature/window: `{stable['feature_group']} {stable['window']}` with average stability score `{fmt_num(stable['avg_stability_score'], 1)}`." if stable is not None else "- Most stable feature/window: `N/A`.",
        f"- Best 4W information row: `{best_4w['feature_group']} {best_4w['window']}`." if best_4w is not None else "- Best 4W information row: `N/A`.",
        f"- Best 8W information row: `{best_8w['feature_group']} {best_8w['window']}`." if best_8w is not None else "- Best 8W information row: `N/A`.",
        f"- Current 8W decision: `{'keep as dashboard baseline for now' if keep_8w else 'review alternative window before replacing anything'}`.",
        "",
        "## Required Questions",
        "",
        "### 1. Why not assume 8W is best?",
        "",
        "8W is a reasonable swing window, but it is a design choice. A shorter window can react faster, while a longer window can reduce noise. This audit compares information, stability, train/test consistency, and interpretability before making any dashboard recommendation.",
        "",
        "### 2. What market rhythm do 2W / 4W / 8W / 12W / 26W represent?",
        "",
        "- 2W: very short-term positioning movement; responsive but noisy.",
        "- 4W: short-term velocity; useful for faster shifts.",
        "- 8W: swing velocity; current GHPR baseline.",
        "- 12W: medium swing velocity; slower but often more stable than 4W.",
        "- 26W: medium-term positioning cycle; more stable but slower to react.",
        "",
        "### 3. Long Velocity best window",
        "",
        f"`{long_best['window'] if long_best is not None else 'N/A'}` based on average 4W/8W total score.",
        "",
        "### 4. Short Velocity best window",
        "",
        f"`{short_best['window'] if short_best is not None else 'N/A'}` based on average 4W/8W total score.",
        "",
        "### 5. Net Velocity best window",
        "",
        f"`{net_best['window'] if net_best is not None else 'N/A'}` based on average 4W/8W total score.",
        "",
        "### 6. Most stable window",
        "",
        f"`{stable['feature_group']} {stable['window']}` has the highest stability score among feature/window pairs." if stable is not None else "N/A.",
        "",
        "### 7. Best information for 4W following return",
        "",
        f"`{best_4w['feature_group']} {best_4w['window']}` has the highest information score for 4W." if best_4w is not None else "N/A.",
        "",
        "### 8. Best information for 8W following return",
        "",
        f"`{best_8w['feature_group']} {best_8w['window']}` has the highest information score for 8W." if best_8w is not None else "N/A.",
        "",
        "### 9. Train / Test consistency",
        "",
        f"Direction consistency rate: `{fmt_pct(bundle.train_test['direction_consistency'].mean())}` across all feature/window/horizon rows.",
        "",
        "### 10. Should the Dashboard continue using 8W?",
        "",
        "Do not replace the current 8W dashboard definition yet. If 8W remains near the top score, keep it as the baseline while reviewing this report. If an alternative clearly dominates, treat it as a v0.6.3 candidate rather than an automatic replacement.",
        "",
        "### 11. If not 8W, should it be 4W / 12W / 26W?",
        "",
        f"The strongest overall candidate in this audit is `{best_overall['feature_group']} {best_overall['window']}`. A formal replacement should wait for human review because each window captures a different market rhythm.",
        "",
        "### 12. Should future Dashboard show short-term, swing, and medium-term velocity?",
        "",
        "Yes, as a research layer. A compact view with 4W short-term, 8W swing, and 12W or 26W medium-term velocity can show whether positioning movement is accelerating across time scales.",
        "",
        "### 13. Research limitations",
        "",
        "- This audit uses historical weekly data only.",
        "- It compares simple correlations, rank correlations, spreads, buckets, and train/test direction consistency.",
        "- It does not include Producer, OI, Options, OGR, or MMP.",
        "- It does not replace the existing dashboard definition.",
        "",
        "## Recommended Window Summary",
        "",
        rec.to_markdown(index=False),
        "",
        "## Top Scorecard Rows",
        "",
        scorecard.sort_values("total_score", ascending=False).head(20).to_markdown(index=False),
        "",
        "## Method Notes",
        "",
        "- Information Score: rank correlation strength plus high-low spread strength.",
        "- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.",
        "- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.",
        "- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.",
        "- Historical structure research only. Not a trading signal. Not financial advice.",
    ]
    SUMMARY_MD_PATH.write_text("\n".join(lines), encoding="utf-8")


def run_discovery() -> DiscoveryBundle:
    source = load_source_dataset()
    dataset = build_velocity_dataset(source)
    base_scorecard = information_scorecard(dataset)
    train_test = train_test_analysis(dataset)
    scorecard = add_final_scores(base_scorecard, train_test)
    bundle = DiscoveryBundle(
        dataset=dataset,
        scorecard=scorecard,
        bucket_analysis=bucket_analysis(dataset),
        train_test=train_test,
        lead_lag=lead_lag_analysis(dataset, scorecard),
    )
    write_outputs(bundle)
    return bundle


def main() -> int:
    bundle = run_discovery()
    print(f"Wrote velocity window dataset: {WINDOW_DATASET_PATH}")
    print(f"Wrote velocity window summary: {SUMMARY_MD_PATH}")
    print(f"Rows: {len(bundle.dataset)}")
    print("Scope: historical structure research only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

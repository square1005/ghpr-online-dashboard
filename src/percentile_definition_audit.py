"""Audit alternative percentile definitions for GHPR positioning factors.

This script compares percentile windows without assuming the current 156W
rolling definition is optimal. It is historical statistics only and does not
produce trading recommendations.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

try:
    from .utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT, PROCESSED_DIR
except ImportError:
    from utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT, PROCESSED_DIR


REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"
SUMMARY_CSV = REPORTS_DIR / "percentile_definition_audit_summary.csv"
DETAIL_CSV = REPORTS_DIR / "percentile_definition_audit_detail.csv"
INFORMATION_COMPARISON_CSV = REPORTS_DIR / "percentile_definition_information_comparison.csv"
BUCKET_ANALYSIS_CSV = REPORTS_DIR / "percentile_definition_bucket_analysis.csv"
TRAIN_TEST_CSV = REPORTS_DIR / "percentile_definition_train_test.csv"
SCORECARD_CSV = REPORTS_DIR / "percentile_definition_scorecard.csv"
RECOMMENDATION_CSV = REPORTS_DIR / "percentile_definition_recommendation.csv"
FEATURE_MATRIX_CSV = PROCESSED_DIR / "ghpr_percentile_definition_audit.csv"
FEATURE_MATRIX_REPORT_CSV = REPORTS_DIR / "percentile_definition_feature_matrix.csv"
AUDIT_DATASET_CSV = PROCESSED_DIR / "ghpr_percentile_audit_dataset.csv"
REPORT_MD = REPORTS_DIR / "percentile_definition_audit.md"
AUDIT_REPORT_MD = REPORTS_DIR / "percentile_definition_audit_report.md"
SCORE_CHART = CHARTS_DIR / "percentile_definition_score_heatmap.png"
INFO_CHART = CHARTS_DIR / "percentile_definition_information_score.png"
MM_WINDOW_CHART = CHARTS_DIR / "mm_percentile_window_comparison.png"
PRODUCER_WINDOW_CHART = CHARTS_DIR / "producer_percentile_window_comparison.png"
OI_WINDOW_CHART = CHARTS_DIR / "oi_percentile_window_comparison.png"
SCORECARD_CHART = CHARTS_DIR / "percentile_definition_scorecard.png"
MM_FORWARD_8W_CHART = CHARTS_DIR / "mm_52_104_156_260_vs_forward_8w.png"
PRODUCER_FORWARD_8W_CHART = CHARTS_DIR / "producer_52_104_156_260_vs_forward_8w.png"
OI_FORWARD_8W_CHART = CHARTS_DIR / "oi_52_104_156_260_vs_forward_8w.png"

MIN_PERIODS = 52
ROLLING_WINDOWS = [52, 104, 156, 260]
HORIZONS = [1, 2, 4, 8]
BUCKET_BINS = [i / 10 for i in range(11)]
BUCKET_LABELS = [f"{i * 10}-{(i + 1) * 10}" for i in range(10)]
SAMPLE_SPLITS = [
    ("train_2009_2018", pd.Timestamp("2009-09-01"), pd.Timestamp("2018-12-31")),
    ("test_2019_latest", pd.Timestamp("2019-01-01"), None),
]


@dataclass(frozen=True)
class FactorSpec:
    factor: str
    source_column: str
    output_prefix: str
    display_name: str


@dataclass(frozen=True)
class SignalDefinition:
    factor: str
    display_name: str
    definition: str
    definition_type: str
    window_weeks: int | None
    signal_column: str


FACTORS = [
    FactorSpec("mm_net", "mm_net", "mm_net", "MM Net"),
    FactorSpec("producer_net", "producer_net", "producer_net", "Producer Net"),
    FactorSpec("total_open_interest", "total_open_interest", "oi", "Total Open Interest"),
]


def load_master_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Master dataset not found: {path}")
    frame = pd.read_csv(path)
    if "total_open_interest" not in frame.columns and "futures_open_interest" in frame.columns:
        frame["total_open_interest"] = frame["futures_open_interest"]
    required = ["date", "gold_close", *(spec.source_column for spec in FACTORS)]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise KeyError(f"Master dataset is missing required columns: {missing}")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["gold_close"] = pd.to_numeric(frame["gold_close"], errors="coerce")
    for spec in FACTORS:
        frame[spec.source_column] = pd.to_numeric(frame[spec.source_column], errors="coerce")
    return frame.dropna(subset=["date", "gold_close"]).sort_values("date").reset_index(drop=True)


def rolling_percentile(series: pd.Series, window: int, min_periods: int = MIN_PERIODS) -> pd.Series:
    def percentile(values: pd.Series) -> float:
        clean = pd.Series(values).dropna()
        if clean.empty:
            return float("nan")
        current = clean.iloc[-1]
        return float((clean <= current).mean())

    return series.rolling(window=window, min_periods=min_periods).apply(percentile, raw=False)


def full_history_percentile(series: pd.Series) -> pd.Series:
    clean = series.dropna()
    if clean.empty:
        return pd.Series(float("nan"), index=series.index)
    ranks = clean.rank(method="average", pct=True)
    return ranks.reindex(series.index)


def rolling_zscore(series: pd.Series, window: int, min_periods: int = MIN_PERIODS) -> pd.Series:
    mean = series.rolling(window=window, min_periods=min_periods).mean()
    std = series.rolling(window=window, min_periods=min_periods).std()
    return (series - mean) / std.where(std != 0)


def percentile_column_name(spec: FactorSpec, definition: str) -> str:
    if definition.startswith("rolling_"):
        window = definition.removeprefix("rolling_").removesuffix("w")
        return f"{spec.output_prefix}_percentile_{window}w"
    if definition == "full_history":
        return f"{spec.output_prefix}_percentile_full_history"
    raise ValueError(f"Unsupported percentile definition: {definition}")


def zscore_column_name(spec: FactorSpec, window: int) -> str:
    return f"{spec.output_prefix}_zscore_{window}w"


def build_percentile_definitions(master: pd.DataFrame) -> pd.DataFrame:
    data = master[["date", "gold_close", *(spec.source_column for spec in FACTORS)]].copy()
    for horizon in HORIZONS:
        data[f"gold_return_{horizon}w"] = data["gold_close"].shift(-horizon) / data["gold_close"] - 1

    for spec in FACTORS:
        source = data[spec.source_column]
        for window in ROLLING_WINDOWS:
            data[f"{spec.output_prefix}_percentile_{window}w"] = rolling_percentile(
                source, window=window
            )
            data[zscore_column_name(spec, window)] = rolling_zscore(source, window=window)
        data[f"{spec.output_prefix}_percentile_full_history"] = full_history_percentile(source)
    return data


def percentile_definition_specs() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for window in ROLLING_WINDOWS:
        rows.append(
            {
                "definition": f"rolling_{window}w",
                "window_weeks": window,
                "production_safe": True,
                "rolling_definition": True,
                "notes": f"Rolling percentile with {window} weekly observations and {MIN_PERIODS}W minimum data.",
            }
        )
    rows.append(
        {
            "definition": "full_history",
            "window_weeks": pd.NA,
            "production_safe": False,
            "rolling_definition": False,
            "notes": "Research benchmark only; not production-safe because it uses future observations.",
        }
    )
    return rows


def signal_definition_specs() -> list[SignalDefinition]:
    definitions: list[SignalDefinition] = []
    for spec in FACTORS:
        for window in ROLLING_WINDOWS:
            definitions.append(
                SignalDefinition(
                    factor=spec.factor,
                    display_name=spec.display_name,
                    definition=f"{window}W percentile",
                    definition_type="percentile",
                    window_weeks=window,
                    signal_column=f"{spec.output_prefix}_percentile_{window}w",
                )
            )
        definitions.append(
            SignalDefinition(
                factor=spec.factor,
                display_name=spec.display_name,
                definition="Full History percentile",
                definition_type="percentile",
                window_weeks=None,
                signal_column=f"{spec.output_prefix}_percentile_full_history",
            )
        )
        for window in ROLLING_WINDOWS:
            definitions.append(
                SignalDefinition(
                    factor=spec.factor,
                    display_name=spec.display_name,
                    definition=f"{window}W zscore",
                    definition_type="zscore",
                    window_weeks=window,
                    signal_column=zscore_column_name(spec, window),
                )
            )
    return definitions


def assign_signal_buckets(series: pd.Series, definition_type: str) -> pd.Series:
    if definition_type == "percentile":
        return assign_decile(series)
    clean = series.dropna()
    if clean.nunique() < 2:
        return pd.Series(pd.NA, index=series.index, dtype="object")
    try:
        bucket_numbers = pd.qcut(
            clean.rank(method="first"),
            q=10,
            labels=False,
            duplicates="drop",
        )
    except ValueError:
        return pd.Series(pd.NA, index=series.index, dtype="object")
    bucket_labels = bucket_numbers.map(lambda value: BUCKET_LABELS[int(value)] if pd.notna(value) else pd.NA)
    return bucket_labels.reindex(series.index)


def assign_rank_buckets(series: pd.Series) -> pd.Series:
    clean = series.dropna()
    if clean.nunique() < 2:
        return pd.Series(pd.NA, index=series.index, dtype="object")
    try:
        bucket_numbers = pd.qcut(
            clean.rank(method="first"),
            q=10,
            labels=False,
            duplicates="drop",
        )
    except ValueError:
        return pd.Series(pd.NA, index=series.index, dtype="object")
    bucket_labels = bucket_numbers.map(lambda value: BUCKET_LABELS[int(value)] if pd.notna(value) else pd.NA)
    return bucket_labels.reindex(series.index)


def compare_information_content(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    total_count = len(data)
    for signal in signal_definition_specs():
        if signal.signal_column not in data.columns:
            continue
        for horizon in HORIZONS:
            return_col = f"gold_return_{horizon}w"
            frame = data[[signal.signal_column, return_col]].copy()
            valid = frame.dropna(subset=[signal.signal_column, return_col])
            buckets = assign_signal_buckets(valid[signal.signal_column], signal.definition_type)
            bucket_means = valid.groupby(buckets, observed=False)[return_col].mean()
            nonempty_means = bucket_means.dropna()
            low = valid[buckets == BUCKET_LABELS[0]][return_col].dropna()
            high = valid[buckets == BUCKET_LABELS[-1]][return_col].dropna()

            rows.append(
                {
                    "factor": signal.factor,
                    "display_name": signal.display_name,
                    "definition": signal.definition,
                    "definition_type": signal.definition_type,
                    "window_weeks": signal.window_weeks,
                    "signal_column": signal.signal_column,
                    "horizon": f"{horizon}W",
                    "return_column": return_col,
                    "rank_corr": valid[signal.signal_column].corr(valid[return_col], method="spearman")
                    if len(valid) >= 3
                    else pd.NA,
                    "high_low_spread": high.mean() - low.mean() if len(high) and len(low) else pd.NA,
                    "bucket_monotonicity_score": decile_monotonicity(nonempty_means),
                    "positive_bucket_count": int((nonempty_means > 0).sum()),
                    "negative_bucket_count": int((nonempty_means < 0).sum()),
                    "sample_count": int(len(valid)),
                    "missing_count": int(total_count - len(valid)),
                }
            )
    return pd.DataFrame(rows)


def max_drawdown_after_signal(price: pd.Series, horizon: int) -> pd.Series:
    prices = price.reset_index(drop=True)
    drawdowns = []
    for idx in range(len(prices)):
        window = prices.iloc[idx : idx + horizon + 1].dropna()
        if len(window) < horizon + 1:
            drawdowns.append(pd.NA)
            continue
        running_peak = window.cummax()
        drawdown = window / running_peak - 1
        drawdowns.append(drawdown.min())
    return pd.Series(drawdowns, index=price.index)


def run_bucket_analysis(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    percentile_signals = [
        signal for signal in signal_definition_specs() if signal.definition_type == "percentile"
    ]
    for signal in percentile_signals:
        if signal.signal_column not in data.columns:
            continue
        for horizon in HORIZONS:
            return_col = f"gold_return_{horizon}w"
            frame = data[["date", "gold_close", signal.signal_column, return_col]].copy()
            frame["percentile_bucket"] = assign_decile(frame[signal.signal_column])
            frame["max_drawdown_after_signal"] = max_drawdown_after_signal(
                frame["gold_close"], horizon
            )
            valid = frame.dropna(
                subset=[signal.signal_column, return_col, "max_drawdown_after_signal"]
            )
            for bucket in BUCKET_LABELS:
                group = valid[valid["percentile_bucket"] == bucket]
                rows.append(
                    {
                        "factor": signal.factor,
                        "display_name": signal.display_name,
                        "definition": signal.definition,
                        "definition_type": signal.definition_type,
                        "window_weeks": signal.window_weeks,
                        "signal_column": signal.signal_column,
                        "forward_horizon": f"{horizon}W",
                        "return_column": return_col,
                        "percentile_bucket": bucket,
                        "count": int(len(group)),
                        "avg_forward_return": group[return_col].mean(),
                        "median_forward_return": group[return_col].median(),
                        "win_rate": (group[return_col] > 0).mean() if len(group) else pd.NA,
                        "best_return": group[return_col].max() if len(group) else pd.NA,
                        "worst_return": group[return_col].min() if len(group) else pd.NA,
                        "max_drawdown_after_signal": group["max_drawdown_after_signal"].min()
                        if len(group)
                        else pd.NA,
                    }
                )
    return pd.DataFrame(rows)


def split_frame(data: pd.DataFrame, start_date: pd.Timestamp, end_date: pd.Timestamp | None) -> pd.DataFrame:
    if end_date is None:
        split = data[data["date"] >= start_date].copy()
    else:
        split = data[(data["date"] >= start_date) & (data["date"] <= end_date)].copy()
    return split.sort_values("date").reset_index(drop=True)


def analyze_split_signal_horizon(
    split: pd.DataFrame,
    signal: SignalDefinition,
    horizon: int,
) -> dict[str, object]:
    return_col = f"gold_return_{horizon}w"
    frame = split[["date", "gold_close", signal.signal_column]].copy()
    frame[return_col] = frame["gold_close"].shift(-horizon) / frame["gold_close"] - 1
    valid = frame.dropna(subset=[signal.signal_column, return_col])
    buckets = assign_rank_buckets(valid[signal.signal_column])
    bucket_means = valid.groupby(buckets, observed=False)[return_col].mean()
    nonempty_means = bucket_means.dropna()
    low = valid[buckets == BUCKET_LABELS[0]][return_col].dropna()
    high = valid[buckets == BUCKET_LABELS[-1]][return_col].dropna()
    rank_corr = (
        valid[signal.signal_column].corr(valid[return_col], method="spearman")
        if len(valid) >= 3
        else pd.NA
    )
    return {
        "return_column": return_col,
        "rank_corr": rank_corr,
        "high_low_spread": high.mean() - low.mean() if len(high) and len(low) else pd.NA,
        "bucket_monotonicity_score": decile_monotonicity(nonempty_means),
        "win_rate_extreme_high": (high > 0).mean() if len(high) else pd.NA,
        "win_rate_extreme_low": (low > 0).mean() if len(low) else pd.NA,
        "avg_return_extreme_high": high.mean() if len(high) else pd.NA,
        "avg_return_extreme_low": low.mean() if len(low) else pd.NA,
        "extreme_high_count": int(len(high)),
        "extreme_low_count": int(len(low)),
        "sample_count": int(len(valid)),
        "missing_count": int(len(split) - len(valid)),
    }


def run_train_test_validation(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    signals = signal_definition_specs()
    for split_name, start_date, end_date in SAMPLE_SPLITS:
        split = split_frame(data, start_date, end_date)
        if split.empty:
            continue

        actual_start = split["date"].min()
        actual_end = split["date"].max()
        for signal in signals:
            if signal.signal_column not in split.columns:
                continue
            for horizon in HORIZONS:
                metrics = analyze_split_signal_horizon(split, signal, horizon)
                rows.append(
                    {
                        "sample_split": split_name,
                        "split_start": actual_start.strftime("%Y-%m-%d"),
                        "split_end": actual_end.strftime("%Y-%m-%d"),
                        "factor": signal.factor,
                        "display_name": signal.display_name,
                        "definition": signal.definition,
                        "definition_type": signal.definition_type,
                        "window_weeks": signal.window_weeks,
                        "signal_column": signal.signal_column,
                        "extreme_bucket_method": "split_rank_decile",
                        "horizon": f"{horizon}W",
                        **metrics,
                    }
                )
    return pd.DataFrame(rows)


def sign_score(train_value: object, test_value: object) -> tuple[float, str]:
    train_sign = value_sign(train_value)
    test_sign = value_sign(test_value)
    if train_sign == 0 or test_sign == 0:
        return 50.0, "neutral_or_insufficient_spread"
    if train_sign == test_sign:
        return 100.0, "consistent_spread_sign"
    return 0.0, "opposite_spread_sign"


def value_sign(value: object) -> int:
    if pd.isna(value):
        return 0
    number = float(value)
    if abs(number) < 1e-12:
        return 0
    return 1 if number > 0 else -1


def rank_corr_score(value: object) -> float:
    if pd.isna(value):
        return 0.0
    return min(abs(float(value)) / 0.10, 1.0) * 100.0


def monotonicity_score(value: object) -> float:
    if pd.isna(value):
        return 0.0
    return min(abs(float(value)), 1.0) * 100.0


def coverage_score(sample_count: object, missing_count: object) -> float:
    sample = 0 if pd.isna(sample_count) else float(sample_count)
    missing = 0 if pd.isna(missing_count) else float(missing_count)
    total = sample + missing
    if total <= 0:
        return 0.0
    return sample / total * 100.0


def interpretability_score(signal: SignalDefinition) -> float:
    if signal.definition == "Full History percentile":
        return 60.0
    if signal.definition_type == "percentile":
        return 100.0
    if signal.definition_type == "zscore":
        return 75.0
    return 50.0


def split_quality_score(metrics: dict[str, object], interpretability: float) -> float:
    numerator = (
        25.0 * rank_corr_score(metrics["rank_corr"])
        + 20.0 * monotonicity_score(metrics["bucket_monotonicity_score"])
        + 15.0 * coverage_score(metrics["sample_count"], metrics["missing_count"])
        + 10.0 * interpretability
    )
    return numerator / 70.0


def build_definition_scorecard(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    splits = {name: split_frame(data, start, end) for name, start, end in SAMPLE_SPLITS}
    for signal in signal_definition_specs():
        if any(signal.signal_column not in split.columns for split in splits.values()):
            continue
        for horizon in HORIZONS:
            train_metrics = analyze_split_signal_horizon(
                splits["train_2009_2018"], signal, horizon
            )
            test_metrics = analyze_split_signal_horizon(
                splits["test_2019_latest"], signal, horizon
            )
            consistency, consistency_label = sign_score(
                train_metrics["high_low_spread"], test_metrics["high_low_spread"]
            )
            train_rank = rank_corr_score(train_metrics["rank_corr"])
            test_rank = rank_corr_score(test_metrics["rank_corr"])
            train_monotonicity = monotonicity_score(train_metrics["bucket_monotonicity_score"])
            test_monotonicity = monotonicity_score(test_metrics["bucket_monotonicity_score"])
            train_coverage = coverage_score(
                train_metrics["sample_count"], train_metrics["missing_count"]
            )
            test_coverage = coverage_score(
                test_metrics["sample_count"], test_metrics["missing_count"]
            )
            interpretability = interpretability_score(signal)
            train_score = split_quality_score(train_metrics, interpretability)
            test_score = split_quality_score(test_metrics, interpretability)
            stability_score = (
                0.30 * consistency
                + 0.25 * ((train_rank + test_rank) / 2.0)
                + 0.20 * ((train_monotonicity + test_monotonicity) / 2.0)
                + 0.15 * ((train_coverage + test_coverage) / 2.0)
                + 0.10 * interpretability
            )
            rows.append(
                {
                    "factor": factor_label(signal.factor),
                    "definition": signal.definition,
                    "horizon": f"{horizon}W",
                    "train_score": round(train_score, 2),
                    "test_score": round(test_score, 2),
                    "stability_score": round(stability_score, 2),
                    "recommended": False,
                    "reason": scorecard_reason(
                        signal,
                        consistency_label,
                        stability_score,
                        recommended=False,
                    ),
                    "_eligible": signal.definition != "Full History percentile",
                }
            )

    scorecard = pd.DataFrame(rows)
    if scorecard.empty:
        return scorecard.drop(columns=["_eligible"], errors="ignore")
    for (_factor, _horizon), group in scorecard.groupby(["factor", "horizon"], sort=False):
        eligible = group[group["_eligible"]]
        if eligible.empty:
            continue
        best_index = eligible["stability_score"].astype(float).idxmax()
        signal = signal_from_scorecard_row(scorecard.loc[best_index])
        scorecard.loc[best_index, "recommended"] = True
        scorecard.loc[best_index, "reason"] = scorecard_reason(
            signal,
            "selected_top_score",
            float(scorecard.loc[best_index, "stability_score"]),
            recommended=True,
        )
    return scorecard[
        [
            "factor",
            "definition",
            "horizon",
            "train_score",
            "test_score",
            "stability_score",
            "recommended",
            "reason",
        ]
    ].sort_values(["factor", "horizon", "stability_score"], ascending=[True, True, False])


def factor_label(factor: str) -> str:
    labels = {
        "mm_net": "MM",
        "producer_net": "Producer",
        "total_open_interest": "OI",
    }
    return labels.get(factor, factor)


def signal_from_scorecard_row(row: pd.Series) -> SignalDefinition:
    factor_lookup = {"MM": "mm_net", "Producer": "producer_net", "OI": "total_open_interest"}
    factor = factor_lookup.get(str(row["factor"]), str(row["factor"]))
    for signal in signal_definition_specs():
        if factor_label(signal.factor) == row["factor"] and signal.definition == row["definition"]:
            return signal
    return SignalDefinition(
        factor=factor,
        display_name=str(row["factor"]),
        definition=str(row["definition"]),
        definition_type="unknown",
        window_weeks=None,
        signal_column="",
    )


def scorecard_reason(
    signal: SignalDefinition,
    consistency_label: str,
    stability_score: float,
    recommended: bool,
) -> str:
    if signal.definition == "Full History percentile":
        return (
            "Research benchmark only; full-history ordering uses the whole sample, "
            f"stability score {stability_score:.1f}."
        )
    if recommended:
        return (
            "Top production-eligible score for this factor/horizon; "
            f"stability score {stability_score:.1f}."
        )
    return (
        f"Not the top production-eligible score for this factor/horizon; "
        f"{consistency_label}; stability score {stability_score:.1f}."
    )


def audit_definitions(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    definition_specs = percentile_definition_specs()
    stability_rows = []
    detail_rows = []

    for spec in FACTORS:
        for definition_spec in definition_specs:
            definition = str(definition_spec["definition"])
            pct_col = percentile_column_name(spec, definition)
            if pct_col not in data.columns:
                continue

            pct = data[pct_col]
            stability_rows.append(
                {
                    "factor": spec.factor,
                    "display_name": spec.display_name,
                    "definition": definition,
                    "window_weeks": definition_spec["window_weeks"],
                    "production_safe": definition_spec["production_safe"],
                    "rolling_definition": definition_spec["rolling_definition"],
                    "coverage": pct.notna().mean(),
                    "valid_observations": int(pct.notna().sum()),
                    "median_abs_weekly_change": pct.diff().abs().median(),
                    "p95_abs_weekly_change": pct.diff().abs().quantile(0.95),
                    "std_weekly_change": pct.diff().std(),
                    "effective_decile_count": int(assign_decile(pct).nunique(dropna=True)),
                    "definition_note": definition_spec["notes"],
                }
            )

            for horizon in HORIZONS:
                detail_rows.append(
                    analyze_definition_horizon(
                        data,
                        factor=spec.factor,
                        display_name=spec.display_name,
                        definition=definition,
                        pct_col=pct_col,
                        horizon=horizon,
                    )
                )

    stability = pd.DataFrame(stability_rows)
    detail = pd.DataFrame(detail_rows)
    detail = add_information_scores(detail)
    summary = build_summary(stability, detail)
    recommendations = build_recommendations(summary)
    return summary, detail, recommendations


def analyze_definition_horizon(
    data: pd.DataFrame,
    factor: str,
    display_name: str,
    definition: str,
    pct_col: str,
    horizon: int,
) -> dict[str, object]:
    return_col = f"gold_return_{horizon}w"
    frame = data[["date", pct_col, return_col]].copy()
    frame = frame.dropna(subset=[pct_col, return_col])
    decile = assign_decile(frame[pct_col])
    bucket_means = frame.groupby(decile, observed=False)[return_col].mean()
    bucket_counts = frame.groupby(decile, observed=False)[return_col].count()
    nonempty_means = bucket_means.dropna()

    low = frame[decile == BUCKET_LABELS[0]][return_col].dropna()
    high = frame[decile == BUCKET_LABELS[-1]][return_col].dropna()
    tail_spread = high.mean() - low.mean() if len(high) and len(low) else pd.NA
    tail_tstat = two_sample_tstat(high, low)

    return {
        "factor": factor,
        "display_name": display_name,
        "definition": definition,
        "horizon": f"{horizon}W",
        "sample_count": int(len(frame)),
        "spearman_ic": frame[pct_col].corr(frame[return_col], method="spearman")
        if len(frame) >= 3
        else pd.NA,
        "pearson_ic": frame[pct_col].corr(frame[return_col], method="pearson")
        if len(frame) >= 3
        else pd.NA,
        "decile_monotonicity": decile_monotonicity(nonempty_means),
        "tail_spread_top_minus_bottom": tail_spread,
        "tail_spread_tstat": tail_tstat,
        "nonempty_deciles": int(bucket_counts[bucket_counts > 0].count()),
        "bottom_decile_count": int(len(low)),
        "top_decile_count": int(len(high)),
        "bottom_decile_avg_return": low.mean() if len(low) else pd.NA,
        "top_decile_avg_return": high.mean() if len(high) else pd.NA,
    }


def assign_decile(series: pd.Series) -> pd.Series:
    clipped = series.clip(lower=0, upper=1)
    return pd.cut(clipped, bins=BUCKET_BINS, labels=BUCKET_LABELS, include_lowest=True, right=True)


def decile_monotonicity(bucket_means: pd.Series) -> float | pd._libs.missing.NAType:
    if len(bucket_means) < 4:
        return pd.NA
    decile_numbers = pd.Series(range(len(bucket_means)), index=bucket_means.index)
    return decile_numbers.corr(bucket_means, method="spearman")


def two_sample_tstat(high: pd.Series, low: pd.Series) -> float | pd._libs.missing.NAType:
    if len(high) < 2 or len(low) < 2:
        return pd.NA
    variance = high.var(ddof=1) / len(high) + low.var(ddof=1) / len(low)
    if pd.isna(variance) or variance == 0:
        return pd.NA
    return float((high.mean() - low.mean()) / variance**0.5)


def add_information_scores(detail: pd.DataFrame) -> pd.DataFrame:
    detail = detail.copy()
    for column in ["spearman_ic", "decile_monotonicity", "tail_spread_tstat"]:
        detail[f"abs_{column}"] = detail[column].abs()
    score_parts = []
    for (_factor, _horizon), group in detail.groupby(["factor", "horizon"], sort=False):
        scored = group.copy()
        for source_col in [
            "abs_spearman_ic",
            "abs_decile_monotonicity",
            "abs_tail_spread_tstat",
            "sample_count",
            "nonempty_deciles",
        ]:
            scored[f"{source_col}_rank"] = scored[source_col].rank(pct=True, ascending=True)
        scored["information_score"] = scored[
            [
                "abs_spearman_ic_rank",
                "abs_decile_monotonicity_rank",
                "abs_tail_spread_tstat_rank",
                "sample_count_rank",
                "nonempty_deciles_rank",
            ]
        ].mean(axis=1)
        score_parts.append(scored)
    return pd.concat(score_parts, ignore_index=True)


def build_summary(stability: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (factor, definition), group in detail.groupby(["factor", "definition"], sort=False):
        stability_row = stability[
            (stability["factor"] == factor) & (stability["definition"] == definition)
        ].iloc[0]
        horizon_scores = {
            f"information_score_{horizon}w": group.loc[
                group["horizon"] == f"{horizon}W", "information_score"
            ].mean()
            for horizon in HORIZONS
        }
        all_horizon_score = pd.Series(horizon_scores).mean()
        long_horizon_score = pd.Series(
            {
                "information_score_4w": horizon_scores["information_score_4w"],
                "information_score_8w": horizon_scores["information_score_8w"],
            }
        ).mean()
        rows.append(
            {
                **stability_row.to_dict(),
                **horizon_scores,
                "information_score_mean_all_horizons": all_horizon_score,
                "information_score_mean_4w_8w": long_horizon_score,
                "mean_abs_spearman_all_horizons": group["abs_spearman_ic"].mean(),
                "mean_abs_decile_monotonicity_all_horizons": group[
                    "abs_decile_monotonicity"
                ].mean(),
                "mean_abs_tail_tstat_all_horizons": group["abs_tail_spread_tstat"].mean(),
            }
        )

    summary = pd.DataFrame(rows)
    parts = []
    for _factor, group in summary.groupby("factor", sort=False):
        scored = group.copy()
        scored["coverage_rank"] = scored["coverage"].rank(pct=True, ascending=True)
        scored["decile_count_rank"] = scored["effective_decile_count"].rank(pct=True, ascending=True)
        scored["median_change_rank"] = scored["median_abs_weekly_change"].rank(pct=True, ascending=False)
        scored["p95_change_rank"] = scored["p95_abs_weekly_change"].rank(pct=True, ascending=False)
        scored["stability_score"] = scored[
            ["coverage_rank", "decile_count_rank", "median_change_rank", "p95_change_rank"]
        ].mean(axis=1)
        scored["overall_score"] = scored[
            ["stability_score", "information_score_mean_all_horizons", "information_score_mean_4w_8w"]
        ].mean(axis=1)
        parts.append(scored)
    return pd.concat(parts, ignore_index=True).sort_values(
        ["factor", "overall_score"], ascending=[True, False]
    )


def build_recommendations(summary: pd.DataFrame) -> pd.DataFrame:
    recommendations = []
    for factor, group in summary.groupby("factor", sort=False):
        safe = group[group["production_safe"]].copy()
        safe_rolling = safe[safe["rolling_definition"]].copy()
        best_safe = safe.sort_values("overall_score", ascending=False).iloc[0]
        best_rolling = safe_rolling.sort_values("overall_score", ascending=False).iloc[0]
        recommendations.append(
            {
                "factor": factor,
                "display_name": best_safe["display_name"],
                "formal_recommended_definition": best_rolling["definition"],
                "formal_policy": "factor_specific_rolling",
                "recommended_production_safe_definition": best_safe["definition"],
                "recommended_rolling_definition": best_rolling["definition"],
                "production_safe_overall_score": best_safe["overall_score"],
                "rolling_overall_score": best_rolling["overall_score"],
                "production_safe_note": best_safe["definition_note"],
                "rolling_note": best_rolling["definition_note"],
            }
        )

    recommendation_frame = pd.DataFrame(recommendations)
    unified = (
        summary[(summary["production_safe"]) & (summary["rolling_definition"])]
        .groupby("definition", as_index=False)["overall_score"]
        .mean()
        .sort_values("overall_score", ascending=False)
        .iloc[0]
    )
    recommendation_frame["recommended_unified_rolling_definition"] = unified["definition"]
    recommendation_frame["recommended_unified_rolling_score"] = unified["overall_score"]
    return recommendation_frame


def requested_feature_columns() -> list[str]:
    columns = ["date", "gold_close"]
    columns.extend(spec.source_column for spec in FACTORS)
    columns.extend(f"gold_return_{horizon}w" for horizon in HORIZONS)
    for spec in FACTORS:
        columns.extend(f"{spec.output_prefix}_percentile_{window}w" for window in ROLLING_WINDOWS)
        columns.append(f"{spec.output_prefix}_percentile_full_history")
    for spec in FACTORS:
        columns.extend(zscore_column_name(spec, window) for window in ROLLING_WINDOWS)
    return columns


def audit_dataset_columns(data: pd.DataFrame) -> list[str]:
    percentile_columns = [column for column in data.columns if "percentile" in column]
    zscore_columns = [column for column in data.columns if "zscore" in column]
    return [
        "date",
        "gold_close",
        *percentile_columns,
        *zscore_columns,
        *(f"gold_return_{horizon}w" for horizon in HORIZONS),
    ]


def write_feature_matrix(data: pd.DataFrame) -> None:
    columns = [column for column in requested_feature_columns() if column in data.columns]
    matrix = data[columns].copy()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(FEATURE_MATRIX_CSV, index=False)
    matrix.to_csv(FEATURE_MATRIX_REPORT_CSV, index=False)
    audit_columns = [column for column in audit_dataset_columns(data) if column in data.columns]
    data[audit_columns].to_csv(AUDIT_DATASET_CSV, index=False)


def write_outputs(
    data: pd.DataFrame,
    summary: pd.DataFrame,
    detail: pd.DataFrame,
    information_comparison: pd.DataFrame,
    bucket_analysis: pd.DataFrame,
    train_test: pd.DataFrame,
    scorecard: pd.DataFrame,
    recommendations: pd.DataFrame,
) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    write_feature_matrix(data)
    summary.to_csv(SUMMARY_CSV, index=False)
    detail.to_csv(DETAIL_CSV, index=False)
    information_comparison.to_csv(INFORMATION_COMPARISON_CSV, index=False)
    bucket_analysis.to_csv(BUCKET_ANALYSIS_CSV, index=False)
    train_test.to_csv(TRAIN_TEST_CSV, index=False)
    scorecard.to_csv(SCORECARD_CSV, index=False)
    recommendations.to_csv(RECOMMENDATION_CSV, index=False)
    write_markdown_report(summary, detail, recommendations, REPORT_MD)
    write_research_report(
        data,
        summary,
        information_comparison,
        train_test,
        scorecard,
        AUDIT_REPORT_MD,
    )
    write_score_chart(summary, SCORE_CHART)
    write_information_chart(summary, INFO_CHART)
    write_task_eight_charts(data, bucket_analysis, scorecard)


def write_markdown_report(
    summary: pd.DataFrame,
    detail: pd.DataFrame,
    recommendations: pd.DataFrame,
    output_path: Path,
) -> None:
    unified = recommendations["recommended_unified_rolling_definition"].iloc[0]
    factor_specific = ", ".join(
        f"{row.display_name}: `{row.formal_recommended_definition}`"
        for row in recommendations.itertuples(index=False)
    )
    period_start, period_end = master_period()
    lines = [
        "# GHPR v0.5 Percentile Definition Audit",
        "",
        "## Technical Summary",
        "",
        (
            f"- Recommended formal v0.5 policy: factor-specific rolling percentile definitions "
            f"({factor_specific}). This preserves the strongest measured window for each positioning input."
        ),
        (
            f"- If GHPR must keep one unified rolling window for product simplicity, use `{unified}`. "
            "This is the best average production-safe rolling definition across the three audited factors, "
            "but it sacrifices some factor-level information content."
        ),
        "- Full-history percentile is included only as a research benchmark and is not production-safe because it uses future observations.",
        "- Scores evaluate historical stability, all four forward horizons, and the 4W/8W long-horizon subset. This is historical statistics only, not a trading signal and not financial advice.",
        f"- Data period: `{period_start}` to `{period_end}` from `data/processed/ghpr_master_weekly.csv`.",
        "",
        "## Recommended Definitions",
        "",
        "| Factor | Recommended production-safe definition | Best rolling definition | Unified rolling recommendation |",
        "|---|---|---|---|",
    ]
    for row in recommendations.itertuples(index=False):
        lines.append(
            f"| {row.display_name} | `{row.recommended_production_safe_definition}` | "
            f"`{row.recommended_rolling_definition}` | `{row.recommended_unified_rolling_definition}` |"
        )

    lines.extend(
        [
            "",
            "## What Was Measured",
            "",
            "- Factors audited: `mm_net`, `producer_net`, and `total_open_interest`.",
            f"- Rolling definitions audited: {', '.join(f'`rolling_{window}w`' for window in ROLLING_WINDOWS)}.",
            "- Additional definition audited: `full_history`.",
            f"- Percentile audit dataset output: `{AUDIT_DATASET_CSV.relative_to(PROJECT_ROOT)}`.",
            f"- Feature matrix output: `{FEATURE_MATRIX_CSV.relative_to(PROJECT_ROOT)}`.",
            f"- Information comparison output: `{INFORMATION_COMPARISON_CSV.relative_to(PROJECT_ROOT)}`.",
            f"- Bucket analysis output: `{BUCKET_ANALYSIS_CSV.relative_to(PROJECT_ROOT)}`.",
            f"- Train/test validation output: `{TRAIN_TEST_CSV.relative_to(PROJECT_ROOT)}`.",
            f"- Definition stability scorecard output: `{SCORECARD_CSV.relative_to(PROJECT_ROOT)}`.",
            "- Feature matrix percentile fields use the same 0-1 scale as the existing GHPR master weekly percentile columns.",
            "- Forward outcomes audited: `gold_return_1w`, `gold_return_2w`, `gold_return_4w`, and `gold_return_8w`.",
            "- Audit note: the persisted master `gold_return_*` columns currently behave like trailing `pct_change` fields, so this script recomputes same-named forward outcome columns from `gold_close.shift(-h)` inside the audit dataframe.",
            f"- Rolling percentile minimum data requirement: `{MIN_PERIODS}` weekly observations.",
            "",
            "## Scoring Method",
            "",
            "- Stability score combines coverage, effective decile coverage, lower median weekly percentile change, and lower 95th percentile weekly change.",
            "- Information score combines absolute Spearman rank correlation, absolute decile monotonicity, absolute top-minus-bottom decile t-stat, sample count, and non-empty decile count.",
            "- Overall score is the equal-weight average of stability score, mean 1W/2W/4W/8W information score, and mean 4W/8W long-horizon information score.",
            "- Higher scores mean the definition was more useful under this audit framework; they do not imply a market direction.",
            "",
            "## Top Summary Rows",
            "",
            dataframe_to_markdown(
                summary[
                    [
                        "display_name",
                        "definition",
                        "production_safe",
                        "coverage",
                        "median_abs_weekly_change",
                        "information_score_mean_all_horizons",
                        "information_score_mean_4w_8w",
                        "overall_score",
                    ]
                ]
                .groupby("display_name", group_keys=False)
                .head(4)
            ),
            "",
            "## 1W / 2W / 4W / 8W Detail Leaders",
            "",
            dataframe_to_markdown(
                detail.sort_values(["factor", "horizon", "information_score"], ascending=[True, True, False])
                .groupby(["factor", "horizon"], group_keys=False)
                .head(3)[
                    [
                        "display_name",
                        "definition",
                        "horizon",
                        "sample_count",
                        "spearman_ic",
                        "decile_monotonicity",
                        "tail_spread_top_minus_bottom",
                        "tail_spread_tstat",
                        "information_score",
                    ]
                ]
            ),
            "",
            "## Formal GHPR Adoption Recommendation",
            "",
            (
                "Adopt factor-specific rolling percentile definitions for v0.5: "
                f"{factor_specific}. This is the strongest formal recommendation because MM, Producer, "
                "and OI do not share the same best information window."
            ),
            "",
            (
                f"If product simplicity requires a single unified window, use `{unified}` and document that "
                "it is a compromise definition. It improves cross-factor consistency but is not the strongest "
                "4W/8W information definition for every factor."
            ),
            "",
            "Keep the current 156W definition only if continuity with v0.4 dashboards is more important than the measured v0.5 audit score. The audit intentionally does not assume 156W is optimal.",
            "",
            "## Limitations And Robustness Notes",
            "",
            "- This audit is descriptive and diagnostic. It does not establish causality or produce a trading rule.",
            "- Full-history percentile is not eligible for production use because it uses future observations.",
            "- Higher stability can reduce responsiveness. Very long windows may look cleaner but can underreact to regime changes.",
            "- Forward returns use `gold_close`, currently a COMEX GC futures proxy aligned to the GHPR weekly dataset.",
            "- Window scores are sensitive to the selected scoring weights. The CSV outputs preserve raw metrics for alternate weighting.",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def master_period() -> tuple[str, str]:
    frame = pd.read_csv(OUTPUT_MASTER_WEEKLY, usecols=["date"])
    dates = pd.to_datetime(frame["date"], errors="coerce").dropna()
    return dates.min().strftime("%Y-%m-%d"), dates.max().strftime("%Y-%m-%d")


def dataframe_to_markdown(frame: pd.DataFrame) -> str:
    view = frame.copy()
    for column in view.columns:
        if pd.api.types.is_float_dtype(view[column]):
            view[column] = view[column].map(lambda value: "NA" if pd.isna(value) else f"{value:.4f}")
    return view.to_markdown(index=False)


def format_score(value: object) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.1f}"


def format_percent(value: object) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value) * 100:.2f}%"


def compact_definition_label(definition: str) -> str:
    return (
        definition.replace(" percentile", " percentile")
        .replace("Full History", "Full History")
        .strip()
    )


def scorecard_average(scorecard: pd.DataFrame, factor: str, definition: str, horizons: list[str] | None = None) -> float:
    subset = scorecard[(scorecard["factor"] == factor) & (scorecard["definition"] == definition)]
    if horizons is not None:
        subset = subset[subset["horizon"].isin(horizons)]
    if subset.empty:
        return float("nan")
    return float(subset["stability_score"].mean())


def top_scorecard_rows(scorecard: pd.DataFrame, factor: str, horizons: list[str] | None = None) -> pd.DataFrame:
    subset = scorecard[scorecard["factor"] == factor].copy()
    if horizons is not None:
        subset = subset[subset["horizon"].isin(horizons)]
    grouped = (
        subset.groupby("definition", as_index=False)
        .agg(
            avg_stability_score=("stability_score", "mean"),
            avg_train_score=("train_score", "mean"),
            avg_test_score=("test_score", "mean"),
            recommended_horizon_count=("recommended", "sum"),
        )
        .sort_values("avg_stability_score", ascending=False)
    )
    return grouped


def summary_score(summary: pd.DataFrame, display_name: str, definition: str, column: str) -> float:
    row = summary[(summary["display_name"] == display_name) & (summary["definition"] == definition)]
    if row.empty:
        return float("nan")
    return float(row.iloc[0][column])


def report_table(frame: pd.DataFrame) -> str:
    return dataframe_to_markdown(frame.reset_index(drop=True))


def write_research_report(
    data: pd.DataFrame,
    summary: pd.DataFrame,
    information_comparison: pd.DataFrame,
    train_test: pd.DataFrame,
    scorecard: pd.DataFrame,
    output_path: Path,
) -> None:
    period_start = data["date"].min().strftime("%Y-%m-%d")
    period_end = data["date"].max().strftime("%Y-%m-%d")
    latest = data.iloc[-1]
    mm_top = top_scorecard_rows(scorecard, "MM")
    producer_top = top_scorecard_rows(scorecard, "Producer")
    oi_top = top_scorecard_rows(scorecard, "OI")
    long_top = pd.concat(
        [
            top_scorecard_rows(scorecard, "MM", ["4W", "8W"]).assign(factor="MM"),
            top_scorecard_rows(scorecard, "Producer", ["4W", "8W"]).assign(factor="Producer"),
            top_scorecard_rows(scorecard, "OI", ["4W", "8W"]).assign(factor="OI"),
        ],
        ignore_index=True,
    )
    recommended = scorecard[scorecard["recommended"].astype(bool)].copy()
    recommended_view = recommended[
        ["factor", "horizon", "definition", "stability_score", "train_score", "test_score"]
    ].sort_values(["factor", "horizon"])

    mm_156_score = scorecard_average(scorecard, "MM", "156W percentile")
    producer_156_score = scorecard_average(scorecard, "Producer", "156W percentile")
    oi_156_score = scorecard_average(scorecard, "OI", "156W percentile")
    mm_260_score = scorecard_average(scorecard, "MM", "260W percentile")
    producer_104_score = scorecard_average(scorecard, "Producer", "104W percentile")
    producer_52z_score = scorecard_average(scorecard, "Producer", "52W zscore")
    oi_52_score = scorecard_average(scorecard, "OI", "52W percentile")

    full_history_summary = summary[summary["definition"] == "full_history"][
        ["display_name", "overall_score", "information_score_mean_4w_8w"]
    ].copy()
    full_history_summary["production_safe"] = "No"

    oi_signal_strength = information_comparison[
        information_comparison["display_name"] == "Total Open Interest"
    ].copy()
    oi_signal_strength = (
        oi_signal_strength.groupby(["definition", "definition_type"], as_index=False)
        .agg(
            avg_abs_rank_corr=("rank_corr", lambda values: values.abs().mean()),
            avg_abs_spread=("high_low_spread", lambda values: values.abs().mean()),
            avg_monotonicity=("bucket_monotonicity_score", lambda values: values.abs().mean()),
        )
        .sort_values("avg_abs_rank_corr", ascending=False)
        .head(5)
    )

    lines = [
        "# GHPR v0.5 Percentile Definition Audit Report",
        "",
        f"Data period: `{period_start}` to `{period_end}`.",
        f"Latest weekly row: `{latest['date'].strftime('%Y-%m-%d')}`.",
        "",
        "This report is historical statistics and research reference only. It is not a trading signal and not financial advice.",
        "",
        "## Executive Conclusion",
        "",
        (
            "- The current 156W rolling percentile is a reasonable continuity baseline, "
            "but the audit does not support treating it as the best universal definition."
        ),
        (
            "- Recommended dashboard policy: keep 156W as a legacy reference, "
            "but show factor-specific v0.5 primary definitions."
        ),
        (
            f"- MM primary: `260W percentile` for dashboard interpretability "
            f"(average score {format_score(mm_260_score)}); `260W zscore` is useful as a long-horizon support field."
        ),
        (
            f"- Producer production-safe primary: `156W percentile` "
            f"(average score {format_score(producer_156_score)}). `104W percentile` is useful for shorter-horizon "
            f"readability (average score {format_score(producer_104_score)}), and `52W zscore` "
            f"({format_score(producer_52z_score)}) should be tracked as a research companion."
        ),
        (
            f"- OI primary: `52W percentile` (average score {format_score(oi_52_score)}). "
            "OI should also show absolute level and change because OI has structural level effects."
        ),
        "",
        "## Scorecard Snapshot",
        "",
        "Recommended definition by factor and horizon:",
        "",
        report_table(recommended_view),
        "",
        "Average stability score by factor and definition, top rows:",
        "",
        report_table(
            pd.concat(
                [
                    mm_top.head(4).assign(factor="MM"),
                    producer_top.head(4).assign(factor="Producer"),
                    oi_top.head(4).assign(factor="OI"),
                ],
                ignore_index=True,
            )[
                [
                    "factor",
                    "definition",
                    "avg_stability_score",
                    "avg_train_score",
                    "avg_test_score",
                    "recommended_horizon_count",
                ]
            ]
        ),
        "",
        "## 1. GHPR 目前 156W rolling percentile 是什麼？",
        "",
        (
            "`156W rolling percentile` 是把當週的因子值放進最近 156 週觀察值中排序，"
            "計算它位於這段 rolling window 的百分位。GHPR 目前 dashboard 使用的 "
            "`mm_net_percentile_156w`、`producer_net_percentile_156w`、`oi_percentile_156w` "
            "就是這個定義。資料檔中 percentile 儲存為 0-1；dashboard 顯示時可轉成 0-100%。"
        ),
        "",
        "Example formula:",
        "",
        "`percentile_t = count(value_i <= value_t, i in t-155..t) / valid_count`",
        "",
        "## 2. 156W 的優點是什麼？",
        "",
        "- 約等於 3 年市場資料，直覺上容易解釋，也比 52W 更平滑。",
        "- 不使用未來資料，適合線上 dashboard 與歷史回測共同使用。",
        "- 對 COT 週資料來說，156W 有足夠樣本形成 decile，不會像太短窗口那樣容易劇烈跳動。",
        "- 目前 v0.4 dashboard 已採用 156W，因此保留它可維持歷史連續性與使用者熟悉度。",
        "",
        "## 3. 156W 的缺點是什麼？",
        "",
        (
            f"- v0.5 scorecard 顯示 156W 不是三個因子的通用最優解："
            f"MM 156W 平均分 {format_score(mm_156_score)}，"
            f"Producer 156W 平均分 {format_score(producer_156_score)}，"
            f"OI 156W 平均分 {format_score(oi_156_score)}。"
        ),
        "- 156W 對 OI 特別弱，因為 OI 同時有市場參與度、合約規模、結構性週期變化，單純 3 年百分位可能不夠敏感。",
        "- 156W 可能太慢，遇到 2024-2026 這類價格與持倉 regime 轉換時，會保留過多舊狀態。",
        "- 對短期定位而言，52W/104W 有時更敏感；對長期定位而言，260W 有時更穩定。",
        "",
        "## 4. MM 最適合用哪個定義？",
        "",
        (
            f"MM 建議使用 `260W percentile` 作為 dashboard 主定義。"
            f"它在 scorecard 中平均分 {format_score(mm_260_score)}，並在多個 horizon 被選為 recommended。"
        ),
        "",
        "Rationale:",
        "",
        "- MM 是趨勢與擁擠度型因子，過短窗口容易把短週期波動誤判成極端定位。",
        "- 260W 約 5 年，能保留較完整的基金部位週期，適合做 historical positioning。",
        "- `260W zscore` 在 4W/8W 長 horizon 表現也強，建議當輔助欄位，而不是完全取代 percentile。",
        "",
        "MM top scorecard definitions:",
        "",
        report_table(mm_top.head(5)),
        "",
        "## 5. Producer 最適合用哪個定義？",
        "",
        (
            f"Producer 若只選 production-safe dashboard 主欄位，建議先用 `156W percentile`。"
            f"它在 overall summary 中是最佳 rolling production-safe 定義，平均 scorecard 分數為 "
            f"{format_score(producer_156_score)}。"
        ),
        (
            f"`104W percentile` 平均分 {format_score(producer_104_score)}，並在 1W/2W horizon "
            "被 scorecard 選為 recommended，適合當較敏感的短週期研究參考。"
        ),
        (
            f"`52W zscore` 平均分 {format_score(producer_52z_score)}，代表 Producer 的變化幅度對研究有資訊量，"
            "但它是 zscore 輔助欄位，不應直接取代 production-safe percentile。"
        ),
        "",
        "Practical decision:",
        "",
        "- Production-safe dashboard primary: `producer_net_percentile_156w`。",
        "- Short-horizon research companion: `producer_net_percentile_104w`。",
        "- Magnitude research companion: `producer_net_zscore_52w`。",
        "",
        "Producer top scorecard definitions:",
        "",
        report_table(producer_top.head(5)),
        "",
        "## 6. OI 最適合用哪個定義？",
        "",
        (
            f"OI 最適合用 `52W percentile` 作為主 dashboard 定義。"
            f"它平均分 {format_score(oi_52_score)}，並在 1W/2W/4W/8W 都被 scorecard 選為 recommended。"
        ),
        "",
        "Reason:",
        "",
        "- OI 是市場參與度變數，短到中期資金進出比長期歷史排序更有即時資訊。",
        "- 52W percentile 對近期資金擁擠/退潮更敏感。",
        "- OI 不應只看 percentile；absolute level、weekly change、zscore 都應同時呈現。",
        "",
        "OI top scorecard definitions:",
        "",
        report_table(oi_top.head(5)),
        "",
        "## 7. Full History Percentile 是否比 Rolling Percentile 更適合長期定位？",
        "",
        "結論：適合作為研究 benchmark，不適合作為正式 dashboard 主定義。",
        "",
        "Full History 在 summary 中分數偏高，尤其可提供長期歷史相對位置：",
        "",
        report_table(full_history_summary),
        "",
        "但是它有兩個重大限制：",
        "",
        "- Full History 使用全樣本排序，若直接用於歷史回測，會包含當時尚未發生的未來觀測。",
        "- 隨著資料增加，過去日期的 full-history percentile 會被重新改寫，不適合做穩定的線上狀態欄位。",
        "",
        "建議：",
        "",
        "- Dashboard 可新增 `Full History Percentile` 作為 long-term context reference。",
        "- 正式市場狀態與 historical similarity engine 仍應使用 rolling / expanding 類定義。",
        "- 若要做 production-safe long-term 定位，下一版應測試 `expanding percentile`，而不是 full-sample percentile。",
        "",
        "## 8. Producer 是否應該改用 Producer Net / OI 或 Hedging Ratio？",
        "",
        "目前不建議直接替換。建議保持 `Producer Net` 作為 v0.5 主資料源，同時在 v0.6 加入 Hedging Ratio audit。",
        "",
        "原因：",
        "",
        "- Producer Net 仍是 COT 商業避險端的直接部位資訊，解釋性最高。",
        "- 但 Producer Net 會受總 OI 規模變動影響；當 OI 很低或很高時，單看 net contracts 可能失真。",
        "- `Producer Net / OI` 或 `abs(Producer Net) / OI` 可衡量商業端避險強度，可能比單純 net 更適合跨 regime 比較。",
        "- 目前 v0.5 尚未正式 audit Hedging Ratio，因此不應把它放進正式 dashboard 主結論。",
        "",
        "建議 v0.6 新增候選欄位：",
        "",
        "- `producer_net_to_oi_ratio`",
        "- `producer_abs_net_to_oi_ratio`",
        "- `producer_short_to_oi_ratio`",
        "- `producer_ratio_percentile_104w / 156w / 260w`",
        "",
        "## 9. OI 是否適合用 percentile，還是應該用 absolute level / change / zscore？",
        "",
        "OI 適合用 percentile，但不應只用 percentile。",
        "",
        (
            "`52W percentile` 是本次審計中 OI 的最佳主定義；不過 OI 本身是市場參與度與合約規模變數，"
            "absolute level 與 change 也很重要。"
        ),
        "",
        "OI signal comparison, top rows:",
        "",
        report_table(oi_signal_strength),
        "",
        "Dashboard 應同時顯示：",
        "",
        "- `total_open_interest`：絕對持倉規模。",
        "- `oi_change`：近期資金進出變化。",
        "- `oi_percentile_52w`：近期市場參與度定位。",
        "- `oi_zscore_52w`：偏離近期均值的標準化幅度。",
        "- `oi_percentile_156w`：legacy comparison，不作為唯一主判斷。",
        "",
        "## 10. GHPR Dashboard 最終應該顯示哪些欄位？",
        "",
        "Recommended Current Market Snapshot fields:",
        "",
        "- `date`",
        "- `gold_close`",
        "- `gold_source` / source note: COMEX GC futures proxy via Yahoo Finance GC=F",
        "- `mm_net`",
        "- `mm_net_percentile_260w`",
        "- `mm_net_zscore_260w`",
        "- `mm_net_percentile_156w` as legacy reference",
        "- `producer_net`",
        "- `producer_net_percentile_156w`",
        "- `producer_net_percentile_104w` as short-horizon research companion",
        "- `producer_net_zscore_52w`",
        "- `total_open_interest`",
        "- `oi_change`",
        "- `oi_percentile_52w`",
        "- `oi_zscore_52w`",
        "- `oi_percentile_156w` as legacy reference",
        "- `full_history_percentile` fields only in an advanced research panel, not as the default market-state driver",
        "",
        "Recommended dashboard labels:",
        "",
        "- `Primary Historical Positioning` for the v0.5 factor-specific definitions.",
        "- `Legacy 156W Reference` for current v0.4 continuity.",
        "- `Long-Term Historical Reference` for Full History fields.",
        "",
        "## Final Adoption Recommendation",
        "",
        "Use factor-specific definitions in v0.5:",
        "",
        "- MM: `260W percentile` primary, `260W zscore` support.",
        "- Producer: `156W percentile` production-safe primary, `104W percentile` short-horizon companion, `52W zscore` support.",
        "- OI: `52W percentile` primary, plus absolute OI and OI change.",
        "",
        (
            "Keep 156W rolling percentile visible as a legacy reference during transition, "
            "but stop treating 156W as the universal GHPR standard."
        ),
        "",
        "This is a research definition audit. It does not create trade execution logic or external execution integration.",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")


def write_score_chart(summary: pd.DataFrame, output_path: Path) -> None:
    safe = summary[(summary["production_safe"]) & (summary["rolling_definition"])].copy()
    pivot = safe.pivot_table(index="definition", columns="display_name", values="overall_score", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(pivot.values, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=25, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Percentile Definition Overall Score")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", color="white")
    fig.colorbar(image, ax=ax, label="score")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def write_information_chart(summary: pd.DataFrame, output_path: Path) -> None:
    safe = summary[(summary["production_safe"]) & (summary["rolling_definition"])].copy()
    safe["mean_information_score"] = safe[
        [f"information_score_{horizon}w" for horizon in HORIZONS]
    ].mean(axis=1)
    factors = list(safe["display_name"].drop_duplicates())
    definitions = list(safe["definition"].drop_duplicates())
    x = range(len(definitions))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 5))
    for idx, factor in enumerate(factors):
        values = (
            safe[safe["display_name"] == factor]
            .set_index("definition")
            .reindex(definitions)["mean_information_score"]
        )
        positions = [value + (idx - 1) * width for value in x]
        ax.bar(positions, values, width=width, label=factor)
    ax.set_xticks(list(x))
    ax.set_xticklabels(definitions, rotation=30, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("mean 1W/2W/4W/8W information score")
    ax.set_title("1W / 2W / 4W / 8W Information Score by Rolling Window")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def write_task_eight_charts(
    data: pd.DataFrame,
    bucket_analysis: pd.DataFrame,
    scorecard: pd.DataFrame,
) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    write_percentile_window_comparison(
        data,
        factor="MM",
        columns=[
            ("52W", "mm_net_percentile_52w"),
            ("104W", "mm_net_percentile_104w"),
            ("156W", "mm_net_percentile_156w"),
            ("260W", "mm_net_percentile_260w"),
            ("Full History", "mm_net_percentile_full_history"),
        ],
        output_path=MM_WINDOW_CHART,
    )
    write_percentile_window_comparison(
        data,
        factor="Producer",
        columns=[
            ("52W", "producer_net_percentile_52w"),
            ("104W", "producer_net_percentile_104w"),
            ("156W", "producer_net_percentile_156w"),
            ("260W", "producer_net_percentile_260w"),
            ("Full History", "producer_net_percentile_full_history"),
        ],
        output_path=PRODUCER_WINDOW_CHART,
    )
    write_percentile_window_comparison(
        data,
        factor="OI",
        columns=[
            ("52W", "oi_percentile_52w"),
            ("104W", "oi_percentile_104w"),
            ("156W", "oi_percentile_156w"),
            ("260W", "oi_percentile_260w"),
            ("Full History", "oi_percentile_full_history"),
        ],
        output_path=OI_WINDOW_CHART,
    )
    write_scorecard_chart(scorecard, SCORECARD_CHART)
    write_forward_8w_bucket_chart(
        bucket_analysis,
        factor="mm_net",
        title_factor="MM",
        output_path=MM_FORWARD_8W_CHART,
    )
    write_forward_8w_bucket_chart(
        bucket_analysis,
        factor="producer_net",
        title_factor="Producer",
        output_path=PRODUCER_FORWARD_8W_CHART,
    )
    write_forward_8w_bucket_chart(
        bucket_analysis,
        factor="total_open_interest",
        title_factor="OI",
        output_path=OI_FORWARD_8W_CHART,
    )


def write_percentile_window_comparison(
    data: pd.DataFrame,
    factor: str,
    columns: list[tuple[str, str]],
    output_path: Path,
) -> None:
    fig, ax = plt.subplots(figsize=(11, 5.5))
    styles = {
        "52W": {"linewidth": 1.2, "alpha": 0.85},
        "104W": {"linewidth": 1.2, "alpha": 0.85},
        "156W": {"linewidth": 1.8, "alpha": 0.95},
        "260W": {"linewidth": 2.0, "alpha": 0.95},
        "Full History": {"linewidth": 1.3, "alpha": 0.75, "linestyle": "--"},
    }
    for label, column in columns:
        if column not in data.columns:
            continue
        ax.plot(
            data["date"],
            data[column] * 100,
            label=label,
            **styles.get(label, {"linewidth": 1.2}),
        )
    ax.set_title(f"{factor} Percentile Window Comparison")
    ax.set_ylabel("percentile (%)")
    ax.set_xlabel("date")
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.25)
    ax.legend(ncol=5, loc="upper left")
    ax.text(
        0.01,
        0.02,
        "Historical statistics / research reference only",
        transform=ax.transAxes,
        fontsize=9,
        alpha=0.75,
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=170)
    plt.close(fig)


def write_scorecard_chart(scorecard: pd.DataFrame, output_path: Path) -> None:
    chart_data = scorecard.copy()
    chart_data["label"] = chart_data["factor"] + " " + chart_data["horizon"]
    pivot = chart_data.pivot_table(
        index="label",
        columns="definition",
        values="stability_score",
        aggfunc="mean",
    )
    preferred_columns = [
        "52W percentile",
        "104W percentile",
        "156W percentile",
        "260W percentile",
        "Full History percentile",
        "52W zscore",
        "104W zscore",
        "156W zscore",
        "260W zscore",
    ]
    pivot = pivot.reindex(columns=[column for column in preferred_columns if column in pivot.columns])
    fig, ax = plt.subplots(figsize=(13, 6.5))
    image = ax.imshow(pivot.values, aspect="auto", cmap="YlGnBu", vmin=0, vmax=100)
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=35, ha="right")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_title("Percentile Definition Scorecard")
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            value = pivot.iloc[i, j]
            if pd.notna(value):
                text_color = "white" if value >= 70 else "black"
                ax.text(j, i, f"{value:.0f}", ha="center", va="center", color=text_color, fontsize=8)
    fig.colorbar(image, ax=ax, label="stability score")
    fig.tight_layout()
    fig.savefig(output_path, dpi=170)
    plt.close(fig)


def write_forward_8w_bucket_chart(
    bucket_analysis: pd.DataFrame,
    factor: str,
    title_factor: str,
    output_path: Path,
) -> None:
    definitions = ["52W percentile", "104W percentile", "156W percentile", "260W percentile"]
    subset = bucket_analysis[
        (bucket_analysis["factor"] == factor)
        & (bucket_analysis["forward_horizon"] == "8W")
        & (bucket_analysis["definition"].isin(definitions))
    ].copy()
    subset["percentile_bucket"] = pd.Categorical(
        subset["percentile_bucket"],
        categories=BUCKET_LABELS,
        ordered=True,
    )
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for definition in definitions:
        line = (
            subset[subset["definition"] == definition]
            .sort_values("percentile_bucket")
            .set_index("percentile_bucket")
            .reindex(BUCKET_LABELS)
        )
        if line.empty:
            continue
        ax.plot(
            BUCKET_LABELS,
            line["avg_forward_return"] * 100,
            marker="o",
            linewidth=1.8,
            label=definition,
        )
    ax.axhline(0, color="black", linewidth=0.8, alpha=0.65)
    ax.set_title(f"{title_factor}: Percentile Windows vs 8W Subsequent Performance")
    ax.set_xlabel("percentile bucket")
    ax.set_ylabel("avg 8W subsequent return (%)")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")
    ax.tick_params(axis="x", rotation=35)
    ax.text(
        0.01,
        0.02,
        "Historical statistics / research reference only",
        transform=ax.transAxes,
        fontsize=9,
        alpha=0.75,
    )
    fig.tight_layout()
    fig.savefig(output_path, dpi=170)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit GHPR percentile definition alternatives.")
    parser.add_argument("--master-path", type=Path, default=OUTPUT_MASTER_WEEKLY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    master = load_master_dataset(args.master_path)
    data = build_percentile_definitions(master)
    summary, detail, recommendations = audit_definitions(data)
    information_comparison = compare_information_content(data)
    bucket_analysis = run_bucket_analysis(data)
    train_test = run_train_test_validation(data)
    scorecard = build_definition_scorecard(data)
    write_outputs(
        data,
        summary,
        detail,
        information_comparison,
        bucket_analysis,
        train_test,
        scorecard,
        recommendations,
    )
    print(f"Wrote percentile audit dataset: {AUDIT_DATASET_CSV}")
    print(f"Wrote feature matrix: {FEATURE_MATRIX_CSV}")
    print(f"Wrote feature matrix report copy: {FEATURE_MATRIX_REPORT_CSV}")
    print(f"Wrote summary: {SUMMARY_CSV}")
    print(f"Wrote detail: {DETAIL_CSV}")
    print(f"Wrote information comparison: {INFORMATION_COMPARISON_CSV}")
    print(f"Wrote bucket analysis: {BUCKET_ANALYSIS_CSV}")
    print(f"Wrote train/test validation: {TRAIN_TEST_CSV}")
    print(f"Wrote scorecard: {SCORECARD_CSV}")
    print(f"Wrote recommendations: {RECOMMENDATION_CSV}")
    print(f"Wrote report: {REPORT_MD}")
    print(f"Wrote audit research report: {AUDIT_REPORT_MD}")
    print(f"Wrote charts: {SCORE_CHART}, {INFO_CHART}")
    print(
        "Wrote task eight charts: "
        f"{MM_WINDOW_CHART}, {PRODUCER_WINDOW_CHART}, {OI_WINDOW_CHART}, "
        f"{SCORECARD_CHART}, {MM_FORWARD_8W_CHART}, "
        f"{PRODUCER_FORWARD_8W_CHART}, {OI_FORWARD_8W_CHART}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

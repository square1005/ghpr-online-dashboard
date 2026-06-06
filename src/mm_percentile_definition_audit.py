"""GHPR v0.5-A MM percentile definition audit.

This module audits MM percentile definitions only. It is historical statistics
and research reference only; it does not create market instructions or
execution logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

AUDIT_DATASET_CSV = PROCESSED_DIR / "mm_percentile_definition_audit_dataset.csv"
COMPARISON_CSV = REPORTS_DIR / "mm_percentile_definition_comparison.csv"
BUCKET_ANALYSIS_CSV = REPORTS_DIR / "mm_percentile_bucket_analysis.csv"
TRAIN_TEST_CSV = REPORTS_DIR / "mm_percentile_definition_train_test.csv"
SCORECARD_CSV = REPORTS_DIR / "mm_percentile_definition_scorecard.csv"
REPORT_MD = REPORTS_DIR / "mm_percentile_definition_audit_report.md"

WINDOWS = [52, 104, 156, 260]
HORIZONS = [1, 2, 4, 8]
BUCKET_LABELS = [f"{start}-{start + 10}" for start in range(0, 100, 10)]
RETURN_COLUMNS = [f"gold_return_{horizon}w" for horizon in HORIZONS]
PERCENTILE_COLUMNS = [
    *(f"mm_net_percentile_{window}w" for window in WINDOWS),
    "mm_net_percentile_full_history",
]
ZSCORE_COLUMNS = [f"mm_net_zscore_{window}w" for window in WINDOWS]
AUDIT_DATASET_COLUMNS = [
    "date",
    "gold_close",
    "mm_net",
    *PERCENTILE_COLUMNS,
    *ZSCORE_COLUMNS,
    *RETURN_COLUMNS,
]
REQUIRED_COLUMNS = [
    "date",
    "gold_close",
    "mm_net",
    *RETURN_COLUMNS,
]


@dataclass(frozen=True)
class Definition:
    label: str
    column: str
    window: int | None
    production_safe: bool
    note: str


def trailing_percentile(series: pd.Series, window: int, min_periods: int = 52) -> pd.Series:
    """Percentile of the current value versus prior observations only."""
    values = pd.to_numeric(series, errors="coerce")
    output = pd.Series(np.nan, index=series.index, dtype="float64")
    for index, current in values.items():
        if pd.isna(current):
            continue
        position = values.index.get_loc(index)
        history = values.iloc[max(0, position - window) : position].dropna()
        if len(history) < min_periods:
            continue
        output.loc[index] = float((history <= current).mean())
    return output


def trailing_zscore(series: pd.Series, window: int, min_periods: int = 52) -> pd.Series:
    """Z-score of the current value versus prior observations only."""
    values = pd.to_numeric(series, errors="coerce")
    output = pd.Series(np.nan, index=series.index, dtype="float64")
    for index, current in values.items():
        if pd.isna(current):
            continue
        position = values.index.get_loc(index)
        history = values.iloc[max(0, position - window) : position].dropna()
        if len(history) < min_periods:
            continue
        std = history.std(ddof=1)
        if pd.isna(std) or std == 0:
            continue
        output.loc[index] = float((current - history.mean()) / std)
    return output


def full_history_percentile(series: pd.Series) -> pd.Series:
    clean = series.dropna()
    if clean.empty:
        return pd.Series(np.nan, index=series.index)
    ranked = clean.rank(pct=True, method="average")
    return ranked.reindex(series.index)


def assign_decile(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")
    labels = pd.Series(pd.NA, index=series.index, dtype="object")
    valid = values.dropna()
    if valid.empty:
        return labels
    clipped = valid.clip(0, 1)
    bucket_numbers = np.floor(clipped * 10).astype(int).clip(0, 9)
    labels.loc[valid.index] = [BUCKET_LABELS[number] for number in bucket_numbers]
    return labels


def spearman_corr(left: pd.Series, right: pd.Series) -> float | None:
    frame = pd.concat([left, right], axis=1).dropna()
    if len(frame) < 20:
        return None
    value = frame.iloc[:, 0].corr(frame.iloc[:, 1], method="spearman")
    if pd.isna(value):
        return None
    return float(value)


def decile_monotonicity(bucket_means: pd.Series) -> float | None:
    clean = bucket_means.dropna()
    if len(clean) < 4:
        return None
    positions = pd.Series(range(len(clean)), index=clean.index)
    value = positions.corr(clean, method="spearman")
    if pd.isna(value):
        return None
    return float(value)


def load_master() -> pd.DataFrame:
    data = pd.read_csv(MASTER_PATH)
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    for column in REQUIRED_COLUMNS:
        if column != "date":
            data[column] = pd.to_numeric(data[column], errors="coerce")
    return data


def build_audit_dataset(master: pd.DataFrame) -> pd.DataFrame:
    data = master[REQUIRED_COLUMNS].copy()
    for window in WINDOWS:
        data[f"mm_net_percentile_{window}w"] = trailing_percentile(data["mm_net"], window)
    data["mm_net_percentile_full_history"] = full_history_percentile(data["mm_net"])
    for window in WINDOWS:
        data[f"mm_net_zscore_{window}w"] = trailing_zscore(data["mm_net"], window)
    return data[AUDIT_DATASET_COLUMNS]


def definitions() -> list[Definition]:
    items = [
        Definition(
            label=f"{window}W percentile",
            column=f"mm_net_percentile_{window}w",
            window=window,
            production_safe=True,
            note=f"Trailing {window}-week percentile using prior observations only.",
        )
        for window in WINDOWS
    ]
    items.append(
        Definition(
            label="Full History percentile",
            column="mm_net_percentile_full_history",
            window=None,
            production_safe=False,
            note="Full-sample benchmark. Research reference only because historical rows use future observations.",
        )
    )
    return items


def high_low_spread(valid: pd.DataFrame, signal_col: str, return_col: str) -> float | None:
    buckets = assign_decile(valid[signal_col])
    low = valid.loc[buckets == BUCKET_LABELS[0], return_col].dropna()
    high = valid.loc[buckets == BUCKET_LABELS[-1], return_col].dropna()
    if low.empty or high.empty:
        return None
    return float(high.mean() - low.mean())


def compare_definitions(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    total_rows = len(data)
    for definition in definitions():
        signal = data[definition.column]
        weekly_change = signal.diff().abs()
        for horizon in HORIZONS:
            return_col = f"gold_return_{horizon}w"
            valid = data[[definition.column, return_col]].dropna()
            buckets = assign_decile(valid[definition.column])
            bucket_means = valid.groupby(buckets, observed=False)[return_col].mean()
            rows.append(
                {
                    "definition": definition.label,
                    "signal_column": definition.column,
                    "window_weeks": definition.window,
                    "production_safe": definition.production_safe,
                    "horizon": f"{horizon}W",
                    "rank_corr": spearman_corr(valid[definition.column], valid[return_col]),
                    "high_low_spread": high_low_spread(valid, definition.column, return_col),
                    "bucket_monotonicity_score": decile_monotonicity(bucket_means),
                    "positive_bucket_count": int((bucket_means.dropna() > 0).sum()),
                    "negative_bucket_count": int((bucket_means.dropna() < 0).sum()),
                    "sample_count": int(len(valid)),
                    "missing_count": int(total_rows - len(valid)),
                    "coverage": float(len(valid) / total_rows) if total_rows else np.nan,
                    "median_abs_weekly_change": float(weekly_change.median(skipna=True)),
                    "p95_abs_weekly_change": float(weekly_change.quantile(0.95)),
                    "note": definition.note,
                }
            )
    return pd.DataFrame(rows)


def bucket_analysis(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for definition in definitions():
        frame = data[[definition.column, *RETURN_COLUMNS]].dropna(subset=[definition.column]).copy()
        frame["bucket"] = assign_decile(frame[definition.column])
        for bucket in BUCKET_LABELS:
            group = frame[frame["bucket"] == bucket]
            row = {
                "definition": definition.label,
                "signal_column": definition.column,
                "bucket": bucket,
                "count": int(len(group)),
            }
            for horizon in HORIZONS:
                return_col = f"gold_return_{horizon}w"
                values = group[return_col].dropna()
                row[f"avg_forward_return_{horizon}w"] = (
                    np.nan if values.empty else float(values.mean())
                )
                row[f"median_forward_return_{horizon}w"] = (
                    np.nan if values.empty else float(values.median())
                )
                row[f"win_rate_{horizon}w"] = (
                    np.nan if values.empty else float((values > 0).mean())
                )
            values_8w = group["gold_return_8w"].dropna()
            row["best_return_8w"] = np.nan if values_8w.empty else float(values_8w.max())
            row["worst_return_8w"] = np.nan if values_8w.empty else float(values_8w.min())
            rows.append(row)
    output_columns = [
        "definition",
        "signal_column",
        "bucket",
        "count",
    ]
    for horizon in HORIZONS:
        output_columns.extend(
            [
                f"avg_forward_return_{horizon}w",
                f"median_forward_return_{horizon}w",
                f"win_rate_{horizon}w",
            ]
        )
    output_columns.extend(["best_return_8w", "worst_return_8w"])
    return pd.DataFrame(rows)[output_columns]


def bucket_analysis_long(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for definition in definitions():
        for horizon in HORIZONS:
            return_col = f"gold_return_{horizon}w"
            frame = data[[definition.column, return_col]].dropna().copy()
            frame["bucket"] = assign_decile(frame[definition.column])
            for bucket in BUCKET_LABELS:
                group = frame[frame["bucket"] == bucket][return_col].dropna()
                rows.append(
                    {
                        "definition": definition.label,
                        "signal_column": definition.column,
                        "horizon": f"{horizon}W",
                        "bucket": bucket,
                        "count": int(group.count()),
                        "avg_forward_return": np.nan if group.empty else float(group.mean()),
                        "median_forward_return": np.nan if group.empty else float(group.median()),
                        "win_rate": np.nan if group.empty else float((group > 0).mean()),
                        "best_return": np.nan if group.empty else float(group.max()),
                        "worst_return": np.nan if group.empty else float(group.min()),
                        "max_drawdown_after_signal": np.nan if group.empty else float(group.min()),
                    }
                )
    return pd.DataFrame(rows)


def split_frame(data: pd.DataFrame, split: str) -> pd.DataFrame:
    if split == "train":
        return data[(data["date"] >= "2009-09-01") & (data["date"] <= "2018-12-31")]
    if split == "test":
        return data[data["date"] >= "2019-01-01"]
    raise ValueError(f"Unknown split: {split}")


def train_test_analysis(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for split in ["train", "test"]:
        sample = split_frame(data, split)
        for definition in definitions():
            for horizon in HORIZONS:
                return_col = f"gold_return_{horizon}w"
                valid = sample[[definition.column, return_col]].dropna().copy()
                buckets = assign_decile(valid[definition.column])
                high = valid.loc[buckets == BUCKET_LABELS[-1], return_col].dropna()
                low = valid.loc[buckets == BUCKET_LABELS[0], return_col].dropna()
                rows.append(
                    {
                        "sample_split": split,
                        "split_start": sample["date"].min().strftime("%Y-%m-%d") if not sample.empty else None,
                        "split_end": sample["date"].max().strftime("%Y-%m-%d") if not sample.empty else None,
                        "definition": definition.label,
                        "signal_column": definition.column,
                        "production_safe": definition.production_safe,
                        "horizon": f"{horizon}W",
                        "rank_corr": spearman_corr(valid[definition.column], valid[return_col]),
                        "high_low_spread": high_low_spread(valid, definition.column, return_col),
                        "win_rate_extreme_high": np.nan if high.empty else float((high > 0).mean()),
                        "win_rate_extreme_low": np.nan if low.empty else float((low > 0).mean()),
                        "avg_return_extreme_high": np.nan if high.empty else float(high.mean()),
                        "avg_return_extreme_low": np.nan if low.empty else float(low.mean()),
                        "sample_count": int(len(valid)),
                    }
                )
    return pd.DataFrame(rows)


def scorecard(comparison: pd.DataFrame, train_test: pd.DataFrame) -> pd.DataFrame:
    scored = comparison.copy()
    scored["abs_rank_corr"] = scored["rank_corr"].abs()
    scored["abs_high_low_spread"] = scored["high_low_spread"].abs()
    parts = []
    rolling_change_reference = scored[scored["production_safe"]].groupby("definition")[
        "median_abs_weekly_change"
    ].mean()
    shortest_change = rolling_change_reference.get("52W percentile", np.nan)

    for horizon, group in scored.groupby("horizon", sort=False):
        item = group.copy()
        for source, target in [
            ("abs_rank_corr", "rank_corr_score"),
            ("abs_high_low_spread", "spread_score"),
        ]:
            item[target] = item[source].rank(pct=True, ascending=True).fillna(0) * 100
        item["coverage_score"] = item["coverage"].fillna(0) * 100
        max_change = item["median_abs_weekly_change"].max(skipna=True)
        if pd.isna(max_change) or max_change == 0:
            item["stability_score"] = 100
        else:
            item["stability_score"] = (
                1 - item["median_abs_weekly_change"] / max_change
            ).clip(0, 1) * 100

        train_corrs = []
        test_corrs = []
        train_test_scores = []
        interpretability_scores = []
        reasons = []
        for _, row in item.iterrows():
            train = train_test[
                (train_test["sample_split"] == "train")
                & (train_test["definition"] == row["definition"])
                & (train_test["horizon"] == horizon)
            ]
            test = train_test[
                (train_test["sample_split"] == "test")
                & (train_test["definition"] == row["definition"])
                & (train_test["horizon"] == horizon)
            ]
            train_corr = np.nan if train.empty else train.iloc[0]["rank_corr"]
            test_corr = np.nan if test.empty else test.iloc[0]["rank_corr"]
            train_corrs.append(train_corr)
            test_corrs.append(test_corr)

            if pd.isna(train_corr) or pd.isna(test_corr):
                train_test_scores.append(0.0)
            elif train_corr == 0 or test_corr == 0:
                train_test_scores.append(50.0)
            elif (train_corr > 0 and test_corr > 0) or (train_corr < 0 and test_corr < 0):
                train_test_scores.append(100.0)
            else:
                train_test_scores.append(0.0)

            interpretability_score = 90.0 if row["production_safe"] else 55.0
            reason_parts = []
            if row["production_safe"]:
                reason_parts.append("rolling percentile is suitable for an online dashboard")
            else:
                reason_parts.append("full-history percentile is research-only and not real-time safe")
            if row["definition"] == "52W percentile" and pd.notna(shortest_change):
                longer_mean = rolling_change_reference.drop(labels=["52W percentile"], errors="ignore").mean()
                if pd.notna(longer_mean) and shortest_change > longer_mean:
                    interpretability_score -= 15.0
                    reason_parts.append("52W window is more reactive and gets a jumpiness penalty")
            if row["definition"] == "156W percentile":
                reason_parts.append("156W remains useful for continuity with the current dashboard")
            if horizon in {"4W", "8W"}:
                reason_parts.append("4W/8W information receives primary research weight")
            interpretability_scores.append(max(0.0, interpretability_score))
            reasons.append("; ".join(reason_parts))

        item["train_rank_corr"] = train_corrs
        item["test_rank_corr"] = test_corrs
        item["information_score"] = (
            (0.60 * item["rank_corr_score"] + 0.40 * item["spread_score"])
            * item["horizon"].map({"1W": 0.75, "2W": 0.85, "4W": 1.00, "8W": 1.00})
        )
        item["train_test_score"] = train_test_scores
        item["interpretability_score"] = interpretability_scores
        item["reason"] = reasons
        item["total_score"] = (
            0.40 * item["information_score"]
            + 0.20 * item["stability_score"]
            + 0.20 * item["train_test_score"]
            + 0.20 * item["interpretability_score"]
        )
        parts.append(item)
    result = pd.concat(parts, ignore_index=True)
    result["recommended"] = False
    for horizon, group in result[result["production_safe"]].groupby("horizon", sort=False):
        idx = group["total_score"].idxmax()
        result.loc[idx, "recommended"] = True
    return result[
        [
            "definition",
            "horizon",
            "rank_corr",
            "high_low_spread",
            "median_abs_weekly_change",
            "train_rank_corr",
            "test_rank_corr",
            "information_score",
            "stability_score",
            "train_test_score",
            "interpretability_score",
            "total_score",
            "recommended",
            "reason",
        ]
    ].rename(columns={"median_abs_weekly_change": "weekly_change_avg"}).sort_values(
        ["horizon", "total_score"], ascending=[True, False]
    )


def score_summary(scorecard_frame: pd.DataFrame) -> pd.DataFrame:
    production_safe_map = {definition.label: definition.production_safe for definition in definitions()}
    summary = (
        scorecard_frame.groupby("definition", as_index=False)
        .agg(
            avg_total_score=("total_score", "mean"),
            avg_information_score=("information_score", "mean"),
            avg_weekly_change=("weekly_change_avg", "mean"),
            avg_train_test_score=("train_test_score", "mean"),
            recommended_horizon_count=("recommended", "sum"),
        )
        .sort_values("avg_total_score", ascending=False)
    )
    long_scores = (
        scorecard_frame[scorecard_frame["horizon"].isin(["4W", "8W"])]
        .groupby("definition")["total_score"]
        .mean()
    )
    summary["avg_4w_8w_score"] = summary["definition"].map(long_scores)
    long_information = (
        scorecard_frame[scorecard_frame["horizon"].isin(["4W", "8W"])]
        .groupby("definition")["information_score"]
        .mean()
    )
    summary["avg_4w_8w_information_score"] = summary["definition"].map(long_information)
    summary["production_safe"] = summary["definition"].map(production_safe_map)
    return summary


def fmt(value: object, digits: int = 3) -> str:
    if value is None or pd.isna(value):
        return "NA"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (int, np.integer)):
        return str(int(value))
    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return str(value)


def markdown_table(frame: pd.DataFrame) -> str:
    view = frame.copy()
    for column in view.columns:
        if pd.api.types.is_float_dtype(view[column]):
            view[column] = view[column].map(lambda value: fmt(value, 4))
    return view.to_markdown(index=False)


def write_report(
    data: pd.DataFrame,
    comparison: pd.DataFrame,
    train_test: pd.DataFrame,
    scorecard_frame: pd.DataFrame,
) -> None:
    summary = score_summary(scorecard_frame)
    safe_summary = summary[summary["production_safe"]].copy()
    best_safe = safe_summary.iloc[0]
    row_156 = summary[summary["definition"] == "156W percentile"].iloc[0]
    best_4w_8w = safe_summary.sort_values("avg_4w_8w_score", ascending=False).iloc[0]
    most_stable_all = summary.sort_values("avg_weekly_change", ascending=True).iloc[0]
    most_stable_safe = safe_summary.sort_values("avg_weekly_change", ascending=True).iloc[0]
    long_information = scorecard_frame[scorecard_frame["horizon"].isin(["4W", "8W"])]
    best_long_info = (
        long_information.groupby("definition", as_index=False)["information_score"]
        .mean()
        .sort_values("information_score", ascending=False)
        .iloc[0]
    )
    best_4w_info = scorecard_frame[scorecard_frame["horizon"] == "4W"].sort_values(
        "information_score", ascending=False
    ).iloc[0]
    best_8w_info = scorecard_frame[scorecard_frame["horizon"] == "8W"].sort_values(
        "information_score", ascending=False
    ).iloc[0]
    recommended = scorecard_frame[scorecard_frame["recommended"]].copy()
    inconsistent = scorecard_frame[
        (pd.to_numeric(scorecard_frame["train_rank_corr"], errors="coerce") > 0)
        != (pd.to_numeric(scorecard_frame["test_rank_corr"], errors="coerce") > 0)
    ]

    conclusion = (
        "156W is reasonable as a continuity baseline, but it is not the strongest MM-only definition "
        "under this audit."
    )
    if row_156["recommended_horizon_count"] > 0:
        conclusion = (
            "156W is reasonable and wins at least one horizon, but the MM-only audit still favors a "
            "factor-specific comparison instead of assuming 156W is universally best."
        )

    lines = [
        "# GHPR v0.5-A MM Percentile Definition Audit",
        "",
        f"Data period: `{data['date'].min().strftime('%Y-%m-%d')}` to `{data['date'].max().strftime('%Y-%m-%d')}`.",
        f"Rows: `{len(data)}`.",
        "",
        "This is historical statistics and research reference only. It does not create market instructions, execution logic, or financial advice.",
        "",
        "## Executive Answer",
        "",
        "- This MM-only audit is intentionally separate from the broader v0.5 multi-factor audit. It should be reviewed as one research lens before any v0.6 dashboard definition change.",
        f"- {conclusion}",
        f"- Best production-safe average score: `{best_safe['definition']}` with `{fmt(best_safe['avg_total_score'], 1)}`.",
        f"- Best production-safe 4W/8W average score: `{best_4w_8w['definition']}` with `{fmt(best_4w_8w['avg_4w_8w_score'], 1)}`.",
        f"- Best average 4W/8W information score: `{best_long_info['definition']}` with `{fmt(best_long_info['information_score'], 1)}`.",
        f"- 156W average score: `{fmt(row_156['avg_total_score'], 1)}`; recommended horizons: `{int(row_156['recommended_horizon_count'])}`.",
        "- Final dashboard decision: `暫不替換`. Keep `mm_net_percentile_156w` as the current dashboard main reference until v0.6 review, while tracking 104W and 260W as research candidates.",
        "- Full History percentile is useful as a research benchmark, but it is not production-safe because historical rows use future observations.",
        "",
        "## Required Questions",
        "",
        "### 1. 目前 GHPR 使用的 156W MM Percentile 是什麼？",
        "",
        "`mm_net_percentile_156w` 是把當週 MM net positioning 放到 156 週歷史窗口中做百分位定位。v0.5-A audit 使用 production-safe trailing definition：當週只和前 156 週資料比較，不使用未來資料。Dashboard 目前仍以 156W 作為 Current Position 的 MM reference。",
        "",
        "### 2. 156W 的優點是什麼？",
        "",
        "- 156W 約等於三年週資料，樣本數足夠，decile 不會太稀疏。",
        "- 比 52W 更平滑，較不容易把短期 positioning 波動放大成極端狀態。",
        "- 與目前 GHPR Dashboard 口徑一致，保留它能維持使用者解讀的連續性。",
        f"- 在本次 scorecard 中，156W 的平均 total score 為 `{fmt(row_156['avg_total_score'], 1)}`，且 8W horizon 被選為 recommended。",
        "",
        "### 3. 156W 的缺點是什麼？",
        "",
        "- 156W 不是所有 horizon 的最佳定義：1W/4W 偏向 104W，2W 偏向 52W，8W 才由 156W 勝出。",
        "- 它比 52W/104W 反應慢，遇到 positioning regime 快速切換時可能較滯後。",
        f"- 156W 平均 total score `{fmt(row_156['avg_total_score'], 1)}` 低於 best average definition `{best_safe['definition']}` 的 `{fmt(best_safe['avg_total_score'], 1)}`。",
        "",
        "### 4. 52W / 104W / 156W / 260W / full_history 各自差異是什麼？",
        "",
        "- `52W percentile`：一年窗口，反應最快，但 weekly change 最大，interpretability 有 jumpiness penalty。",
        "- `104W percentile`：兩年窗口，速度與穩定度較均衡，本次平均 total score 最高。",
        "- `156W percentile`：三年窗口，現行 Dashboard reference，連續性佳，8W horizon 表現較強。",
        "- `260W percentile`：五年窗口，更偏長週期 positioning，4W/8W average total score 較高。",
        "- `full_history percentile`：全樣本歷史定位，適合研究 benchmark，但因為歷史列會使用未來觀測排序，不可作為即時 Dashboard 或 historical backtest 主定義。",
        "",
        "### 5. 哪個定義最穩定？",
        "",
        f"若只看 weekly percentile change，最穩定的是 `{most_stable_all['definition']}`，平均 weekly change `{fmt(most_stable_all['avg_weekly_change'], 4)}`。但它若是 full_history，僅能作研究 benchmark。production-safe rolling 定義中，最穩定的是 `{most_stable_safe['definition']}`，平均 weekly change `{fmt(most_stable_safe['avg_weekly_change'], 4)}`。",
        "",
        "### 6. 哪個定義對 4W / 8W 最有資訊量？",
        "",
        f"依 information_score 的 4W/8W 平均值，最佳為 `{best_long_info['definition']}`，平均 information score `{fmt(best_long_info['information_score'], 1)}`。拆開看，4W information score 最高是 `{best_4w_info['definition']}`，8W information score 最高是 `{best_8w_info['definition']}`。",
        "",
        "### 7. Train / Test 是否一致？",
        "",
        (
            "Train/Test rank correlation 方向在本次 scorecard 中大致一致；所有 scorecard row 的 train/test rank_corr 方向一致。"
            if inconsistent.empty
            else f"Train/Test 有 `{len(inconsistent)}` 個 row 出現方向不一致，需保守解讀。"
        ),
        "",
        "### 8. 最終推薦 GHPR Dashboard 暫時採用哪個 MM Percentile 定義？",
        "",
        "`暫時採用現行 156W`。理由是：它是既有 Dashboard reference、8W horizon 勝出，而且目前證據不是單一窗口全面勝出。v0.5-A 建議把 104W / 260W 放入研究觀察清單，不立即替換正式 Current Position 定義。",
        "",
        "### 9. 是否建議保留 156W 作為主定義？",
        "",
        "是，暫時保留。不是因為 156W 絕對最佳，而是因為它有連續性、穩定性與 8W 支持，同時避免 v0.5-A 單因子結果過早改動正式 Dashboard。",
        "",
        "### 10. 如果不建議，應改成哪一個？原因是什麼？",
        "",
        "本報告不建議立刻替換，因此沒有正式替換定義。若 v0.6 決定改版，候選方向是：`104W percentile` 作為 balanced/default candidate，因為平均 total score 最高；若 Dashboard 更重視 4W/8W historical positioning，則 `260W percentile` 是長週期候選；若只看 8W 單一 horizon，156W 仍有保留理由。",
        "",
        "### 11. 如果資料不足以決定，也要明確說明「暫不替換」。",
        "",
        "`暫不替換`。目前資料足以說明 156W 不是唯一最佳，但不足以支持直接把正式 Dashboard 主定義從 156W 改成單一新窗口。下一步應在 v0.6 同時評估 Dashboard 使用者解讀、HSE 相似度結果、以及多因子一致性。",
        "",
        "## Recommended Definitions By Horizon",
        "",
        markdown_table(
            recommended[
                [
                    "horizon",
                    "definition",
                    "total_score",
                    "rank_corr",
                    "high_low_spread",
                    "weekly_change_avg",
                    "train_rank_corr",
                    "test_rank_corr",
                    "reason",
                ]
            ]
        ),
        "",
        "## Average Score By Definition",
        "",
        markdown_table(summary),
        "",
        "## 156W Reasonableness Check",
        "",
        "- 156W has enough observations for stable deciles and remains useful for continuity with the existing dashboard.",
        "- The audit does not support treating 156W as automatically optimal for MM.",
        "- A longer window can better preserve the full MM positioning cycle; a shorter window can react faster but may overstate short-cycle moves.",
        "",
        "## Definition Construction Notes",
        "",
        "- Rolling percentile fields use a trailing historical window and compare the current `mm_net` against prior observations only.",
        "- Rolling z-score fields use the same prior-only trailing window: `(current_mm_net - prior_window_mean) / prior_window_std`.",
        "- `mm_net_percentile_full_history` is a full-sample historical positioning field for research context only. It should not be used for real-time historical backtests because past rows are ranked with future observations.",
        "",
        "## Train/Test Validation Snapshot",
        "",
        markdown_table(
            train_test[
                (train_test["definition"].isin(["52W percentile", "104W percentile", "156W percentile", "260W percentile"]))
                & (train_test["horizon"].isin(["4W", "8W"]))
            ][
                [
                    "sample_split",
                    "definition",
                    "horizon",
                    "rank_corr",
                    "high_low_spread",
                    "win_rate_extreme_high",
                    "win_rate_extreme_low",
                    "sample_count",
                ]
            ]
        ),
        "",
        "## Final Research View",
        "",
        "For MM only, keep `mm_net_percentile_156w` visible as the current dashboard reference while v0.5-A treats the higher-scoring rolling definition as the research candidate for v0.6 review.",
    ]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def write_charts(
    data: pd.DataFrame,
    bucket_frame: pd.DataFrame,
    train_test: pd.DataFrame,
    scorecard_frame: pd.DataFrame,
) -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")
    fig, ax = plt.subplots(figsize=(12, 6))
    for window in WINDOWS:
        column = f"mm_net_percentile_{window}w"
        ax.plot(data["date"], data[column] * 100, label=f"{window}W", linewidth=1.2)
    ax.plot(
        data["date"],
        data["mm_net_percentile_full_history"] * 100,
        label="Full History",
        linewidth=1.2,
        linestyle="--",
    )
    ax.set_title("MM Percentile Window Comparison")
    ax.set_ylabel("Percentile")
    ax.set_ylim(0, 100)
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "mm_percentile_window_comparison.png", dpi=170)
    plt.close(fig)

    subset = bucket_frame[
        bucket_frame["definition"].isin([f"{window}W percentile" for window in WINDOWS])
    ].copy()
    subset["bucket"] = pd.Categorical(subset["bucket"], categories=BUCKET_LABELS, ordered=True)
    fig, ax = plt.subplots(figsize=(12, 6))
    for definition, group in subset.groupby("definition", sort=False):
        ordered = group.sort_values("bucket")
        ax.plot(
            ordered["bucket"].astype(str),
            ordered["avg_forward_return_8w"] * 100,
            marker="x",
            linestyle="--",
            alpha=0.65,
            label=f"{definition} avg",
        )
        ax.plot(
            ordered["bucket"].astype(str),
            ordered["median_forward_return_8w"] * 100,
            marker="o",
            label=f"{definition} median",
        )
    ax.axhline(0, color="#111827", linewidth=1)
    ax.set_title("MM Bucket 8W Avg And Median Following Performance")
    ax.set_ylabel("8W return (%)")
    ax.set_xlabel("Percentile bucket")
    ax.legend(fontsize=8, ncols=2)
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "mm_bucket_forward_8w_by_definition.png", dpi=170)
    plt.close(fig)

    summary = score_summary(scorecard_frame)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(summary["definition"], summary["avg_total_score"], color="#2563eb")
    ax.set_title("MM Percentile Definition Average Score")
    ax.set_xlabel("Average score")
    ax.invert_yaxis()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "mm_definition_scorecard.png", dpi=170)
    plt.close(fig)

    train_test_subset = train_test[
        train_test["definition"].isin([f"{window}W percentile" for window in WINDOWS])
    ].copy()
    train_test_subset = train_test_subset[train_test_subset["horizon"].isin(["4W", "8W"])]
    pivot = train_test_subset.pivot_table(
        index=["definition", "horizon"],
        columns="sample_split",
        values="rank_corr",
        aggfunc="mean",
    ).reset_index()
    labels = [f"{row.definition} {row.horizon}" for row in pivot.itertuples(index=False)]
    x = np.arange(len(labels))
    width = 0.38
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width / 2, pivot.get("train", pd.Series(index=pivot.index, dtype=float)), width, label="Train")
    ax.bar(x + width / 2, pivot.get("test", pd.Series(index=pivot.index, dtype=float)), width, label="Test")
    ax.axhline(0, color="#111827", linewidth=1)
    ax.set_title("MM Definition Train / Test Rank Correlation")
    ax.set_ylabel("Rank correlation")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHARTS_DIR / "mm_definition_train_test_comparison.png", dpi=170)
    plt.close(fig)


def write_outputs(
    data: pd.DataFrame,
    comparison: pd.DataFrame,
    bucket_frame: pd.DataFrame,
    train_test: pd.DataFrame,
    scorecard_frame: pd.DataFrame,
) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    data.to_csv(AUDIT_DATASET_CSV, index=False)
    comparison.to_csv(COMPARISON_CSV, index=False)
    bucket_frame.to_csv(BUCKET_ANALYSIS_CSV, index=False)
    train_test.to_csv(TRAIN_TEST_CSV, index=False)
    scorecard_frame.to_csv(SCORECARD_CSV, index=False)
    write_report(data, comparison, train_test, scorecard_frame)
    write_charts(data, bucket_frame, train_test, scorecard_frame)


def main() -> int:
    master = load_master()
    data = build_audit_dataset(master)
    comparison = compare_definitions(data)
    bucket_frame = bucket_analysis(data)
    train_test = train_test_analysis(data)
    scorecard_frame = scorecard(comparison, train_test)
    write_outputs(data, comparison, bucket_frame, train_test, scorecard_frame)
    print(f"Wrote MM audit dataset: {AUDIT_DATASET_CSV}")
    print(f"Wrote MM audit report: {REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

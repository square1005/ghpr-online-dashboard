"""Historical Similarity Engine for GHPR v0.3."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

try:
    from .utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT
except ImportError:
    from utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT


FEATURE_COLUMNS = [
    "mm_net_percentile_156w",
    "producer_net_percentile_156w",
    "oi_percentile_156w",
]
CONTEXT_COLUMNS = ["gold_return_1w", "gold_return_2w", "gold_return_4w", "gold_return_8w"]
REQUIRED_COLUMNS = ["date", "gold_close", *FEATURE_COLUMNS]
FORWARD_HORIZONS = [1, 2, 4, 8]
MAX_DISTANCE_POINTS = 300

REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"
HSE_SIMILARITY_CSV = REPORTS_DIR / "hse_current_similarity.csv"
HSE_FEATURE_VECTOR_CSV = REPORTS_DIR / "hse_current_feature_vector.csv"
HSE_SUMMARY_CSV = REPORTS_DIR / "hse_current_similarity_summary.csv"
HSE_REPORT_MD = REPORTS_DIR / "hse_current_similarity_report.md"
HISTORICAL_SIMILARITY_REPORT_CSV = REPORTS_DIR / "historical_similarity_report.csv"
HISTORICAL_SIMILARITY_STATS_CSV = REPORTS_DIR / "historical_similarity_stats.csv"
HISTORICAL_SIMILARITY_SUMMARY_MD = REPORTS_DIR / "historical_similarity_summary.md"
HISTORICAL_SIMILARITY_CASES_CHART = CHARTS_DIR / "historical_similarity_cases.png"


def load_master_dataset(path: Path = OUTPUT_MASTER_WEEKLY) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Master dataset not found: {path}")

    frame = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise KeyError(f"Master dataset is missing required columns: {missing}")

    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in [*REQUIRED_COLUMNS, *CONTEXT_COLUMNS]:
        if column != "date":
            if column in frame.columns:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame = frame.dropna(subset=["date", "gold_close"]).sort_values("date").reset_index(drop=True)
    return add_forward_returns(frame)


def add_forward_returns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for weeks in FORWARD_HORIZONS:
        out[f"forward_return_{weeks}w"] = out["gold_close"].shift(-weeks) / out["gold_close"] - 1
    return out


def compute_current_similarity(
    master_path: Path = OUTPUT_MASTER_WEEKLY,
    top_n: int = 20,
    exclude_recent_weeks: int = 8,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, object]]:
    master = load_master_dataset(master_path)
    if master.empty:
        raise ValueError("Master dataset is empty.")

    complete_states = master.dropna(subset=FEATURE_COLUMNS)
    if complete_states.empty:
        raise ValueError("No row has a complete current market state.")

    current_pos = int(complete_states.index[-1])
    current = master.loc[current_pos].copy()

    recent_rows_to_exclude = max(exclude_recent_weeks, 1)
    candidate_end = max(current_pos + 1 - recent_rows_to_exclude, 0)
    candidates = master.iloc[:candidate_end].copy()
    rows_before_feature_drop = len(candidates)
    candidates = candidates.dropna(subset=FEATURE_COLUMNS).copy()
    rows_after_feature_drop = len(candidates)
    if candidates.empty:
        raise ValueError("No historical candidate rows have complete similarity features.")

    means = candidates[FEATURE_COLUMNS].mean()
    stds = candidates[FEATURE_COLUMNS].std().replace(0, pd.NA).fillna(1)

    for column in FEATURE_COLUMNS:
        scale = percentile_scale(master[column])
        candidates[f"diff_{column}_points"] = ((candidates[column] - current[column]) * scale).abs()

    diff_columns = [f"diff_{column}_points" for column in FEATURE_COLUMNS]
    candidates["distance"] = candidates[diff_columns].sum(axis=1)
    candidates["normalized_distance"] = (candidates["distance"] / MAX_DISTANCE_POINTS * 100).clip(lower=0, upper=100)
    candidates["similarity_score"] = 100 - candidates["normalized_distance"]

    output_columns = [
        "date",
        "gold_close",
        "similarity_score",
        "distance",
        "normalized_distance",
        *FEATURE_COLUMNS,
        *[column for column in CONTEXT_COLUMNS if column in candidates.columns],
        *diff_columns,
        *[f"forward_return_{weeks}w" for weeks in FORWARD_HORIZONS],
    ]
    for optional in ["sample_split", "gold_regime", "gold_anomaly_2025_2026"]:
        if optional in candidates.columns:
            output_columns.append(optional)

    result = candidates.sort_values(["distance", "date"], ascending=[True, True]).head(top_n).copy()
    result = result[output_columns].copy()
    result.insert(0, "rank", range(1, len(result) + 1))

    current_vector = build_current_vector(current, means, stds)
    summary = summarize_similarity_result(result)
    metadata = {
        "master_path": str(master_path),
        "latest_date": current["date"].strftime("%Y-%m-%d"),
        "latest_gold_close": float(current["gold_close"]),
        "master_rows": int(len(master)),
        "current_row_position": int(current_pos),
        "candidate_rows_before_feature_drop": int(rows_before_feature_drop),
        "candidate_rows_after_feature_drop": int(rows_after_feature_drop),
        "dropped_incomplete_candidate_rows": int(rows_before_feature_drop - rows_after_feature_drop),
        "exclude_recent_weeks": int(recent_rows_to_exclude),
        "top_n": int(top_n),
    }
    return result, current_vector, summary, metadata


def build_current_vector(current: pd.Series, means: pd.Series, stds: pd.Series) -> pd.DataFrame:
    rows = []
    for column in FEATURE_COLUMNS:
        value = current[column]
        rows.append(
            {
                "date": current["date"].strftime("%Y-%m-%d"),
                "feature": column,
                "current_value": value,
                "candidate_mean": means[column],
                "candidate_std": stds[column],
            }
        )
    return pd.DataFrame(rows)


def percentile_scale(series: pd.Series) -> int:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return 100
    if clean.min() >= 0 and clean.max() <= 1:
        return 100
    return 1


def summarize_similarity_result(result: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for weeks in FORWARD_HORIZONS:
        column = f"forward_return_{weeks}w"
        values = pd.to_numeric(result[column], errors="coerce").dropna()
        rows.append(
            {
                "horizon": f"{weeks}W",
                "similar_case_count": int(values.count()),
                "avg_forward_return": values.mean() if not values.empty else pd.NA,
                "median_forward_return": values.median() if not values.empty else pd.NA,
                "win_rate": (values > 0).mean() if not values.empty else pd.NA,
                "worst_forward_return": values.min() if not values.empty else pd.NA,
                "best_forward_return": values.max() if not values.empty else pd.NA,
            }
        )
    return pd.DataFrame(rows)


def write_hse_outputs(
    result: pd.DataFrame,
    current_vector: pd.DataFrame,
    summary: pd.DataFrame,
    metadata: dict[str, object],
    similarity_csv: Path = HSE_SIMILARITY_CSV,
    feature_vector_csv: Path = HSE_FEATURE_VECTOR_CSV,
    summary_csv: Path = HSE_SUMMARY_CSV,
    report_md: Path = HSE_REPORT_MD,
    historical_similarity_report_csv: Path = HISTORICAL_SIMILARITY_REPORT_CSV,
    historical_similarity_stats_csv: Path = HISTORICAL_SIMILARITY_STATS_CSV,
    historical_similarity_summary_md: Path = HISTORICAL_SIMILARITY_SUMMARY_MD,
    historical_similarity_cases_chart: Path = HISTORICAL_SIMILARITY_CASES_CHART,
) -> None:
    similarity_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(similarity_csv, index=False)
    current_vector.to_csv(feature_vector_csv, index=False)
    summary.to_csv(summary_csv, index=False)
    historical_report = build_historical_similarity_report(result, current_vector, metadata)
    historical_report.to_csv(
        historical_similarity_report_csv,
        index=False,
    )
    historical_stats = build_historical_similarity_stats(historical_report)
    historical_stats.to_csv(
        historical_similarity_stats_csv,
        index=False,
    )
    chart_warnings = build_historical_similarity_cases_chart(
        master=load_master_dataset(Path(str(metadata["master_path"]))),
        historical_report=historical_report,
        metadata=metadata,
        output_path=historical_similarity_cases_chart,
    )
    metadata["chart_warnings"] = chart_warnings
    historical_similarity_summary_md.write_text(
        build_historical_similarity_summary_report(historical_report, historical_stats),
        encoding="utf-8",
    )
    report_md.write_text(build_markdown_report(result, current_vector, summary, metadata), encoding="utf-8")


def build_historical_similarity_report(
    result: pd.DataFrame,
    current_vector: pd.DataFrame,
    metadata: dict[str, object],
) -> pd.DataFrame:
    current_values = current_vector.set_index("feature")["current_value"].to_dict()
    rows = []
    for row in result.head(20).itertuples(index=False):
        historical_date = pd.Timestamp(row.date).strftime("%Y-%m-%d")
        rows.append(
            {
                "current_date": metadata["latest_date"],
                "current_gold_close": metadata["latest_gold_close"],
                "current_mm_percentile": percentile_to_points(current_values["mm_net_percentile_156w"]),
                "current_producer_percentile": percentile_to_points(current_values["producer_net_percentile_156w"]),
                "current_oi_percentile": percentile_to_points(current_values["oi_percentile_156w"]),
                "historical_date": historical_date,
                "similarity_score": row.similarity_score,
                "historical_gold_close": row.gold_close,
                "historical_mm_percentile": percentile_to_points(row.mm_net_percentile_156w),
                "historical_producer_percentile": percentile_to_points(row.producer_net_percentile_156w),
                "historical_oi_percentile": percentile_to_points(row.oi_percentile_156w),
                "future_return_1w": row.forward_return_1w,
                "future_return_2w": row.forward_return_2w,
                "future_return_4w": row.forward_return_4w,
                "future_return_8w": row.forward_return_8w,
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "current_date",
            "current_gold_close",
            "current_mm_percentile",
            "current_producer_percentile",
            "current_oi_percentile",
            "historical_date",
            "similarity_score",
            "historical_gold_close",
            "historical_mm_percentile",
            "historical_producer_percentile",
            "historical_oi_percentile",
            "future_return_1w",
            "future_return_2w",
            "future_return_4w",
            "future_return_8w",
        ],
    )


def percentile_to_points(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    number = float(value)
    if 0 <= number <= 1:
        return number * 100
    return number


def build_historical_similarity_stats(historical_report: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for size in [5, 10, 20]:
        group = historical_report.head(size).copy()
        rows.append(
            {
                "group": f"Top {size}",
                "case_count": int(len(group)),
                **return_stats(group, 1),
                **return_stats(group, 2),
                **return_stats(group, 4),
                **return_stats(group, 8),
                "best_return_8w": best_return(group, 8),
                "worst_return_8w": worst_return(group, 8),
            }
        )
    return pd.DataFrame(
        rows,
        columns=[
            "group",
            "case_count",
            "avg_return_1w",
            "median_return_1w",
            "win_rate_1w",
            "avg_return_2w",
            "median_return_2w",
            "win_rate_2w",
            "avg_return_4w",
            "median_return_4w",
            "win_rate_4w",
            "avg_return_8w",
            "median_return_8w",
            "win_rate_8w",
            "best_return_8w",
            "worst_return_8w",
        ],
    )


def return_stats(frame: pd.DataFrame, weeks: int) -> dict[str, object]:
    values = return_values(frame, weeks)
    return {
        f"avg_return_{weeks}w": values.mean() if not values.empty else pd.NA,
        f"median_return_{weeks}w": values.median() if not values.empty else pd.NA,
        f"win_rate_{weeks}w": (values > 0).mean() if not values.empty else pd.NA,
    }


def best_return(frame: pd.DataFrame, weeks: int) -> object:
    values = return_values(frame, weeks)
    return values.max() if not values.empty else pd.NA


def worst_return(frame: pd.DataFrame, weeks: int) -> object:
    values = return_values(frame, weeks)
    return values.min() if not values.empty else pd.NA


def return_values(frame: pd.DataFrame, weeks: int) -> pd.Series:
    return pd.to_numeric(frame[f"future_return_{weeks}w"], errors="coerce").dropna()


def build_historical_similarity_summary_report(
    historical_report: pd.DataFrame,
    historical_stats: pd.DataFrame,
) -> str:
    if historical_report.empty:
        return "# Historical Similarity Summary\n\nN/A\n"

    current = historical_report.iloc[0]
    top10 = historical_report.head(10).copy()
    best_8w = historical_report.loc[pd.to_numeric(historical_report["future_return_8w"], errors="coerce").idxmax()]
    worst_8w = historical_report.loc[pd.to_numeric(historical_report["future_return_8w"], errors="coerce").idxmin()]
    classification = classify_market_state(
        current_mm_percentile=current["current_mm_percentile"],
        current_oi_percentile=current["current_oi_percentile"],
    )

    lines = [
        "# Historical Similarity Summary",
        "",
        "Historical Statistics / Research Reference.",
        "",
        "Reminder: classification is historical positioning only, not a trading recommendation.",
        "",
        "分類只是歷史定位，不是交易建議。",
        "",
        "## Hard Scope Limits",
        "",
        "- Does not connect to TradeDock.",
        "- Does not place orders.",
        "- Does not provide trading recommendations.",
        "- Does not include Options, OGR, or MMP.",
        "- Does not use AI or ML.",
        "- Does not optimize weights.",
        "- Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile.",
        "",
        "Future version candidates: MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.",
        "",
        "## Current Market State",
        "",
        f"- Latest data date: `{format_date(current['current_date'])}`",
        f"- Latest gold close: `{float(current['current_gold_close']):,.2f}`",
        f"- MM Percentile: `{format_percent_points(current['current_mm_percentile'])}`",
        f"- Producer Percentile: `{format_percent_points(current['current_producer_percentile'])}`",
        f"- OI Percentile: `{format_percent_points(current['current_oi_percentile'])}`",
        f"- Temporary market-state classification: `{classification}`",
        "",
        "## Top 10 Most Similar Historical Periods",
        "",
        top10_summary_to_markdown(top10),
        "",
        "## Top Similarity Outcome Statistics",
        "",
        outcome_stats_to_markdown(historical_stats),
        "",
        "## 8W Extremes In Top 20 Similar Cases",
        "",
        (
            f"- Best 8W case: `{format_date(best_8w['historical_date'])}` "
            f"with `{format_return(best_8w['future_return_8w'])}`"
        ),
        (
            f"- Worst 8W case: `{format_date(worst_8w['historical_date'])}` "
            f"with `{format_return(worst_8w['future_return_8w'])}`"
        ),
        "",
        "## Classification Rules",
        "",
        "- MM >= 80 and OI >= 60: Expansion / Momentum",
        "- MM >= 80 and OI < 60: Euphoria / Thin Momentum",
        "- MM 60-80: Healthy Bullish Positioning",
        "- MM 40-60: Neutral / Transition",
        "- MM 20-40: Accumulation / Weak Positioning",
        "- MM <= 20: Extreme Low / Potential Reset",
    ]
    return "\n".join(lines) + "\n"


def classify_market_state(current_mm_percentile: object, current_oi_percentile: object) -> str:
    mm = float(current_mm_percentile)
    oi = float(current_oi_percentile)
    if mm >= 80 and oi >= 60:
        return "Expansion / Momentum"
    if mm >= 80 and oi < 60:
        return "Euphoria / Thin Momentum"
    if 60 <= mm < 80:
        return "Healthy Bullish Positioning"
    if 40 <= mm < 60:
        return "Neutral / Transition"
    if 20 <= mm < 40:
        return "Accumulation / Weak Positioning"
    return "Extreme Low / Potential Reset"


def top10_summary_to_markdown(frame: pd.DataFrame) -> str:
    display = frame[
        [
            "historical_date",
            "similarity_score",
            "historical_gold_close",
            "historical_mm_percentile",
            "historical_producer_percentile",
            "historical_oi_percentile",
        ]
    ].copy()
    display["historical_date"] = display["historical_date"].apply(format_date)
    display["similarity_score"] = display["similarity_score"].apply(lambda value: f"{float(value):.2f}")
    display["historical_gold_close"] = display["historical_gold_close"].apply(lambda value: f"{float(value):,.2f}")
    for column in [
        "historical_mm_percentile",
        "historical_producer_percentile",
        "historical_oi_percentile",
    ]:
        display[column] = display[column].apply(format_percent_points)
    return display.to_markdown(index=False)


def outcome_stats_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "N/A"

    rows = []
    for row in frame.itertuples(index=False):
        rows.append(
            {
                "group": row.group,
                "case_count": row.case_count,
                "avg_return_1w": format_return(row.avg_return_1w),
                "win_rate_1w": format_rate(row.win_rate_1w),
                "avg_return_2w": format_return(row.avg_return_2w),
                "win_rate_2w": format_rate(row.win_rate_2w),
                "avg_return_4w": format_return(row.avg_return_4w),
                "win_rate_4w": format_rate(row.win_rate_4w),
                "avg_return_8w": format_return(row.avg_return_8w),
                "win_rate_8w": format_rate(row.win_rate_8w),
            }
        )
    return pd.DataFrame(rows).to_markdown(index=False)


def format_date(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def format_percent_points(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value):.2f}%"


def format_return(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def format_rate(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def build_historical_similarity_cases_chart(
    master: pd.DataFrame,
    historical_report: pd.DataFrame,
    metadata: dict[str, object],
    output_path: Path = HISTORICAL_SIMILARITY_CASES_CHART,
    pre_weeks: int = 12,
    post_weeks: int = 12,
) -> list[str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    top_cases = historical_report.head(5).copy()
    warnings: list[str] = []

    fig, ax = plt.subplots(figsize=(14, 7))
    case_paths: list[pd.DataFrame] = []
    colors = ["#2563eb", "#dc2626", "#16a34a", "#7c3aed", "#ea580c"]

    current_path, current_warning = build_indexed_event_window(
        master=master,
        event_date=pd.Timestamp(metadata["latest_date"]),
        pre_weeks=pre_weeks,
        post_weeks=0,
        require_full=True,
    )
    if current_warning:
        warnings.append(f"Current Market: {current_warning}")
    elif not current_path.empty:
        ax.plot(
            current_path["week_offset"],
            current_path["indexed_gold_path"],
            color="#111827",
            linewidth=3.0,
            linestyle="--",
            label=f"Current Market {metadata['latest_date']}",
            zorder=5,
        )

    for idx, row in enumerate(top_cases.itertuples(index=False)):
        historical_date = pd.Timestamp(row.historical_date)
        path, warning = build_indexed_event_window(
            master=master,
            event_date=historical_date,
            pre_weeks=pre_weeks,
            post_weeks=post_weeks,
            require_full=True,
        )
        label_date = historical_date.strftime("%Y-%m-%d")
        if warning:
            warnings.append(f"historical_date={label_date}: {warning}")
            continue

        path["historical_date"] = label_date
        path["similarity_score"] = row.similarity_score
        case_paths.append(path)

        ax.plot(
            path["week_offset"],
            path["indexed_gold_path"],
            linewidth=1.9,
            alpha=0.78,
            color=colors[idx % len(colors)],
            label=f"historical_date={label_date} | similarity_score={row.similarity_score:.2f}",
        )

    if case_paths:
        average_path = (
            pd.concat(case_paths, ignore_index=True)
            .groupby("week_offset", as_index=False)["indexed_gold_path"]
            .mean()
        )
        ax.plot(
            average_path["week_offset"],
            average_path["indexed_gold_path"],
            color="#111827",
            linewidth=3.4,
            label=f"Top 5 Average Path ({len(case_paths)} valid cases)",
            zorder=6,
        )
    else:
        warnings.append("No Top 5 historical case has a complete -12/+12 week event window.")

    ax.axvline(0, color="#111827", linewidth=1.2, linestyle=":", alpha=0.85)
    ax.axhline(100, color="#6b7280", linewidth=1, alpha=0.55)
    ax.set_title("Current Market vs Top 5 Similar Historical Cases", fontsize=16, pad=14)
    ax.set_xlabel("Week Offset")
    ax.set_ylabel("Indexed Gold Path (Week 0 = 100)")
    ax.set_xlim(-pre_weeks, post_weeks)
    ax.set_xticks(list(range(-pre_weeks, post_weeks + 1, 2)))
    ax.grid(True, axis="y", alpha=0.25)

    if warnings:
        warning_text = "Warnings: " + " | ".join(warnings[:3])
        if len(warnings) > 3:
            warning_text += f" | +{len(warnings) - 3} more"
        ax.text(
            0.01,
            0.01,
            warning_text,
            transform=ax.transAxes,
            fontsize=8.5,
            color="#92400e",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="#fef3c7", edgecolor="#f59e0b", alpha=0.92),
        )

    ax.legend(frameon=False, fontsize=9, loc="center left", bbox_to_anchor=(1.01, 0.5))
    fig.tight_layout()
    fig.savefig(output_path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return warnings


def build_indexed_event_window(
    master: pd.DataFrame,
    event_date: pd.Timestamp,
    pre_weeks: int,
    post_weeks: int,
    require_full: bool,
) -> tuple[pd.DataFrame, str | None]:
    data = master.dropna(subset=["date", "gold_close"]).sort_values("date").reset_index(drop=True)
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    matches = data.index[data["date"] == event_date].tolist()
    if not matches:
        return pd.DataFrame(), "event date not found"

    event_pos = matches[0]
    start = event_pos - pre_weeks
    end = event_pos + post_weeks
    if require_full and (start < 0 or end >= len(data)):
        return pd.DataFrame(), "insufficient history around selected event"

    start = max(0, start)
    end = min(len(data) - 1, end)
    window = data.iloc[start : end + 1].copy()
    base = data.loc[event_pos, "gold_close"]
    if pd.isna(base) or base == 0:
        return pd.DataFrame(), "invalid Week 0 gold_close"

    window["week_offset"] = range(start - event_pos, end - event_pos + 1)
    window["indexed_gold_path"] = window["gold_close"] / base * 100
    return window[["date", "week_offset", "gold_close", "indexed_gold_path"]], None


def build_markdown_report(
    result: pd.DataFrame,
    current_vector: pd.DataFrame,
    summary: pd.DataFrame,
    metadata: dict[str, object],
) -> str:
    lines = [
        "# GHPR v0.3 Historical Similarity Engine",
        "",
        "Historical Statistics / Research Reference.",
        "",
        "This engine compares the latest GHPR weekly state with past weekly states. It does not connect to TradeDock, does not place orders, and does not produce trading instructions.",
        "",
        "Hard scope limits: no TradeDock connection, no automated order placement, no trading recommendations, no Options / OGR / MMP inputs, no AI / ML, and no optimized weights.",
        "",
        "Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile. Future candidates include MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.",
        "",
        "## Current State",
        "",
        f"- Latest date: `{metadata['latest_date']}`",
        f"- Latest gold_close: `{metadata['latest_gold_close']:,.2f}`",
        f"- Master rows: `{metadata['master_rows']}`",
        f"- Historical candidates after recent-row exclusion: `{metadata['candidate_rows_before_feature_drop']}`",
        f"- Complete feature candidates: `{metadata['candidate_rows_after_feature_drop']}`",
        f"- Dropped incomplete candidates: `{metadata['dropped_incomplete_candidate_rows']}`",
        f"- Excluded latest rows: `{metadata['exclude_recent_weeks']}`",
        "",
        "## Similarity Method",
        "",
        "Version 0.3 uses a simple percentile-distance score. It does not use AI, machine learning, parameter fitting, or optimized weights.",
        "",
        "Distance uses only three fields: `mm_net_percentile_156w`, `producer_net_percentile_156w`, and `oi_percentile_156w`.",
        "",
        "`distance = abs(current_mm - historical_mm) + abs(current_producer - historical_producer) + abs(current_oi - historical_oi)`",
        "",
        "`normalized_distance = distance / 300 * 100`",
        "",
        "`similarity_score = 100 - normalized_distance`",
        "",
        "The engine converts dataset percentiles to 0-100 percentile points before scoring. Higher score means a closer historical match.",
        "",
        "## Current Feature Vector",
        "",
        feature_vector_to_markdown(current_vector),
        "",
        "## Top Historical Matches",
        "",
        dataframe_to_markdown(
            result[
                [
                    "rank",
                    "date",
                    "gold_close",
                    "similarity_score",
                    "distance",
                    "normalized_distance",
                    "mm_net_percentile_156w",
                    "producer_net_percentile_156w",
                    "oi_percentile_156w",
                    "gold_return_1w",
                    "gold_return_2w",
                    "gold_return_4w",
                    "gold_return_8w",
                    "forward_return_1w",
                    "forward_return_2w",
                    "forward_return_4w",
                    "forward_return_8w",
                ]
            ],
            percent_features=True,
        ),
        "",
        "## Similar Case Forward Return Summary",
        "",
        dataframe_to_markdown(summary, percent_features=True),
        "",
        "## Output Files",
        "",
        f"- `{HSE_SIMILARITY_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{HSE_FEATURE_VECTOR_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{HSE_SUMMARY_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{HISTORICAL_SIMILARITY_REPORT_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{HISTORICAL_SIMILARITY_STATS_CSV.relative_to(PROJECT_ROOT)}`",
        f"- `{HISTORICAL_SIMILARITY_SUMMARY_MD.relative_to(PROJECT_ROOT)}`",
        f"- `{HISTORICAL_SIMILARITY_CASES_CHART.relative_to(PROJECT_ROOT)}`",
    ]
    if metadata.get("chart_warnings"):
        lines.extend(
            [
                "",
                "## Historical Case Viewer Warnings",
                "",
                *[f"- {warning}" for warning in metadata["chart_warnings"]],
            ]
        )
    return "\n".join(lines) + "\n"


def dataframe_to_markdown(frame: pd.DataFrame, percent_features: bool = False) -> str:
    if frame.empty:
        return "N/A"

    formatted = frame.copy()
    for column in formatted.columns:
        if column == "date":
            formatted[column] = pd.to_datetime(formatted[column], errors="coerce").dt.strftime("%Y-%m-%d")
        elif is_percent_like(column, percent_features):
            formatted[column] = formatted[column].apply(lambda value: format_percent(value))
        elif pd.api.types.is_numeric_dtype(formatted[column]):
            formatted[column] = formatted[column].apply(lambda value: format_number(value))
    return formatted.to_markdown(index=False)


def feature_vector_to_markdown(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "N/A"

    formatted = frame.copy()
    value_columns = ["current_value", "candidate_mean", "candidate_std"]
    for column in value_columns:
        formatted[column] = pd.to_numeric(formatted[column], errors="coerce")

    percent_rows = formatted["feature"].str.contains("percentile|gold_return", regex=True, na=False)
    for column in value_columns:
        display_values = []
        for is_percent, value in zip(percent_rows, formatted[column], strict=False):
            display_values.append(format_percent(value) if is_percent else format_number(value))
        formatted[column] = display_values
    return formatted.to_markdown(index=False)


def is_percent_like(column: str, percent_features: bool) -> bool:
    if not percent_features:
        return False
    return (
        column in FEATURE_COLUMNS
        or column.startswith("gold_return_")
        or column.startswith("forward_return_")
        or column in {"avg_forward_return", "median_forward_return", "win_rate", "worst_forward_return", "best_forward_return"}
    )


def format_percent(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value) * 100:.2f}%"


def format_number(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value):,.4f}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GHPR v0.3 Historical Similarity Engine.")
    parser.add_argument("--master-path", type=Path, default=OUTPUT_MASTER_WEEKLY)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--exclude-recent-weeks", type=int, default=8)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result, current_vector, summary, metadata = compute_current_similarity(
        master_path=args.master_path,
        top_n=args.top_n,
        exclude_recent_weeks=args.exclude_recent_weeks,
    )
    write_hse_outputs(result, current_vector, summary, metadata)
    print(f"Wrote {HSE_SIMILARITY_CSV}")
    print(f"Wrote {HSE_REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

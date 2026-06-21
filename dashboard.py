from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.candlestick_viewer import (
    CANDLESTICK_SOURCE_NOTE_EN,
    CANDLESTICK_SOURCE_NOTE_ZH,
    VIEW_RANGE_OPTIONS,
    build_candlestick_figure,
    candlestick_title,
    load_gold_daily_ohlc,
    ohlc_for_window,
    week_window_for_event,
)
from src.chart_layout import apply_ghpr_plotly_layout
from src.historical_similarity_engine import (
    DEFAULT_EXCLUDE_RECENT_WEEKS,
    build_historical_similarity_report,
    build_historical_similarity_stats,
    compute_current_similarity,
)
from src.update_pipeline import (
    UPDATE_LOG_PATH,
    build_freshness_status,
    latest_cftc_available_date_from_current_file,
    latest_dataset_date,
    run_update_pipeline,
)


PROJECT_ROOT = Path(__file__).resolve().parent
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
FACTOR_PATH = PROJECT_ROOT / "outputs" / "reports" / "single_factor_decile_analysis.csv"
REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "ghpr_factor_report.md"
PERCENTILE_AUDIT_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "percentile_definition_audit_report.md"
)
PERCENTILE_SCORECARD_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "percentile_definition_scorecard.csv"
)
PERCENTILE_RECOMMENDATION_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "percentile_definition_recommendation.csv"
)
MM_DEFINITION_AUDIT_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_percentile_definition_audit_report.md"
)
MM_DEFINITION_SCORECARD_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_percentile_definition_scorecard.csv"
)
MM_LIFECYCLE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_lifecycle_dataset.csv"
MM_LIFECYCLE_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "mm_lifecycle_summary.md"
MM_LIFECYCLE_LEAD_LAG_PATH = PROJECT_ROOT / "outputs" / "reports" / "mm_lifecycle_lead_lag.csv"
MM_LIFECYCLE_STATE_ANALYSIS_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_lifecycle_state_analysis.csv"
)
MM_TRAJECTORY_SIMILARITY_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_trajectory_similarity.csv"
)
MM_STRUCTURE_DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "mm_structure_lifecycle_dataset.csv"
MM_STRUCTURE_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_structure_lifecycle_summary.md"
)
MM_STRUCTURE_LEAD_LAG_PATH = PROJECT_ROOT / "outputs" / "reports" / "mm_structure_lead_lag.csv"
MM_STRUCTURE_STATE_ANALYSIS_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_structure_state_analysis.csv"
)
MM_STRUCTURE_CONTRIBUTION_ANALYSIS_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_structure_contribution_analysis.csv"
)
MM_VELOCITY_WINDOW_DATASET_PATH = (
    PROJECT_ROOT / "data" / "processed" / "mm_velocity_window_dataset.csv"
)
MM_VELOCITY_WINDOW_SCORECARD_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_velocity_window_scorecard.csv"
)
MM_VELOCITY_WINDOW_BUCKET_ANALYSIS_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_velocity_window_bucket_analysis.csv"
)
MM_VELOCITY_WINDOW_TRAIN_TEST_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_velocity_window_train_test.csv"
)
MM_VELOCITY_WINDOW_SUMMARY_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_velocity_window_summary.md"
)
MM_VELOCITY_WINDOW_REVIEW_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_velocity_window_review.md"
)
MM_VELOCITY_READING_LAYER_PATH = (
    PROJECT_ROOT / "data" / "processed" / "mm_velocity_reading_layer.csv"
)
MM_VELOCITY_READING_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "mm_velocity_reading_layer.md"
)
HISTORICAL_SIMILARITY_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_report.csv"
)
HISTORICAL_SIMILARITY_STATS_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_stats.csv"
)
HUB_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "reports" / "ghpr_summary_for_hub.json"
DATA_FRESHNESS_DIAGNOSTICS_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "data_freshness_diagnostics.json"
)
HISTORICAL_SIMILARITY_CASES_CHART_PATH = (
    PROJECT_ROOT / "outputs" / "charts" / "historical_similarity_cases.png"
)
GOLD_DAILY_OHLC_PATH = PROJECT_ROOT / "data" / "processed" / "gold_daily_ohlc.csv"
PERCENTILE_AUDIT_CHARTS = [
    ("MM Percentile Window Comparison", PROJECT_ROOT / "outputs" / "charts" / "mm_percentile_window_comparison.png"),
    (
        "Producer Percentile Window Comparison",
        PROJECT_ROOT / "outputs" / "charts" / "producer_percentile_window_comparison.png",
    ),
    ("OI Percentile Window Comparison", PROJECT_ROOT / "outputs" / "charts" / "oi_percentile_window_comparison.png"),
    ("Definition Scorecard", PROJECT_ROOT / "outputs" / "charts" / "percentile_definition_scorecard.png"),
    (
        "MM Windows vs 8W Historical Following Performance",
        PROJECT_ROOT / "outputs" / "charts" / "mm_52_104_156_260_vs_forward_8w.png",
    ),
    (
        "Producer Windows vs 8W Historical Following Performance",
        PROJECT_ROOT / "outputs" / "charts" / "producer_52_104_156_260_vs_forward_8w.png",
    ),
    (
        "OI Windows vs 8W Historical Following Performance",
        PROJECT_ROOT / "outputs" / "charts" / "oi_52_104_156_260_vs_forward_8w.png",
    ),
]
MM_DEFINITION_AUDIT_CHARTS = [
    (
        "MM Percentile Window Comparison",
        PROJECT_ROOT / "outputs" / "charts" / "mm_percentile_window_comparison.png",
    ),
    (
        "MM Definition Scorecard",
        PROJECT_ROOT / "outputs" / "charts" / "mm_definition_scorecard.png",
    ),
    (
        "MM Bucket 8W Following Performance",
        PROJECT_ROOT / "outputs" / "charts" / "mm_bucket_forward_8w_by_definition.png",
    ),
    (
        "MM Definition Train / Test Comparison",
        PROJECT_ROOT / "outputs" / "charts" / "mm_definition_train_test_comparison.png",
    ),
]
MM_LIFECYCLE_CHARTS = [
    (
        "Gold vs MM Lifecycle",
        PROJECT_ROOT / "outputs" / "charts" / "gold_vs_mm_lifecycle.png",
    ),
    (
        "MM Velocity / Acceleration",
        PROJECT_ROOT / "outputs" / "charts" / "mm_velocity_acceleration.png",
    ),
    (
        "MM Lead-Lag Correlation",
        PROJECT_ROOT / "outputs" / "charts" / "mm_lead_lag_correlation.png",
    ),
    (
        "MM Lifecycle State Outcomes",
        PROJECT_ROOT / "outputs" / "charts" / "mm_lifecycle_state_outcomes.png",
    ),
    (
        "MM Trajectory Similarity Cases",
        PROJECT_ROOT / "outputs" / "charts" / "mm_trajectory_similarity_cases.png",
    ),
]
MM_STRUCTURE_CHARTS = [
    (
        "Gold vs MM Long / Short / Net",
        PROJECT_ROOT / "outputs" / "charts" / "gold_vs_mm_long_short_net.png",
    ),
    (
        "MM Long / Short / Net Percentiles",
        PROJECT_ROOT / "outputs" / "charts" / "mm_long_short_net_percentiles.png",
    ),
    (
        "MM Structure Velocity",
        PROJECT_ROOT / "outputs" / "charts" / "mm_structure_velocity.png",
    ),
    (
        "MM Structure Lead-Lag Correlation",
        PROJECT_ROOT / "outputs" / "charts" / "mm_structure_lead_lag_correlation.png",
    ),
    (
        "MM Structure State Outcomes",
        PROJECT_ROOT / "outputs" / "charts" / "mm_structure_state_outcomes.png",
    ),
]
MM_VELOCITY_WINDOW_CHARTS = [
    (
        "Velocity Window Scorecard",
        PROJECT_ROOT / "outputs" / "charts" / "mm_velocity_window_scorecard.png",
    ),
    (
        "MM Long Velocity Windows",
        PROJECT_ROOT / "outputs" / "charts" / "mm_long_velocity_windows.png",
    ),
    (
        "MM Short Velocity Windows",
        PROJECT_ROOT / "outputs" / "charts" / "mm_short_velocity_windows.png",
    ),
    (
        "MM Net Velocity Windows",
        PROJECT_ROOT / "outputs" / "charts" / "mm_net_velocity_windows.png",
    ),
    (
        "Velocity Window vs 8W Following Return",
        PROJECT_ROOT / "outputs" / "charts" / "mm_velocity_window_forward_8w.png",
    ),
    (
        "Velocity Window Lead-Lag",
        PROJECT_ROOT / "outputs" / "charts" / "mm_velocity_window_lead_lag.png",
    ),
]

MM_FACTOR = "mm_net_percentile_156w"
FORWARD_HORIZONS = [1, 2, 4, 8]
HSE_EXCLUDE_RECENT_OPTIONS = [8, 26, 52, 104]
GOLD_SOURCE_TEXT = "COMEX GC futures proxy via Yahoo Finance GC=F"
RESEARCH_WARNING_ZH = "此系統為歷史統計研究工具，不是交易訊號，不提供買賣建議。"
RESEARCH_WARNING_EN = (
    "Historical statistics only. Not a trading signal. Not financial advice."
)
FUTURES_PROXY_NOTE = (
    "This is a futures proxy, not official LBMA PM benchmark or broker XAUUSD spot."
)
MM_STATE_ORDER = [
    "MM_EXTREME_LOW",
    "MM_LOW",
    "MM_NEUTRAL",
    "MM_HIGH",
    "MM_EXTREME_HIGH",
]
VELOCITY_WINDOW_DEFINITION_ROWS = [
    {
        "Component": "Long Velocity",
        "Current Baseline": "8W",
        "Research Candidate": "26W",
        "Interpretation": "中期建倉 / 減倉週期",
    },
    {
        "Component": "Short Velocity",
        "Current Baseline": "8W",
        "Research Candidate": "2W / 4W",
        "Interpretation": "短線壓力 / 空單回補週期",
    },
    {
        "Component": "Net Velocity",
        "Current Baseline": "8W",
        "Research Candidate": "26W",
        "Interpretation": "綜合中期資金週期",
    },
]
VELOCITY_READING_SNAPSHOT_COLUMNS = [
    "date",
    "long_baseline_8w",
    "long_candidate_26w",
    "long_alignment_status",
    "short_baseline_8w",
    "short_candidate_2w",
    "short_candidate_4w",
    "short_candidate_fast_avg",
    "short_alignment_status",
    "net_baseline_8w",
    "net_candidate_26w",
    "net_alignment_status",
    "overall_velocity_reading",
]
TEXT_COLUMNS = {
    "gold_price_source",
    "gold_price_benchmark_recommendation",
    "gold_anomaly_reason",
    "sample_split",
    "gold_regime",
    "mm_state",
}


st.set_page_config(
    page_title="GHPR Online Dashboard v0.4",
    page_icon="GHPR",
    layout="wide",
)

st.markdown(
    """
<style>
.ghpr-chart-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin-top: 1.25rem;
  margin-bottom: 0.6rem;
  color: #111827;
}
</style>
""",
    unsafe_allow_html=True,
)


def render_interactive_chart(
    title: str,
    fig: go.Figure,
    key: str,
    height: int = 520,
    config: dict | None = None,
    show_legend: bool = True,
    has_range_slider: bool = False,
) -> None:
    st.markdown(f"<div class='ghpr-chart-title'>{title}</div>", unsafe_allow_html=True)
    render_fig = go.Figure(fig)
    apply_ghpr_plotly_layout(
        render_fig,
        title=None,
        height=height,
        show_legend=show_legend,
        has_range_slider=has_range_slider,
        uirevision=key,
    )
    chart_config = {"responsive": True, **(config or {})}
    st.plotly_chart(render_fig, use_container_width=True, config=chart_config, key=key)


@st.cache_data(show_spinner=False)
def load_master_dataset() -> pd.DataFrame:
    if not MASTER_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MASTER_PATH)
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in frame.columns:
        if column != "date" and column not in TEXT_COLUMNS:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "date" in frame.columns and "gold_close" in frame.columns:
        frame = frame.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
        frame = add_forward_return_columns(frame)
    if MM_FACTOR in frame.columns:
        frame["mm_state"] = frame[MM_FACTOR].apply(mm_state_from_percentile)
    return frame


@st.cache_data(show_spinner=False)
def load_factor_dataset() -> pd.DataFrame:
    if not FACTOR_PATH.exists():
        return pd.DataFrame()
    return pd.read_csv(FACTOR_PATH)


@st.cache_data(show_spinner=False)
def load_gold_daily_ohlc_dataset() -> pd.DataFrame:
    return load_gold_daily_ohlc(GOLD_DAILY_OHLC_PATH)


@st.cache_data(show_spinner=False)
def load_historical_similarity_report() -> pd.DataFrame:
    if not HISTORICAL_SIMILARITY_REPORT_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(HISTORICAL_SIMILARITY_REPORT_PATH)
    for column in ["current_date", "historical_date"]:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    for column in frame.columns:
        if column not in {"current_date", "historical_date"}:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_historical_similarity_stats() -> pd.DataFrame:
    if not HISTORICAL_SIMILARITY_STATS_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(HISTORICAL_SIMILARITY_STATS_PATH)
    for column in frame.columns:
        if column != "group":
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_hub_summary() -> dict:
    if not HUB_SUMMARY_PATH.exists():
        return {}
    try:
        return json.loads(HUB_SUMMARY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


@st.cache_data(show_spinner=False)
def load_data_freshness_diagnostics() -> dict:
    if not DATA_FRESHNESS_DIAGNOSTICS_PATH.exists():
        return {}
    try:
        return json.loads(DATA_FRESHNESS_DIAGNOSTICS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


@st.cache_data(show_spinner=False)
def load_historical_similarity_for_exclusion(
    exclude_recent_weeks: int,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    try:
        result, current_vector, _summary, metadata = compute_current_similarity(
            master_path=MASTER_PATH,
            top_n=20,
            exclude_recent_weeks=exclude_recent_weeks,
        )
        report = build_historical_similarity_report(result, current_vector, metadata)
        stats = build_historical_similarity_stats(report)
        report["current_date"] = pd.to_datetime(report["current_date"], errors="coerce")
        report["historical_date"] = pd.to_datetime(report["historical_date"], errors="coerce")
        for column in report.columns:
            if column not in {"current_date", "historical_date"}:
                report[column] = pd.to_numeric(report[column], errors="coerce")
        for column in stats.columns:
            if column != "group":
                stats[column] = pd.to_numeric(stats[column], errors="coerce")
        return report, stats, metadata
    except Exception as error:
        fallback_report = load_historical_similarity_report()
        fallback_stats = load_historical_similarity_stats()
        return fallback_report, fallback_stats, {
            "exclude_recent_weeks": exclude_recent_weeks,
            "dashboard_hse_error": str(error),
            "fallback": True,
        }


@st.cache_data(show_spinner=False)
def load_research_report() -> str:
    if not REPORT_PATH.exists():
        return "N/A"
    return REPORT_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_percentile_audit_report() -> str:
    if not PERCENTILE_AUDIT_REPORT_PATH.exists():
        return "N/A"
    return PERCENTILE_AUDIT_REPORT_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_percentile_scorecard() -> pd.DataFrame:
    if not PERCENTILE_SCORECARD_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(PERCENTILE_SCORECARD_PATH)
    for column in ["train_score", "test_score", "stability_score"]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "recommended" in frame.columns:
        frame["recommended"] = frame["recommended"].astype(str).str.lower().isin(
            {"true", "1", "yes"}
        )
    return frame


@st.cache_data(show_spinner=False)
def load_percentile_recommendation() -> pd.DataFrame:
    if not PERCENTILE_RECOMMENDATION_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(PERCENTILE_RECOMMENDATION_PATH)
    for column in frame.columns:
        if "score" in column:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_definition_audit_report() -> str:
    if not MM_DEFINITION_AUDIT_REPORT_PATH.exists():
        return "N/A"
    return MM_DEFINITION_AUDIT_REPORT_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_mm_definition_scorecard() -> pd.DataFrame:
    if not MM_DEFINITION_SCORECARD_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_DEFINITION_SCORECARD_PATH)
    for column in [
        "rank_corr",
        "high_low_spread",
        "weekly_change_avg",
        "train_rank_corr",
        "test_rank_corr",
        "information_score",
        "stability_score",
        "train_test_score",
        "interpretability_score",
        "total_score",
    ]:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "recommended" in frame.columns:
        frame["recommended"] = frame["recommended"].astype(str).str.lower().isin(
            {"true", "1", "yes"}
        )
    return frame


@st.cache_data(show_spinner=False)
def load_mm_lifecycle_dataset() -> pd.DataFrame:
    if not MM_LIFECYCLE_DATASET_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_LIFECYCLE_DATASET_PATH)
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    text_columns = {"mm_lifecycle_state"}
    for column in frame.columns:
        if column != "date" and column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values("date").reset_index(drop=True) if "date" in frame.columns else frame


@st.cache_data(show_spinner=False)
def load_mm_lifecycle_state_analysis() -> pd.DataFrame:
    if not MM_LIFECYCLE_STATE_ANALYSIS_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_LIFECYCLE_STATE_ANALYSIS_PATH)
    for column in frame.columns:
        if column != "mm_lifecycle_state":
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_lifecycle_lead_lag() -> pd.DataFrame:
    if not MM_LIFECYCLE_LEAD_LAG_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_LIFECYCLE_LEAD_LAG_PATH)
    text_columns = {"mm_feature", "gold_horizon", "interpretation"}
    for column in frame.columns:
        if column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_trajectory_similarity() -> pd.DataFrame:
    if not MM_TRAJECTORY_SIMILARITY_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_TRAJECTORY_SIMILARITY_PATH)
    for column in ["historical_start_date", "historical_end_date"]:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    text_columns = {"window", "current_path", "historical_path"}
    for column in frame.columns:
        if column not in text_columns and not column.endswith("_date"):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_lifecycle_summary() -> str:
    if not MM_LIFECYCLE_SUMMARY_PATH.exists():
        return "N/A"
    return MM_LIFECYCLE_SUMMARY_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_mm_structure_dataset() -> pd.DataFrame:
    if not MM_STRUCTURE_DATASET_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_STRUCTURE_DATASET_PATH)
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    text_columns = {"mm_structure_state", "mm_structure_contribution_state"}
    for column in frame.columns:
        if column != "date" and column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values("date").reset_index(drop=True) if "date" in frame.columns else frame


@st.cache_data(show_spinner=False)
def load_mm_structure_state_analysis() -> pd.DataFrame:
    if not MM_STRUCTURE_STATE_ANALYSIS_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_STRUCTURE_STATE_ANALYSIS_PATH)
    for column in frame.columns:
        if column != "mm_structure_state":
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_structure_contribution_analysis() -> pd.DataFrame:
    if not MM_STRUCTURE_CONTRIBUTION_ANALYSIS_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_STRUCTURE_CONTRIBUTION_ANALYSIS_PATH)
    for column in frame.columns:
        if column != "mm_structure_contribution_state":
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_structure_lead_lag() -> pd.DataFrame:
    if not MM_STRUCTURE_LEAD_LAG_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_STRUCTURE_LEAD_LAG_PATH)
    text_columns = {"mm_feature", "gold_horizon", "interpretation"}
    for column in frame.columns:
        if column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_structure_summary() -> str:
    if not MM_STRUCTURE_SUMMARY_PATH.exists():
        return "N/A"
    return MM_STRUCTURE_SUMMARY_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_mm_velocity_window_dataset() -> pd.DataFrame:
    if not MM_VELOCITY_WINDOW_DATASET_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_VELOCITY_WINDOW_DATASET_PATH)
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in frame.columns:
        if column != "date":
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values("date").reset_index(drop=True) if "date" in frame.columns else frame


@st.cache_data(show_spinner=False)
def load_mm_velocity_window_scorecard() -> pd.DataFrame:
    if not MM_VELOCITY_WINDOW_SCORECARD_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_VELOCITY_WINDOW_SCORECARD_PATH)
    text_columns = {"feature_group", "window", "feature_name", "horizon", "reason"}
    for column in frame.columns:
        if column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "recommended" in frame.columns:
        frame["recommended"] = frame["recommended"].astype(str).str.lower().isin({"true", "1", "yes"})
    if "direction_consistency" in frame.columns:
        frame["direction_consistency"] = frame["direction_consistency"].astype(str).str.lower().isin(
            {"true", "1", "yes"}
        )
    return frame


@st.cache_data(show_spinner=False)
def load_mm_velocity_window_bucket_analysis() -> pd.DataFrame:
    if not MM_VELOCITY_WINDOW_BUCKET_ANALYSIS_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_VELOCITY_WINDOW_BUCKET_ANALYSIS_PATH)
    text_columns = {"feature_group", "window", "feature_name", "bucket"}
    for column in frame.columns:
        if column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def load_mm_velocity_window_train_test() -> pd.DataFrame:
    if not MM_VELOCITY_WINDOW_TRAIN_TEST_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_VELOCITY_WINDOW_TRAIN_TEST_PATH)
    text_columns = {"feature_group", "window", "feature_name", "horizon"}
    for column in frame.columns:
        if column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if "direction_consistency" in frame.columns:
        frame["direction_consistency"] = frame["direction_consistency"].astype(str).str.lower().isin(
            {"true", "1", "yes"}
        )
    return frame


@st.cache_data(show_spinner=False)
def load_mm_velocity_window_summary() -> str:
    if not MM_VELOCITY_WINDOW_SUMMARY_PATH.exists():
        return "N/A"
    return MM_VELOCITY_WINDOW_SUMMARY_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_mm_velocity_window_review() -> str:
    if not MM_VELOCITY_WINDOW_REVIEW_PATH.exists():
        return "N/A"
    return MM_VELOCITY_WINDOW_REVIEW_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_mm_velocity_reading_layer() -> pd.DataFrame:
    if not MM_VELOCITY_READING_LAYER_PATH.exists():
        return pd.DataFrame()
    frame = pd.read_csv(MM_VELOCITY_READING_LAYER_PATH)
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    text_columns = {
        "long_alignment_status",
        "short_alignment_status",
        "net_alignment_status",
        "overall_velocity_reading",
        "mm_structure_state",
    }
    for column in frame.columns:
        if column != "date" and column not in text_columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.sort_values("date").reset_index(drop=True) if "date" in frame.columns else frame


@st.cache_data(show_spinner=False)
def load_mm_velocity_reading_report() -> str:
    if not MM_VELOCITY_READING_REPORT_PATH.exists():
        return "N/A"
    return MM_VELOCITY_READING_REPORT_PATH.read_text(encoding="utf-8", errors="replace")


@st.cache_data(show_spinner=False)
def load_update_log() -> str:
    if not UPDATE_LOG_PATH.exists():
        return "N/A"
    return UPDATE_LOG_PATH.read_text(encoding="utf-8", errors="replace")


def add_forward_return_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for weeks in FORWARD_HORIZONS:
        out[f"forward_return_{weeks}w"] = (
            out["gold_close"].shift(-weeks) / out["gold_close"] - 1
        )
    return out


def percent_points(value: object) -> float | None:
    if pd.isna(value):
        return None
    number = float(value)
    return number * 100 if abs(number) <= 1 else number


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


def missing_columns(frame: pd.DataFrame, required: list[str]) -> list[str]:
    return [column for column in required if column not in frame.columns]


def require_columns(frame: pd.DataFrame, required: list[str]) -> bool:
    missing = missing_columns(frame, required)
    if missing:
        st.error("Missing columns: " + ", ".join(missing))
        return False
    return True


def latest_row(master: pd.DataFrame) -> pd.Series | None:
    if master.empty or "date" not in master.columns:
        return None
    return master.sort_values("date").iloc[-1]


def fmt_date(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def latest_dataset_date_from_master(master: pd.DataFrame) -> str:
    latest = latest_row(master)
    if latest is None:
        return "N/A"
    return fmt_date(latest.get("date"))


def latest_cftc_available_date() -> str:
    return latest_cftc_available_date_from_current_file() or "N/A"


def date_semantics_note() -> str:
    return (
        "Last updated time is when GHPR files were refreshed. "
        "Dataset/COT date is the latest weekly report date available in the research dataset."
    )


def render_component_date_context(component_name: str, component_date: str) -> None:
    master_date = latest_dataset_date() or "N/A"
    cftc_date = latest_cftc_available_date()
    st.caption(
        f"{component_name} data date: `{component_date}` | "
        f"Master dataset date: `{master_date}` | Latest CFTC available date: `{cftc_date}`"
    )
    st.caption(date_semantics_note())
    if component_date != "N/A" and master_date != "N/A" and component_date != master_date:
        st.warning(
            f"{component_name} is not aligned with the master dataset date. "
            "Please rerun a full refresh if this persists."
        )


def fmt_number(value: object, digits: int = 2) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{float(value):,.{digits}f}"


def fmt_int(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return f"{int(float(value)):,}"


def fmt_percent(value: object, digits: int = 2, input_scale: str = "return") -> str:
    if pd.isna(value):
        return "N/A"
    number = float(value)
    if input_scale in {"return", "fraction"}:
        number *= 100
    return f"{number:.{digits}f}%"


def scalar_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def top20_stats_row(historical_stats: pd.DataFrame) -> pd.Series | None:
    if historical_stats.empty or "group" not in historical_stats.columns:
        return None
    top20 = historical_stats[historical_stats["group"].astype(str).str.lower().eq("top 20")]
    if top20.empty:
        return None
    return top20.iloc[0]


def classify_historical_tendency(stats_row: pd.Series | None) -> str:
    """
    Classify Top 20 historical following stats into:
    - tailwind
    - mixed
    - risk_off_caution
    - high_risk
    - na
    """
    if stats_row is None:
        return "na"

    avg_1w = scalar_float(stats_row.get("avg_return_1w"))
    avg_2w = scalar_float(stats_row.get("avg_return_2w"))
    avg_4w = scalar_float(stats_row.get("avg_return_4w"))
    avg_8w = scalar_float(stats_row.get("avg_return_8w"))
    win_8w = scalar_float(stats_row.get("win_rate_8w"))

    if any(value is None for value in [avg_1w, avg_2w, avg_4w, avg_8w, win_8w]):
        return "na"
    if avg_1w < 0 and avg_4w < 0 and avg_8w < 0 and win_8w < 0.45:
        return "risk_off_caution"
    if avg_1w < 0 and avg_2w < 0 and avg_4w < 0 and avg_8w < 0 and win_8w < 0.35:
        return "high_risk"
    if avg_1w > 0 and avg_4w > 0 and avg_8w > 0 and win_8w >= 0.55:
        return "tailwind"
    return "mixed"


def build_historical_tendency_summary(latest_row: pd.Series | None, historical_stats: pd.DataFrame) -> dict:
    """
    Return a dict with:
    - tendency_label
    - tendency_color
    - plain_language_summary_zh
    - risk_context_zh
    - interpretation_limit_zh
    - monitor_zh
    - stats_used
    """
    stats_row = top20_stats_row(historical_stats)
    status = classify_historical_tendency(stats_row)
    copy = {
        "tailwind": {
            "tendency_label": "Historical Tendency: Positive Sample Tilt",
            "tendency_color": "#16a34a",
            "plain_language_summary_zh": "歷史相似案例後續表現偏正向；這只代表歷史統計傾向。",
            "risk_context_zh": "歷史樣本偏正向，但 GHPR 不提供進出場點，不能轉換為操作結論。",
            "interpretation_limit_zh": "不要把此傾向單獨解讀成市場方向；仍需搭配其他研究資料。",
            "monitor_zh": "觀察價格結構、OI 變化、成交量與後續資料更新。",
        },
        "mixed": {
            "tendency_label": "Historical Tendency: Mixed Sample",
            "tendency_color": "#ca8a04",
            "plain_language_summary_zh": "歷史相似案例分布分歧，目前只能視為混合樣本狀態。",
            "risk_context_zh": "歷史樣本沒有一致分布，適合降低單一假設強度並觀察後續資料。",
            "interpretation_limit_zh": "不可把混合樣本解讀成明確市場方向或操作依據。",
            "monitor_zh": "觀察價格結構、OI 變化、成交量與後續資料更新。",
        },
        "risk_off_caution": {
            "tendency_label": "Historical Tendency: Weak Sample Tilt",
            "tendency_color": "#f97316",
            "plain_language_summary_zh": "目前歷史相似案例後續表現偏弱；這只是歷史樣本傾向。",
            "risk_context_zh": "歷史樣本偏弱，代表研究背景需提高風險意識，但不等於操作方向。",
            "interpretation_limit_zh": "不可把偏弱樣本直接解讀成市場方向或交易結論。",
            "monitor_zh": "觀察價格結構、OI 變化、成交量與後續資料更新。",
        },
        "high_risk": {
            "tendency_label": "Historical Tendency: Weak High-Dispersion Sample",
            "tendency_color": "#dc2626",
            "plain_language_summary_zh": "歷史相似案例短中期後續表現偏弱，且需留意樣本波動；這不是交易結論。",
            "risk_context_zh": "歷史樣本顯示風險背景偏高，但只代表統計分布。",
            "interpretation_limit_zh": "不可把高風險背景單獨解讀成明確市場方向。",
            "monitor_zh": "觀察價格結構、OI 變化、成交量與後續資料更新。",
        },
        "na": {
            "tendency_label": "Historical Tendency: N/A",
            "tendency_color": "#64748b",
            "plain_language_summary_zh": "目前歷史相似案例統計不足，暫不做定位判讀。",
            "risk_context_zh": "資料不足，暫不做歷史風險背景判讀。",
            "interpretation_limit_zh": "資料不足時不應做任何方向性推論。",
            "monitor_zh": "等待資料更新完成後，再查看歷史統計研究結果。",
        },
    }

    stats_used = {
        "group": stats_row.get("group") if stats_row is not None else "Top 20",
        "avg_1w": scalar_float(stats_row.get("avg_return_1w")) if stats_row is not None else None,
        "avg_2w": scalar_float(stats_row.get("avg_return_2w")) if stats_row is not None else None,
        "avg_4w": scalar_float(stats_row.get("avg_return_4w")) if stats_row is not None else None,
        "avg_8w": scalar_float(stats_row.get("avg_return_8w")) if stats_row is not None else None,
        "win_8w": scalar_float(stats_row.get("win_rate_8w")) if stats_row is not None else None,
    }
    latest_snapshot = {
        "date": fmt_date(latest_row.get("date")) if latest_row is not None else "N/A",
        "gold_close": fmt_number(latest_row.get("gold_close")) if latest_row is not None else "N/A",
    }
    return {
        **copy[status],
        "status_key": status,
        "stats_used": stats_used,
        "latest_snapshot": latest_snapshot,
    }


def render_historical_tendency_summary(summary: dict) -> None:
    """
    Render Streamlit cards / info boxes for historical tendency interpretation.
    """
    st.subheader("GHPR Historical Tendency / 歷史統計傾向")
    st.caption("Historical Tendency is historical statistics only. Not a trading signal. Not financial advice.")
    st.markdown(
        f"""
<div style="border:1px solid #e5e7eb;border-left:8px solid {summary['tendency_color']};
padding:16px 18px;border-radius:8px;background:#ffffff;margin-bottom:12px;">
  <div style="font-size:0.85rem;color:#475569;">Historical statistics only</div>
  <div style="font-size:1.35rem;font-weight:700;color:#0f172a;">{summary['tendency_label']}</div>
  <div style="margin-top:8px;color:#334155;">{summary['plain_language_summary_zh']}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**歷史樣本風險背景**")
        st.write(summary["risk_context_zh"])
    with c2:
        st.markdown("**解讀限制**")
        st.write(summary["interpretation_limit_zh"])
    with c3:
        st.markdown("**觀察項目**")
        st.write(summary["monitor_zh"])

    stats = summary["stats_used"]
    st.caption(
        "Historical sample stats used: Top20 historical similar cases "
        f"1W {fmt_percent(stats['avg_1w'])}, "
        f"2W {fmt_percent(stats['avg_2w'])}, "
        f"4W {fmt_percent(stats['avg_4w'])}, "
        f"8W {fmt_percent(stats['avg_8w'])}, "
        f"8W win rate {fmt_percent(stats['win_8w'], input_scale='fraction')}."
    )


def percentile_level(value: object) -> str:
    percentile = percent_points(value)
    if percentile is None:
        return "N/A"
    if percentile < 10:
        return "極低"
    if percentile < 20:
        return "偏低到極低"
    if percentile < 40:
        return "偏低"
    if percentile < 60:
        return "中性"
    if percentile < 80:
        return "偏高"
    if percentile < 90:
        return "高"
    return "極高"


def percentile_rank_phrase(value: object) -> str:
    percentile = percent_points(value)
    if percentile is None:
        return "N/A"
    return f"約高於 {percentile:.1f}% 的近 156 週樣本，低於 {100 - percentile:.1f}% 的樣本"


def fmt_percentile_rank(value: object) -> str:
    percentile = percent_points(value)
    if percentile is None:
        return "N/A"
    return f"第 {percentile:.1f} 百分位"


def managed_money_position_sentence(value: object) -> str:
    percentile = percent_points(value)
    if percentile is None:
        return "Managed Money 目前百分位資料不足。"
    if percentile < 40:
        return "這代表基金淨部位偏低，不是高擁擠多頭狀態。"
    if percentile < 60:
        return "這代表基金淨部位接近中性區，投機端尚未呈現明顯極端。"
    if percentile < 80:
        return "這代表基金淨部位偏高，投機端參與度較強，但尚未進入最高擁擠區。"
    return "這代表基金淨部位位於高擁擠區，需要留意追價風險，但不等於價格一定反轉。"


def producer_position_sentence(value: object) -> str:
    percentile = percent_points(value)
    if percentile is None:
        return "Producer / Merchant 目前百分位資料不足。"
    if percentile >= 90:
        return "Producer / Merchant 部位位於極高百分位。這通常代表商業避險端處於歷史偏極端位置，但不等於價格一定反轉。"
    if percentile >= 70:
        return "Producer / Merchant 部位位於偏高百分位。這代表商業避險端位置較歷史多數週偏高，需要搭配價格與 OI 一起解讀。"
    if percentile <= 20:
        return "Producer / Merchant 部位位於偏低百分位。這代表商業避險端結構並未處於高位極端。"
    return "Producer / Merchant 部位位於中性區間。這代表商業避險端位置沒有明顯歷史極端。"


def open_interest_position_sentence(value: object) -> str:
    percentile = percent_points(value)
    if percentile is None:
        return "Open Interest 目前百分位資料不足。"
    if percentile < 10:
        return "Open Interest 位於極低百分位。這代表市場參與度或持倉規模極低，市場可能處於低參與、重新累積或資金退潮狀態。"
    if percentile < 30:
        return "Open Interest 位於偏低百分位。這代表市場參與度或持倉規模偏低，趨勢延續需要更多資金參與確認。"
    if percentile < 70:
        return "Open Interest 位於中性區間。這代表市場參與度沒有明顯歷史極端。"
    return "Open Interest 位於偏高百分位。這代表市場參與度或持倉規模偏高，需要留意波動擴大與部位擁擠。"


def render_how_to_read_dashboard() -> None:
    st.subheader("How to Read This Dashboard")
    steps = [
        (
            "Step 1",
            "先看 Current Market Snapshot，確認目前 MM、Producer、OI 的歷史位置。",
        ),
        (
            "Step 2",
            "看 Historical Positioning Explanation，理解目前是資金擁擠、低參與、還是弱部位狀態。",
        ),
        (
            "Step 3",
            "看 Top 20 Similar Cases 的 median return 與 win rate，理解歷史相似案例後續分布。",
        ),
        (
            "Step 4",
            "打開 Event Study，查看單一歷史案例前後走勢。",
        ),
        (
            "Step 5",
            "所有結果只能作為盤前背景與風險提醒，不可單獨作為交易決策。",
        ),
    ]
    for label, body in steps:
        st.markdown(f"**{label}：** {body}")


def summary_or_latest(summary: dict, summary_key: str, latest: pd.Series, latest_key: str) -> object:
    value = summary.get(summary_key)
    if value is not None:
        return value
    return latest.get(latest_key)


def fmt_snapshot_percent(summary: dict, summary_key: str, latest: pd.Series, latest_key: str) -> str:
    value = summary.get(summary_key)
    if value is not None:
        return fmt_percent(value, input_scale="points")
    return fmt_percent(latest.get(latest_key), input_scale="fraction")


def render_current_market_snapshot(
    latest: pd.Series,
    hub_summary: dict,
    diagnostics: dict,
) -> None:
    st.subheader("Current Market Snapshot")
    state = hub_summary.get("market_state") or market_state(
        latest.get(MM_FACTOR),
        latest.get("oi_percentile_156w"),
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Dataset / COT Date", fmt_date(summary_or_latest(hub_summary, "date", latest, "date")))
    c2.metric("Gold Close", fmt_number(summary_or_latest(hub_summary, "gold_close", latest, "gold_close")))
    c3.metric("Market State", state)
    c4.metric("MM Net", fmt_int(latest.get("mm_net")))

    c1, c2, c3 = st.columns(3)
    c1.metric("MM Percentile", fmt_snapshot_percent(hub_summary, "mm_percentile", latest, MM_FACTOR))
    c2.metric(
        "Producer Percentile",
        fmt_snapshot_percent(
            hub_summary,
            "producer_percentile",
            latest,
            "producer_net_percentile_156w",
        ),
    )
    c3.metric(
        "OI Percentile",
        fmt_snapshot_percent(hub_summary, "oi_percentile", latest, "oi_percentile_156w"),
    )

    master_date = fmt_date(latest.get("date"))
    hub_date = fmt_date(hub_summary.get("date")) if hub_summary else "N/A"
    diagnostics_status = diagnostics.get("overall_status") or hub_summary.get(
        "data_health",
        {},
    ).get("overall_freshness_status")
    st.caption(
        f"hub date: `{hub_date}` | master latest date: `{master_date}` | "
        f"latest CFTC available date: `{latest_cftc_available_date()}` | "
        f"data freshness status: `{diagnostics_status or 'N/A'}`"
    )
    st.caption(date_semantics_note())
    if hub_summary.get("last_update_time"):
        st.caption(f"Hub summary last refresh UTC: `{hub_summary.get('last_update_time')}`")
    if hub_summary and hub_date != "N/A" and master_date != "N/A" and hub_date != master_date:
        st.warning("Dashboard summary 尚未同步到最新 master dataset，請重新執行完整更新。")


def render_historical_positioning_explanation(latest: pd.Series) -> None:
    st.subheader("Historical Positioning Explanation")
    mm = latest.get(MM_FACTOR)
    producer = latest.get("producer_net_percentile_156w")
    oi = latest.get("oi_percentile_156w")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**MM Percentile**")
        st.write(
            f"Managed Money 目前位於過去 156 週 rolling window 的{fmt_percentile_rank(mm)}。"
        )
        st.write(managed_money_position_sentence(mm))
    with c2:
        st.markdown("**Producer Percentile**")
        st.write(
            f"Producer / Merchant 部位目前位於過去 156 週 rolling window 的{fmt_percentile_rank(producer)}。"
        )
        st.write(producer_position_sentence(producer))
    with c3:
        st.markdown("**OI Percentile**")
        st.write(
            f"Open Interest 目前位於過去 156 週 rolling window 的{fmt_percentile_rank(oi)}。"
        )
        st.write(open_interest_position_sentence(oi))


def render_indicator_dictionary_cards(latest: pd.Series) -> None:
    st.subheader("Indicator Dictionary")
    oi_value = fmt_percent(latest.get("oi_percentile_156w"), input_scale="fraction")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### MM Percentile 是什麼？")
        st.markdown(
            """
MM = Managed Money，通常代表基金、CTA、投機型資金在 COT 報告中的部位。

MM Percentile 不是多空訊號，而是用來判斷目前基金部位在歷史上偏高或偏低。

低百分位：基金參與度偏低或淨多偏低。

高百分位：基金部位偏積極或較擁擠。
"""
        )
    with c2:
        st.markdown("### Producer Percentile 是什麼？")
        st.markdown(
            """
Producer / Merchant 通常代表生產商、商業避險端。

高百分位代表其部位處於歷史偏高區間，可能反映避險需求或商業端壓力。

此數值需搭配 MM、OI、價格趨勢一起看，不能單獨解讀。
"""
        )
    with c3:
        st.markdown("### OI Percentile 是什麼？")
        st.markdown(
            f"""
OI = Open Interest，代表期貨市場未平倉合約總量。

OI 高代表市場參與度高、資金擁擠度高。

OI 低代表市場參與度低、資金尚未大規模進場或退場後沉澱。

OI Percentile {oi_value} 代表目前 OI 位於極低歷史位置。
"""
        )


def render_executive_readability_summary(latest: pd.Series, summary: dict) -> None:
    state = market_state(latest.get(MM_FACTOR), latest.get("oi_percentile_156w"))
    stats = summary["stats_used"]
    st.subheader("Executive Summary / 首頁快讀")
    st.markdown(
        f"""
**目前市場歷史定位：** {state}

**Historical Tendency：** {summary['tendency_label']}（僅為歷史統計傾向）

**MM 位置：** {fmt_percent(latest.get(MM_FACTOR), input_scale='fraction')}，{percentile_level(latest.get(MM_FACTOR))}

**Producer 位置：** {fmt_percent(latest.get('producer_net_percentile_156w'), input_scale='fraction')}，{percentile_level(latest.get('producer_net_percentile_156w'))}

**OI 位置：** {fmt_percent(latest.get('oi_percentile_156w'), input_scale='fraction')}，{percentile_level(latest.get('oi_percentile_156w'))}

**Top20 歷史相似案例後續統計：** 1W {fmt_percent(stats['avg_1w'])}, 2W {fmt_percent(stats['avg_2w'])}, 4W {fmt_percent(stats['avg_4w'])}, 8W {fmt_percent(stats['avg_8w'])}, 8W win rate {fmt_percent(stats['win_8w'], input_scale='fraction')}。

**核心提醒：** GHPR 只描述大型資金籌碼與歷史相似案例，不提供進出場點。
"""
    )


def build_indicator_explanation_rows(latest: pd.Series) -> list[dict]:
    mm = latest.get(MM_FACTOR)
    producer = latest.get("producer_net_percentile_156w")
    oi = latest.get("oi_percentile_156w")
    return [
        {
            "Indicator": "MM Percentile",
            "Current": fmt_percent(mm, input_scale="fraction"),
            "Historical position": percentile_level(mm),
            "How to read": (
                f"MM 代表 Managed Money 淨部位在近 156 週的位置。"
                f"{fmt_percent(mm, input_scale='fraction')} 表示目前{percentile_rank_phrase(mm)}，"
                "投機資金位置偏低，尚未呈現擁擠追價結構。"
            ),
        },
        {
            "Indicator": "Producer Percentile",
            "Current": fmt_percent(producer, input_scale="fraction"),
            "Historical position": percentile_level(producer),
            "How to read": (
                f"Producer / Merchant 代表商業避險端淨部位在近 156 週的位置。"
                f"{fmt_percent(producer, input_scale='fraction')} 表示目前{percentile_rank_phrase(producer)}，"
                "商業端結構處於偏高區，需要搭配價格與 OI 一起解讀。"
            ),
        },
        {
            "Indicator": "OI Percentile",
            "Current": fmt_percent(oi, input_scale="fraction"),
            "Historical position": percentile_level(oi),
            "How to read": (
                f"OI 代表期貨總未平倉量在近 156 週的位置。"
                f"{fmt_percent(oi, input_scale='fraction')} 表示目前{percentile_rank_phrase(oi)}，"
                "市場參與度極低，歷史相似案例需要等待 OI 或價格結構確認。"
            ),
        },
    ]


def render_indicator_explanations(latest: pd.Series) -> None:
    st.subheader("MM / Producer / OI 指標怎麼讀")
    st.dataframe(
        pd.DataFrame(build_indicator_explanation_rows(latest)),
        width="stretch",
        hide_index=True,
    )


def render_top20_following_explanation(summary: dict) -> None:
    stats = summary["stats_used"]
    st.subheader("Top 20 Similar Cases 後續統計代表什麼")
    st.markdown(
        f"""
Top 20 Similar Cases 是用目前的 MM / Producer / OI percentile 去找過去最相近的 20 個歷史週。
表格中的 1W / 2W / 4W / 8W 是那些歷史案例發生後的後續表現統計，不是對現在行情的保證。

目前 Top20 平均後續表現為：1W {fmt_percent(stats['avg_1w'])}, 2W {fmt_percent(stats['avg_2w'])}, 4W {fmt_percent(stats['avg_4w'])}, 8W {fmt_percent(stats['avg_8w'])}；8W win rate 為 {fmt_percent(stats['win_8w'], input_scale='fraction')}。
這代表歷史樣本傾向偏弱，但仍只是歷史統計研究參考。
"""
    )


def render_not_signal_explanation() -> None:
    st.subheader("為什麼這不是交易訊號")
    st.markdown(
        """
1. Percentile 只代表相對歷史位置，不代表方向預測。
2. Top 20 Similar Cases 是歷史樣本統計，不保證當前市場會重複。
3. GHPR 沒有納入即時價格結構、流動性事件、總體消息或風控條件。
4. GHPR 的用途是風險濾網與歷史定位，最後仍需結合其他市場確認。
"""
    )


def data_freshness(latest_date: object) -> str:
    if pd.isna(latest_date):
        return "N/A"
    age_days = (pd.Timestamp(datetime.now().date()) - pd.Timestamp(latest_date).normalize()).days
    if age_days <= 10:
        return "Fresh"
    if age_days <= 21:
        return "Slightly stale"
    return "Stale"


def build_data_health(latest_row: pd.Series | None) -> dict:
    source = GOLD_SOURCE_TEXT
    if latest_row is not None and "gold_price_source" in latest_row:
        source = str(latest_row.get("gold_price_source") or GOLD_SOURCE_TEXT)
    latest_date = latest_row.get("date") if latest_row is not None else None
    return {
        "Latest COT Date": fmt_date(latest_date),
        "Latest Gold Price": fmt_number(latest_row.get("gold_close")) if latest_row is not None else "N/A",
        "Gold Price Source": source,
        "Snapshot Generated At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Data Freshness": data_freshness(latest_date),
    }


def render_data_health(latest_row: pd.Series | None) -> None:
    st.subheader("Data Health")
    st.dataframe(pd.DataFrame([build_data_health(latest_row)]), width="stretch", hide_index=True)


def diagnostics_component_map(diagnostics: dict) -> dict[str, dict]:
    components = diagnostics.get("components") if isinstance(diagnostics, dict) else None
    if not isinstance(components, list):
        return {}
    return {
        str(component.get("component")): component
        for component in components
        if isinstance(component, dict) and component.get("component")
    }


def component_date_from_sources(
    component_name: str,
    component_map: dict[str, dict],
    hub_summary: dict,
) -> str:
    component = component_map.get(component_name, {})
    if component.get("latest_date"):
        return str(component["latest_date"])
    component_dates = hub_summary.get("data_health", {}).get("component_dates", {})
    if isinstance(component_dates, dict) and component_dates.get(component_name):
        return str(component_dates[component_name])
    return "N/A"


def dashboard_freshness_status(
    master_date: str,
    hub_date: str,
    diagnostics: dict,
    hub_summary: dict,
) -> str:
    diagnostics_status = diagnostics.get("overall_status") if isinstance(diagnostics, dict) else None
    if diagnostics_status:
        return str(diagnostics_status)
    hub_status = hub_summary.get("data_health", {}).get("overall_freshness_status")
    if hub_status:
        return str(hub_status)
    if master_date == "N/A" or hub_date == "N/A":
        return "ERROR"
    if master_date != hub_date:
        return "STALE"
    return "OK"


def render_dashboard_data_freshness(
    master: pd.DataFrame,
    hub_summary: dict,
    diagnostics: dict,
) -> None:
    st.subheader("Data Freshness")
    latest = latest_row(master)
    master_date = fmt_date(latest.get("date")) if latest is not None else "N/A"
    hub_date = fmt_date(hub_summary.get("date")) if hub_summary else "N/A"
    component_map = diagnostics_component_map(diagnostics)
    status = dashboard_freshness_status(master_date, hub_date, diagnostics, hub_summary)

    c1, c2, c3 = st.columns(3)
    c1.metric("Output File Updated Time", latest_update_time())
    c2.metric("Master Dataset / COT Date", master_date)
    c3.metric("Latest CFTC Available Date", latest_cftc_available_date())
    st.caption(date_semantics_note())

    if component_map:
        rows = []
        for component in component_map.values():
            rows.append(
                {
                    "Component": component.get("component", "N/A"),
                    "File": component.get("file", "N/A"),
                    "Latest Data Date": component.get("latest_date") or "N/A",
                    "Expected Master Date": component.get("expected_latest_date") or "N/A",
                    "Current": str(component.get("is_current", False)).lower(),
                    "Stale Reason": component.get("stale_reason") or "",
                }
            )
        rows.append(
            {
                "Component": "overall_status",
                "File": "",
                "Latest Data Date": status,
                "Expected Master Date": master_date,
                "Current": str(status == "OK").lower(),
                "Stale Reason": "",
            }
        )
    else:
        rows = [
            {
                "Component": "master",
                "File": "data/processed/ghpr_master_weekly.csv",
                "Latest Data Date": master_date,
                "Expected Master Date": master_date,
                "Current": str(master_date != "N/A").lower(),
                "Stale Reason": "",
            },
            {
                "Component": "hub_summary",
                "File": "outputs/reports/ghpr_summary_for_hub.json",
                "Latest Data Date": hub_date,
                "Expected Master Date": master_date,
                "Current": str(hub_date == master_date and hub_date != "N/A").lower(),
                "Stale Reason": "" if hub_date == master_date else "hub date differs from master date",
            },
            {
                "Component": "historical_similarity",
                "File": "outputs/reports/historical_similarity_report.csv",
                "Latest Data Date": component_date_from_sources(
                    "historical_similarity",
                    component_map,
                    hub_summary,
                ),
                "Expected Master Date": master_date,
                "Current": "N/A",
                "Stale Reason": "diagnostics file unavailable",
            },
            {
                "Component": "mm_lifecycle",
                "File": "data/processed/mm_lifecycle_dataset.csv",
                "Latest Data Date": component_date_from_sources("mm_lifecycle", component_map, hub_summary),
                "Expected Master Date": master_date,
                "Current": "N/A",
                "Stale Reason": "diagnostics file unavailable",
            },
            {
                "Component": "mm_structure",
                "File": "data/processed/mm_structure_lifecycle_dataset.csv",
                "Latest Data Date": component_date_from_sources("mm_structure", component_map, hub_summary),
                "Expected Master Date": master_date,
                "Current": "N/A",
                "Stale Reason": "diagnostics file unavailable",
            },
            {
                "Component": "velocity_reading",
                "File": "data/processed/mm_velocity_reading_layer.csv",
                "Latest Data Date": component_date_from_sources("velocity_reading", component_map, hub_summary),
                "Expected Master Date": master_date,
                "Current": "N/A",
                "Stale Reason": "diagnostics file unavailable",
            },
            {
                "Component": "overall_status",
                "File": "",
                "Latest Data Date": status,
                "Expected Master Date": master_date,
                "Current": str(status == "OK").lower(),
                "Stale Reason": "",
            },
        ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    stale_components = diagnostics.get("stale_components") or hub_summary.get(
        "data_health",
        {},
    ).get("stale_components", [])
    if status == "OK":
        st.success("Data freshness OK: all tracked modules match the master dataset date.")
    elif status == "STALE":
        st.warning("Dashboard summary 尚未同步到最新 master dataset，請重新執行完整更新。")
    elif status == "PARTIAL_STALE":
        st.warning("Some modules are stale: " + ", ".join(map(str, stale_components)))
    else:
        st.error("Data freshness check has missing or unreadable files.")


def render_how_to_use_ghpr() -> None:
    st.subheader("如何使用 GHPR")
    st.markdown(
        """
1. 先看 Historical Tendency，了解歷史相似樣本分布是偏正向、偏弱或分歧。
2. 再看 MM / Producer / OI percentile，判斷大型資金位置。
3. 再看 Top 20 Similar Cases，了解歷史樣本後續表現。
4. GHPR 不提供進出場點，只提供歷史定位與風險背景。
5. 最後仍需結合價格結構、OGR / MMP、成交量或其他市場確認。
"""
    )


def fmt_current_following_return(value: object) -> str:
    if pd.isna(value):
        return "N/A"
    return fmt_percent(value, input_scale="return")


def following_return_note(value: object) -> str:
    if pd.isna(value):
        return "Future data not formed yet / 未來資料尚未形成"
    return "Historical following data available"


def latest_update_time() -> str:
    candidates = [
        MASTER_PATH,
        FACTOR_PATH,
        REPORT_PATH,
        HISTORICAL_SIMILARITY_REPORT_PATH,
        HISTORICAL_SIMILARITY_STATS_PATH,
        HISTORICAL_SIMILARITY_CASES_CHART_PATH,
        UPDATE_LOG_PATH,
    ]
    existing = [path for path in candidates if path.exists()]
    if not existing:
        return "N/A"
    latest_mtime = max(path.stat().st_mtime for path in existing)
    return datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M:%S")


def format_update_command(command: list[str]) -> str:
    return " ".join(str(part) for part in command)


def build_update_failure_summary(result: object) -> dict[str, str]:
    failed_step = next((step for step in result.steps if not step.success), None)
    return {
        "failed_step": failed_step.name if failed_step else "N/A",
        "command": format_update_command(failed_step.command) if failed_step else "N/A",
        "exit_code": str(failed_step.return_code) if failed_step else "N/A",
        "stderr": failed_step.stderr if failed_step and failed_step.stderr else "N/A",
        "update_log_path": str(result.log_path),
        "error_message": result.error_message or "N/A",
    }


def build_update_freshness_summary(result: object | None = None) -> dict[str, object]:
    if result is not None:
        return {
            "mode": getattr(result, "mode", "N/A"),
            "latest_dataset_date": getattr(result, "latest_dataset_date_after", None) or "N/A",
            "latest_cftc_available_date": getattr(result, "latest_cftc_available_date", None) or "N/A",
            "data_is_current": bool(getattr(result, "data_is_current", False)),
            "stale_reason": getattr(result, "stale_reason", "") or "N/A",
        }

    dataset_date = latest_dataset_date()
    cftc_date = latest_cftc_available_date_from_current_file()
    data_is_current, stale_reason = build_freshness_status(dataset_date, cftc_date)
    return {
        "mode": "N/A",
        "latest_dataset_date": dataset_date or "N/A",
        "latest_cftc_available_date": cftc_date or "N/A",
        "data_is_current": data_is_current,
        "stale_reason": stale_reason or "N/A",
    }


def render_update_failure_summary(summary: dict[str, str]) -> None:
    with st.sidebar.expander("Update failure details", expanded=True):
        st.markdown(f"**Failed step:** `{summary.get('failed_step', 'N/A')}`")
        st.markdown(f"**Exit code:** `{summary.get('exit_code', 'N/A')}`")
        st.markdown("**Command**")
        st.code(summary.get("command", "N/A"), language="text")
        st.markdown("**stderr**")
        st.code(summary.get("stderr", "N/A"), language="text")
        st.markdown("**Update log path**")
        st.code(summary.get("update_log_path", "N/A"), language="text")


def render_freshness_summary(summary: dict[str, object]) -> None:
    st.sidebar.caption("Data freshness")
    st.sidebar.write(f"latest_dataset_date: `{summary.get('latest_dataset_date', 'N/A')}`")
    st.sidebar.write(f"latest_cftc_available_date: `{summary.get('latest_cftc_available_date', 'N/A')}`")
    st.sidebar.write(f"data_is_current: `{str(summary.get('data_is_current', False)).lower()}`")
    if summary.get("data_is_current"):
        st.sidebar.success("Data is current with the latest available CFTC date.")
    else:
        st.sidebar.warning("資料尚未更新到最新 CFTC 報告日期。")
        st.sidebar.caption(str(summary.get("stale_reason", "N/A")))


def render_update_controls() -> None:
    st.sidebar.subheader("Update")
    st.sidebar.caption("Historical statistics / research reference refresh.")
    st.sidebar.info(
        """
Cloud deployment note:
On Streamlit Cloud, runtime file writes may be temporary.
For stable production data, refresh locally/VPS, commit updated data and outputs, then push to GitHub.

雲端部署環境中的檔案寫入可能是暫時性的。
若要穩定保存資料，建議在本機或 VPS 更新後，將 data/ 與 outputs/ 提交回 GitHub。
"""
    )

    if st.sidebar.button("快速重建本地資料", width="stretch"):
        st.sidebar.caption("不下載新 COT，只用目前本地資料重算報告與圖表。")
        with st.spinner("Rebuilding GHPR outputs from local data..."):
            result = run_update_pipeline(mode="local")
            st.cache_data.clear()
        st.session_state["last_update_status"] = result.status_text
        st.session_state["last_update_mode"] = result.mode
        st.session_state["last_update_log"] = str(result.log_path)
        st.session_state["last_update_error"] = result.error_message
        st.session_state["last_update_freshness"] = build_update_freshness_summary(result)
        st.session_state["last_update_failure_summary"] = (
            build_update_failure_summary(result) if not result.success else None
        )

    if st.sidebar.button("完整更新最新資料", width="stretch"):
        st.sidebar.caption("嘗試下載最新 CFTC / Gold price，再重建報告與圖表。")
        with st.spinner("Running full GHPR data refresh..."):
            result = run_update_pipeline(mode="full")
            st.cache_data.clear()
        st.session_state["last_update_status"] = result.status_text
        st.session_state["last_update_mode"] = result.mode
        st.session_state["last_update_log"] = str(result.log_path)
        st.session_state["last_update_error"] = result.error_message
        st.session_state["last_update_freshness"] = build_update_freshness_summary(result)
        st.session_state["last_update_failure_summary"] = (
            build_update_failure_summary(result) if not result.success else None
        )

    status = st.session_state.get("last_update_status")
    if status == "success":
        mode = st.session_state.get("last_update_mode", "N/A")
        st.sidebar.success(f"Update completed successfully ({mode}). 資料已更新並重新載入。")
    elif status == "fail":
        st.sidebar.error("Update failed")
        error = st.session_state.get("last_update_error")
        if error:
            st.sidebar.caption(error)
        summary = st.session_state.get("last_update_failure_summary")
        if summary:
            render_update_failure_summary(summary)

    log_path = st.session_state.get("last_update_log")
    if log_path:
        st.sidebar.caption(f"Update log: {log_path}")

    render_freshness_summary(
        st.session_state.get("last_update_freshness") or build_update_freshness_summary()
    )

def render_sidebar_metadata(master: pd.DataFrame, hub_summary: dict) -> None:
    st.sidebar.subheader("Status")
    st.sidebar.metric("Output file updated time", latest_update_time())
    st.sidebar.metric("Latest dataset / COT date", latest_dataset_date_from_master(master))
    st.sidebar.metric("Latest CFTC available date", latest_cftc_available_date())
    if hub_summary.get("last_update_time"):
        st.sidebar.caption(f"Hub summary refresh UTC: `{hub_summary.get('last_update_time')}`")
    st.sidebar.caption(date_semantics_note())
    st.sidebar.caption("Gold price source:")
    st.sidebar.code(GOLD_SOURCE_TEXT)
    st.sidebar.warning(FUTURES_PROXY_NOTE)
    st.sidebar.info(RESEARCH_WARNING_EN)

    latest = latest_row(master)
    if latest is not None:
        st.sidebar.caption("Current market state")
        st.sidebar.write(
            market_state(
                latest.get(MM_FACTOR),
                latest.get("oi_percentile_156w"),
            )
        )


def render_hse_exclusion_control() -> int:
    st.sidebar.subheader("HSE Similarity Window")
    labels = {
        8: "Exclude recent 8 weeks",
        26: "Exclude recent 26 weeks",
        52: "Exclude recent 52 weeks",
        104: "Exclude recent 104 weeks",
    }
    default_index = HSE_EXCLUDE_RECENT_OPTIONS.index(DEFAULT_EXCLUDE_RECENT_WEEKS)
    selected_label = st.sidebar.selectbox(
        "Recent history exclusion",
        [labels[value] for value in HSE_EXCLUDE_RECENT_OPTIONS],
        index=default_index,
        help="Avoid having Top Similar Cases dominated by the same recent market phase.",
    )
    selected_weeks = next(
        value for value, label in labels.items() if label == selected_label
    )
    st.sidebar.caption(
        f"Recent {selected_weeks} weeks are excluded from similarity search by default."
        if selected_weeks == DEFAULT_EXCLUDE_RECENT_WEEKS
        else f"Recent {selected_weeks} weeks are excluded from similarity search for this view."
    )
    return selected_weeks


def render_research_banner() -> None:
    st.info(RESEARCH_WARNING_ZH)
    st.caption(RESEARCH_WARNING_EN)


def render_data_source_box(master: pd.DataFrame) -> None:
    latest = latest_row(master)
    source = GOLD_SOURCE_TEXT
    if latest is not None and "gold_price_source" in latest:
        source = str(latest.get("gold_price_source") or GOLD_SOURCE_TEXT)
    st.markdown(
        f"""
**Gold price source:** `{source}`

{FUTURES_PROXY_NOTE}

Cloud runtime note: dashboard-triggered file writes can be temporary on hosted platforms.
For durable deployed data, commit refreshed `data/` and `outputs/` files back to GitHub.
"""
    )


def page_current_position(
    master: pd.DataFrame,
    historical_report: pd.DataFrame,
    historical_stats: pd.DataFrame,
    hse_exclude_recent_weeks: int,
    hub_summary: dict,
    diagnostics: dict,
) -> None:
    st.header("GHPR Executive Summary")
    st.caption(RESEARCH_WARNING_EN)

    required = [
        "date",
        "gold_close",
        "mm_net",
        MM_FACTOR,
        "mm_net_zscore_156w",
        "producer_net_percentile_156w",
        "oi_percentile_156w",
    ]
    if not require_columns(master, required):
        return
    latest = latest_row(master)
    if latest is None:
        st.info("N/A")
        return

    tendency_summary = build_historical_tendency_summary(latest, historical_stats)
    render_how_to_read_dashboard()
    render_current_market_snapshot(latest, hub_summary, diagnostics)
    render_dashboard_data_freshness(master, hub_summary, diagnostics)
    render_historical_positioning_explanation(latest)
    render_indicator_dictionary_cards(latest)

    st.divider()
    render_research_banner()
    render_historical_tendency_summary(tendency_summary)
    render_top20_following_explanation(tendency_summary)
    render_not_signal_explanation()
    render_how_to_use_ghpr()

    st.subheader("Current Metrics")
    state = market_state(latest.get(MM_FACTOR), latest.get("oi_percentile_156w"))
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current data date", fmt_date(latest["date"]))
    c2.metric("Gold price", fmt_number(latest["gold_close"]))
    c3.metric("MM State", latest.get("mm_state", mm_state_from_percentile(latest.get(MM_FACTOR))))
    c4.metric("Market State", state)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MM Percentile", fmt_percent(latest[MM_FACTOR], input_scale="fraction"))
    c2.metric(
        "Producer Percentile",
        fmt_percent(latest["producer_net_percentile_156w"], input_scale="fraction"),
    )
    c3.metric("OI Percentile", fmt_percent(latest["oi_percentile_156w"], input_scale="fraction"))
    c4.metric("MM Net", fmt_int(latest["mm_net"]))

    st.subheader("Top 20 Similar Cases — Historical Outcome")
    st.caption(
        "這代表歷史上與目前 MM / Producer / OI 結構相似的案例，在後續 1W / 2W / 4W / 8W 的統計結果。"
        "這不是預測，只是歷史樣本後續表現分布。"
    )
    st.caption(
        "Recent 52 weeks are excluded from similarity search by default."
        if hse_exclude_recent_weeks == DEFAULT_EXCLUDE_RECENT_WEEKS
        else f"Recent {hse_exclude_recent_weeks} weeks are excluded from similarity search for this view."
    )
    top20 = top20_similarity_summary(historical_report, historical_stats)
    if top20.empty:
        st.info("N/A")
    else:
        render_historical_confidence(
            build_historical_confidence(historical_report, historical_stats)
        )
        st.dataframe(format_top20_historical_outcome(top20), width="stretch", hide_index=True)

    st.subheader("Current Position Detail")
    detail = {
        "date": fmt_date(latest["date"]),
        "gold_close": fmt_number(latest["gold_close"]),
        "mm_net": fmt_int(latest["mm_net"]),
        "mm_net_percentile_156w": fmt_percent(latest[MM_FACTOR], input_scale="fraction"),
        "mm_net_zscore_156w": fmt_number(latest["mm_net_zscore_156w"], 3),
        "producer_net_percentile_156w": fmt_percent(
            latest["producer_net_percentile_156w"], input_scale="fraction"
        ),
        "oi_percentile_156w": fmt_percent(latest["oi_percentile_156w"], input_scale="fraction"),
        "gold_return_1w": fmt_current_following_return(latest.get("forward_return_1w")),
        "gold_return_1w_reason": following_return_note(latest.get("forward_return_1w")),
        "gold_return_2w": fmt_current_following_return(latest.get("forward_return_2w")),
        "gold_return_2w_reason": following_return_note(latest.get("forward_return_2w")),
        "gold_return_4w": fmt_current_following_return(latest.get("forward_return_4w")),
        "gold_return_4w_reason": following_return_note(latest.get("forward_return_4w")),
        "gold_return_8w": fmt_current_following_return(latest.get("forward_return_8w")),
        "gold_return_8w_reason": following_return_note(latest.get("forward_return_8w")),
    }
    st.dataframe(pd.DataFrame([detail]), width="stretch", hide_index=True)
    render_data_source_box(master)


def top20_similarity_summary(
    historical_report: pd.DataFrame,
    historical_stats: pd.DataFrame,
) -> pd.DataFrame:
    if not historical_stats.empty and "group" in historical_stats.columns:
        top20 = historical_stats[historical_stats["group"].astype(str).str.lower().eq("top 20")]
        if not top20.empty:
            return format_historical_stats_for_display(top20, historical_report)

    if historical_report.empty:
        return pd.DataFrame()

    rows = {"group": "Top 20", "case_count": len(historical_report.head(20))}
    top = historical_report.head(20)
    for weeks in FORWARD_HORIZONS:
        column = f"future_return_{weeks}w"
        values = pd.to_numeric(top.get(column), errors="coerce").dropna()
        rows[f"avg_return_{weeks}w"] = fmt_percent(values.mean(), input_scale="return") if not values.empty else "N/A"
        rows[f"median_return_{weeks}w"] = fmt_percent(values.median(), input_scale="return") if not values.empty else "N/A"
        rows[f"win_rate_{weeks}w"] = fmt_percent((values > 0).mean(), input_scale="fraction") if not values.empty else "N/A"
    values_8w = pd.to_numeric(top.get("future_return_8w"), errors="coerce").dropna()
    rows["best_return_8w"] = fmt_percent(values_8w.max(), input_scale="return") if not values_8w.empty else "N/A"
    rows["worst_return_8w"] = fmt_percent(values_8w.min(), input_scale="return") if not values_8w.empty else "N/A"
    return pd.DataFrame([rows])


def format_top20_historical_outcome(frame: pd.DataFrame) -> pd.DataFrame:
    preferred_columns = [
        "case_count",
        "median_return_1w",
        "win_rate_1w",
        "median_return_2w",
        "win_rate_2w",
        "median_return_4w",
        "win_rate_4w",
        "median_return_8w",
        "win_rate_8w",
        "best_return_8w",
        "worst_return_8w",
    ]
    display = frame.copy()
    if "group" in display.columns:
        display = display.drop(columns=["group"])
    ordered_columns = [column for column in preferred_columns if column in display.columns]
    return display[ordered_columns]


def same_return_direction(left: object, right: object) -> bool:
    left_number = scalar_float(left)
    right_number = scalar_float(right)
    if left_number is None or right_number is None:
        return False
    return (left_number > 0 and right_number > 0) or (left_number < 0 and right_number < 0)


def top20_similarity_score_average(historical_report: pd.DataFrame) -> float | None:
    if historical_report.empty or "similarity_score" not in historical_report.columns:
        return None
    values = pd.to_numeric(historical_report.head(20)["similarity_score"], errors="coerce").dropna()
    if values.empty:
        return None
    return float(values.mean())


def build_historical_confidence(
    historical_report: pd.DataFrame,
    historical_stats: pd.DataFrame,
) -> dict:
    stats_row = top20_stats_row(historical_stats)
    if stats_row is not None:
        case_count = scalar_float(stats_row.get("case_count"))
        win_rate_8w = scalar_float(stats_row.get("win_rate_8w"))
        median_return_8w = scalar_float(stats_row.get("median_return_8w"))
        avg_return_8w = scalar_float(stats_row.get("avg_return_8w"))
        best_return_8w = scalar_float(stats_row.get("best_return_8w"))
        worst_return_8w = scalar_float(stats_row.get("worst_return_8w"))
    elif not historical_report.empty:
        top = historical_report.head(20)
        values_8w = pd.to_numeric(top.get("future_return_8w"), errors="coerce").dropna()
        case_count = float(len(top))
        win_rate_8w = float((values_8w > 0).mean()) if not values_8w.empty else None
        median_return_8w = float(values_8w.median()) if not values_8w.empty else None
        avg_return_8w = float(values_8w.mean()) if not values_8w.empty else None
        best_return_8w = float(values_8w.max()) if not values_8w.empty else None
        worst_return_8w = float(values_8w.min()) if not values_8w.empty else None
    else:
        case_count = None
        win_rate_8w = None
        median_return_8w = None
        avg_return_8w = None
        best_return_8w = None
        worst_return_8w = None

    avg_similarity_score = top20_similarity_score_average(historical_report)
    direction_consistent = same_return_direction(median_return_8w, avg_return_8w)

    confidence = "Low"
    if case_count is not None and case_count >= 20 and direction_consistent:
        if (
            win_rate_8w is not None
            and (win_rate_8w >= 0.75 or win_rate_8w <= 0.25)
            and avg_similarity_score is not None
            and avg_similarity_score >= 85
        ):
            confidence = "High"
        elif win_rate_8w is not None and (win_rate_8w >= 0.65 or win_rate_8w <= 0.35):
            confidence = "Medium"

    if case_count is None or case_count < 10:
        confidence = "Low"

    return {
        "confidence": confidence,
        "case_count": case_count,
        "win_rate_8w": win_rate_8w,
        "median_return_8w": median_return_8w,
        "avg_return_8w": avg_return_8w,
        "best_return_8w": best_return_8w,
        "worst_return_8w": worst_return_8w,
        "avg_similarity_score": avg_similarity_score,
        "direction_consistent": direction_consistent,
    }


def render_historical_confidence(confidence: dict) -> None:
    st.metric("Historical Confidence", confidence["confidence"])
    st.caption("Confidence 代表歷史樣本方向一致性與相似度品質，不代表交易勝率。")
    details = {
        "case_count": fmt_number(confidence.get("case_count"), 0),
        "win_rate_8w": fmt_percent(confidence.get("win_rate_8w"), input_scale="fraction"),
        "median_return_8w": fmt_percent(confidence.get("median_return_8w")),
        "avg_return_8w": fmt_percent(confidence.get("avg_return_8w")),
        "best_return_8w": fmt_percent(confidence.get("best_return_8w")),
        "worst_return_8w": fmt_percent(confidence.get("worst_return_8w")),
        "avg_similarity_score": fmt_number(confidence.get("avg_similarity_score"), 2),
        "median_avg_same_direction": "Yes" if confidence.get("direction_consistent") else "No",
    }
    st.dataframe(pd.DataFrame([details]), width="stretch", hide_index=True)


def page_historical_database(master: pd.DataFrame) -> None:
    st.header("Historical Database")
    st.caption("Gold price vs MM percentile historical viewer.")
    render_research_banner()

    required = ["date", "gold_close", "mm_net", MM_FACTOR, "mm_state"]
    if not require_columns(master, required):
        return
    if master.empty:
        st.info("N/A")
        return

    filtered = historical_filters(master)
    if filtered.empty:
        st.info("N/A: no rows match the selected filters.")
        return

    render_interactive_chart(
        "Gold Price vs MM Net Percentile",
        gold_mm_plot(filtered),
        key="historical_database_gold_mm_percentile",
        height=620,
        has_range_slider=True,
    )
    with st.expander("Filtered rows", expanded=False):
        display = filtered[["date", "gold_close", "mm_net", MM_FACTOR, "mm_state"]].copy()
        display["date"] = display["date"].dt.strftime("%Y-%m-%d")
        display[MM_FACTOR] = display[MM_FACTOR].apply(lambda value: percent_points(value))
        st.dataframe(display, width="stretch", hide_index=True)


def historical_filters(master: pd.DataFrame) -> pd.DataFrame:
    min_date = master["date"].min().date()
    max_date = master["date"].max().date()
    date_range = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    mm_range = st.sidebar.slider("MM percentile range", 0, 100, (0, 100), 1)
    state_filter = st.sidebar.multiselect("MM state", MM_STATE_ORDER, default=MM_STATE_ORDER)

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    else:
        start_date, end_date = pd.Timestamp(min_date), pd.Timestamp(max_date)

    lower, upper = mm_range[0] / 100, mm_range[1] / 100
    return master[
        (master["date"] >= start_date)
        & (master["date"] <= end_date)
        & (master[MM_FACTOR] >= lower)
        & (master[MM_FACTOR] <= upper)
        & (master["mm_state"].isin(state_filter))
    ].copy()


def gold_mm_plot(frame: pd.DataFrame) -> go.Figure:
    customdata = frame[["gold_close", "mm_net", MM_FACTOR, "mm_state"]].copy()
    customdata[MM_FACTOR] = customdata[MM_FACTOR] * 100

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=frame["date"],
            y=frame["gold_close"],
            mode="lines",
            name="gold_close",
            line=dict(color="#1f2937", width=2),
            customdata=customdata,
            hovertemplate=(
                "date=%{x|%Y-%m-%d}<br>"
                "gold_close=%{customdata[0]:,.2f}<br>"
                "mm_net=%{customdata[1]:,.0f}<br>"
                "mm_percentile=%{customdata[2]:.2f}%<br>"
                "MM state=%{customdata[3]}<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=frame["date"],
            y=frame[MM_FACTOR] * 100,
            mode="lines",
            name="MM percentile",
            line=dict(color="#2563eb", width=2),
            customdata=customdata,
            hovertemplate=(
                "date=%{x|%Y-%m-%d}<br>"
                "gold_close=%{customdata[0]:,.2f}<br>"
                "mm_net=%{customdata[1]:,.0f}<br>"
                "mm_percentile=%{customdata[2]:.2f}%<br>"
                "MM state=%{customdata[3]}<extra></extra>"
            ),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title=None,
        hovermode="x unified",
        height=620,
        margin=dict(l=30, r=30, t=70, b=30),
        xaxis=lifecycle_range_controls(),
    )
    fig.update_yaxes(title_text="gold_close", secondary_y=False)
    fig.update_yaxes(title_text="MM percentile (%)", range=[0, 100], secondary_y=True)
    return fig


def page_similar_cases(master: pd.DataFrame) -> None:
    st.header("Similar Cases")
    st.caption("Most similar historical MM percentile cases. Recent 8 weeks are excluded.")
    render_research_banner()

    similar = find_similar_mm_cases(master)
    if similar.empty:
        st.info("N/A")
        return

    st.subheader("Historical Similar Cases")
    st.dataframe(format_similar_cases(similar), width="stretch", hide_index=True)

    st.subheader("Historical Similar Cases Following Statistics")
    st.dataframe(similar_cases_summary(similar), width="stretch", hide_index=True)

    st.divider()
    render_single_event_study(master, similar)
    st.divider()
    render_group_event_study(master)


def find_similar_mm_cases(master: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    required = ["date", "gold_close", "mm_net", MM_FACTOR, "mm_state"]
    if not require_columns(master, required):
        return pd.DataFrame()
    if len(master) <= 8:
        st.info("N/A: not enough rows after excluding the latest 8 weeks.")
        return pd.DataFrame()

    current = master.sort_values("date").iloc[-1]
    current_percentile = current[MM_FACTOR]
    if pd.isna(current_percentile):
        st.info("N/A: current MM percentile is missing.")
        return pd.DataFrame()

    history = master.sort_values("date").iloc[:-8].dropna(subset=[MM_FACTOR]).copy()
    history["similarity"] = (history[MM_FACTOR] - current_percentile).abs()
    return history.sort_values(["similarity", "date"]).head(top_n).copy()


def format_similar_cases(similar: pd.DataFrame) -> pd.DataFrame:
    return_columns = [f"forward_return_{weeks}w" for weeks in FORWARD_HORIZONS]
    display = similar[["date", "gold_close", "mm_net", MM_FACTOR, "similarity", *return_columns]].copy()
    display = display.rename(
        columns={
            f"forward_return_{weeks}w": f"historical_case_following_return_{weeks}w"
            for weeks in FORWARD_HORIZONS
        }
    )
    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    display[MM_FACTOR] = display[MM_FACTOR].apply(lambda value: percent_points(value))
    display["similarity"] = display["similarity"] * 100
    for weeks in FORWARD_HORIZONS:
        column = f"historical_case_following_return_{weeks}w"
        display[column] = display[column].apply(lambda value: fmt_percent(value, input_scale="return"))
    return display


def similar_cases_summary(similar: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for weeks in FORWARD_HORIZONS:
        column = f"forward_return_{weeks}w"
        values = pd.to_numeric(similar[column], errors="coerce").dropna()
        rows.append(
            {
                "horizon": f"{weeks}W",
                "avg_return": fmt_percent(values.mean(), input_scale="return") if not values.empty else "N/A",
                "median_return": fmt_percent(values.median(), input_scale="return") if not values.empty else "N/A",
                "win_rate": fmt_percent((values > 0).mean(), input_scale="fraction") if not values.empty else "N/A",
                "case_count": len(values),
            }
        )
    return pd.DataFrame(rows)


def page_event_study(master: pd.DataFrame) -> None:
    st.header("Event Study")
    st.caption("Clickable historical event study and grouped MM-condition event paths.")
    render_research_banner()

    similar = find_similar_mm_cases(master)
    if similar.empty:
        st.info("N/A")
        return
    render_single_event_study(master, similar)
    st.divider()
    render_group_event_study(master)


def render_single_event_study(master: pd.DataFrame, similar: pd.DataFrame) -> None:
    st.subheader("Event Detail")
    event_options = [fmt_date(value) for value in similar["date"]]
    selected_date_text = st.selectbox("Select historical event date", event_options)
    if not selected_date_text:
        st.info("N/A")
        return

    selected_date = pd.Timestamp(selected_date_text)
    event_rows = master[master["date"] == selected_date]
    if event_rows.empty:
        st.info("N/A: selected event date not found in master dataset.")
        return

    event = event_rows.iloc[0]
    detail = {
        "event_date": fmt_date(event["date"]),
        "event_gold_close": fmt_number(event["gold_close"]),
        "event_mm_net": fmt_int(event["mm_net"]),
        "event_mm_percentile": fmt_percent(event[MM_FACTOR], input_scale="fraction"),
        "event_mm_state": event.get("mm_state", mm_state_from_percentile(event.get(MM_FACTOR))),
        "historical_case_following_return_1w": fmt_percent(event.get("forward_return_1w"), input_scale="return"),
        "historical_case_following_return_2w": fmt_percent(event.get("forward_return_2w"), input_scale="return"),
        "historical_case_following_return_4w": fmt_percent(event.get("forward_return_4w"), input_scale="return"),
        "historical_case_following_return_8w": fmt_percent(event.get("forward_return_8w"), input_scale="return"),
    }
    st.dataframe(pd.DataFrame([detail]), width="stretch", hide_index=True)

    window, insufficient = event_window(master, selected_date)
    if insufficient:
        st.warning("Insufficient history around selected event")
    if window.empty:
        st.info("N/A")
        return

    render_interactive_chart(
        "Event Study: Gold Indexed Path",
        event_gold_path_plot(window),
        key="event_study_gold_indexed_path",
        height=520,
    )
    render_interactive_chart(
        "Event Study: MM Percentile Path",
        event_mm_percentile_plot(window),
        key="event_study_mm_percentile_path",
        height=500,
    )


def event_window(
    master: pd.DataFrame,
    event_date: pd.Timestamp,
    pre_weeks: int = 12,
    post_weeks: int = 12,
) -> tuple[pd.DataFrame, bool]:
    data = master.sort_values("date").reset_index(drop=True)
    matches = data.index[data["date"] == event_date].tolist()
    if not matches:
        return pd.DataFrame(), True

    event_pos = matches[0]
    start = max(0, event_pos - pre_weeks)
    end = min(len(data) - 1, event_pos + post_weeks)
    window = data.iloc[start : end + 1].copy()
    base = data.loc[event_pos, "gold_close"]
    if pd.isna(base) or base == 0:
        return pd.DataFrame(), True

    window["week_offset"] = range(start - event_pos, end - event_pos + 1)
    window["gold_indexed_return"] = window["gold_close"] / base * 100
    window["mm_percentile_pct"] = window[MM_FACTOR] * 100
    insufficient = event_pos < pre_weeks or event_pos + post_weeks >= len(data)
    return window, insufficient


def event_gold_path_plot(window: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    customdata = window[["date", "gold_close", "gold_indexed_return", "mm_percentile_pct"]]
    fig.add_trace(
        go.Scatter(
            x=window["week_offset"],
            y=window["gold_indexed_return"],
            mode="lines+markers",
            name="gold_indexed_return",
            line=dict(color="#2563eb", width=3),
            customdata=customdata,
            hovertemplate=(
                "date=%{customdata[0]|%Y-%m-%d}<br>"
                "gold_close=%{customdata[1]:,.2f}<br>"
                "indexed_return=%{customdata[2]:.2f}<br>"
                "mm_percentile=%{customdata[3]:.2f}%<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="#111827")
    fig.update_layout(
        title=None,
        xaxis_title="week_offset",
        yaxis_title="gold_indexed_return",
        height=500,
        margin=dict(l=30, r=30, t=60, b=40),
    )
    return fig


def event_mm_percentile_plot(window: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    customdata = window[["date", "gold_close", "gold_indexed_return", "mm_percentile_pct"]]
    fig.add_trace(
        go.Scatter(
            x=window["week_offset"],
            y=window["mm_percentile_pct"],
            mode="lines+markers",
            name="mm_net_percentile_156w",
            line=dict(color="#7c3aed", width=3),
            customdata=customdata,
            hovertemplate=(
                "date=%{customdata[0]|%Y-%m-%d}<br>"
                "gold_close=%{customdata[1]:,.2f}<br>"
                "indexed_return=%{customdata[2]:.2f}<br>"
                "mm_percentile=%{customdata[3]:.2f}%<extra></extra>"
            ),
        )
    )
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="#111827")
    fig.update_layout(
        title=None,
        xaxis_title="week_offset",
        yaxis_title="mm_net_percentile_156w (%)",
        yaxis=dict(range=[0, 100]),
        height=420,
        margin=dict(l=30, r=30, t=60, b=40),
    )
    return fig


def render_group_event_study(master: pd.DataFrame) -> None:
    st.subheader("Group Event Study")
    st.caption(
        "Historical Statistics / Research Reference. Events closer than 8 weeks keep the first occurrence."
    )
    condition = st.selectbox("MM condition", ["MM >= 80", "MM <= 20", "MM 60-80", "MM 40-60"])
    events = dedupe_close_events(filter_events_by_mm_condition(master, condition), min_gap_weeks=8)
    if events.empty:
        st.info("N/A: no historical events for the selected MM condition.")
        return

    paths, valid_events = build_group_event_paths(master, events)
    stats = group_event_stats(valid_events)
    st.dataframe(pd.DataFrame([stats]), width="stretch", hide_index=True)

    if paths.empty:
        st.warning("Insufficient history around selected event")
        return

    render_interactive_chart(
        "Average Gold Event Path",
        group_event_path_plot(paths),
        key="event_study_group_average_gold_path",
        height=540,
    )


def filter_events_by_mm_condition(master: pd.DataFrame, condition: str) -> pd.DataFrame:
    data = master.dropna(subset=[MM_FACTOR]).sort_values("date").copy()
    if condition == "MM >= 80":
        return data[data[MM_FACTOR] >= 0.80]
    if condition == "MM <= 20":
        return data[data[MM_FACTOR] <= 0.20]
    if condition == "MM 60-80":
        return data[(data[MM_FACTOR] >= 0.60) & (data[MM_FACTOR] < 0.80)]
    if condition == "MM 40-60":
        return data[(data[MM_FACTOR] >= 0.40) & (data[MM_FACTOR] < 0.60)]
    return pd.DataFrame()


def dedupe_close_events(events: pd.DataFrame, min_gap_weeks: int = 8) -> pd.DataFrame:
    if events.empty:
        return events
    kept = []
    last_date: pd.Timestamp | None = None
    min_gap = pd.Timedelta(weeks=min_gap_weeks)
    for row in events.sort_values("date").itertuples(index=False):
        event_date = pd.Timestamp(row.date)
        if last_date is None or event_date - last_date >= min_gap:
            kept.append(row._asdict())
            last_date = event_date
    return pd.DataFrame(kept)


def build_group_event_paths(master: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    paths = []
    valid_event_rows = []
    for event in events.itertuples(index=False):
        event_date = pd.Timestamp(event.date)
        window, insufficient = event_window(master, event_date)
        if insufficient or window.empty:
            continue
        path = window[["week_offset", "gold_indexed_return"]].copy()
        path["event_date"] = event_date.strftime("%Y-%m-%d")
        paths.append(path)
        valid_event_rows.append(event._asdict())

    if not paths:
        return pd.DataFrame(), pd.DataFrame()
    return pd.concat(paths, ignore_index=True), pd.DataFrame(valid_event_rows)


def group_event_stats(events: pd.DataFrame) -> dict[str, object]:
    if events.empty:
        return {
            "event_count": 0,
            "avg_return_4w": "N/A",
            "win_rate_4w": "N/A",
            "avg_return_8w": "N/A",
            "win_rate_8w": "N/A",
            "worst_case_8w": "N/A",
            "best_case_8w": "N/A",
        }

    ret4 = pd.to_numeric(events.get("forward_return_4w"), errors="coerce").dropna()
    ret8 = pd.to_numeric(events.get("forward_return_8w"), errors="coerce").dropna()
    return {
        "event_count": len(events),
        "avg_return_4w": fmt_percent(ret4.mean(), input_scale="return") if not ret4.empty else "N/A",
        "win_rate_4w": fmt_percent((ret4 > 0).mean(), input_scale="fraction") if not ret4.empty else "N/A",
        "avg_return_8w": fmt_percent(ret8.mean(), input_scale="return") if not ret8.empty else "N/A",
        "win_rate_8w": fmt_percent((ret8 > 0).mean(), input_scale="fraction") if not ret8.empty else "N/A",
        "worst_case_8w": fmt_percent(ret8.min(), input_scale="return") if not ret8.empty else "N/A",
        "best_case_8w": fmt_percent(ret8.max(), input_scale="return") if not ret8.empty else "N/A",
    }


def group_event_path_plot(paths: pd.DataFrame) -> go.Figure:
    average = paths.groupby("week_offset", as_index=False)["gold_indexed_return"].mean()
    fig = go.Figure()
    for event_date, group in paths.groupby("event_date"):
        fig.add_trace(
            go.Scatter(
                x=group["week_offset"],
                y=group["gold_indexed_return"],
                mode="lines",
                name=event_date,
                line=dict(color="#2563eb", width=1),
                opacity=0.18,
                hovertemplate=(
                    f"event_date={event_date}<br>"
                    "week_offset=%{x}<br>"
                    "indexed_return=%{y:.2f}<extra></extra>"
                ),
                showlegend=False,
            )
        )
    fig.add_trace(
        go.Scatter(
            x=average["week_offset"],
            y=average["gold_indexed_return"],
            mode="lines+markers",
            name="Average Gold Event Path",
            line=dict(color="#111827", width=4),
            marker=dict(size=7),
            hovertemplate="week_offset=%{x}<br>average_indexed_return=%{y:.2f}<extra></extra>",
        )
    )
    fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="#111827")
    fig.update_layout(
        title=None,
        xaxis_title="week_offset",
        yaxis_title="gold_indexed_return",
        height=540,
        margin=dict(l=30, r=30, t=60, b=40),
    )
    return fig


def page_forward_statistics(factor_result: pd.DataFrame) -> None:
    st.header("Forward Statistics")
    st.caption("MM percentile bucket historical following-performance statistics.")
    render_research_banner()

    required = ["factor", "forward_horizon", "percentile_bucket", "count", "avg_forward_return", "win_rate"]
    if not require_columns(factor_result, required):
        return
    if factor_result.empty:
        st.info("N/A")
        return

    data = factor_result[factor_result["factor"] == MM_FACTOR].copy()
    if "sample_split" in data.columns:
        data = data[data["sample_split"].fillna("all") == "all"]
    if "gold_regime" in data.columns:
        data = data[data["gold_regime"].fillna("all") == "all"]
    if data.empty:
        st.info("N/A: no rows for factor = mm_net_percentile_156w.")
        return

    horizon = st.selectbox("Historical following-performance horizon", ["1W", "2W", "4W", "8W"], index=3)
    view = data[data["forward_horizon"] == horizon].copy()
    view["avg_forward_return_pct"] = view["avg_forward_return"] * 100
    view["win_rate_pct"] = view["win_rate"] * 100

    render_interactive_chart(
        "Average Historical Following Return (%)",
        bucket_line_chart(view, "avg_forward_return_pct", "Average Historical Following Return (%)"),
        key="forward_statistics_avg_following_return",
        height=500,
        show_legend=False,
    )
    c1, c2 = st.columns(2)
    with c1:
        render_interactive_chart(
            "Win Rate (%)",
            bucket_bar_chart(view, "win_rate_pct", "Win Rate (%)"),
            key="forward_statistics_win_rate",
            height=500,
            show_legend=False,
        )
    with c2:
        render_interactive_chart(
            "Count",
            bucket_bar_chart(view, "count", "Count"),
            key="forward_statistics_count",
            height=500,
            show_legend=False,
        )

    st.dataframe(view, width="stretch", hide_index=True)


def bucket_line_chart(frame: pd.DataFrame, y_column: str, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["percentile_bucket"],
            y=frame[y_column],
            mode="lines+markers",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=8),
            hovertemplate="bucket=%{x}<br>value=%{y:.2f}<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color="#6b7280", line_width=1)
    fig.update_layout(title=None, height=420, margin=dict(l=30, r=30, t=60, b=60))
    return fig


def bucket_bar_chart(frame: pd.DataFrame, y_column: str, title: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=frame["percentile_bucket"],
            y=frame[y_column],
            marker_color="#2563eb",
            hovertemplate="bucket=%{x}<br>value=%{y:.2f}<extra></extra>",
        )
    )
    fig.update_layout(title=None, height=420, margin=dict(l=30, r=30, t=60, b=60))
    return fig


def page_historical_similarity_engine(
    historical_report: pd.DataFrame,
    historical_stats: pd.DataFrame,
    hse_exclude_recent_weeks: int,
) -> None:
    st.header("Historical Similarity Engine")
    st.caption("Historical Statistics / Research Reference.")
    render_research_banner()
    st.info("This page compares the current feature vector with prior weekly states. It is not a forecast.")
    st.info(
        "Recent 52 weeks are excluded from similarity search by default."
        if hse_exclude_recent_weeks == DEFAULT_EXCLUDE_RECENT_WEEKS
        else f"Recent {hse_exclude_recent_weeks} weeks are excluded from similarity search for this view."
    )
    st.caption("Current Snapshot Date 是目前資料快照日期；Historical Case Date 是歷史相似案例的發生日期。")

    if historical_report.empty:
        st.info(f"N/A: HSE output not found. Run `python src/historical_similarity_engine.py` from `{PROJECT_ROOT}`.")
        return

    current_snapshot_date = "N/A"
    if "current_date" in historical_report.columns and not historical_report.empty:
        current_snapshot_date = fmt_date(historical_report["current_date"].iloc[0])
    render_component_date_context("Historical Similarity", current_snapshot_date)

    required_report = [
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
    ]
    if not require_columns(historical_report, required_report):
        return

    current = historical_report.iloc[0]
    st.subheader("Current Market State")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Current Snapshot Date", fmt_date(current["current_date"]))
    c2.metric("Current Snapshot Gold", fmt_number(current["current_gold_close"]))
    c3.metric("Current MM Percentile", fmt_number(current["current_mm_percentile"], 2))
    c4.metric("Current Producer Percentile", fmt_number(current["current_producer_percentile"], 2))
    c5.metric("Current OI Percentile", fmt_number(current["current_oi_percentile"], 2))

    st.subheader("Top Similar Historical Cases")
    st.dataframe(
        format_historical_similarity_report(historical_report.head(20)),
        width="stretch",
        hide_index=True,
    )

    render_historical_weekly_candlestick(historical_report)

    st.subheader("歷史相似案例後續統計")
    if historical_stats.empty:
        st.info("N/A")
    else:
        st.dataframe(
            format_historical_stats_for_display(historical_stats, historical_report),
            width="stretch",
            hide_index=True,
        )

    st.subheader("Historical Case Viewer")
    if HISTORICAL_SIMILARITY_CASES_CHART_PATH.exists():
        st.image(str(HISTORICAL_SIMILARITY_CASES_CHART_PATH), width="stretch")
    else:
        st.info(f"N/A: chart not found: {HISTORICAL_SIMILARITY_CASES_CHART_PATH}")


def format_historical_similarity_report(frame: pd.DataFrame) -> pd.DataFrame:
    display = frame.copy()
    for column in ["current_date", "historical_date"]:
        if column in display.columns:
            display[column] = pd.to_datetime(display[column], errors="coerce").dt.strftime("%Y-%m-%d")
    rename_map = {
        "current_date": "Current Snapshot Date",
        "current_gold_close": "Current Snapshot Gold",
        "current_mm_percentile": "Current MM Percentile",
        "current_producer_percentile": "Current Producer Percentile",
        "current_oi_percentile": "Current OI Percentile",
        "historical_date": "Historical Case Date",
        "similarity_score": "Similarity Score",
        "historical_gold_close": "Historical Case Gold",
        "historical_mm_percentile": "Historical MM Percentile",
        "historical_producer_percentile": "Historical Producer Percentile",
        "historical_oi_percentile": "Historical OI Percentile",
        "future_return_1w": "Historical Case Forward Return 1W",
        "future_return_2w": "Historical Case Forward Return 2W",
        "future_return_4w": "Historical Case Forward Return 4W",
        "future_return_8w": "Historical Case Forward Return 8W",
    }
    display = display.rename(columns=rename_map)
    return_columns = [f"Historical Case Forward Return {weeks}W" for weeks in FORWARD_HORIZONS]
    for column in return_columns:
        if column in display.columns:
            display[column] = display[column].apply(lambda value: fmt_percent(value, input_scale="return"))
    return display


def format_historical_stats_for_display(
    stats: pd.DataFrame,
    historical_report: pd.DataFrame,
) -> pd.DataFrame:
    display = stats.copy()
    for column in display.columns:
        if column.startswith(("avg_return_", "median_return_", "win_rate_", "best_return_", "worst_return_")):
            display[column] = display[column].apply(lambda value: fmt_percent(value, input_scale="return"))

    best_worst = best_worst_cases_by_group(historical_report)
    if not best_worst.empty and "group" in display.columns:
        display = display.merge(best_worst, on="group", how="left")
    return display


def best_worst_cases_by_group(historical_report: pd.DataFrame) -> pd.DataFrame:
    if historical_report.empty or "future_return_8w" not in historical_report.columns:
        return pd.DataFrame()
    rows = []
    group_sizes = {"Top 5": 5, "Top 10": 10, "Top 20": 20}
    for group, size in group_sizes.items():
        subset = historical_report.head(size).copy()
        values = pd.to_numeric(subset["future_return_8w"], errors="coerce")
        if values.dropna().empty:
            rows.append({"group": group, "best_case": "N/A", "worst_case": "N/A"})
            continue
        best = subset.loc[values.idxmax()]
        worst = subset.loc[values.idxmin()]
        rows.append(
            {
                "group": group,
                "best_case": f"{fmt_date(best['historical_date'])} ({fmt_percent(best['future_return_8w'], input_scale='return')})",
                "worst_case": f"{fmt_date(worst['historical_date'])} ({fmt_percent(worst['future_return_8w'], input_scale='return')})",
            }
        )
    return pd.DataFrame(rows)


def render_historical_weekly_candlestick(historical_report: pd.DataFrame) -> None:
    st.subheader("Historical Weekly Candlestick")
    st.caption("K 線只作為歷史案例視覺化與研究參考。")
    if historical_report.empty or "historical_date" not in historical_report.columns:
        st.info("N/A: historical case dates are unavailable.")
        return

    top20_dates = (
        pd.to_datetime(historical_report.head(20)["historical_date"], errors="coerce")
        .dropna()
        .dt.strftime("%Y-%m-%d")
        .drop_duplicates()
        .tolist()
    )
    if not top20_dates:
        st.info("N/A: Top 20 historical case dates are unavailable.")
        return

    selected_date = st.selectbox(
        "Select historical case date",
        top20_dates,
        key="hse_candlestick_case_date",
    )
    view_range = st.selectbox(
        "View Range:",
        VIEW_RANGE_OPTIONS,
        index=0,
        key="hse_candlestick_view_range",
    )

    ohlc = load_gold_daily_ohlc_dataset()
    if ohlc.empty:
        st.info(
            "N/A: daily OHLC data is missing. Run `python src/fetch_gold_daily_ohlc.py` "
            "or use the one-click update after daily data access is available."
        )
        st.caption(CANDLESTICK_SOURCE_NOTE_EN)
        st.caption(CANDLESTICK_SOURCE_NOTE_ZH)
        return

    window = week_window_for_event(selected_date, view_range)
    window_ohlc = ohlc_for_window(ohlc, window)
    if window_ohlc.empty:
        st.warning(
            "N/A: no daily OHLC rows found for "
            f"{window.range_start:%Y-%m-%d} to {window.range_end:%Y-%m-%d}."
        )
        st.caption(CANDLESTICK_SOURCE_NOTE_EN)
        st.caption(CANDLESTICK_SOURCE_NOTE_ZH)
        return

    render_interactive_chart(
        candlestick_title(window).replace("<br>", " / "),
        build_candlestick_figure(window_ohlc, window),
        key="historical_similarity_weekly_candlestick",
        height=560,
    )
    st.caption(CANDLESTICK_SOURCE_NOTE_EN)
    st.caption(CANDLESTICK_SOURCE_NOTE_ZH)


def page_research_report() -> None:
    st.header("Research Report")
    render_research_banner()
    st.markdown(load_research_report())


def format_scorecard_table(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    display = frame.copy()
    score_columns = [
        column
        for column in display.columns
        if column in {"train_score", "test_score", "stability_score"} or "score" in column
    ]
    for column in score_columns:
        if column in display.columns:
            display[column] = display[column].map(
                lambda value: "N/A" if pd.isna(value) else f"{float(value):.1f}"
            )
    return display


def format_lifecycle_table(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    display = frame.copy()
    for column in display.columns:
        if column == "count" or column.endswith("_count") or column == "sample_count":
            display[column] = display[column].map(lambda value: "N/A" if pd.isna(value) else f"{int(float(value)):,}")
        elif (
            "return" in column
            or "win_rate" in column
            or "velocity" in column
            or "acceleration" in column
            or "percentile" in column
        ):
            display[column] = display[column].map(lambda value: fmt_percent(value, input_scale="fraction"))
        elif "correlation" in column or "score" in column:
            display[column] = display[column].map(lambda value: "N/A" if pd.isna(value) else f"{float(value):.3f}")
    return display


PLOTLY_LIFECYCLE_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": True,
    "modeBarButtonsToAdd": ["select2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "ghpr_mm_lifecycle_interactive",
        "scale": 2,
    },
}

PLOTLY_STRUCTURE_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": True,
    "modeBarButtonsToAdd": ["select2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "ghpr_mm_structure_lifecycle_interactive",
        "scale": 2,
    },
}

PLOTLY_VELOCITY_READING_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "scrollZoom": True,
    "modeBarButtonsToAdd": ["select2d"],
    "toImageButtonOptions": {
        "format": "png",
        "filename": "ghpr_mm_velocity_reading_layer",
        "scale": 2,
    },
}


def lifecycle_plot_frame(lifecycle: pd.DataFrame) -> pd.DataFrame:
    required = [
        "date",
        "gold_close",
        "mm_percentile",
        "mm_velocity_8w",
        "mm_acceleration_8w",
        "mm_lifecycle_state",
    ]
    missing = missing_columns(lifecycle, required)
    if missing:
        raise ValueError("Missing lifecycle columns: " + ", ".join(missing))
    frame = lifecycle[required].copy().dropna(subset=["date", "gold_close", "mm_percentile"])
    if frame.empty:
        raise ValueError("No valid lifecycle rows for interactive chart.")
    first_gold = frame["gold_close"].dropna().iloc[0]
    frame["gold_normalized_index"] = frame["gold_close"] / first_gold * 100
    frame["mm_percentile_pct"] = frame["mm_percentile"] * 100
    frame["mm_velocity_8w_pct"] = frame["mm_velocity_8w"] * 100
    frame["mm_acceleration_8w_pct"] = frame["mm_acceleration_8w"] * 100
    return frame


def lifecycle_hover_template(trace_name: str) -> str:
    return (
        "Date: %{x|%Y-%m-%d}<br>"
        "gold_close: %{customdata[0]:,.2f}<br>"
        "gold_normalized_index: %{customdata[1]:.2f}<br>"
        "mm_percentile: %{customdata[2]:.2f}%<br>"
        "mm_velocity_8w: %{customdata[3]:.2f} pct points<br>"
        "mm_acceleration_8w: %{customdata[4]:.2f} pct points<br>"
        "mm_lifecycle_state: %{customdata[5]}<extra>" + trace_name + "</extra>"
    )


def lifecycle_range_controls() -> dict[str, object]:
    return {
        "rangeslider": {"visible": True},
        "rangeselector": {
            "x": 0,
            "y": 1.18,
            "buttons": [
                {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                {"count": 3, "label": "3Y", "step": "year", "stepmode": "backward"},
                {"count": 5, "label": "5Y", "step": "year", "stepmode": "backward"},
                {"label": "All", "step": "all"},
            ]
        },
        "type": "date",
    }


def build_interactive_lifecycle_core_chart(lifecycle: pd.DataFrame) -> go.Figure:
    frame = lifecycle_plot_frame(lifecycle)
    customdata = frame[
        [
            "gold_close",
            "gold_normalized_index",
            "mm_percentile_pct",
            "mm_velocity_8w_pct",
            "mm_acceleration_8w_pct",
            "mm_lifecycle_state",
        ]
    ].to_numpy()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=frame["date"],
            y=frame["gold_normalized_index"],
            mode="lines",
            name="Gold normalized index",
            line={"color": "#111827", "width": 2},
            customdata=customdata,
            hovertemplate=lifecycle_hover_template("Gold normalized index"),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=frame["date"],
            y=frame["mm_percentile_pct"],
            mode="lines",
            name="MM Percentile",
            line={"color": "#2563eb", "width": 2},
            customdata=customdata,
            hovertemplate=lifecycle_hover_template("MM Percentile"),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title=None,
        height=520,
        margin={"l": 40, "r": 48, "t": 58, "b": 35},
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis=lifecycle_range_controls(),
    )
    fig.update_yaxes(title_text="Gold normalized index", secondary_y=False)
    fig.update_yaxes(title_text="MM Percentile", range=[0, 100], secondary_y=True)
    return fig


def build_interactive_velocity_acceleration_chart(lifecycle: pd.DataFrame) -> go.Figure:
    frame = lifecycle_plot_frame(lifecycle)
    customdata = frame[
        [
            "gold_close",
            "gold_normalized_index",
            "mm_percentile_pct",
            "mm_velocity_8w_pct",
            "mm_acceleration_8w_pct",
            "mm_lifecycle_state",
        ]
    ].to_numpy()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame["date"],
            y=frame["mm_velocity_8w_pct"],
            mode="lines",
            name="MM Velocity 8W",
            line={"color": "#f97316", "width": 2},
            customdata=customdata,
            hovertemplate=lifecycle_hover_template("MM Velocity 8W"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=frame["date"],
            y=frame["mm_acceleration_8w_pct"],
            mode="lines",
            name="MM Acceleration 8W",
            line={"color": "#16a34a", "width": 2},
            customdata=customdata,
            hovertemplate=lifecycle_hover_template("MM Acceleration 8W"),
        )
    )
    fig.add_hline(y=0, line_color="#111827", line_width=1)
    fig.update_layout(
        title=None,
        height=420,
        margin={"l": 40, "r": 40, "t": 58, "b": 35},
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis=lifecycle_range_controls(),
        yaxis={"title": "Pct points"},
    )
    return fig


def structure_plot_frame(structure: pd.DataFrame) -> pd.DataFrame:
    required = [
        "date",
        "gold_close",
        "mm_long",
        "mm_short",
        "mm_net",
        "mm_long_percentile_156w",
        "mm_short_percentile_156w",
        "mm_net_percentile_156w",
        "mm_long_velocity_8w",
        "mm_short_velocity_8w",
        "mm_net_velocity_8w",
        "mm_structure_state",
    ]
    missing = missing_columns(structure, required)
    if missing:
        raise ValueError("Missing structure columns: " + ", ".join(missing))
    frame = structure[required].copy().dropna(
        subset=[
            "date",
            "gold_close",
            "mm_long_percentile_156w",
            "mm_short_percentile_156w",
            "mm_net_percentile_156w",
        ]
    )
    if frame.empty:
        raise ValueError("No valid structure rows for interactive chart.")
    first_gold = frame["gold_close"].dropna().iloc[0]
    frame["gold_normalized_index"] = frame["gold_close"] / first_gold * 100
    for column in [
        "mm_long_percentile_156w",
        "mm_short_percentile_156w",
        "mm_net_percentile_156w",
        "mm_long_velocity_8w",
        "mm_short_velocity_8w",
        "mm_net_velocity_8w",
    ]:
        frame[f"{column}_pct"] = frame[column] * 100
    return frame


def structure_customdata(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[
        [
            "gold_close",
            "gold_normalized_index",
            "mm_long",
            "mm_short",
            "mm_net",
            "mm_long_percentile_156w_pct",
            "mm_short_percentile_156w_pct",
            "mm_net_percentile_156w_pct",
            "mm_long_velocity_8w_pct",
            "mm_short_velocity_8w_pct",
            "mm_net_velocity_8w_pct",
            "mm_structure_state",
        ]
    ]


def structure_hover_template(trace_name: str) -> str:
    return (
        "Date: %{x|%Y-%m-%d}<br>"
        "gold_close: %{customdata[0]:,.2f}<br>"
        "gold_normalized_index: %{customdata[1]:.2f}<br>"
        "mm_long: %{customdata[2]:,.0f}<br>"
        "mm_short: %{customdata[3]:,.0f}<br>"
        "mm_net: %{customdata[4]:,.0f}<br>"
        "mm_long_percentile_156w: %{customdata[5]:.2f}%<br>"
        "mm_short_percentile_156w: %{customdata[6]:.2f}%<br>"
        "mm_net_percentile_156w: %{customdata[7]:.2f}%<br>"
        "mm_long_velocity_8w: %{customdata[8]:.2f} pct points<br>"
        "mm_short_velocity_8w: %{customdata[9]:.2f} pct points<br>"
        "mm_net_velocity_8w: %{customdata[10]:.2f} pct points<br>"
        "mm_structure_state: %{customdata[11]}<extra>" + trace_name + "</extra>"
    )


def build_interactive_structure_core_chart(structure: pd.DataFrame) -> go.Figure:
    frame = structure_plot_frame(structure)
    customdata = structure_customdata(frame).to_numpy()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=frame["date"],
            y=frame["gold_normalized_index"],
            mode="lines",
            name="Gold normalized index",
            line={"color": "#111827", "width": 2},
            customdata=customdata,
            hovertemplate=structure_hover_template("Gold normalized index"),
        ),
        secondary_y=False,
    )
    for name, column, color in [
        ("MM Long Percentile", "mm_long_percentile_156w_pct", "#16a34a"),
        ("MM Short Percentile", "mm_short_percentile_156w_pct", "#ef4444"),
        ("MM Net Percentile", "mm_net_percentile_156w_pct", "#2563eb"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=frame["date"],
                y=frame[column],
                mode="lines",
                name=name,
                line={"color": color, "width": 2},
                customdata=customdata,
                hovertemplate=structure_hover_template(name),
            ),
            secondary_y=True,
        )
    fig.update_layout(
        title=None,
        height=540,
        margin={"l": 40, "r": 52, "t": 58, "b": 35},
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis=lifecycle_range_controls(),
    )
    fig.update_yaxes(title_text="Gold normalized index", secondary_y=False)
    fig.update_yaxes(title_text="MM percentile", range=[0, 100], secondary_y=True)
    return fig


def build_interactive_structure_velocity_chart(structure: pd.DataFrame) -> go.Figure:
    frame = structure_plot_frame(structure)
    customdata = structure_customdata(frame).to_numpy()
    fig = go.Figure()
    for name, column, color in [
        ("Long velocity 8W", "mm_long_velocity_8w_pct", "#16a34a"),
        ("Short velocity 8W", "mm_short_velocity_8w_pct", "#ef4444"),
        ("Net velocity 8W", "mm_net_velocity_8w_pct", "#2563eb"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=frame["date"],
                y=frame[column],
                mode="lines",
                name=name,
                line={"color": color, "width": 2},
                customdata=customdata,
                hovertemplate=structure_hover_template(name),
            )
        )
    fig.add_hline(y=0, line_color="#111827", line_width=1)
    fig.update_layout(
        title=None,
        height=430,
        margin={"l": 40, "r": 40, "t": 58, "b": 35},
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.08, "x": 0},
        xaxis=lifecycle_range_controls(),
        yaxis={"title": "Percentile point change"},
    )
    return fig


def format_velocity_reading_table(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    display = frame.copy()
    for column in display.columns:
        if column == "date":
            display[column] = display[column].map(lambda value: fmt_date(value))
        elif column == "gold_close":
            display[column] = display[column].map(lambda value: fmt_number(value, digits=2))
        elif column.endswith("_8w") or column.endswith("_26w") or column.endswith("_2w") or column.endswith("_4w") or "delta" in column or "fast_avg" in column:
            display[column] = display[column].map(
                lambda value: "N/A" if pd.isna(value) else f"{float(value) * 100:.2f} pct points"
            )
    return display


def velocity_reading_description(reading: object) -> str:
    descriptions = {
        "MEDIUM_TERM_PARTICIPATION_BUILDING": (
            "Long 26W and Net 26W are both above zero, so the medium-term historical structure "
            "is showing participation building."
        ),
        "SHORT_TERM_ONLY_REACTION": (
            "The fast Short window is active while Long 26W and Net 26W are near zero. "
            "This is mainly a short-term structure reading."
        ),
        "SHORT_TERM_RECOVERY_MEDIUM_TERM_UNCONFIRMED": (
            "The 8W baseline has moved above zero, but the 26W candidate has not aligned. "
            "The swing reading is not yet confirmed by the medium-term candidate window."
        ),
        "MEDIUM_TERM_STRUCTURE_WEAKENING": (
            "Long 26W and Net 26W are both below zero, so the medium-term historical structure "
            "is showing participation easing."
        ),
        "MIXED_STRUCTURE": (
            "Long, Short, and Net readings are mixed or incomplete. Treat this as a research "
            "context state rather than a directional conclusion."
        ),
    }
    return descriptions.get(str(reading), "N/A: no reading description available.")


def velocity_reading_plot_frame(reading: pd.DataFrame) -> pd.DataFrame:
    required = [
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
    ]
    missing = missing_columns(reading, required)
    if missing:
        raise ValueError("Missing velocity reading columns: " + ", ".join(missing))
    frame = reading[required].copy().dropna(subset=["date"])
    if frame.empty:
        raise ValueError("No valid velocity reading rows for interactive chart.")
    numeric_columns = [
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
    ]
    for column in numeric_columns:
        frame[f"{column}_pct_points"] = pd.to_numeric(frame[column], errors="coerce") * 100
    return frame


def velocity_reading_customdata(frame: pd.DataFrame) -> pd.DataFrame:
    return frame[
        [
            "gold_close",
            "long_baseline_8w_pct_points",
            "long_candidate_26w_pct_points",
            "long_baseline_candidate_delta_pct_points",
            "short_baseline_8w_pct_points",
            "short_candidate_2w_pct_points",
            "short_candidate_4w_pct_points",
            "short_candidate_fast_avg_pct_points",
            "short_baseline_candidate_delta_pct_points",
            "net_baseline_8w_pct_points",
            "net_candidate_26w_pct_points",
            "net_baseline_candidate_delta_pct_points",
            "long_alignment_status",
            "short_alignment_status",
            "net_alignment_status",
            "overall_velocity_reading",
        ]
    ]


def velocity_reading_hover_template(trace_name: str) -> str:
    return (
        "Date: %{x|%Y-%m-%d}<br>"
        "gold_close: %{customdata[0]:,.2f}<br>"
        "long_baseline_8w: %{customdata[1]:.2f} pct points<br>"
        "long_candidate_26w: %{customdata[2]:.2f} pct points<br>"
        "long_delta: %{customdata[3]:.2f} pct points<br>"
        "short_baseline_8w: %{customdata[4]:.2f} pct points<br>"
        "short_candidate_2w: %{customdata[5]:.2f} pct points<br>"
        "short_candidate_4w: %{customdata[6]:.2f} pct points<br>"
        "short_candidate_fast_avg: %{customdata[7]:.2f} pct points<br>"
        "short_delta: %{customdata[8]:.2f} pct points<br>"
        "net_baseline_8w: %{customdata[9]:.2f} pct points<br>"
        "net_candidate_26w: %{customdata[10]:.2f} pct points<br>"
        "net_delta: %{customdata[11]:.2f} pct points<br>"
        "long_status: %{customdata[12]}<br>"
        "short_status: %{customdata[13]}<br>"
        "net_status: %{customdata[14]}<br>"
        "overall_reading: %{customdata[15]}<extra>" + trace_name + "</extra>"
    )


def build_interactive_velocity_baseline_candidate_chart(reading: pd.DataFrame) -> go.Figure:
    frame = velocity_reading_plot_frame(reading)
    customdata = velocity_reading_customdata(frame).to_numpy()
    fig = go.Figure()
    for name, column, color, dash in [
        ("Long 8W baseline", "long_baseline_8w_pct_points", "#16a34a", "solid"),
        ("Long 26W candidate", "long_candidate_26w_pct_points", "#166534", "dash"),
        ("Short 8W baseline", "short_baseline_8w_pct_points", "#ef4444", "solid"),
        ("Short 2W / 4W average", "short_candidate_fast_avg_pct_points", "#991b1b", "dash"),
        ("Net 8W baseline", "net_baseline_8w_pct_points", "#2563eb", "solid"),
        ("Net 26W candidate", "net_candidate_26w_pct_points", "#1e3a8a", "dash"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=frame["date"],
                y=frame[column],
                mode="lines",
                name=name,
                line={"color": color, "width": 2, "dash": dash},
                customdata=customdata,
                hovertemplate=velocity_reading_hover_template(name),
            )
        )
    fig.add_hline(y=0, line_color="#111827", line_width=1)
    fig.update_layout(
        title=None,
        height=500,
        margin={"l": 40, "r": 40, "t": 58, "b": 35},
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.10, "x": 0},
        xaxis=lifecycle_range_controls(),
        yaxis={"title": "Percentile point change"},
    )
    return fig


def build_interactive_velocity_delta_chart(reading: pd.DataFrame) -> go.Figure:
    frame = velocity_reading_plot_frame(reading)
    customdata = velocity_reading_customdata(frame).to_numpy()
    fig = go.Figure()
    for name, column, color in [
        ("Long baseline - candidate", "long_baseline_candidate_delta_pct_points", "#16a34a"),
        ("Short baseline - candidate", "short_baseline_candidate_delta_pct_points", "#ef4444"),
        ("Net baseline - candidate", "net_baseline_candidate_delta_pct_points", "#2563eb"),
    ]:
        fig.add_trace(
            go.Scatter(
                x=frame["date"],
                y=frame[column],
                mode="lines",
                name=name,
                line={"color": color, "width": 2},
                customdata=customdata,
                hovertemplate=velocity_reading_hover_template(name),
            )
        )
    fig.add_hline(y=0, line_color="#111827", line_width=1)
    fig.update_layout(
        title=None,
        height=420,
        margin={"l": 40, "r": 40, "t": 58, "b": 35},
        hovermode="x unified",
        dragmode="pan",
        legend={"orientation": "h", "y": 1.10, "x": 0},
        xaxis=lifecycle_range_controls(),
        yaxis={"title": "Baseline minus candidate, pct points"},
    )
    return fig


def page_percentile_definition_audit() -> None:
    st.header("Percentile Definition Audit")
    render_research_banner()
    st.info(
        "v0.5 research page only. Current Position still uses the existing 156W rolling percentile logic. "
        "Formal dashboard definition changes should wait for the v0.6 decision."
    )

    scorecard = load_percentile_scorecard()
    recommendation = load_percentile_recommendation()

    st.subheader("Recommended Definitions")
    if not recommendation.empty:
        preferred = [
            "display_name",
            "formal_recommended_definition",
            "recommended_production_safe_definition",
            "recommended_rolling_definition",
            "recommended_unified_rolling_definition",
            "production_safe_overall_score",
            "rolling_overall_score",
        ]
        columns = [column for column in preferred if column in recommendation.columns]
        st.dataframe(format_scorecard_table(recommendation[columns]), width="stretch", hide_index=True)
    elif not scorecard.empty and "recommended" in scorecard.columns:
        recommended = scorecard[scorecard["recommended"]].copy()
        preferred = [
            "factor",
            "horizon",
            "definition",
            "stability_score",
            "train_score",
            "test_score",
            "reason",
        ]
        columns = [column for column in preferred if column in recommended.columns]
        st.dataframe(format_scorecard_table(recommended[columns]), width="stretch", hide_index=True)
    else:
        st.warning(f"N/A: missing recommendation data: {PERCENTILE_RECOMMENDATION_PATH}")

    st.subheader("Scorecard")
    if scorecard.empty:
        st.warning(f"N/A: missing scorecard data: {PERCENTILE_SCORECARD_PATH}")
    else:
        c1, c2 = st.columns(2)
        factor_options = ["All", *sorted(scorecard["factor"].dropna().astype(str).unique())]
        horizon_options = ["All", *sorted(scorecard["horizon"].dropna().astype(str).unique())]
        selected_factor = c1.selectbox("Factor", factor_options)
        selected_horizon = c2.selectbox("Horizon", horizon_options)
        filtered = scorecard.copy()
        if selected_factor != "All":
            filtered = filtered[filtered["factor"].astype(str) == selected_factor]
        if selected_horizon != "All":
            filtered = filtered[filtered["horizon"].astype(str) == selected_horizon]
        st.dataframe(format_scorecard_table(filtered), width="stretch", hide_index=True)

    st.subheader("Main Comparison Charts")
    for title, path in PERCENTILE_AUDIT_CHARTS:
        if path.exists():
            st.markdown(f"**{title}**")
            st.image(str(path), width="stretch")
        else:
            st.warning(f"N/A: missing chart: {path.name}")

    st.subheader("Audit Report Markdown")
    report = load_percentile_audit_report()
    if report == "N/A":
        st.warning(f"N/A: missing audit report: {PERCENTILE_AUDIT_REPORT_PATH}")
    else:
        st.markdown(report)


def page_mm_definition_audit() -> None:
    st.header("MM Definition Audit")
    render_research_banner()
    st.info(
        "Research page only. Current Position still displays the existing "
        "`mm_net_percentile_156w` value. Formal homepage definition changes should wait for GHPR v0.5-B."
    )

    scorecard = load_mm_definition_scorecard()

    st.subheader("Recommended Definition Summary")
    st.markdown(
        "`暫不替換`: keep `mm_net_percentile_156w` as the current dashboard MM reference while reviewing "
        "`104W percentile` and `260W percentile` as research candidates."
    )
    if scorecard.empty:
        st.warning(f"N/A: missing MM scorecard data: {MM_DEFINITION_SCORECARD_PATH}")
    else:
        recommended = (
            scorecard[scorecard["recommended"]].copy()
            if "recommended" in scorecard.columns
            else pd.DataFrame()
        )
        preferred = [
            "horizon",
            "definition",
            "total_score",
            "information_score",
            "stability_score",
            "train_test_score",
            "interpretability_score",
            "reason",
        ]
        columns = [column for column in preferred if column in recommended.columns]
        if columns and not recommended.empty:
            st.dataframe(format_scorecard_table(recommended[columns]), width="stretch", hide_index=True)
        else:
            st.info("N/A: no recommended rows in MM scorecard.")

        summary = (
            scorecard.groupby("definition", as_index=False)
            .agg(
                avg_total_score=("total_score", "mean"),
                recommended_horizon_count=("recommended", "sum"),
            )
            .sort_values("avg_total_score", ascending=False)
        )
        st.dataframe(format_scorecard_table(summary), width="stretch", hide_index=True)

    st.subheader("Scorecard")
    if scorecard.empty:
        st.warning(f"N/A: missing scorecard data: {MM_DEFINITION_SCORECARD_PATH}")
    else:
        c1, c2 = st.columns(2)
        definition_options = ["All", *sorted(scorecard["definition"].dropna().astype(str).unique())]
        horizon_options = ["All", *sorted(scorecard["horizon"].dropna().astype(str).unique())]
        selected_definition = c1.selectbox("Definition", definition_options)
        selected_horizon = c2.selectbox("Horizon", horizon_options)
        filtered = scorecard.copy()
        if selected_definition != "All":
            filtered = filtered[filtered["definition"].astype(str) == selected_definition]
        if selected_horizon != "All":
            filtered = filtered[filtered["horizon"].astype(str) == selected_horizon]
        st.dataframe(format_scorecard_table(filtered), width="stretch", hide_index=True)

    st.subheader("Audit Report Markdown")
    report = load_mm_definition_audit_report()
    if report == "N/A":
        st.warning(f"N/A: missing MM audit report: {MM_DEFINITION_AUDIT_REPORT_PATH}")
    else:
        st.markdown(report)

    st.subheader("Main Charts")
    for title, path in MM_DEFINITION_AUDIT_CHARTS:
        if path.exists():
            st.markdown(f"**{title}**")
            st.image(str(path), width="stretch")
        else:
            st.warning(f"N/A: missing chart: {path.name}")


def page_mm_lifecycle_research() -> None:
    st.header("MM Lifecycle Research")
    render_research_banner()
    st.info(
        "Historical Lifecycle Research only. This page adds MM velocity, acceleration, lifecycle state, "
        "lead-lag correlation, and trajectory similarity context around the existing 156W MM percentile."
    )

    lifecycle = load_mm_lifecycle_dataset()
    state_analysis = load_mm_lifecycle_state_analysis()
    lead_lag = load_mm_lifecycle_lead_lag()
    trajectories = load_mm_trajectory_similarity()

    st.subheader("Current MM Lifecycle State")
    if lifecycle.empty:
        st.warning(f"N/A: missing MM lifecycle dataset: {MM_LIFECYCLE_DATASET_PATH}")
    else:
        latest = lifecycle.dropna(subset=["date"]).sort_values("date").iloc[-1]
        lifecycle_date = latest["date"].strftime("%Y-%m-%d") if pd.notna(latest["date"]) else "N/A"
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lifecycle Data Date", lifecycle_date)
        c2.metric("MM Lifecycle State", latest.get("mm_lifecycle_state", "N/A"))
        c3.metric("MM Velocity 8W", fmt_percent(latest.get("mm_velocity_8w"), input_scale="fraction"))
        c4.metric("MM Acceleration 8W", fmt_percent(latest.get("mm_acceleration_8w"), input_scale="fraction"))
        c5, c6, c7 = st.columns(3)
        c5.metric("MM Percentile", fmt_percent(latest.get("mm_percentile"), input_scale="fraction"))
        c6.metric("MM Velocity 4W", fmt_percent(latest.get("mm_velocity_4w"), input_scale="fraction"))
        c7.metric("MM Velocity 26W", fmt_percent(latest.get("mm_velocity_26w"), input_scale="fraction"))
        render_component_date_context("MM Lifecycle", lifecycle_date)

    st.subheader("Interactive Gold vs MM Lifecycle")
    st.caption(
        "此圖用來觀察黃金價格生命週期與 Managed Money Percentile 生命週期的同步、背離與轉折。"
    )
    if lifecycle.empty:
        st.warning("N/A: lifecycle data unavailable for interactive chart.")
    else:
        try:
            render_interactive_chart(
                "Interactive Gold vs MM Lifecycle",
                build_interactive_lifecycle_core_chart(lifecycle),
                key="mm_lifecycle_gold_vs_mm",
                height=560,
                config=PLOTLY_LIFECYCLE_CONFIG,
                has_range_slider=True,
            )
        except ValueError as error:
            st.warning(f"N/A: {error}")

    st.subheader("Interactive MM Velocity / Acceleration")
    if lifecycle.empty:
        st.warning("N/A: lifecycle velocity data unavailable for interactive chart.")
    else:
        try:
            render_interactive_chart(
                "Interactive MM Velocity / Acceleration",
                build_interactive_velocity_acceleration_chart(lifecycle),
                key="mm_lifecycle_velocity_acceleration",
                height=540,
                config=PLOTLY_LIFECYCLE_CONFIG,
                has_range_slider=True,
            )
        except ValueError as error:
            st.warning(f"N/A: {error}")

    st.subheader("MM Velocity / Acceleration")
    if lifecycle.empty:
        st.warning("N/A: lifecycle velocity data unavailable.")
    else:
        required = ["date", "mm_percentile", "mm_velocity_4w", "mm_velocity_8w", "mm_velocity_12w", "mm_velocity_26w", "mm_acceleration_4w", "mm_acceleration_8w"]
        missing = missing_columns(lifecycle, required)
        if missing:
            st.warning("N/A: missing lifecycle columns: " + ", ".join(missing))
        else:
            view = lifecycle[required + ["mm_lifecycle_state"]].tail(52).copy()
            st.dataframe(format_lifecycle_table(view), width="stretch", hide_index=True)

    st.subheader("Lead-Lag Summary")
    if lead_lag.empty:
        st.warning(f"N/A: missing lead-lag data: {MM_LIFECYCLE_LEAD_LAG_PATH}")
    else:
        c1, c2 = st.columns(2)
        features = ["All", *sorted(lead_lag["mm_feature"].dropna().astype(str).unique())]
        horizons = ["All", *sorted(lead_lag["gold_horizon"].dropna().astype(str).unique())]
        selected_feature = c1.selectbox("MM feature", features)
        selected_horizon = c2.selectbox("Gold horizon", horizons)
        filtered = lead_lag.copy()
        if selected_feature != "All":
            filtered = filtered[filtered["mm_feature"].astype(str) == selected_feature]
        if selected_horizon != "All":
            filtered = filtered[filtered["gold_horizon"].astype(str) == selected_horizon]
        filtered = filtered.assign(abs_rank=filtered["rank_correlation"].abs()).sort_values(
            "abs_rank", ascending=False
        )
        preferred = [
            "mm_feature",
            "gold_horizon",
            "lag_weeks",
            "correlation",
            "rank_correlation",
            "sample_count",
            "interpretation",
        ]
        st.dataframe(format_lifecycle_table(filtered[preferred].head(30)), width="stretch", hide_index=True)

    st.subheader("Lifecycle State Outcomes")
    if state_analysis.empty:
        st.warning(f"N/A: missing lifecycle state analysis: {MM_LIFECYCLE_STATE_ANALYSIS_PATH}")
    else:
        st.dataframe(format_lifecycle_table(state_analysis), width="stretch", hide_index=True)

    st.subheader("Top Similar MM Trajectories")
    if trajectories.empty:
        st.warning(f"N/A: missing trajectory similarity data: {MM_TRAJECTORY_SIMILARITY_PATH}")
    else:
        window_options = sorted(trajectories["window"].dropna().astype(str).unique())
        default_index = window_options.index("8W") if "8W" in window_options else 0
        selected_window = st.selectbox("Trajectory window", window_options, index=default_index)
        view = trajectories[trajectories["window"].astype(str) == selected_window].head(20).copy()
        preferred = [
            "window",
            "historical_start_date",
            "historical_end_date",
            "similarity_score",
            "historical_gold_return_1w",
            "historical_gold_return_2w",
            "historical_gold_return_4w",
            "historical_gold_return_8w",
        ]
        available = [column for column in preferred if column in view.columns]
        st.caption("Recent 52 weeks are excluded from trajectory similarity by default.")
        st.dataframe(format_lifecycle_table(view[available]), width="stretch", hide_index=True)

    st.subheader("Lifecycle Charts")
    for title, path in MM_LIFECYCLE_CHARTS:
        if path.exists():
            st.markdown(f"**{title}**")
            st.image(str(path), width="stretch")
        else:
            st.warning(f"N/A: missing chart: {path.name}")

    st.subheader("MM Lifecycle Summary Markdown")
    summary = load_mm_lifecycle_summary()
    if summary == "N/A":
        st.warning(f"N/A: missing lifecycle summary: {MM_LIFECYCLE_SUMMARY_PATH}")
    else:
        st.markdown(summary)


def page_mm_structure_lifecycle() -> None:
    st.header("MM Structure Lifecycle")
    render_research_banner()
    st.info(
        "Historical Structure Lifecycle Research only. This page decomposes MM Net into Long, Short, "
        "and Net structure, without changing the existing Current Position definition."
    )

    structure = load_mm_structure_dataset()
    state_analysis = load_mm_structure_state_analysis()
    contribution_analysis = load_mm_structure_contribution_analysis()
    lead_lag = load_mm_structure_lead_lag()

    st.subheader("Current MM Structure Snapshot")
    if structure.empty:
        st.warning(f"N/A: missing MM structure dataset: {MM_STRUCTURE_DATASET_PATH}")
    else:
        latest = structure.dropna(subset=["date"]).sort_values("date").iloc[-1]
        structure_date = latest["date"].strftime("%Y-%m-%d") if pd.notna(latest["date"]) else "N/A"
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Structure Data Date", structure_date)
        c2.metric("Gold Close", fmt_number(latest.get("gold_close")))
        c3.metric("Structure State", latest.get("mm_structure_state", "N/A"))
        c4.metric("Contribution State", latest.get("mm_structure_contribution_state", "N/A"))

        c5, c6, c7 = st.columns(3)
        c5.metric("MM Long", fmt_int(latest.get("mm_long")))
        c6.metric("MM Short", fmt_int(latest.get("mm_short")))
        c7.metric("MM Net", fmt_int(latest.get("mm_net")))

        c8, c9, c10 = st.columns(3)
        c8.metric("Long Percentile", fmt_percent(latest.get("mm_long_percentile_156w"), input_scale="fraction"))
        c9.metric("Short Percentile", fmt_percent(latest.get("mm_short_percentile_156w"), input_scale="fraction"))
        c10.metric("Net Percentile", fmt_percent(latest.get("mm_net_percentile_156w"), input_scale="fraction"))

        c11, c12, c13 = st.columns(3)
        c11.metric("Long Velocity 8W", fmt_percent(latest.get("mm_long_velocity_8w"), input_scale="fraction"))
        c12.metric("Short Velocity 8W", fmt_percent(latest.get("mm_short_velocity_8w"), input_scale="fraction"))
        c13.metric("Net Velocity 8W", fmt_percent(latest.get("mm_net_velocity_8w"), input_scale="fraction"))
        render_component_date_context("MM Structure", structure_date)

    st.subheader("Interactive MM Structure Lifecycle")
    st.caption(
        "此圖用來觀察 Gold、MM Long、MM Short、MM Net 的長期結構生命週期，"
        "並檢查 Long / Short / Net 誰在推動 MM Net 變化。"
    )
    st.markdown("**Interactive Gold vs MM Long / Short / Net Structure**")
    if structure.empty:
        st.warning("N/A: structure data unavailable for interactive chart.")
    else:
        try:
            render_interactive_chart(
                "Interactive Gold vs MM Long / Short / Net Structure",
                build_interactive_structure_core_chart(structure),
                key="mm_structure_gold_long_short_net",
                height=580,
                config=PLOTLY_STRUCTURE_CONFIG,
                has_range_slider=True,
            )
        except ValueError as error:
            st.warning(f"N/A: {error}")

    st.subheader("Interactive MM Structure Velocity")
    if structure.empty:
        st.warning("N/A: structure velocity data unavailable for interactive chart.")
    else:
        try:
            render_interactive_chart(
                "Interactive MM Structure Velocity",
                build_interactive_structure_velocity_chart(structure),
                key="mm_structure_velocity",
                height=540,
                config=PLOTLY_STRUCTURE_CONFIG,
                has_range_slider=True,
            )
        except ValueError as error:
            st.warning(f"N/A: {error}")

    st.subheader("MM Structure Charts")
    for title, path in MM_STRUCTURE_CHARTS:
        if path.exists():
            st.markdown(f"**{title}**")
            st.image(str(path), width="stretch")
        else:
            st.warning(f"N/A: missing chart: {path.name}")

    st.subheader("Long / Short / Net Structure Table")
    if structure.empty:
        st.warning("N/A: structure table unavailable.")
    else:
        required = [
            "date",
            "mm_long_percentile_156w",
            "mm_short_percentile_156w",
            "mm_net_percentile_156w",
            "mm_long_velocity_8w",
            "mm_short_velocity_8w",
            "mm_net_velocity_8w",
            "mm_structure_state",
            "mm_structure_contribution_state",
        ]
        missing = missing_columns(structure, required)
        if missing:
            st.warning("N/A: missing structure columns: " + ", ".join(missing))
        else:
            st.dataframe(
                format_lifecycle_table(structure[required].tail(52)),
                width="stretch",
                hide_index=True,
            )

    st.subheader("MM Structure State Analysis")
    if state_analysis.empty:
        st.warning(f"N/A: missing structure state analysis: {MM_STRUCTURE_STATE_ANALYSIS_PATH}")
    else:
        st.dataframe(format_lifecycle_table(state_analysis), width="stretch", hide_index=True)

    st.subheader("MM Structure Contribution Analysis")
    if contribution_analysis.empty:
        st.warning(f"N/A: missing contribution analysis: {MM_STRUCTURE_CONTRIBUTION_ANALYSIS_PATH}")
    else:
        st.dataframe(format_lifecycle_table(contribution_analysis), width="stretch", hide_index=True)

    st.subheader("Long / Short / Net Lead-Lag Summary")
    if lead_lag.empty:
        st.warning(f"N/A: missing structure lead-lag data: {MM_STRUCTURE_LEAD_LAG_PATH}")
    else:
        c1, c2 = st.columns(2)
        features = ["All", *sorted(lead_lag["mm_feature"].dropna().astype(str).unique())]
        horizons = ["All", *sorted(lead_lag["gold_horizon"].dropna().astype(str).unique())]
        selected_feature = c1.selectbox("Structure feature", features)
        selected_horizon = c2.selectbox("Following return horizon", horizons)
        filtered = lead_lag.copy()
        if selected_feature != "All":
            filtered = filtered[filtered["mm_feature"].astype(str) == selected_feature]
        if selected_horizon != "All":
            filtered = filtered[filtered["gold_horizon"].astype(str) == selected_horizon]
        filtered = filtered.assign(abs_rank=filtered["rank_correlation"].abs()).sort_values(
            "abs_rank", ascending=False
        )
        preferred = [
            "mm_feature",
            "gold_horizon",
            "lag_weeks",
            "correlation",
            "rank_correlation",
            "sample_count",
            "interpretation",
        ]
        st.dataframe(format_lifecycle_table(filtered[preferred].head(40)), width="stretch", hide_index=True)

    st.subheader("MM Structure Lifecycle Summary Markdown")
    summary = load_mm_structure_summary()
    if summary == "N/A":
        st.warning(f"N/A: missing structure summary: {MM_STRUCTURE_SUMMARY_PATH}")
    else:
        st.markdown(summary)


def page_mm_velocity_window_discovery() -> None:
    st.header("MM Velocity Window Discovery")
    render_research_banner()
    st.info(
        "Historical Structure Research only. This page compares MM Long / Short / Net velocity windows "
        "without replacing the current 8W definition on the dashboard."
    )

    velocity_window_dataset = load_mm_velocity_window_dataset()
    if velocity_window_dataset.empty:
        st.warning(f"N/A: missing velocity window dataset: {MM_VELOCITY_WINDOW_DATASET_PATH}")
    elif "date" not in velocity_window_dataset.columns:
        st.warning("N/A: missing velocity window dataset columns: date")
    else:
        velocity_window_dates = velocity_window_dataset.dropna(subset=["date"]).sort_values("date")
        if velocity_window_dates.empty:
            st.warning("N/A: velocity window dataset has no valid date rows.")
        else:
            latest_velocity_window = velocity_window_dates.iloc[-1]
            render_component_date_context(
                "Velocity Window Dataset",
                fmt_date(latest_velocity_window.get("date")),
            )

    reading = load_mm_velocity_reading_layer()
    st.subheader("Velocity Reading Layer")
    st.caption(
        "This layer compares the current 8W baseline with research candidate windows. "
        "Historical structure research only."
    )
    if reading.empty:
        st.warning(f"N/A: missing velocity reading layer dataset: {MM_VELOCITY_READING_LAYER_PATH}")
    else:
        if "date" not in reading.columns:
            st.warning("N/A: missing velocity reading columns: date")
            latest_reading = pd.DataFrame()
        else:
            latest_reading = reading.dropna(subset=["date"]).sort_values("date").tail(1)
        snapshot_columns = [
            column for column in VELOCITY_READING_SNAPSHOT_COLUMNS if column in latest_reading.columns
        ]
        missing_snapshot = [
            column for column in VELOCITY_READING_SNAPSHOT_COLUMNS if column not in reading.columns
        ]
        if missing_snapshot:
            st.warning("N/A: missing velocity reading columns: " + ", ".join(missing_snapshot))
        if snapshot_columns:
            st.subheader("Current Velocity Reading Snapshot")
            st.dataframe(
                format_velocity_reading_table(latest_reading[snapshot_columns]),
                width="stretch",
                hide_index=True,
            )

        latest_row = latest_reading.iloc[0] if not latest_reading.empty else None
        if latest_row is not None:
            render_component_date_context("Velocity Reading Layer", fmt_date(latest_row.get("date")))
        card_cols = st.columns(3)
        reading_cards = [
            {
                "title": "Long Velocity Reading",
                "baseline": "8W",
                "candidate": "26W",
                "status": "long_alignment_status",
                "explanation": (
                    "Long 8W shows the current swing movement. Long 26W shows the medium-term "
                    "positioning lifecycle candidate."
                ),
            },
            {
                "title": "Short Velocity Reading",
                "baseline": "8W",
                "candidate": "2W / 4W",
                "status": "short_alignment_status",
                "explanation": (
                    "Short 2W / 4W tracks faster event reaction, stress, or covering-window movement."
                ),
            },
            {
                "title": "Net Velocity Reading",
                "baseline": "8W",
                "candidate": "26W",
                "status": "net_alignment_status",
                "explanation": (
                    "Net 26W checks whether Long and Short component movement is visible in the "
                    "medium-term net structure."
                ),
            },
        ]
        for column, card in zip(card_cols, reading_cards):
            status_value = "N/A" if latest_row is None else latest_row.get(card["status"], "N/A")
            with column.container(border=True):
                st.markdown(f"**{card['title']}**")
                st.metric("Current Baseline", card["baseline"])
                st.metric("Research Candidate", card["candidate"])
                st.markdown(f"**Status:** `{status_value}`")
                st.markdown(card["explanation"])

        st.subheader("Current Historical Structure Reading")
        if latest_row is None:
            st.info("N/A: no current velocity reading row available.")
        else:
            overall = latest_row.get("overall_velocity_reading", "N/A")
            st.info(f"`{overall}`\n\n{velocity_reading_description(overall)}")
            st.caption("Historical structure research only. Not a trading signal. Not financial advice.")

        st.subheader("Interactive Velocity Baseline vs Candidate")
        try:
            render_interactive_chart(
                "Interactive Velocity Baseline vs Candidate",
                build_interactive_velocity_baseline_candidate_chart(reading),
                key="velocity_reading_baseline_candidate",
                height=580,
                config=PLOTLY_VELOCITY_READING_CONFIG,
                has_range_slider=True,
            )
        except Exception as error:
            st.warning(f"N/A: unable to render velocity baseline/candidate chart: {error}")

        st.subheader("Interactive Velocity Delta")
        try:
            render_interactive_chart(
                "Interactive Velocity Delta",
                build_interactive_velocity_delta_chart(reading),
                key="velocity_reading_delta",
                height=540,
                config=PLOTLY_VELOCITY_READING_CONFIG,
                has_range_slider=True,
            )
        except Exception as error:
            st.warning(f"N/A: unable to render velocity delta chart: {error}")

        st.subheader("MM Velocity Reading Layer Markdown")
        reading_report = load_mm_velocity_reading_report()
        if reading_report == "N/A":
            st.warning(f"N/A: missing velocity reading layer report: {MM_VELOCITY_READING_REPORT_PATH}")
        else:
            st.markdown(reading_report)

    st.subheader("Velocity Window Review")
    st.caption(
        "Current Dashboard Baseline remains 8W. Research candidates are shown as a definition layer only."
    )
    card_cols = st.columns(3)
    cards = [
        {
            "title": "MM Long Velocity Window",
            "primary": "26W",
            "baseline": "8W",
            "meaning": (
                "Long velocity reflects slower managed-money position building or reduction. "
                "Current research suggests 26W may better capture the medium-term lifecycle of long positioning."
            ),
            "zh": (
                "MM Long Velocity 比較像中期建倉或減倉週期。"
                "目前研究顯示 26W 可能比 8W 更適合觀察 Long 的中期生命週期。"
            ),
        },
        {
            "title": "MM Short Velocity Window",
            "primary": "2W / 4W",
            "baseline": "8W",
            "meaning": (
                "Short velocity appears to react faster and may be more event-driven. "
                "Current research suggests 2W and 4W should be monitored as short-term stress / covering windows."
            ),
            "zh": (
                "MM Short Velocity 比較像短線避險、事件反應或空單回補週期。"
                "目前研究顯示 2W / 4W 可能比 8W 更適合觀察 Short 的快速變化。"
            ),
        },
        {
            "title": "MM Net Velocity Window",
            "primary": "26W",
            "baseline": "8W",
            "meaning": (
                "Net velocity combines Long and Short behavior. Current research suggests it behaves more like "
                "a medium-term cycle, closer to Long positioning."
            ),
            "zh": (
                "MM Net Velocity 是 Long 與 Short 的綜合結果。"
                "目前研究顯示 Net 的節奏比較接近 Long 的中期週期，因此 26W 值得作為候選主視窗。"
            ),
        },
    ]
    for column, card in zip(card_cols, cards):
        with column.container(border=True):
            st.markdown(f"**{card['title']}**")
            st.metric("Primary Research Window", card["primary"])
            st.metric("Current Dashboard Baseline", card["baseline"])
            st.markdown(f"**Meaning:** {card['meaning']}")
            st.markdown(card["zh"])

    st.subheader("Velocity Window Summary")
    st.dataframe(pd.DataFrame(VELOCITY_WINDOW_DEFINITION_ROWS), width="stretch", hide_index=True)
    st.caption(
        "These rows are historical research definitions only. They do not change the current 8W baseline."
    )

    scorecard = load_mm_velocity_window_scorecard()
    train_test = load_mm_velocity_window_train_test()
    bucket = load_mm_velocity_window_bucket_analysis()

    st.subheader("Recommendation Summary")
    if scorecard.empty:
        st.warning(f"N/A: missing velocity window scorecard: {MM_VELOCITY_WINDOW_SCORECARD_PATH}")
    else:
        recommended = scorecard[scorecard["recommended"]].copy() if "recommended" in scorecard.columns else pd.DataFrame()
        if recommended.empty:
            st.info("N/A: no recommended rows in velocity window scorecard.")
        else:
            summary = (
                recommended.groupby(["feature_group", "window"], as_index=False)
                .agg(
                    avg_total_score=("total_score", "mean"),
                    avg_information_score=("information_score", "mean"),
                    avg_stability_score=("stability_score", "mean"),
                    avg_train_test_score=("train_test_score", "mean"),
                )
                .sort_values(["feature_group", "avg_total_score"], ascending=[True, False])
            )
            st.dataframe(format_lifecycle_table(summary), width="stretch", hide_index=True)
        st.caption("Current dashboard velocity definitions are unchanged; v0.6.2 is research only.")

    st.subheader("Scorecard")
    if scorecard.empty:
        st.warning(f"N/A: missing scorecard data: {MM_VELOCITY_WINDOW_SCORECARD_PATH}")
    else:
        c1, c2, c3 = st.columns(3)
        group_options = ["All", *sorted(scorecard["feature_group"].dropna().astype(str).unique())]
        window_options = ["All", *sorted(scorecard["window"].dropna().astype(str).unique(), key=lambda value: int(value.replace("W", "")))]
        horizon_options = ["All", *sorted(scorecard["horizon"].dropna().astype(str).unique())]
        selected_group = c1.selectbox("Feature group", group_options)
        selected_window = c2.selectbox("Window", window_options)
        selected_horizon = c3.selectbox("Horizon", horizon_options)
        filtered = scorecard.copy()
        if selected_group != "All":
            filtered = filtered[filtered["feature_group"].astype(str) == selected_group]
        if selected_window != "All":
            filtered = filtered[filtered["window"].astype(str) == selected_window]
        if selected_horizon != "All":
            filtered = filtered[filtered["horizon"].astype(str) == selected_horizon]
        st.dataframe(format_lifecycle_table(filtered), width="stretch", hide_index=True)

    st.subheader("Train / Test Validation")
    if train_test.empty:
        st.warning(f"N/A: missing train/test data: {MM_VELOCITY_WINDOW_TRAIN_TEST_PATH}")
    else:
        st.dataframe(format_lifecycle_table(train_test), width="stretch", hide_index=True)

    st.subheader("Bucket Analysis")
    if bucket.empty:
        st.warning(f"N/A: missing bucket analysis: {MM_VELOCITY_WINDOW_BUCKET_ANALYSIS_PATH}")
    else:
        c1, c2 = st.columns(2)
        bucket_group_options = ["All", *sorted(bucket["feature_group"].dropna().astype(str).unique())]
        bucket_window_options = ["All", *sorted(bucket["window"].dropna().astype(str).unique(), key=lambda value: int(value.replace("W", "")))]
        selected_bucket_group = c1.selectbox("Bucket feature group", bucket_group_options)
        selected_bucket_window = c2.selectbox("Bucket window", bucket_window_options)
        bucket_view = bucket.copy()
        if selected_bucket_group != "All":
            bucket_view = bucket_view[bucket_view["feature_group"].astype(str) == selected_bucket_group]
        if selected_bucket_window != "All":
            bucket_view = bucket_view[bucket_view["window"].astype(str) == selected_bucket_window]
        st.dataframe(format_lifecycle_table(bucket_view), width="stretch", hide_index=True)

    st.subheader("Charts")
    for title, path in MM_VELOCITY_WINDOW_CHARTS:
        if path.exists():
            st.markdown(f"**{title}**")
            st.image(str(path), width="stretch")
        else:
            st.warning(f"N/A: missing chart: {path.name}")

    st.subheader("MM Velocity Window Summary Markdown")
    summary_md = load_mm_velocity_window_summary()
    if summary_md == "N/A":
        st.warning(f"N/A: missing velocity window summary: {MM_VELOCITY_WINDOW_SUMMARY_PATH}")
    else:
        st.markdown(summary_md)

    st.subheader("MM Velocity Window Review Markdown")
    review_md = load_mm_velocity_window_review()
    if review_md == "N/A":
        st.warning(f"N/A: missing velocity window review: {MM_VELOCITY_WINDOW_REVIEW_PATH}")
    else:
        st.markdown(review_md)


def page_update_log() -> None:
    st.header("Update Log")
    render_research_banner()
    st.markdown(load_update_log())


def main() -> None:
    st.title("GHPR Online Dashboard v0.4")
    st.caption("Cloud-ready historical positioning dashboard with one-click research data refresh.")

    render_update_controls()

    master = load_master_dataset()
    factor_result = load_factor_dataset()
    hub_summary = load_hub_summary()
    data_freshness_diagnostics = load_data_freshness_diagnostics()

    render_sidebar_metadata(master, hub_summary)
    hse_exclude_recent_weeks = render_hse_exclusion_control()
    (
        historical_similarity_report,
        historical_similarity_stats,
        hse_metadata,
    ) = load_historical_similarity_for_exclusion(hse_exclude_recent_weeks)
    if hse_metadata.get("fallback"):
        st.sidebar.warning("HSE used saved CSV fallback.")

    if master.empty:
        st.warning(f"N/A: master dataset not found or empty: {MASTER_PATH}")

    page = st.sidebar.radio(
        "Page",
        [
            "Current Position",
            "Historical Database",
            "Similar Cases",
            "Event Study",
            "Forward Statistics",
            "Research Report",
            "Percentile Definition Audit",
            "MM Definition Audit",
            "MM Lifecycle Research",
            "MM Structure Lifecycle",
            "MM Velocity Window Discovery",
            "Historical Similarity Engine",
            "Update Log",
        ],
    )

    if page == "Current Position":
        page_current_position(
            master,
            historical_similarity_report,
            historical_similarity_stats,
            hse_exclude_recent_weeks,
            hub_summary,
            data_freshness_diagnostics,
        )
    elif page == "Historical Database":
        page_historical_database(master)
    elif page == "Similar Cases":
        page_similar_cases(master)
    elif page == "Event Study":
        page_event_study(master)
    elif page == "Forward Statistics":
        page_forward_statistics(factor_result)
    elif page == "Research Report":
        page_research_report()
    elif page == "Percentile Definition Audit":
        page_percentile_definition_audit()
    elif page == "MM Definition Audit":
        page_mm_definition_audit()
    elif page == "MM Lifecycle Research":
        page_mm_lifecycle_research()
    elif page == "MM Structure Lifecycle":
        page_mm_structure_lifecycle()
    elif page == "MM Velocity Window Discovery":
        page_mm_velocity_window_discovery()
    elif page == "Historical Similarity Engine":
        page_historical_similarity_engine(
            historical_similarity_report,
            historical_similarity_stats,
            hse_exclude_recent_weeks,
        )
    else:
        page_update_log()


if __name__ == "__main__":
    main()

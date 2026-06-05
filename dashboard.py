from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.historical_similarity_engine import (
    DEFAULT_EXCLUDE_RECENT_WEEKS,
    build_historical_similarity_report,
    build_historical_similarity_stats,
    compute_current_similarity,
)
from src.update_pipeline import UPDATE_LOG_PATH, run_update_pipeline


PROJECT_ROOT = Path(__file__).resolve().parent
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
FACTOR_PATH = PROJECT_ROOT / "outputs" / "reports" / "single_factor_decile_analysis.csv"
REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "ghpr_factor_report.md"
HISTORICAL_SIMILARITY_REPORT_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_report.csv"
)
HISTORICAL_SIMILARITY_STATS_PATH = (
    PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_stats.csv"
)
HISTORICAL_SIMILARITY_CASES_CHART_PATH = (
    PROJECT_ROOT / "outputs" / "charts" / "historical_similarity_cases.png"
)

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


def render_current_market_snapshot(latest: pd.Series) -> None:
    st.subheader("Current Market Snapshot")
    state = market_state(latest.get(MM_FACTOR), latest.get("oi_percentile_156w"))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Date", fmt_date(latest.get("date")))
    c2.metric("Gold Close", fmt_number(latest.get("gold_close")))
    c3.metric("Market State", state)
    c4.metric("MM Net", fmt_int(latest.get("mm_net")))

    c1, c2, c3 = st.columns(3)
    c1.metric("MM Percentile", fmt_percent(latest.get(MM_FACTOR), input_scale="fraction"))
    c2.metric(
        "Producer Percentile",
        fmt_percent(latest.get("producer_net_percentile_156w"), input_scale="fraction"),
    )
    c3.metric("OI Percentile", fmt_percent(latest.get("oi_percentile_156w"), input_scale="fraction"))


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
    if st.sidebar.button("一鍵更新 GHPR 資料", width="stretch"):
        with st.spinner("Running GHPR update pipeline..."):
            result = run_update_pipeline(no_download=True)
            st.cache_data.clear()
        st.session_state["last_update_status"] = result.status_text
        st.session_state["last_update_log"] = str(result.log_path)
        st.session_state["last_update_error"] = result.error_message
        st.session_state["last_update_failure_summary"] = (
            build_update_failure_summary(result) if not result.success else None
        )

    status = st.session_state.get("last_update_status")
    if status == "success":
        st.sidebar.success("Update completed successfully")
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


def render_sidebar_metadata(master: pd.DataFrame) -> None:
    st.sidebar.subheader("Status")
    st.sidebar.metric("Last updated time", latest_update_time())
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
    render_current_market_snapshot(latest)
    render_historical_positioning_explanation(latest)
    render_indicator_dictionary_cards(latest)

    st.divider()
    render_research_banner()
    render_historical_tendency_summary(tendency_summary)
    render_top20_following_explanation(tendency_summary)
    render_not_signal_explanation()
    render_data_health(latest)
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

    st.plotly_chart(gold_mm_plot(filtered), width="stretch")
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
        title="Gold Price vs MM Net Percentile",
        hovermode="x unified",
        height=620,
        margin=dict(l=30, r=30, t=70, b=30),
        xaxis=dict(rangeslider=dict(visible=True), type="date"),
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

    st.plotly_chart(event_gold_path_plot(window), width="stretch")
    st.plotly_chart(event_mm_percentile_plot(window), width="stretch")


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
        title="Event Study: Gold Indexed Path",
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
        title="Event Study: MM Percentile Path",
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

    st.plotly_chart(group_event_path_plot(paths), width="stretch")


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
        title="Average Gold Event Path",
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

    st.plotly_chart(bucket_line_chart(view, "avg_forward_return_pct", "Average Historical Following Return (%)"), width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bucket_bar_chart(view, "win_rate_pct", "Win Rate (%)"), width="stretch")
    with c2:
        st.plotly_chart(bucket_bar_chart(view, "count", "Count"), width="stretch")

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
    fig.update_layout(title=title, height=420, margin=dict(l=30, r=30, t=60, b=60))
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
    fig.update_layout(title=title, height=420, margin=dict(l=30, r=30, t=60, b=60))
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


def page_research_report() -> None:
    st.header("Research Report")
    render_research_banner()
    st.markdown(load_research_report())


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

    render_sidebar_metadata(master)
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

"""Candlestick helpers for GHPR historical weekly case visualization."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go


OHLC_COLUMNS = ["date", "open", "high", "low", "close", "volume", "source"]
VIEW_RANGE_OPTIONS = [
    "Event week only",
    "Event week ±1 week",
    "Event week ±4 weeks",
    "Event week ±8 weeks",
]
CANDLESTICK_SOURCE_NOTE_EN = (
    "This candlestick chart uses COMEX GC futures proxy via Yahoo Finance GC=F. "
    "It is not official LBMA PM benchmark and not broker XAUUSD spot."
)
CANDLESTICK_SOURCE_NOTE_ZH = (
    "此 K 線使用 Yahoo Finance GC=F COMEX 黃金期貨代理資料，"
    "不是 LBMA PM 官方基準，也不是券商 XAUUSD 現貨報價。"
)


@dataclass(frozen=True)
class CandlestickWindow:
    event_date: pd.Timestamp
    event_week_start: pd.Timestamp
    event_week_end: pd.Timestamp
    range_start: pd.Timestamp
    range_end: pd.Timestamp
    view_range: str


def load_gold_daily_ohlc(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=OHLC_COLUMNS)
    frame = pd.read_csv(path)
    missing = [column for column in OHLC_COLUMNS if column not in frame.columns]
    if missing:
        return pd.DataFrame(columns=OHLC_COLUMNS)
    frame = frame[OHLC_COLUMNS].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["source"] = frame["source"].fillna("Yahoo Finance GC=F futures proxy")
    frame = frame.dropna(subset=["date", "open", "high", "low", "close"])
    return frame.sort_values("date").reset_index(drop=True)


def week_window_for_event(event_date: object, view_range: str) -> CandlestickWindow:
    event_ts = pd.Timestamp(event_date).normalize()
    event_week_start = event_ts - pd.Timedelta(days=event_ts.weekday())
    event_week_end = event_week_start + pd.Timedelta(days=4)
    extra_weeks = view_range_extra_weeks(view_range)
    return CandlestickWindow(
        event_date=event_ts,
        event_week_start=event_week_start,
        event_week_end=event_week_end,
        range_start=event_week_start - pd.Timedelta(weeks=extra_weeks),
        range_end=event_week_end + pd.Timedelta(weeks=extra_weeks),
        view_range=view_range,
    )


def view_range_extra_weeks(view_range: str) -> int:
    if view_range == "Event week ±1 week":
        return 1
    if view_range == "Event week ±4 weeks":
        return 4
    if view_range == "Event week ±8 weeks":
        return 8
    return 0


def ohlc_for_window(ohlc: pd.DataFrame, window: CandlestickWindow) -> pd.DataFrame:
    if ohlc.empty or "date" not in ohlc.columns:
        return pd.DataFrame(columns=OHLC_COLUMNS)
    mask = (ohlc["date"] >= window.range_start) & (ohlc["date"] <= window.range_end)
    return ohlc.loc[mask, OHLC_COLUMNS].copy().sort_values("date").reset_index(drop=True)


def candlestick_title(window: CandlestickWindow) -> str:
    return (
        "Historical Weekly Candlestick<br>"
        f"Case Date: {window.event_date:%Y-%m-%d}<br>"
        f"Week: {window.event_week_start:%Y-%m-%d} to {window.event_week_end:%Y-%m-%d}"
    )


def build_candlestick_figure(frame: pd.DataFrame, window: CandlestickWindow) -> go.Figure:
    plot_frame = frame.copy()
    plot_frame["date_label"] = plot_frame["date"].dt.strftime("%Y-%m-%d")
    plot_frame["source"] = plot_frame["source"].fillna("Yahoo Finance GC=F futures proxy")
    customdata = plot_frame[["date_label", "volume", "source"]]

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=plot_frame["date"],
                open=plot_frame["open"],
                high=plot_frame["high"],
                low=plot_frame["low"],
                close=plot_frame["close"],
                name="GC=F daily OHLC",
                customdata=customdata,
                hovertemplate=(
                    "date=%{customdata[0]}<br>"
                    "open=%{open:,.2f}<br>"
                    "high=%{high:,.2f}<br>"
                    "low=%{low:,.2f}<br>"
                    "close=%{close:,.2f}<br>"
                    "volume=%{customdata[1]:,.0f}<br>"
                    "source=%{customdata[2]}<extra></extra>"
                ),
            )
        ]
    )
    if view_range_extra_weeks(window.view_range) > 0:
        fig.add_vline(
            x=window.event_date,
            line_width=2,
            line_dash="dash",
            line_color="#111827",
            annotation_text="historical_case_date",
            annotation_position="top",
        )
    fig.update_layout(
        title=candlestick_title(window),
        xaxis_title="date",
        yaxis_title="GC=F futures proxy price",
        height=520,
        margin=dict(l=30, r=30, t=110, b=40),
        xaxis_rangeslider_visible=False,
    )
    return fig

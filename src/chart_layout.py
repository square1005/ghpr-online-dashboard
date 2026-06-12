"""Shared Plotly layout helpers for GHPR interactive charts."""

from __future__ import annotations

import plotly.graph_objects as go


RANGE_SELECTOR_BUTTONS = [
    dict(count=1, label="1Y", step="year", stepmode="backward"),
    dict(count=3, label="3Y", step="year", stepmode="backward"),
    dict(count=5, label="5Y", step="year", stepmode="backward"),
    dict(step="all", label="All"),
]


def apply_ghpr_plotly_layout(
    fig: go.Figure,
    title: str | None = None,
    height: int = 520,
    show_legend: bool = True,
    has_range_slider: bool | None = None,
) -> go.Figure:
    """Apply a consistent non-overlapping layout for Streamlit Plotly charts."""
    margin_top = 148 if has_range_slider else 96
    fig.update_layout(
        title=None if title is None else dict(text=title, y=0.98, x=0, xanchor="left"),
        height=max(height, 500),
        margin=dict(l=55, r=35, t=margin_top, b=88 if has_range_slider else 72),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.06,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            traceorder="normal",
        ),
        hovermode="x unified",
        showlegend=show_legend,
    )
    return fig


def apply_ghpr_time_axis(
    fig: go.Figure,
    rangeslider_visible: bool = True,
    rangeselector_visible: bool = True,
) -> go.Figure:
    """Apply standard GHPR time-axis controls."""
    xaxis: dict[str, object] = {"type": "date"}
    if rangeslider_visible:
        xaxis["rangeslider"] = {"visible": True}
    if rangeselector_visible:
        xaxis["rangeselector"] = {"buttons": RANGE_SELECTOR_BUTTONS, "x": 0, "y": 1.18}
    fig.update_xaxes(**xaxis)
    return fig

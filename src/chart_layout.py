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
    uirevision: str | None = None,
) -> go.Figure:
    """Apply a consistent non-overlapping layout for Streamlit Plotly charts."""
    margin_top = 115 if has_range_slider else 90
    fig.update_layout(
        title=dict(text="" if title is None else title, y=0.96, x=0, xanchor="left"),
        height=max(height, 500),
        margin=dict(l=50, r=30, t=margin_top, b=80 if has_range_slider else 70),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.08 if has_range_slider else 1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0)",
            borderwidth=0,
            traceorder="normal",
        ),
        hovermode="x unified",
        showlegend=show_legend,
        uirevision=uirevision,
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

from __future__ import annotations

import json
import lzma
import math
import struct
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import matplotlib
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

AUDIT_CSV = REPORTS_DIR / "gold_source_audit.csv"
RECENT_100_CSV = REPORTS_DIR / "gold_close_recent_100.csv"
ANOMALY_CSV = REPORTS_DIR / "gold_anomaly_2025_2026_true.csv"
COMPARISON_CSV = REPORTS_DIR / "gold_price_comparison_detail.csv"
COMPARISON_PNG = CHARTS_DIR / "gold_price_comparison.png"

SPOT_START = "20250101"
SPOT_END = "20260526"

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
    "blue": "#5477C4",
    "gold": "#B8A037",
    "orange": "#CC6F47",
}


def load_master() -> pd.DataFrame:
    if not MASTER_PATH.exists():
        raise FileNotFoundError(f"Missing master dataset: {MASTER_PATH}")

    df = pd.read_csv(MASTER_PATH)
    required = {
        "date",
        "gold_close",
        "gold_price_source",
        "gold_anomaly_2025_2026",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Missing required master columns: {missing}")

    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["gold_close"] = pd.to_numeric(df["gold_close"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return df


def classify_gold_source(value: object) -> str:
    text = str(value or "").lower()
    if "fred" in text:
        return "FRED"
    if "gc=f" in text or "yahoo" in text:
        return "Yahoo GC=F"
    if "stooq" in text:
        return "Stooq"
    if not text or text == "nan":
        return "Missing"
    return "Other"


def bool_series(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes", "y"})


def source_audit_rows(df: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    stats = df["gold_close"].dropna()
    source_bucket = df["gold_price_source"].map(classify_gold_source)

    rows.append(
        {
            "section": "gold_close_stats",
            "item": "row_count",
            "value": int(df["gold_close"].notna().sum()),
            "row_count": int(df["gold_close"].notna().sum()),
            "first_date": df["date"].min().date().isoformat(),
            "last_date": df["date"].max().date().isoformat(),
            "notes": "Rows with non-null gold_close in ghpr_master_weekly.csv",
        }
    )
    rows.append(
        {
            "section": "gold_close_stats",
            "item": "min",
            "value": round(float(stats.min()), 6) if not stats.empty else None,
            "row_count": int(stats.count()),
            "first_date": "",
            "last_date": "",
            "notes": "Minimum gold_close",
        }
    )
    rows.append(
        {
            "section": "gold_close_stats",
            "item": "max",
            "value": round(float(stats.max()), 6) if not stats.empty else None,
            "row_count": int(stats.count()),
            "first_date": "",
            "last_date": "",
            "notes": "Maximum gold_close",
        }
    )
    rows.append(
        {
            "section": "gold_close_stats",
            "item": "mean",
            "value": round(float(stats.mean()), 6) if not stats.empty else None,
            "row_count": int(stats.count()),
            "first_date": "",
            "last_date": "",
            "notes": "Average gold_close",
        }
    )

    for source in ["FRED", "Yahoo GC=F", "Stooq", "Other", "Missing"]:
        subset = df[source_bucket == source]
        rows.append(
            {
                "section": "gold_price_source_count",
                "item": source,
                "value": int(len(subset)),
                "row_count": int(len(subset)),
                "first_date": subset["date"].min().date().isoformat() if not subset.empty else "",
                "last_date": subset["date"].max().date().isoformat() if not subset.empty else "",
                "notes": (
                    "Classified from gold_price_source text in ghpr_master_weekly.csv"
                ),
            }
        )

    source_detail = (
        df.assign(source_bucket=source_bucket)
        .groupby(["source_bucket", "gold_price_source"], dropna=False)
        .size()
        .reset_index(name="rows")
        .sort_values(["source_bucket", "rows"], ascending=[True, False])
    )
    for _, row in source_detail.iterrows():
        rows.append(
            {
                "section": "gold_price_source_detail",
                "item": row["source_bucket"],
                "value": int(row["rows"]),
                "row_count": int(row["rows"]),
                "first_date": "",
                "last_date": "",
                "notes": str(row["gold_price_source"]),
            }
        )

    rows.append(
        {
            "section": "benchmark_note",
            "item": "xauusd_spot_benchmark",
            "value": "External XAUUSD spot benchmark",
            "row_count": "",
            "first_date": "",
            "last_date": "",
            "notes": (
                "External benchmark for comparison only; see xauusd_spot_comparison "
                "rows for the benchmark source used in this run."
            ),
        }
    )
    return rows


def read_stooq_xauusd_spot(start: str, end: str, max_pages: int = 20) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    seen_dates: set[pd.Timestamp] = set()
    earliest_needed = pd.to_datetime(start, format="%Y%m%d")

    for page in range(1, max_pages + 1):
        query = urlencode({"s": "xauusd", "i": "d", "f": start, "t": end, "l": page})
        url = f"https://stooq.com/q/d/?{query}"
        tables = pd.read_html(url)
        candidates: list[pd.DataFrame] = []

        for table in tables:
            columns = {str(col).strip() for col in table.columns}
            if {"No.", "Date", "Open", "High", "Low", "Close"}.issubset(columns):
                tmp = table.copy()
                tmp.columns = [str(col).strip() for col in tmp.columns]
                tmp["date"] = pd.to_datetime(
                    tmp["Date"], errors="coerce", format="mixed"
                )
                tmp["spot_close"] = pd.to_numeric(tmp["Close"], errors="coerce")
                tmp["spot_open"] = pd.to_numeric(tmp["Open"], errors="coerce")
                tmp["spot_high"] = pd.to_numeric(tmp["High"], errors="coerce")
                tmp["spot_low"] = pd.to_numeric(tmp["Low"], errors="coerce")
                tmp["No."] = pd.to_numeric(tmp["No."], errors="coerce")
                tmp = tmp.dropna(subset=["No.", "date", "spot_close"])
                if not tmp.empty:
                    candidates.append(
                        tmp[["date", "spot_open", "spot_high", "spot_low", "spot_close"]]
                    )

        if not candidates:
            break

        page_df = max(candidates, key=len).copy()
        new_dates = set(page_df["date"]).difference(seen_dates)
        if not new_dates:
            break

        seen_dates.update(new_dates)
        frames.append(page_df)

        if page_df["date"].min() <= earliest_needed:
            break

    if not frames:
        return pd.DataFrame(
            columns=["date", "spot_open", "spot_high", "spot_low", "spot_close"]
        )

    spot = (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(subset=["date"], keep="first")
        .sort_values("date")
        .reset_index(drop=True)
    )
    start_dt = pd.to_datetime(start, format="%Y%m%d")
    end_dt = pd.to_datetime(end, format="%Y%m%d")
    return spot[(spot["date"] >= start_dt) & (spot["date"] <= end_dt)].reset_index(
        drop=True
    )


def read_dukascopy_xauusd_spot(start: str, end: str) -> pd.DataFrame:
    start_dt = pd.to_datetime(start, format="%Y%m%d")
    end_dt = pd.to_datetime(end, format="%Y%m%d")
    frames: list[pd.DataFrame] = []

    for year in range(start_dt.year, end_dt.year + 1):
        try:
            frames.append(read_dukascopy_daily_year(year))
        except Exception:
            hourly_daily = read_dukascopy_hourly_as_daily(year, start_dt, end_dt)
            if not hourly_daily.empty:
                frames.append(hourly_daily)

    if not frames:
        return pd.DataFrame(
            columns=[
                "date",
                "spot_open",
                "spot_high",
                "spot_low",
                "spot_close",
                "spot_volume",
            ]
        )

    spot = (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(subset=["date"], keep="first")
        .sort_values("date")
        .reset_index(drop=True)
    )
    return spot[(spot["date"] >= start_dt) & (spot["date"] <= end_dt)].reset_index(
        drop=True
    )


def read_dukascopy_daily_year(year: int) -> pd.DataFrame:
    url = (
        "https://datafeed.dukascopy.com/datafeed/"
        f"XAUUSD/{year}/BID_candles_day_1.bi5"
    )
    raw = read_dukascopy_bi5(url)
    base = pd.Timestamp(year=year, month=1, day=1)
    return decode_dukascopy_candles(raw, base)


def read_dukascopy_hourly_as_daily(
    year: int, start_dt: pd.Timestamp, end_dt: pd.Timestamp
) -> pd.DataFrame:
    month_start = 1 if year > start_dt.year else start_dt.month
    month_end = 12 if year < end_dt.year else end_dt.month
    monthly_frames: list[pd.DataFrame] = []

    for month in range(month_start, month_end + 1):
        url = (
            "https://datafeed.dukascopy.com/datafeed/"
            f"XAUUSD/{year}/{month - 1:02d}/BID_candles_hour_1.bi5"
        )
        try:
            raw = read_dukascopy_bi5(url)
        except Exception:
            continue
        base = pd.Timestamp(year=year, month=month, day=1)
        decoded = decode_dukascopy_candles(raw, base)
        if not decoded.empty:
            monthly_frames.append(decoded)

    if not monthly_frames:
        return pd.DataFrame(
            columns=[
                "date",
                "spot_open",
                "spot_high",
                "spot_low",
                "spot_close",
                "spot_volume",
            ]
        )

    hourly = (
        pd.concat(monthly_frames, ignore_index=True)
        .sort_values("date")
        .reset_index(drop=True)
    )
    hourly["day"] = hourly["date"].dt.normalize()
    daily = (
        hourly.groupby("day", as_index=False)
        .agg(
            spot_open=("spot_open", "first"),
            spot_high=("spot_high", "max"),
            spot_low=("spot_low", "min"),
            spot_close=("spot_close", "last"),
            spot_volume=("spot_volume", "sum"),
        )
        .rename(columns={"day": "date"})
    )
    return daily


def read_dukascopy_bi5(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    compressed = urlopen(request, timeout=30).read()
    return lzma.decompress(compressed)


def decode_dukascopy_candles(raw: bytes, base: pd.Timestamp) -> pd.DataFrame:
    record_size = struct.calcsize(">IIIIIf")
    records: list[dict[str, object]] = []

    for offset in range(0, len(raw), record_size):
        chunk = raw[offset : offset + record_size]
        if len(chunk) < record_size:
            continue
        seconds, open_i, high_i, low_i, close_i, volume = struct.unpack(
            ">IIIIIf", chunk
        )
        date = base + pd.Timedelta(seconds=int(seconds))
        records.append(
            {
                "date": date,
                "spot_open": open_i / 1000.0,
                "spot_high": high_i / 1000.0,
                "spot_low": low_i / 1000.0,
                "spot_close": close_i / 1000.0,
                "spot_volume": float(volume),
            }
        )

    return pd.DataFrame(records)


def build_comparison(df: pd.DataFrame, spot: pd.DataFrame) -> pd.DataFrame:
    window = df[
        (df["date"] >= pd.Timestamp("2025-01-01"))
        & (df["date"] <= pd.Timestamp("2026-05-26"))
    ][["date", "gold_close", "gold_price_source"]].copy()

    if spot.empty:
        window["spot_date"] = pd.NaT
        window["spot_close"] = math.nan
        window["gold_close_minus_xauusd_spot"] = math.nan
        window["gold_close_pct_diff"] = math.nan
        return window

    comparison = pd.merge_asof(
        window.sort_values("date"),
        spot[["date", "spot_close"]].sort_values("date").rename(
            columns={"date": "spot_date"}
        ),
        left_on="date",
        right_on="spot_date",
        direction="backward",
        tolerance=pd.Timedelta(days=7),
    )
    comparison["gold_close_minus_xauusd_spot"] = (
        comparison["gold_close"] - comparison["spot_close"]
    )
    comparison["gold_close_pct_diff"] = (
        comparison["gold_close"] / comparison["spot_close"] - 1.0
    )
    return comparison


def add_header(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(
        0.075,
        0.965,
        title,
        ha="left",
        va="top",
        fontsize=16,
        fontweight="bold",
        color=TOKENS["ink"],
    )
    fig.text(
        0.075,
        0.925,
        subtitle,
        ha="left",
        va="top",
        fontsize=10,
        color=TOKENS["muted"],
    )


def render_comparison_chart(
    comparison: pd.DataFrame, spot_ok: bool, benchmark_label: str
) -> None:
    plt.rcParams.update(
        {
            "font.family": ["Segoe UI", "DejaVu Sans", "Arial", "sans-serif"],
            "figure.facecolor": TOKENS["surface"],
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "xtick.color": TOKENS["muted"],
            "ytick.color": TOKENS["muted"],
        }
    )

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(13, 8),
        gridspec_kw={"height_ratios": [3, 1.2], "hspace": 0.18},
        sharex=True,
    )
    ax_price, ax_diff = axes

    subtitle = (
        f"Weekly GHPR master prices matched to nearest prior {benchmark_label} "
        "close; window 2025-01-01 to 2026-05-26."
    )
    add_header(fig, "GHPR gold_close vs XAUUSD Spot", subtitle)

    if not spot_ok or comparison["spot_close"].dropna().empty:
        ax_price.text(
            0.5,
            0.5,
            "XAUUSD spot benchmark unavailable; internal GHPR audit still completed.",
            ha="center",
            va="center",
            transform=ax_price.transAxes,
            color=TOKENS["muted"],
            fontsize=12,
        )
        ax_price.plot(
            comparison["date"],
            comparison["gold_close"],
            color=TOKENS["blue"],
            linewidth=1.8,
            label="GHPR gold_close",
        )
    else:
        ax_price.plot(
            comparison["date"],
            comparison["gold_close"],
            color=TOKENS["blue"],
            linewidth=1.9,
            label="GHPR gold_close",
        )
        ax_price.plot(
            comparison["date"],
            comparison["spot_close"],
            color=TOKENS["gold"],
            linewidth=1.7,
            linestyle="--",
            label=f"{benchmark_label} close",
        )
        ax_diff.axhline(0, color=TOKENS["ink"], linewidth=0.9)
        ax_diff.plot(
            comparison["date"],
            comparison["gold_close_pct_diff"] * 100,
            color=TOKENS["orange"],
            linewidth=1.6,
            label="GHPR minus spot (%)",
        )
        max_abs = comparison["gold_close_pct_diff"].abs().max()
        if pd.notna(max_abs):
            ax_diff.text(
                0.995,
                0.88,
                f"Max abs diff: {max_abs * 100:.2f}%",
                ha="right",
                va="center",
                transform=ax_diff.transAxes,
                color=TOKENS["muted"],
                fontsize=9,
            )

    for axis in axes:
        axis.grid(True, axis="y", color=TOKENS["grid"], linewidth=0.8)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
        axis.spines["left"].set_color(TOKENS["axis"])
        axis.spines["bottom"].set_color(TOKENS["axis"])

    ax_price.set_ylabel("Gold close")
    ax_diff.set_ylabel("Diff (%)")
    ax_diff.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100))
    ax_diff.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax_diff.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    if ax_price.get_legend_handles_labels()[0]:
        ax_price.legend(loc="upper left", frameon=False, ncol=2)
    if ax_diff.get_legend_handles_labels()[0]:
        ax_diff.legend(loc="upper left", bbox_to_anchor=(0.0, 1.08), frameon=False)

    fig.subplots_adjust(top=0.86, left=0.075, right=0.98, bottom=0.1)
    COMPARISON_PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(COMPARISON_PNG, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_master()
    recent_100 = df[["date", "gold_close"]].tail(100).copy()
    recent_100["date"] = recent_100["date"].dt.date.astype(str)
    recent_100.to_csv(RECENT_100_CSV, index=False)

    anomaly_mask = (
        (df["date"] >= pd.Timestamp("2025-01-01"))
        & (df["date"] <= pd.Timestamp("2026-05-26"))
        & bool_series(df["gold_anomaly_2025_2026"])
    )
    anomaly_cols = [
        col
        for col in [
            "date",
            "gold_close",
            "gold_anomaly_2025_2026",
            "gold_anomaly_reason",
            "gold_price_source",
        ]
        if col in df.columns
    ]
    anomalies = df.loc[anomaly_mask, anomaly_cols].copy()
    anomalies["date"] = anomalies["date"].dt.date.astype(str)
    anomalies.to_csv(ANOMALY_CSV, index=False)

    audit_rows = source_audit_rows(df)

    spot_warning = ""
    benchmark_label = "Dukascopy XAUUSD bid spot"
    benchmark_source_note = (
        "Dukascopy XAUUSD BID daily candles; 2026 daily values are aggregated "
        "from hourly candles where the annual daily file is not available."
    )
    try:
        spot = read_dukascopy_xauusd_spot(SPOT_START, SPOT_END)
    except Exception as exc:
        spot = pd.DataFrame(
            columns=["date", "spot_open", "spot_high", "spot_low", "spot_close"]
        )
        spot_warning = f"Dukascopy XAUUSD spot benchmark fetch failed: {exc}"

    comparison = build_comparison(df, spot)
    comparison.to_csv(COMPARISON_CSV, index=False)
    render_comparison_chart(
        comparison,
        spot_ok=not spot.empty,
        benchmark_label=benchmark_label,
    )

    valid_comp = comparison.dropna(subset=["spot_close", "gold_close_pct_diff"])
    audit_rows.append(
        {
            "section": "xauusd_spot_comparison",
            "item": "comparison_rows",
            "value": int(len(valid_comp)),
            "row_count": int(len(valid_comp)),
            "first_date": valid_comp["date"].min().date().isoformat()
            if not valid_comp.empty
            else "",
            "last_date": valid_comp["date"].max().date().isoformat()
            if not valid_comp.empty
            else "",
            "notes": (
                f"{benchmark_source_note} {spot_warning}".strip()
                if spot_warning
                else (
                    f"{benchmark_source_note} GHPR weekly gold_close matched to "
                    "nearest prior benchmark close."
                )
            ),
        }
    )
    audit_rows.append(
        {
            "section": "xauusd_spot_comparison",
            "item": "mean_pct_diff",
            "value": round(float(valid_comp["gold_close_pct_diff"].mean() * 100), 6)
            if not valid_comp.empty
            else None,
            "row_count": int(len(valid_comp)),
            "first_date": "",
            "last_date": "",
            "notes": "Percent difference: GHPR gold_close / XAUUSD spot close - 1.",
        }
    )
    audit_rows.append(
        {
            "section": "xauusd_spot_comparison",
            "item": "max_abs_pct_diff",
            "value": round(float(valid_comp["gold_close_pct_diff"].abs().max() * 100), 6)
            if not valid_comp.empty
            else None,
            "row_count": int(len(valid_comp)),
            "first_date": "",
            "last_date": "",
            "notes": "Largest absolute percent difference in the comparison window.",
        }
    )

    audit = pd.DataFrame(audit_rows)
    audit.to_csv(AUDIT_CSV, index=False)

    source_counts = (
        audit[audit["section"].eq("gold_price_source_count")]
        .set_index("item")["row_count"]
        .to_dict()
    )
    summary = {
        "master_rows": int(len(df)),
        "gold_close_recent_100_csv": str(RECENT_100_CSV),
        "gold_close_min": round(float(df["gold_close"].min()), 6),
        "gold_close_max": round(float(df["gold_close"].max()), 6),
        "gold_close_mean": round(float(df["gold_close"].mean()), 6),
        "anomaly_rows_2025_2026": int(len(anomalies)),
        "source_counts": {k: int(v) for k, v in source_counts.items()},
        "spot_rows": int(len(spot)),
        "comparison_rows": int(len(valid_comp)),
        "benchmark_label": benchmark_label,
        "mean_pct_diff": round(float(valid_comp["gold_close_pct_diff"].mean() * 100), 6)
        if not valid_comp.empty
        else None,
        "max_abs_pct_diff": round(
            float(valid_comp["gold_close_pct_diff"].abs().max() * 100), 6
        )
        if not valid_comp.empty
        else None,
        "outputs": {
            "gold_source_audit_csv": str(AUDIT_CSV),
            "recent_100_csv": str(RECENT_100_CSV),
            "anomaly_csv": str(ANOMALY_CSV),
            "comparison_csv": str(COMPARISON_CSV),
            "comparison_png": str(COMPARISON_PNG),
        },
        "spot_warning": spot_warning,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

"""Fetch daily COMEX gold futures proxy OHLC data for GHPR candlestick views."""

from __future__ import annotations

import argparse
import csv
import io
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import requests

try:
    from .utils import PROCESSED_DIR, ensure_project_dirs
except ImportError:
    from utils import PROCESSED_DIR, ensure_project_dirs


OUTPUT_PATH = PROCESSED_DIR / "gold_daily_ohlc.csv"
YAHOO_SYMBOL = "GC=F"
SOURCE_LABEL = "Yahoo Finance GC=F futures proxy"
START_DATE = "2009-01-01"
YAHOO_URL_TEMPLATE = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    "?period1={period1}&period2={period2}&interval=1d&events=history"
)
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
    )
}
OUTPUT_COLUMNS = ["date", "open", "high", "low", "close", "volume", "source"]


def yahoo_period_seconds(start_date: str) -> tuple[int, int]:
    start = pd.Timestamp(start_date).to_pydatetime().replace(tzinfo=timezone.utc)
    end = pd.Timestamp.now(tz="UTC").normalize() + pd.Timedelta(days=2)
    return int(start.timestamp()), int(end.timestamp())


def fetch_yahoo_daily_ohlc(start_date: str = START_DATE, timeout: int = 90) -> pd.DataFrame:
    period1, period2 = yahoo_period_seconds(start_date)
    url = YAHOO_URL_TEMPLATE.format(
        symbol=quote(YAHOO_SYMBOL, safe=""),
        period1=period1,
        period2=period2,
    )
    response = requests.get(url, timeout=timeout, headers=REQUEST_HEADERS)
    response.raise_for_status()
    payload = response.json()

    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp") or []
    quote_data = result["indicators"]["quote"][0]
    opens = quote_data.get("open") or []
    highs = quote_data.get("high") or []
    lows = quote_data.get("low") or []
    closes = quote_data.get("close") or []
    volumes = quote_data.get("volume") or []

    rows = []
    for timestamp, open_, high, low, close, volume in zip(
        timestamps,
        opens,
        highs,
        lows,
        closes,
        volumes,
        strict=False,
    ):
        if any(value is None for value in [open_, high, low, close]):
            continue
        rows.append(
            {
                "date": pd.to_datetime(timestamp, unit="s", utc=True).date().isoformat(),
                "open": open_,
                "high": high,
                "low": low,
                "close": close,
                "volume": int(volume or 0),
                "source": SOURCE_LABEL,
            }
        )

    frame = pd.DataFrame(rows, columns=OUTPUT_COLUMNS)
    if frame.empty:
        raise RuntimeError("Yahoo Finance returned no usable GC=F OHLC rows.")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame = frame.dropna(subset=["date"]).drop_duplicates(subset=["date"], keep="last")
    frame = frame.sort_values("date").reset_index(drop=True)
    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")
    return frame[OUTPUT_COLUMNS]


def write_ohlc_csv(frame: pd.DataFrame, output_path: Path = OUTPUT_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
    writer.writeheader()
    for row in frame[OUTPUT_COLUMNS].to_dict("records"):
        writer.writerow(row)
    output_path.write_text(buffer.getvalue(), encoding="utf-8")


def ensure_empty_csv(output_path: Path = OUTPUT_PATH) -> None:
    if output_path.exists():
        return
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(",".join(OUTPUT_COLUMNS) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"WARNING: could not create daily OHLC placeholder: {type(exc).__name__}: {exc}")


def run_fetch(output_path: Path = OUTPUT_PATH, start_date: str = START_DATE) -> bool:
    ensure_project_dirs()
    try:
        frame = fetch_yahoo_daily_ohlc(start_date=start_date)
    except Exception as exc:
        ensure_empty_csv(output_path)
        print(f"WARNING: daily OHLC download failed: {type(exc).__name__}: {exc}")
        print(f"Daily OHLC file is available as placeholder or previous data: {output_path}")
        return False

    write_ohlc_csv(frame, output_path=output_path)
    print(f"Wrote {len(frame):,} daily OHLC rows to {output_path}")
    print(f"Source: {SOURCE_LABEL}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GC=F daily OHLC data for GHPR.")
    parser.add_argument("--start-date", default=START_DATE)
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_fetch(output_path=args.output, start_date=args.start_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

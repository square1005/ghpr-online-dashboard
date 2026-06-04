"""Build the GHPR master weekly dataset.

The master dataset is keyed by CFTC report date. Gold prices are aligned with
the most recent available daily close on or before each report date.
"""

from __future__ import annotations

import argparse
import csv
import io
import re
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote
from zipfile import ZipFile

import pandas as pd
import requests

try:
    from .utils import (
        COT_RAW_DIR,
        GOLD_RAW_DIR,
        OUTPUT_MASTER_WEEKLY,
        PROJECT_ROOT,
        ensure_project_dirs,
        rolling_percentile,
        rolling_zscore,
    )
except ImportError:
    from utils import (
        COT_RAW_DIR,
        GOLD_RAW_DIR,
        OUTPUT_MASTER_WEEKLY,
        PROJECT_ROOT,
        ensure_project_dirs,
        rolling_percentile,
        rolling_zscore,
    )


START_DATE = "2009-09-01"
GOLD_MARKET_NAME = "GOLD - COMMODITY EXCHANGE INC."
ROLLING_WINDOW = 156
ROLLING_MIN_PERIODS = 52
GOLD_SOURCE_DEFAULT = "COMEX GC futures proxy via Yahoo Finance GC=F"
GOLD_SOURCE_RECOMMENDATION = (
    "Keep GC futures for COT/COMEX alignment; use licensed LBMA PM or reliable XAUUSD spot "
    "for benchmark-grade v0.2 pricing."
)
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
    )
}

CFTC_BASE_URLS = (
    "https://www.cftc.gov/files/dea/history",
    "https://www.cftc.gov/sites/default/files/files/dea/history",
)
CFTC_HISTORY_BUNDLE = "fut_disagg_txt_hist_2006_2016.zip"
CFTC_YEARLY_TEMPLATE = "fut_disagg_txt_{year}.zip"

FRED_SERIES_ID = "GOLDPMGBD228NLBM"
FRED_URL = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={FRED_SERIES_ID}"
STOOQ_URL = "https://stooq.com/q/d/l/?s=xauusd&i=d"
YAHOO_SYMBOL = "GC=F"
YAHOO_URL_TEMPLATE = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    "?period1={period1}&period2={period2}&interval=1d"
)

MASTER_COLUMNS = [
    "date",
    "gold_close",
    "gold_price_source",
    "gold_price_benchmark_recommendation",
    "gold_return_1w",
    "gold_return_2w",
    "gold_return_4w",
    "gold_return_8w",
    "gold_return_zscore_52w",
    "gold_close_percentile_156w",
    "gold_close_zscore_156w",
    "gold_anomaly_2025_2026",
    "gold_anomaly_reason",
    "sample_split",
    "gold_regime",
    "mm_long",
    "mm_short",
    "mm_net",
    "mm_net_change",
    "mm_net_percentile_156w",
    "mm_net_zscore_156w",
    "producer_long",
    "producer_short",
    "producer_net",
    "producer_net_percentile_156w",
    "producer_net_zscore_156w",
    "swap_long",
    "swap_short",
    "swap_net",
    "swap_net_percentile_156w",
    "swap_net_zscore_156w",
    "total_open_interest",
    "oi_change",
    "oi_percentile_156w",
    "oi_zscore_156w",
]

CFTC_COLUMN_ALIASES = {
    "market": ("Market_and_Exchange_Names",),
    "date": (
        "Report_Date_as_YYYY-MM-DD",
        "Report_Date_as_MM_DD_YYYY",
        "As_of_Date_Form_YYYY-MM-DD",
        "As_of_Date_In_Form_YYMMDD",
    ),
    "open_interest": ("Open_Interest_All",),
    "mm_long": ("M_Money_Positions_Long_All",),
    "mm_short": ("M_Money_Positions_Short_All",),
    "producer_long": ("Prod_Merc_Positions_Long_All",),
    "producer_short": ("Prod_Merc_Positions_Short_All",),
    "swap_long": ("Swap_Positions_Long_All",),
    "swap_short": ("Swap__Positions_Short_All", "Swap_Positions_Short_All"),
}


def build_master_dataset(
    output_path: Path = OUTPUT_MASTER_WEEKLY,
    download: bool = True,
    force: bool = False,
    end_year: int | None = None,
) -> pd.DataFrame:
    ensure_project_dirs()
    end_year = end_year or date.today().year

    if download:
        ensure_cot_archives(end_year=end_year, force=force)
        ensure_gold_price_csv(end_year=end_year, force=force)

    cot_archives = find_cot_archives()
    if not cot_archives:
        raise FileNotFoundError(
            f"No CFTC COT archives found in {COT_RAW_DIR}. "
            "Run without --no-download or place fut_disagg_txt*.zip files there."
        )

    gold_csv = find_gold_price_csv()
    if gold_csv is None:
        raise FileNotFoundError(
            f"No gold price CSV found in {GOLD_RAW_DIR}. "
            "Run without --no-download or place a CSV with Date/Close columns there."
        )

    cot = load_gold_cot(cot_archives)
    cot = cot[(cot["date"] >= pd.Timestamp(START_DATE)) & (cot["date"].dt.year <= end_year)]
    cot = cot.drop_duplicates(subset=["date"], keep="last").sort_values("date")
    gold_daily = load_gold_price_csv(gold_csv)
    master = align_gold_price(cot, gold_daily)
    master = add_features(master)
    master = master[MASTER_COLUMNS].sort_values("date").reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    master.to_csv(output_path, index=False)
    write_gold_price_quality_outputs(master)
    return master


def ensure_cot_archives(end_year: int, force: bool = False) -> None:
    archives = [CFTC_HISTORY_BUNDLE]
    archives.extend(CFTC_YEARLY_TEMPLATE.format(year=year) for year in range(2017, end_year + 1))

    for archive in archives:
        output = COT_RAW_DIR / archive
        if output.exists() and not force:
            continue
        errors = []
        downloaded = False
        for base_url in CFTC_BASE_URLS:
            url = f"{base_url.rstrip('/')}/{archive}"
            try:
                response = requests.get(url, timeout=60, headers=REQUEST_HEADERS)
                response.raise_for_status()
                output.write_bytes(response.content)
                with ZipFile(output) as zf:
                    if zf.namelist():
                        downloaded = True
                        break
                output.unlink(missing_ok=True)
                errors.append(f"{url}: invalid zip")
            except requests.RequestException as exc:
                errors.append(f"{url}: {exc}")
        if not downloaded and archive == CFTC_HISTORY_BUNDLE:
            fallback = PROJECT_ROOT.parent / "data" / "raw" / "cftc" / archive
            if fallback.exists():
                output.write_bytes(fallback.read_bytes())
                downloaded = True
        if not downloaded and archive == CFTC_HISTORY_BUNDLE:
            raise RuntimeError("Could not download required CFTC history bundle.\n" + "\n".join(errors))


def ensure_gold_price_csv(end_year: int, force: bool = False) -> Path:
    output = GOLD_RAW_DIR / "gold_price.csv"
    if output.exists() and not force and csv_is_daily_enough(output, end_year=end_year):
        return output

    errors = []
    if download_csv(FRED_URL, output, errors) and csv_is_daily_enough(output, end_year=end_year):
        return output
    if download_csv(STOOQ_URL, output, errors) and csv_is_daily_enough(output, end_year=end_year):
        return output
    if download_yahoo_chart(output, end_year=end_year, errors=errors):
        return output

    fallback = PROJECT_ROOT.parent / "data" / "raw" / "fred" / "gold_price.csv"
    if fallback.exists() and csv_is_daily_enough(fallback, end_year=end_year):
        output.write_bytes(fallback.read_bytes())
        return output

    raise RuntimeError("Could not download gold price data.\n" + "\n".join(errors))


def download_csv(url: str, output: Path, errors: list[str]) -> bool:
    try:
        response = requests.get(url, timeout=60, headers=REQUEST_HEADERS)
        response.raise_for_status()
    except requests.RequestException as exc:
        errors.append(f"{url}: {exc}")
        return False
    if not looks_like_csv(response.content):
        errors.append(f"{url}: response did not look like price CSV data")
        return False
    output.write_bytes(response.content)
    return True


def download_yahoo_chart(output: Path, end_year: int, errors: list[str]) -> bool:
    period1 = int(
        (pd.Timestamp(START_DATE) - pd.Timedelta(days=14))
        .to_pydatetime()
        .replace(tzinfo=timezone.utc)
        .timestamp()
    )
    period2 = int(datetime(end_year + 1, 1, 15, tzinfo=timezone.utc).timestamp())
    url = YAHOO_URL_TEMPLATE.format(
        symbol=quote(YAHOO_SYMBOL, safe=""),
        period1=period1,
        period2=period2,
    )
    try:
        response = requests.get(url, timeout=60, headers=REQUEST_HEADERS)
        response.raise_for_status()
        payload = response.json()
        result = payload["chart"]["result"][0]
        timestamps = result["timestamp"]
        closes = result["indicators"]["quote"][0]["close"]
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError) as exc:
        errors.append(f"{url}: {exc}")
        return False

    rows = []
    for timestamp, close in zip(timestamps, closes, strict=False):
        if close is None:
            continue
        rows.append(
            {
                "Date": pd.to_datetime(timestamp, unit="s", utc=True).date().isoformat(),
                "Close": close,
                "Source": GOLD_SOURCE_DEFAULT,
            }
        )
    if not rows:
        errors.append(f"{url}: no close prices returned")
        return False

    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["Date", "Close", "Source"])
    writer.writeheader()
    writer.writerows(rows)
    output.write_text(buffer.getvalue(), encoding="utf-8")
    return True


def find_cot_archives() -> list[Path]:
    local = sorted(COT_RAW_DIR.glob("fut_disagg_txt*.zip"), key=cot_archive_sort_key)
    if local:
        return local
    fallback_dir = PROJECT_ROOT.parent / "data" / "raw" / "cftc"
    return sorted(fallback_dir.glob("fut_disagg_txt*.zip"), key=cot_archive_sort_key)


def find_gold_price_csv() -> Path | None:
    local = sorted(GOLD_RAW_DIR.glob("*.csv"))
    if local:
        return local[0]
    fallback = PROJECT_ROOT.parent / "data" / "raw" / "fred" / "gold_price.csv"
    return fallback if fallback.exists() else None


def load_gold_cot(archive_paths: list[Path]) -> pd.DataFrame:
    frames = []
    for archive_path in archive_paths:
        frame = read_cot_archive(archive_path)
        if frame.empty:
            continue
        market_col = pick_column(frame, CFTC_COLUMN_ALIASES["market"])
        market = frame[market_col].astype(str).str.upper().str.strip()
        exact = frame[market == GOLD_MARKET_NAME].copy()
        if not exact.empty:
            selected = exact
        else:
            selected = frame[
                market.str.contains("GOLD", na=False)
                & market.str.contains("COMMODITY EXCHANGE", na=False)
                & ~market.str.contains("MICRO", na=False)
            ].copy()
        if not selected.empty:
            frames.append(normalize_cot(selected))
    if not frames:
        raise ValueError("Could not find COMEX Gold rows in CFTC COT archives.")
    return pd.concat(frames, ignore_index=True)


def read_cot_archive(path: Path) -> pd.DataFrame:
    with ZipFile(path) as zf:
        members = [
            name
            for name in zf.namelist()
            if name.lower().endswith((".txt", ".csv")) and not name.endswith("/")
        ]
        if not members:
            return pd.DataFrame()
        with zf.open(members[0]) as fh:
            frame = pd.read_csv(fh, encoding="latin1", low_memory=False)
    frame.columns = [str(column).strip() for column in frame.columns]
    return frame


def normalize_cot(frame: pd.DataFrame) -> pd.DataFrame:
    cols = {name: pick_column(frame, aliases) for name, aliases in CFTC_COLUMN_ALIASES.items()}
    out = pd.DataFrame(
        {
            "date": parse_cot_date(frame[cols["date"]]),
            "mm_long": to_number(frame[cols["mm_long"]]),
            "mm_short": to_number(frame[cols["mm_short"]]),
            "producer_long": to_number(frame[cols["producer_long"]]),
            "producer_short": to_number(frame[cols["producer_short"]]),
            "swap_long": to_number(frame[cols["swap_long"]]),
            "swap_short": to_number(frame[cols["swap_short"]]),
            "total_open_interest": to_number(frame[cols["open_interest"]]),
        }
    )
    out = out.dropna(subset=["date"])
    out["mm_net"] = out["mm_long"] - out["mm_short"]
    out["producer_net"] = out["producer_long"] - out["producer_short"]
    out["swap_net"] = out["swap_long"] - out["swap_short"]
    return out


def load_gold_price_csv(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    date_col = pick_column(frame, ("DATE", "Date", "date", "observation_date"))
    close_col = pick_column(frame, (FRED_SERIES_ID, "Close", "close", "gold_close", "price"))
    source = infer_gold_price_source(frame)
    out = pd.DataFrame(
        {
            "date": pd.to_datetime(frame[date_col], errors="coerce"),
            "gold_close": to_number(frame[close_col].replace(".", pd.NA)),
            "gold_price_source": source,
            "gold_price_benchmark_recommendation": GOLD_SOURCE_RECOMMENDATION,
        }
    )
    return out.dropna(subset=["date", "gold_close"]).sort_values("date").reset_index(drop=True)


def align_gold_price(cot: pd.DataFrame, gold_daily: pd.DataFrame) -> pd.DataFrame:
    left = cot.sort_values("date").reset_index(drop=True)
    right = gold_daily.sort_values("date").reset_index(drop=True)
    return pd.merge_asof(left, right, on="date", direction="backward")


def add_features(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for weeks in [1, 2, 4, 8]:
        out[f"gold_return_{weeks}w"] = out["gold_close"].pct_change(weeks)

    out["gold_return_zscore_52w"] = rolling_zscore(
        out["gold_return_1w"], window=52, min_periods=26
    )
    out["gold_close_percentile_156w"] = rolling_percentile(
        out["gold_close"], window=ROLLING_WINDOW, min_periods=ROLLING_MIN_PERIODS
    )
    out["gold_close_zscore_156w"] = rolling_zscore(
        out["gold_close"], window=ROLLING_WINDOW, min_periods=ROLLING_MIN_PERIODS
    )
    out["sample_split"] = out["date"].apply(assign_sample_split)
    out["gold_regime"] = assign_gold_regime(out)
    out["gold_anomaly_reason"] = out.apply(gold_anomaly_reason, axis=1)
    out["gold_anomaly_2025_2026"] = out["gold_anomaly_reason"].ne("")

    out["mm_net_change"] = out["mm_net"].diff()
    out["oi_change"] = out["total_open_interest"].diff()

    for source, prefix in [
        ("mm_net", "mm_net"),
        ("producer_net", "producer_net"),
        ("swap_net", "swap_net"),
        ("total_open_interest", "oi"),
    ]:
        out[f"{prefix}_percentile_156w"] = rolling_percentile(
            out[source], window=ROLLING_WINDOW, min_periods=ROLLING_MIN_PERIODS
        )
        out[f"{prefix}_zscore_156w"] = rolling_zscore(
            out[source], window=ROLLING_WINDOW, min_periods=ROLLING_MIN_PERIODS
        )
    return out


def infer_gold_price_source(frame: pd.DataFrame) -> str:
    if "Source" in frame.columns:
        source_values = frame["Source"].dropna().astype(str).str.strip()
        if not source_values.empty:
            return source_values.iloc[0]
    if FRED_SERIES_ID in frame.columns:
        return "LBMA PM Gold Price via FRED"
    return GOLD_SOURCE_DEFAULT


def assign_sample_split(value: pd.Timestamp) -> str:
    if value <= pd.Timestamp("2018-12-31"):
        return "train_2009_2018"
    if value >= pd.Timestamp("2019-01-01"):
        return "test_2019_2026"
    return "out_of_scope"


def assign_gold_regime(frame: pd.DataFrame) -> pd.Series:
    close = frame["gold_close"]
    ma_52w = close.rolling(window=52, min_periods=26).mean()
    return_26w = close.pct_change(26)
    regime = pd.Series("range", index=frame.index, dtype="object")
    regime[(close > ma_52w) & (return_26w > 0.05)] = "bull"
    regime[(close < ma_52w) & (return_26w < -0.05)] = "bear"
    regime[ma_52w.isna() | return_26w.isna()] = "unclassified"
    return regime


def gold_anomaly_reason(row: pd.Series) -> str:
    date_value = row["date"]
    if pd.isna(date_value) or date_value.year < 2025:
        return ""

    reasons: list[str] = []
    gold_close = row.get("gold_close")
    return_1w = row.get("gold_return_1w")
    return_zscore = row.get("gold_return_zscore_52w")
    close_zscore = row.get("gold_close_zscore_156w")

    if pd.notna(gold_close) and gold_close >= 4000:
        reasons.append("level>=4000")
    if pd.notna(gold_close) and gold_close >= 5000:
        reasons.append("level>=5000")
    if pd.notna(return_1w) and abs(return_1w) >= 0.05:
        reasons.append("abs_1w_return>=5pct")
    if pd.notna(return_zscore) and abs(return_zscore) >= 2.5:
        reasons.append("abs_return_zscore_52w>=2.5")
    if pd.notna(close_zscore) and close_zscore >= 2.5:
        reasons.append("level_zscore_156w>=2.5")
    return "; ".join(reasons)


def write_gold_price_quality_outputs(master: pd.DataFrame) -> None:
    reports_dir = PROJECT_ROOT / "outputs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    anomalies = master[master["gold_anomaly_2025_2026"]].copy()
    anomaly_path = reports_dir / "gold_price_anomalies_2025_2026.csv"
    anomalies[
        [
            "date",
            "gold_close",
            "gold_return_1w",
            "gold_return_zscore_52w",
            "gold_close_zscore_156w",
            "gold_anomaly_reason",
        ]
    ].to_csv(anomaly_path, index=False)

    source = master["gold_price_source"].dropna().iloc[-1]
    audit_lines = [
        "# Gold Price Source Audit",
        "",
        f"- Current `gold_close` source: {source}",
        "- Current status: GC futures proxy, not XAUUSD spot and not LBMA PM benchmark.",
        f"- Recommendation: {GOLD_SOURCE_RECOMMENDATION}",
        "- Rationale: COT positioning is COMEX futures data, so GC futures are internally aligned for v0.1 research. For v0.2 benchmark-grade price research, prefer licensed LBMA PM or a stable XAUUSD spot feed.",
        "",
        "## 2025-2026 Anomaly Flags",
        "",
        f"- Flagged rows: {len(anomalies):,}",
        "- Rules: date >= 2025-01-01 and any of `level>=4000`, `level>=5000`, `abs_1w_return>=5pct`, `abs_return_zscore_52w>=2.5`, `level_zscore_156w>=2.5`.",
        f"- Detail CSV: {anomaly_path.name}",
        "",
    ]
    if not anomalies.empty:
        start = anomalies["date"].min().strftime("%Y-%m-%d")
        end = anomalies["date"].max().strftime("%Y-%m-%d")
        audit_lines.append(f"- Flagged interval: {start} to {end}")
    (reports_dir / "gold_price_source_audit.md").write_text(
        "\n".join(audit_lines) + "\n",
        encoding="utf-8",
    )


def pick_column(frame: pd.DataFrame, aliases: tuple[str, ...]) -> str:
    for alias in aliases:
        if alias in frame.columns:
            return alias
    normalized = {normalize_name(column): column for column in frame.columns}
    for alias in aliases:
        key = normalize_name(alias)
        if key in normalized:
            return normalized[key]
    raise KeyError(f"Missing column. Tried aliases: {aliases!r}")


def parse_cot_date(series: pd.Series) -> pd.Series:
    values = series.astype(str).str.strip()
    numeric = values.str.fullmatch(r"\d{6}")
    parsed = pd.to_datetime(values, errors="coerce")
    if numeric.any():
        parsed.loc[numeric] = pd.to_datetime(values.loc[numeric], format="%y%m%d", errors="coerce")
    return parsed


def to_number(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def normalize_name(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())


def cot_archive_sort_key(path: Path) -> tuple[int, str]:
    return (0 if "hist" in path.name else 1, path.name)


def looks_like_csv(content: bytes) -> bool:
    head = content[:512].decode("utf-8", errors="ignore").strip()
    if not head or "<html" in head.lower():
        return False
    first_line = head.splitlines()[0].lower()
    return "," in first_line and ("date" in first_line or "observation" in first_line)


def csv_is_daily_enough(path: Path, end_year: int) -> bool:
    try:
        frame = pd.read_csv(path)
        date_col = pick_column(frame, ("DATE", "Date", "date", "observation_date"))
        dates = pd.to_datetime(frame[date_col], errors="coerce").dropna()
    except Exception:
        return False
    if dates.empty:
        return False
    start = pd.Timestamp(START_DATE)
    end = pd.Timestamp(f"{end_year + 1}-01-15")
    rows = dates[(dates >= start) & (dates <= end)].shape[0]
    expected_min = max(30, (end - start).days // 10)
    return rows >= expected_min


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build GHPR master weekly dataset.")
    parser.add_argument("--no-download", action="store_true", help="Use existing raw files only.")
    parser.add_argument("--force", action="store_true", help="Redownload raw files.")
    parser.add_argument("--end-year", type=int, default=None, help="Limit COT data through this year.")
    parser.add_argument(
        "--output",
        default=str(OUTPUT_MASTER_WEEKLY),
        help="Output CSV path.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    master = build_master_dataset(
        output_path=Path(args.output),
        download=not args.no_download,
        force=args.force,
        end_year=args.end_year,
    )
    print(f"Built {len(master):,} rows")
    print(f"Output: {Path(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

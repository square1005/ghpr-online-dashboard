"""Run single-factor percentile bucket analysis for GHPR Engine."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from .utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT
except ImportError:
    from utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT


FACTORS = [
    "mm_net_percentile_156w",
    "producer_net_percentile_156w",
    "swap_net_percentile_156w",
    "oi_percentile_156w",
]
HORIZONS = [1, 2, 4, 8]
BUCKET_LABELS = [
    "0-10 percentile",
    "10-20 percentile",
    "20-30 percentile",
    "30-40 percentile",
    "40-50 percentile",
    "50-60 percentile",
    "60-70 percentile",
    "70-80 percentile",
    "80-90 percentile",
    "90-100 percentile",
]
BUCKET_BINS = [i / 10 for i in range(11)]

REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports"
SUMMARY_CSV = REPORTS_DIR / "single_factor_decile_analysis.csv"
SUMMARY_MD = REPORTS_DIR / "single_factor_decile_analysis.md"
TRAIN_TEST_CSV = REPORTS_DIR / "single_factor_train_test_analysis.csv"
REGIME_CSV = REPORTS_DIR / "single_factor_regime_analysis.csv"


def run_single_factor_analysis(master_path: Path = OUTPUT_MASTER_WEEKLY) -> pd.DataFrame:
    master = load_master_dataset(master_path)
    rows = []
    for factor in FACTORS:
        for horizon in HORIZONS:
            rows.extend(
                analyze_factor_horizon(
                    master,
                    factor=factor,
                    horizon=horizon,
                    sample_split="all",
                    gold_regime="all",
                )
            )
    return pd.DataFrame(rows)


def run_train_test_analysis(master_path: Path = OUTPUT_MASTER_WEEKLY) -> pd.DataFrame:
    master = load_master_dataset(master_path)
    rows = []
    for split in ["train_2009_2018", "test_2019_2026"]:
        subset = master[master["sample_split"] == split].copy()
        for factor in FACTORS:
            for horizon in HORIZONS:
                rows.extend(
                    analyze_factor_horizon(
                        subset,
                        factor=factor,
                        horizon=horizon,
                        sample_split=split,
                        gold_regime="all",
                    )
                )
    return pd.DataFrame(rows)


def run_regime_analysis(master_path: Path = OUTPUT_MASTER_WEEKLY) -> pd.DataFrame:
    master = load_master_dataset(master_path)
    rows = []
    for regime in ["bull", "bear", "range"]:
        subset = master[master["gold_regime"] == regime].copy()
        for factor in FACTORS:
            for horizon in HORIZONS:
                rows.extend(
                    analyze_factor_horizon(
                        subset,
                        factor=factor,
                        horizon=horizon,
                        sample_split="all",
                        gold_regime=regime,
                    )
                )
    return pd.DataFrame(rows)


def load_master_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Master dataset not found: {path}")

    frame = pd.read_csv(path)
    required = ["date", "gold_close", *FACTORS]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise KeyError(f"Master dataset is missing required columns: {missing}")

    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["gold_close"] = pd.to_numeric(frame["gold_close"], errors="coerce")
    for factor in FACTORS:
        frame[factor] = pd.to_numeric(frame[factor], errors="coerce")

    frame = frame.dropna(subset=["date", "gold_close"]).sort_values("date").reset_index(drop=True)
    if "sample_split" not in frame.columns:
        frame["sample_split"] = frame["date"].apply(assign_sample_split)
    if "gold_regime" not in frame.columns:
        frame["gold_regime"] = assign_fallback_regime(frame)
    return frame


def analyze_factor_horizon(
    master: pd.DataFrame,
    factor: str,
    horizon: int,
    sample_split: str,
    gold_regime: str,
) -> list[dict[str, object]]:
    data = master[["date", "gold_close", factor]].copy()
    data["forward_return"] = data["gold_close"].shift(-horizon) / data["gold_close"] - 1
    data["max_drawdown_after_signal"] = max_drawdown_after_signal(data["gold_close"], horizon)
    data["percentile_bucket"] = assign_percentile_bucket(data[factor])

    rows = []
    for bucket in BUCKET_LABELS:
        group = data[
            (data["percentile_bucket"] == bucket)
            & data["forward_return"].notna()
            & data["max_drawdown_after_signal"].notna()
        ]
        rows.append(
            {
                "factor": factor,
                "sample_split": sample_split,
                "gold_regime": gold_regime,
                "forward_horizon": f"{horizon}W",
                "percentile_bucket": bucket,
                "count": int(len(group)),
                "avg_forward_return": group["forward_return"].mean(),
                "median_forward_return": group["forward_return"].median(),
                "win_rate": (group["forward_return"] > 0).mean() if len(group) else pd.NA,
                "max_drawdown_after_signal": group["max_drawdown_after_signal"].min()
                if len(group)
                else pd.NA,
            }
        )
    return rows


def assign_sample_split(value: pd.Timestamp) -> str:
    if value <= pd.Timestamp("2018-12-31"):
        return "train_2009_2018"
    return "test_2019_2026"


def assign_fallback_regime(frame: pd.DataFrame) -> pd.Series:
    close = frame["gold_close"]
    ma_52w = close.rolling(window=52, min_periods=26).mean()
    return_26w = close.pct_change(26)
    regime = pd.Series("range", index=frame.index, dtype="object")
    regime[(close > ma_52w) & (return_26w > 0.05)] = "bull"
    regime[(close < ma_52w) & (return_26w < -0.05)] = "bear"
    regime[ma_52w.isna() | return_26w.isna()] = "unclassified"
    return regime


def assign_percentile_bucket(series: pd.Series) -> pd.Series:
    clipped = series.clip(lower=0, upper=1)
    return pd.cut(
        clipped,
        bins=BUCKET_BINS,
        labels=BUCKET_LABELS,
        include_lowest=True,
        right=True,
    )


def max_drawdown_after_signal(price: pd.Series, horizon: int) -> pd.Series:
    prices = price.reset_index(drop=True)
    drawdowns = []
    for idx in range(len(prices)):
        window = prices.iloc[idx : idx + horizon + 1].dropna()
        if len(window) < horizon + 1:
            drawdowns.append(pd.NA)
            continue
        running_peak = window.cummax()
        drawdown = window / running_peak - 1
        drawdowns.append(drawdown.min())
    return pd.Series(drawdowns, index=price.index)


def write_reports(result: pd.DataFrame, output_csv: Path = SUMMARY_CSV, output_md: Path = SUMMARY_MD) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_csv, index=False)
    write_markdown_report(result, output_md)

    for factor in FACTORS:
        factor_path = output_csv.parent / f"{factor}_single_factor_analysis.csv"
        result[result["factor"] == factor].to_csv(factor_path, index=False)


def write_segment_reports(train_test: pd.DataFrame, regime: pd.DataFrame) -> None:
    TRAIN_TEST_CSV.parent.mkdir(parents=True, exist_ok=True)
    train_test.to_csv(TRAIN_TEST_CSV, index=False)
    regime.to_csv(REGIME_CSV, index=False)


def write_markdown_report(result: pd.DataFrame, output_path: Path) -> None:
    lines = [
        "# GHPR Single-Factor Decile Analysis",
        "",
        "Each table studies one factor at a time. No mixed indicators are used.",
        "",
        "Forward returns are based on `gold_close`. `max_drawdown_after_signal` is the worst peak-to-trough drawdown inside the forward horizon after each signal, summarized by the worst drawdown in that bucket.",
        "",
    ]

    for factor in FACTORS:
        lines.extend([f"## {factor}", ""])
        factor_result = result[result["factor"] == factor]
        for horizon in [f"{weeks}W" for weeks in HORIZONS]:
            lines.extend([f"### Forward {horizon}", ""])
            view = factor_result[factor_result["forward_horizon"] == horizon]
            lines.append(
                "| percentile_bucket | count | avg_forward_return | median_forward_return | win_rate | max_drawdown_after_signal |"
            )
            lines.append("|---|---:|---:|---:|---:|---:|")
            for row in view.itertuples(index=False):
                lines.append(
                    "| {bucket} | {count} | {avg} | {median} | {win} | {drawdown} |".format(
                        bucket=row.percentile_bucket,
                        count=row.count,
                        avg=format_percent(row.avg_forward_return),
                        median=format_percent(row.median_forward_return),
                        win=format_percent(row.win_rate),
                        drawdown=format_percent(row.max_drawdown_after_signal),
                    )
                )
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def format_percent(value: object) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value) * 100:.2f}%"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run GHPR single-factor decile analysis.")
    parser.add_argument("--input", default=str(OUTPUT_MASTER_WEEKLY), help="Master weekly CSV path.")
    parser.add_argument("--output-csv", default=str(SUMMARY_CSV), help="Summary CSV output path.")
    parser.add_argument("--output-md", default=str(SUMMARY_MD), help="Markdown report output path.")
    parser.add_argument(
        "--skip-segments",
        action="store_true",
        help="Only write the all-sample analysis; skip train/test and regime outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = run_single_factor_analysis(master_path=Path(args.input))
    write_reports(result, output_csv=Path(args.output_csv), output_md=Path(args.output_md))
    if not args.skip_segments:
        train_test = run_train_test_analysis(master_path=Path(args.input))
        regime = run_regime_analysis(master_path=Path(args.input))
        write_segment_reports(train_test, regime)
    print(f"Built {len(result):,} factor bucket rows")
    print(f"CSV: {Path(args.output_csv)}")
    print(f"Markdown: {Path(args.output_md)}")
    if not args.skip_segments:
        print(f"Train/Test CSV: {TRAIN_TEST_CSV}")
        print(f"Regime CSV: {REGIME_CSV}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

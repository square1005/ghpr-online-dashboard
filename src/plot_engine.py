"""Create GHPR charts."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

try:
    from .factor_analysis import SUMMARY_CSV, run_single_factor_analysis, write_reports
    from .utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT
except ImportError:
    from factor_analysis import SUMMARY_CSV, run_single_factor_analysis, write_reports
    from utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT


CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

PRICE_PERCENTILE_CHARTS = [
    (
        "Gold Price vs MM Net Percentile",
        "mm_net_percentile_156w",
        "MM Net Percentile",
        "gold_price_vs_mm_net_percentile.png",
        "#2563eb",
    ),
    (
        "Gold Price vs Producer Net Percentile",
        "producer_net_percentile_156w",
        "Producer Net Percentile",
        "gold_price_vs_producer_net_percentile.png",
        "#dc2626",
    ),
    (
        "Gold Price vs Total OI Percentile",
        "oi_percentile_156w",
        "Total OI Percentile",
        "gold_price_vs_total_oi_percentile.png",
        "#16a34a",
    ),
]

FORWARD_RETURN_CHARTS = [
    (
        "Forward Return by MM Percentile Bucket",
        "mm_net_percentile_156w",
        "forward_return_by_mm_percentile_bucket.png",
    ),
    (
        "Forward Return by Producer Percentile Bucket",
        "producer_net_percentile_156w",
        "forward_return_by_producer_percentile_bucket.png",
    ),
    (
        "Forward Return by OI Percentile Bucket",
        "oi_percentile_156w",
        "forward_return_by_oi_percentile_bucket.png",
    ),
]

HORIZON_ORDER = ["1W", "2W", "4W", "8W"]
HORIZON_COLORS = {
    "1W": "#2563eb",
    "2W": "#7c3aed",
    "4W": "#ea580c",
    "8W": "#16a34a",
}


def create_charts(
    master_path: Path = OUTPUT_MASTER_WEEKLY,
    factor_result_path: Path = SUMMARY_CSV,
    output_dir: Path = CHARTS_DIR,
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    master = load_master(master_path)
    factor_results = load_or_build_factor_results(master_path, factor_result_path)

    written: list[Path] = []
    for title, factor, label, filename, color in PRICE_PERCENTILE_CHARTS:
        path = output_dir / filename
        plot_gold_vs_percentile(
            master=master,
            factor=factor,
            factor_label=label,
            title=title,
            color=color,
            output_path=path,
        )
        written.append(path)

    for title, factor, filename in FORWARD_RETURN_CHARTS:
        path = output_dir / filename
        plot_forward_return_by_bucket(
            factor_results=factor_results,
            factor=factor,
            title=title,
            output_path=path,
        )
        written.append(path)

    return written


def load_master(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Master weekly dataset not found: {path}")

    frame = pd.read_csv(path)
    required = [
        "date",
        "gold_close",
        "mm_net_percentile_156w",
        "producer_net_percentile_156w",
        "oi_percentile_156w",
    ]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise KeyError(f"Master weekly dataset is missing columns: {missing}")

    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for column in required[1:]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.dropna(subset=["date", "gold_close"]).sort_values("date").reset_index(drop=True)


def load_or_build_factor_results(master_path: Path, factor_result_path: Path) -> pd.DataFrame:
    if factor_result_path.exists():
        return pd.read_csv(factor_result_path)

    result = run_single_factor_analysis(master_path=master_path)
    write_reports(result)
    return result


def plot_gold_vs_percentile(
    master: pd.DataFrame,
    factor: str,
    factor_label: str,
    title: str,
    color: str,
    output_path: Path,
) -> None:
    data = master[["date", "gold_close", factor]].dropna()

    fig, ax_price = plt.subplots(figsize=(13, 6.5))
    ax_factor = ax_price.twinx()

    price_line = ax_price.plot(
        data["date"],
        data["gold_close"],
        color="#111827",
        linewidth=1.8,
        label="Gold Close",
    )
    factor_line = ax_factor.plot(
        data["date"],
        data[factor] * 100,
        color=color,
        linewidth=1.2,
        alpha=0.78,
        label=factor_label,
    )

    ax_price.set_title(title, fontsize=16, pad=14)
    ax_price.set_xlabel("Date")
    ax_price.set_ylabel("Gold Close")
    ax_factor.set_ylabel(f"{factor_label} (%)")
    ax_factor.set_ylim(0, 100)
    ax_price.grid(True, axis="y", alpha=0.25)

    lines = price_line + factor_line
    labels = [line.get_label() for line in lines]
    ax_price.legend(lines, labels, loc="upper left", frameon=False)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def plot_forward_return_by_bucket(
    factor_results: pd.DataFrame,
    factor: str,
    title: str,
    output_path: Path,
) -> None:
    data = factor_results[factor_results["factor"] == factor].copy()
    if data.empty:
        raise ValueError(f"No factor results found for {factor}")

    data["avg_forward_return"] = pd.to_numeric(data["avg_forward_return"], errors="coerce")
    pivot = data.pivot(
        index="percentile_bucket",
        columns="forward_horizon",
        values="avg_forward_return",
    )
    pivot = pivot.reindex(columns=HORIZON_ORDER)

    fig, ax = plt.subplots(figsize=(13, 6.5))
    x = range(len(pivot.index))
    for horizon in HORIZON_ORDER:
        if horizon not in pivot.columns:
            continue
        ax.plot(
            x,
            pivot[horizon] * 100,
            marker="o",
            linewidth=1.8,
            markersize=4,
            color=HORIZON_COLORS[horizon],
            label=f"Forward {horizon}",
        )

    ax.axhline(0, color="#111827", linewidth=1, alpha=0.5)
    ax.set_title(title, fontsize=16, pad=14)
    ax.set_xlabel("Percentile Bucket")
    ax.set_ylabel("Average Forward Return (%)")
    ax.set_xticks(list(x))
    ax.set_xticklabels([short_bucket_label(label) for label in pivot.index], rotation=35, ha="right")
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, ncols=4, loc="upper left")
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)


def short_bucket_label(label: object) -> str:
    return str(label).replace(" percentile", "")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create GHPR charts.")
    parser.add_argument("--master", default=str(OUTPUT_MASTER_WEEKLY), help="Master weekly CSV path.")
    parser.add_argument(
        "--factor-results",
        default=str(SUMMARY_CSV),
        help="Single-factor analysis CSV path.",
    )
    parser.add_argument("--output-dir", default=str(CHARTS_DIR), help="Chart output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    written = create_charts(
        master_path=Path(args.master),
        factor_result_path=Path(args.factor_results),
        output_dir=Path(args.output_dir),
    )
    print(f"Created {len(written)} charts")
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Generate the GHPR factor research report."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    from .factor_analysis import (
        FACTORS,
        HORIZONS,
        REGIME_CSV,
        SUMMARY_CSV,
        TRAIN_TEST_CSV,
        run_regime_analysis,
        run_single_factor_analysis,
        run_train_test_analysis,
        write_reports,
        write_segment_reports,
    )
    from .utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT
except ImportError:
    from factor_analysis import (
        FACTORS,
        HORIZONS,
        REGIME_CSV,
        SUMMARY_CSV,
        TRAIN_TEST_CSV,
        run_regime_analysis,
        run_single_factor_analysis,
        run_train_test_analysis,
        write_reports,
        write_segment_reports,
    )
    from utils import OUTPUT_MASTER_WEEKLY, PROJECT_ROOT


REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "ghpr_factor_report.md"
MIN_BUCKET_COUNT = 30
POSITIVE_WIN_RATE = 0.55
NEGATIVE_WIN_RATE = 0.45

FACTOR_LABELS = {
    "mm_net_percentile_156w": "Managed Money Net Percentile",
    "producer_net_percentile_156w": "Producer / Merchant Net Percentile",
    "swap_net_percentile_156w": "Swap Net Percentile",
    "oi_percentile_156w": "Total Open Interest Percentile",
}

BUCKET_MIDPOINTS = {
    "0-10 percentile": 5,
    "10-20 percentile": 15,
    "20-30 percentile": 25,
    "30-40 percentile": 35,
    "40-50 percentile": 45,
    "50-60 percentile": 55,
    "60-70 percentile": 65,
    "70-80 percentile": 75,
    "80-90 percentile": 85,
    "90-100 percentile": 95,
}


def generate_factor_report(
    master_path: Path = OUTPUT_MASTER_WEEKLY,
    factor_result_path: Path = SUMMARY_CSV,
    output_path: Path = REPORT_PATH,
) -> Path:
    master = load_master(master_path)
    factor_results = load_or_build_factor_results(master_path, factor_result_path)
    train_test_results, regime_results = load_or_build_segment_results(master_path)
    summary = build_predictive_summary(factor_results)
    train_test_summary = build_segment_summary(train_test_results, "sample_split")
    regime_summary = build_segment_summary(regime_results, "gold_regime")
    positive = find_obvious_buckets(factor_results, direction="positive")
    negative = find_obvious_buckets(factor_results, direction="negative")
    no_value_factors = identify_no_value_factors(summary)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        "\n".join(
            [
                "# GHPR Factor Research Report",
                "",
                "## 1. 資料期間",
                "",
                data_period_section(master),
                "",
                "## 2. 資料筆數",
                "",
                f"- Master weekly rows: {len(master):,}",
                f"- Single-factor result rows: {len(factor_results):,}",
                "",
                "## 3. 缺值狀況",
                "",
                missing_section(master),
                "",
                "## 4. Gold Price Source 與 2025-2026 異常區間",
                "",
                gold_price_source_section(master),
                "",
                gold_anomaly_section(master),
                "",
                "## 5. 每個因子的 1W / 2W / 4W / 8W 預測力",
                "",
                predictive_power_section(summary),
                "",
                "## 6. 樣本外測試：Train 2009-2018 / Test 2019-2026",
                "",
                train_test_section(train_test_summary),
                "",
                "## 7. 牛市 / 熊市 / 震盪 Regime 切分",
                "",
                regime_section(regime_summary),
                "",
                "## 8. 明顯正報酬 percentile 區間",
                "",
                obvious_bucket_section(positive, "目前符合明顯正報酬規則的區間如下。"),
                "",
                "## 9. 明顯負報酬 percentile 區間",
                "",
                obvious_bucket_section(negative, "目前符合明顯負報酬規則的區間如下。"),
                "",
                "## 10. 目前沒有參考價值的因子",
                "",
                no_value_section(no_value_factors, summary),
                "",
                "## 11. 是否建議進入 v0.2 綜合指數階段",
                "",
                v02_recommendation_section(no_value_factors),
                "",
                "## 判定規則",
                "",
                rules_section(),
                "",
            ]
        ),
        encoding="utf-8",
    )
    return output_path


def load_master(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Master dataset not found: {path}")
    frame = pd.read_csv(path)
    if "date" not in frame.columns:
        raise KeyError("Master dataset is missing date column.")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    return frame.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


def load_or_build_factor_results(master_path: Path, factor_result_path: Path) -> pd.DataFrame:
    if factor_result_path.exists():
        return pd.read_csv(factor_result_path)
    result = run_single_factor_analysis(master_path=master_path)
    write_reports(result)
    return result


def load_or_build_segment_results(master_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    if TRAIN_TEST_CSV.exists() and REGIME_CSV.exists():
        return pd.read_csv(TRAIN_TEST_CSV), pd.read_csv(REGIME_CSV)
    train_test = run_train_test_analysis(master_path=master_path)
    regime = run_regime_analysis(master_path=master_path)
    write_segment_reports(train_test, regime)
    return train_test, regime


def build_predictive_summary(result: pd.DataFrame) -> pd.DataFrame:
    if "sample_split" in result.columns:
        result = result[result["sample_split"].fillna("all") == "all"].copy()
    if "gold_regime" in result.columns:
        result = result[result["gold_regime"].fillna("all") == "all"].copy()
    rows = []
    for factor in FACTORS:
        for horizon in [f"{weeks}W" for weeks in HORIZONS]:
            data = result[
                (result["factor"] == factor)
                & (result["forward_horizon"] == horizon)
            ].copy()
            data["bucket_midpoint"] = data["percentile_bucket"].map(BUCKET_MIDPOINTS)
            data["avg_forward_return"] = pd.to_numeric(data["avg_forward_return"], errors="coerce")
            data["median_forward_return"] = pd.to_numeric(data["median_forward_return"], errors="coerce")
            data["win_rate"] = pd.to_numeric(data["win_rate"], errors="coerce")

            best = data.loc[data["avg_forward_return"].idxmax()]
            worst = data.loc[data["avg_forward_return"].idxmin()]
            high = data.loc[
                data["percentile_bucket"] == "90-100 percentile",
                "avg_forward_return",
            ].iloc[0]
            low = data.loc[
                data["percentile_bucket"] == "0-10 percentile",
                "avg_forward_return",
            ].iloc[0]
            rank_corr = data["bucket_midpoint"].corr(data["avg_forward_return"], method="spearman")
            obvious_positive = find_obvious_buckets(data, direction="positive")
            obvious_negative = find_obvious_buckets(data, direction="negative")
            assessment = assess_predictive_power(
                rank_corr=rank_corr,
                high_low_spread=high - low,
                positive_count=len(obvious_positive),
                negative_count=len(obvious_negative),
            )
            rows.append(
                {
                    "factor": factor,
                    "factor_label": FACTOR_LABELS[factor],
                    "forward_horizon": horizon,
                    "rank_corr": rank_corr,
                    "high_low_spread": high - low,
                    "best_bucket": best["percentile_bucket"],
                    "best_avg_forward_return": best["avg_forward_return"],
                    "worst_bucket": worst["percentile_bucket"],
                    "worst_avg_forward_return": worst["avg_forward_return"],
                    "obvious_positive_bucket_count": len(obvious_positive),
                    "obvious_negative_bucket_count": len(obvious_negative),
                    "assessment": assessment,
                }
            )
    return pd.DataFrame(rows)


def build_segment_summary(result: pd.DataFrame, segment_column: str) -> pd.DataFrame:
    rows = []
    for segment in sorted(result[segment_column].dropna().unique()):
        for factor in FACTORS:
            for horizon in [f"{weeks}W" for weeks in HORIZONS]:
                data = result[
                    (result[segment_column] == segment)
                    & (result["factor"] == factor)
                    & (result["forward_horizon"] == horizon)
                ].copy()
                if data.empty:
                    continue
                data["bucket_midpoint"] = data["percentile_bucket"].map(BUCKET_MIDPOINTS)
                data["avg_forward_return"] = pd.to_numeric(data["avg_forward_return"], errors="coerce")
                data["median_forward_return"] = pd.to_numeric(
                    data["median_forward_return"], errors="coerce"
                )
                data["win_rate"] = pd.to_numeric(data["win_rate"], errors="coerce")
                if data["avg_forward_return"].dropna().empty:
                    continue
                best = data.loc[data["avg_forward_return"].idxmax()]
                high = data.loc[
                    data["percentile_bucket"] == "90-100 percentile",
                    "avg_forward_return",
                ].iloc[0]
                low = data.loc[
                    data["percentile_bucket"] == "0-10 percentile",
                    "avg_forward_return",
                ].iloc[0]
                rank_corr = data["bucket_midpoint"].corr(
                    data["avg_forward_return"], method="spearman"
                )
                obvious_positive = find_obvious_buckets(data, direction="positive")
                obvious_negative = find_obvious_buckets(data, direction="negative")
                rows.append(
                    {
                        segment_column: segment,
                        "factor": factor,
                        "factor_label": FACTOR_LABELS[factor],
                        "forward_horizon": horizon,
                        "rank_corr": rank_corr,
                        "high_low_spread": high - low,
                        "best_bucket": best["percentile_bucket"],
                        "best_avg_forward_return": best["avg_forward_return"],
                        "assessment": assess_predictive_power(
                            rank_corr=rank_corr,
                            high_low_spread=high - low,
                            positive_count=len(obvious_positive),
                            negative_count=len(obvious_negative),
                        ),
                    }
                )
    return pd.DataFrame(rows)


def find_obvious_buckets(result: pd.DataFrame, direction: str) -> pd.DataFrame:
    data = result.copy()
    data["count"] = pd.to_numeric(data["count"], errors="coerce")
    data["avg_forward_return"] = pd.to_numeric(data["avg_forward_return"], errors="coerce")
    data["median_forward_return"] = pd.to_numeric(data["median_forward_return"], errors="coerce")
    data["win_rate"] = pd.to_numeric(data["win_rate"], errors="coerce")
    base = data["count"] >= MIN_BUCKET_COUNT
    if direction == "positive":
        return data[
            base
            & (data["avg_forward_return"] > 0)
            & (data["median_forward_return"] > 0)
            & (data["win_rate"] >= POSITIVE_WIN_RATE)
        ].copy()
    if direction == "negative":
        return data[
            base
            & (data["avg_forward_return"] < 0)
            & (data["median_forward_return"] < 0)
            & (data["win_rate"] <= NEGATIVE_WIN_RATE)
        ].copy()
    raise ValueError(f"Unknown direction: {direction}")


def assess_predictive_power(
    rank_corr: float,
    high_low_spread: float,
    positive_count: int,
    negative_count: int,
) -> str:
    abs_corr = abs(rank_corr) if pd.notna(rank_corr) else 0
    abs_spread = abs(high_low_spread) if pd.notna(high_low_spread) else 0
    obvious_count = positive_count + negative_count
    if abs_corr >= 0.60 and abs_spread >= 0.008:
        return "強：bucket 報酬具明顯單調性與高低分位差"
    if abs_corr >= 0.30 and abs_spread >= 0.005:
        return "中：有可研究方向，但仍需樣本外驗證"
    if obvious_count >= 2 and abs_spread >= 0.003:
        return "弱：有局部 bucket 現象，但方向不夠穩定"
    return "無：暫無穩定單因子預測力"


def identify_no_value_factors(summary: pd.DataFrame) -> list[str]:
    no_value = []
    for factor in FACTORS:
        assessments = summary.loc[summary["factor"] == factor, "assessment"].astype(str)
        if not assessments.str.startswith(("強", "中")).any():
            no_value.append(factor)
    return no_value


def data_period_section(master: pd.DataFrame) -> str:
    start = master["date"].min().strftime("%Y-%m-%d")
    end = master["date"].max().strftime("%Y-%m-%d")
    return f"- 資料期間：{start} 至 {end}"


def missing_section(master: pd.DataFrame) -> str:
    missing = master.isna().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if missing.empty:
        return "- 無缺值。"

    lines = ["| column | missing_count | missing_pct |", "|---|---:|---:|"]
    total = len(master)
    for column, count in missing.items():
        lines.append(f"| {column} | {int(count):,} | {count / total:.2%} |")
    lines.append("")
    lines.append("前幾週的 forward return、change 與 156-week rolling 指標出現缺值屬正常現象。")
    return "\n".join(lines)


def gold_price_source_section(master: pd.DataFrame) -> str:
    source = (
        master["gold_price_source"].dropna().iloc[-1]
        if "gold_price_source" in master.columns and master["gold_price_source"].notna().any()
        else "unknown"
    )
    recommendation = (
        master["gold_price_benchmark_recommendation"].dropna().iloc[-1]
        if "gold_price_benchmark_recommendation" in master.columns
        and master["gold_price_benchmark_recommendation"].notna().any()
        else "Use licensed LBMA PM or reliable XAUUSD spot for benchmark-grade pricing."
    )
    return "\n".join(
        [
            f"- 目前 `gold_close` 來源：{source}",
            "- 判斷：目前欄位不應被解讀為 XAUUSD spot 或 LBMA PM。它是 COMEX GC futures proxy，和 COT/COMEX 籌碼資料在市場結構上較一致。",
            f"- 建議：{recommendation}",
            "- v0.1 可保留 GC futures proxy 做籌碼研究；v0.2 若要做正式價格基準或跨市場比較，應新增可切換資料源，優先順序為 licensed LBMA PM，其次 reliable XAUUSD spot，最後才是 GC futures proxy。",
        ]
    )


def gold_anomaly_section(master: pd.DataFrame) -> str:
    if "gold_anomaly_2025_2026" not in master.columns:
        return "- Master dataset 尚未包含 anomaly 標記。請先重新執行 `python main.py --no-download`。"

    anomalies = master[master["gold_anomaly_2025_2026"]].copy()
    if anomalies.empty:
        return "- 2025-2026 未標記到異常價格區間。"

    intervals = condense_date_intervals(anomalies["date"])
    lines = [
        f"- 標記筆數：{len(anomalies):,}",
        "- 標記規則：2025 年以後，符合 `level>=4000`、`level>=5000`、`abs_1w_return>=5pct`、`abs_return_zscore_52w>=2.5`、`level_zscore_156w>=2.5` 任一條件。",
        "- 異常區間："
    ]
    for start, end in intervals:
        lines.append(f"  - {start.strftime('%Y-%m-%d')} 至 {end.strftime('%Y-%m-%d')}")

    largest_moves = anomalies.reindex(
        anomalies["gold_return_1w"].abs().sort_values(ascending=False).index
    ).head(8)
    lines.extend(
        [
            "",
            "| date | gold_close | gold_return_1w | gold_return_zscore_52w | reason |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for row in largest_moves.itertuples(index=False):
        lines.append(
            "| {date} | {close} | {ret} | {z} | {reason} |".format(
                date=row.date.strftime("%Y-%m-%d"),
                close=format_number(row.gold_close, 2),
                ret=format_percent(row.gold_return_1w),
                z=format_number(row.gold_return_zscore_52w, 2),
                reason=row.gold_anomaly_reason,
            )
        )
    return "\n".join(lines)


def condense_date_intervals(dates: pd.Series) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    values = pd.to_datetime(dates).dropna().sort_values().reset_index(drop=True)
    if values.empty:
        return []
    intervals: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    start = values.iloc[0]
    previous = values.iloc[0]
    for current in values.iloc[1:]:
        if (current - previous).days > 14:
            intervals.append((start, previous))
            start = current
        previous = current
    intervals.append((start, previous))
    return intervals


def predictive_power_section(summary: pd.DataFrame) -> str:
    lines = [
        "| factor | horizon | rank_corr | high_low_spread | best_bucket | best_avg | worst_bucket | worst_avg | assessment |",
        "|---|---:|---:|---:|---|---:|---|---:|---|",
    ]
    for row in summary.itertuples(index=False):
        lines.append(
            "| {factor} | {horizon} | {corr} | {spread} | {best_bucket} | {best_avg} | {worst_bucket} | {worst_avg} | {assessment} |".format(
                factor=row.factor_label,
                horizon=row.forward_horizon,
                corr=format_number(row.rank_corr, 3),
                spread=format_percent(row.high_low_spread),
                best_bucket=row.best_bucket,
                best_avg=format_percent(row.best_avg_forward_return),
                worst_bucket=row.worst_bucket,
                worst_avg=format_percent(row.worst_avg_forward_return),
                assessment=row.assessment,
            )
        )
    return "\n".join(lines)


def train_test_section(summary: pd.DataFrame) -> str:
    train = summary[summary["sample_split"] == "train_2009_2018"].copy()
    test = summary[summary["sample_split"] == "test_2019_2026"].copy()
    merged = train.merge(
        test,
        on=["factor", "factor_label", "forward_horizon"],
        suffixes=("_train", "_test"),
    )
    if merged.empty:
        return "- Train/Test analysis 尚無結果。"

    lines = [
        "| factor | horizon | train_rank_corr | test_rank_corr | train_spread | test_spread | train_best | test_best | stability |",
        "|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    for row in merged.itertuples(index=False):
        same_direction = same_sign(row.rank_corr_train, row.rank_corr_test)
        useful_test = not str(row.assessment_test).startswith("無")
        stability = "pass" if same_direction and useful_test else "weak"
        lines.append(
            "| {factor} | {horizon} | {train_corr} | {test_corr} | {train_spread} | {test_spread} | {train_best} | {test_best} | {stability} |".format(
                factor=row.factor_label,
                horizon=row.forward_horizon,
                train_corr=format_number(row.rank_corr_train, 3),
                test_corr=format_number(row.rank_corr_test, 3),
                train_spread=format_percent(row.high_low_spread_train),
                test_spread=format_percent(row.high_low_spread_test),
                train_best=row.best_bucket_train,
                test_best=row.best_bucket_test,
                stability=stability,
            )
        )
    return "\n".join(lines)


def regime_section(summary: pd.DataFrame) -> str:
    if summary.empty:
        return "- Regime analysis 尚無結果。"

    lines = [
        "| regime | factor | horizon | rank_corr | high_low_spread | best_bucket | best_avg | assessment |",
        "|---|---|---:|---:|---:|---|---:|---|",
    ]
    ordered = summary.sort_values(["gold_regime", "factor", "forward_horizon"])
    for row in ordered.itertuples(index=False):
        lines.append(
            "| {regime} | {factor} | {horizon} | {corr} | {spread} | {best_bucket} | {best_avg} | {assessment} |".format(
                regime=row.gold_regime,
                factor=row.factor_label,
                horizon=row.forward_horizon,
                corr=format_number(row.rank_corr, 3),
                spread=format_percent(row.high_low_spread),
                best_bucket=row.best_bucket,
                best_avg=format_percent(row.best_avg_forward_return),
                assessment=row.assessment,
            )
        )
    return "\n".join(lines)


def same_sign(left: float, right: float) -> bool:
    if pd.isna(left) or pd.isna(right):
        return False
    if left == 0 or right == 0:
        return False
    return (left > 0 and right > 0) or (left < 0 and right < 0)


def obvious_bucket_section(buckets: pd.DataFrame, intro: str) -> str:
    if buckets.empty:
        return "- 無。"

    lines = [
        intro,
        "",
        "| factor | horizon | bucket | count | avg_forward_return | median_forward_return | win_rate |",
        "|---|---:|---|---:|---:|---:|---:|",
    ]
    ordered = buckets.sort_values(["factor", "forward_horizon", "percentile_bucket"])
    for row in ordered.itertuples(index=False):
        lines.append(
            "| {factor} | {horizon} | {bucket} | {count} | {avg} | {median} | {win} |".format(
                factor=FACTOR_LABELS.get(row.factor, row.factor),
                horizon=row.forward_horizon,
                bucket=row.percentile_bucket,
                count=int(row.count),
                avg=format_percent(row.avg_forward_return),
                median=format_percent(row.median_forward_return),
                win=format_percent(row.win_rate),
            )
        )
    return "\n".join(lines)


def no_value_section(no_value_factors: list[str], summary: pd.DataFrame) -> str:
    if not no_value_factors:
        return "- 依目前規則，沒有完全失去參考價值的因子；但仍需樣本外測試。"

    lines = []
    for factor in no_value_factors:
        factor_summary = summary[summary["factor"] == factor]
        best_abs_corr = factor_summary["rank_corr"].abs().max()
        best_abs_spread = factor_summary["high_low_spread"].abs().max()
        lines.append(
            "- {label}：目前沒有穩定單因子參考價值。最大 |rank_corr|={corr}，最大 |90-100 vs 0-10 spread|={spread}。".format(
                label=FACTOR_LABELS[factor],
                corr=format_number(best_abs_corr, 3),
                spread=format_percent(best_abs_spread),
            )
        )
    return "\n".join(lines)


def v02_recommendation_section(no_value_factors: list[str]) -> str:
    candidate_factors = [factor for factor in FACTORS if factor not in no_value_factors]
    if len(candidate_factors) >= 2:
        candidates = ", ".join(FACTOR_LABELS[factor] for factor in candidate_factors)
        excluded = ", ".join(FACTOR_LABELS[factor] for factor in no_value_factors) or "無"
        return (
            "- 建議進入 v0.2 綜合指數的研究階段，但只做 research prototype，不建議直接交易化。\n"
            f"- v0.2 初版候選因子：{candidates}。\n"
            f"- 暫不納入或僅作觀察因子：{excluded}。\n"
            "- v0.2 應加入樣本外驗證、走勢 regime 切分、訊號冷卻期與風險調整後報酬，再決定是否形成綜合指數。"
        )
    return (
        "- 不建議立即進入 v0.2 綜合指數階段。\n"
        "- 目前可先擴充資料品質、改進 forward drawdown 定義，並做樣本外檢驗後再評估。"
    )


def rules_section() -> str:
    return "\n".join(
        [
            f"- 明顯正報酬 bucket：count >= {MIN_BUCKET_COUNT}，avg_forward_return > 0，median_forward_return > 0，win_rate >= {POSITIVE_WIN_RATE:.0%}。",
            f"- 明顯負報酬 bucket：count >= {MIN_BUCKET_COUNT}，avg_forward_return < 0，median_forward_return < 0，win_rate <= {NEGATIVE_WIN_RATE:.0%}。",
            "- rank_corr：percentile bucket midpoint 與 avg_forward_return 的 Spearman 相關。",
            "- high_low_spread：90-100 percentile bucket 平均 forward return 減 0-10 percentile bucket 平均 forward return。",
            "- 預測力分級只代表 v0.1 單因子歷史研究結果，不代表交易訊號。"
        ]
    )


def format_percent(value: object) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value) * 100:.2f}%"


def format_number(value: object, digits: int) -> str:
    if pd.isna(value):
        return "NA"
    return f"{float(value):.{digits}f}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate GHPR factor research report.")
    parser.add_argument("--master", default=str(OUTPUT_MASTER_WEEKLY), help="Master weekly CSV path.")
    parser.add_argument("--factor-results", default=str(SUMMARY_CSV), help="Single-factor result CSV path.")
    parser.add_argument("--output", default=str(REPORT_PATH), help="Markdown report output path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    output = generate_factor_report(
        master_path=Path(args.master),
        factor_result_path=Path(args.factor_results),
        output_path=Path(args.output),
    )
    print(f"Report: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

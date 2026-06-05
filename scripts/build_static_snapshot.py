from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MASTER_PATH = PROJECT_ROOT / "data" / "processed" / "ghpr_master_weekly.csv"
HISTORICAL_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_report.csv"
HISTORICAL_STATS_PATH = PROJECT_ROOT / "outputs" / "reports" / "historical_similarity_stats.csv"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "index.html"

MM_FACTOR = "mm_net_percentile_156w"
FORWARD_HORIZONS = [1, 2, 4, 8]
GOLD_SOURCE_TEXT = "COMEX GC futures proxy via Yahoo Finance GC=F"
FUTURES_PROXY_NOTE = "This is not official LBMA PM benchmark or broker XAUUSD spot."
RESEARCH_WARNING_ZH = "本頁為 GHPR 歷史定位研究摘要，不是交易訊號，不提供買賣建議。"


def read_csv(path: Path, date_columns: list[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    frame = pd.read_csv(path)
    for column in date_columns or []:
        if column in frame.columns:
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
    return frame


def scalar_float(value: object) -> float | None:
    if value is None or pd.isna(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def percent_points(value: object) -> float | None:
    number = scalar_float(value)
    if number is None:
        return None
    return number * 100 if abs(number) <= 1 else number


def fmt_date(value: object) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return pd.Timestamp(value).strftime("%Y-%m-%d")


def fmt_number(value: object, digits: int = 2) -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    return f"{number:,.{digits}f}"


def fmt_percent(value: object, digits: int = 2, input_scale: str = "return") -> str:
    number = scalar_float(value)
    if number is None:
        return "N/A"
    if input_scale in {"return", "fraction"}:
        number *= 100
    return f"{number:.{digits}f}%"


def latest_row(master: pd.DataFrame) -> pd.Series | None:
    if master.empty or "date" not in master.columns:
        return None
    return master.dropna(subset=["date"]).sort_values("date").iloc[-1]


def top20_stats_row(stats: pd.DataFrame) -> pd.Series | None:
    if stats.empty or "group" not in stats.columns:
        return None
    top20 = stats[stats["group"].astype(str).str.lower().eq("top 20")]
    if top20.empty:
        return None
    return top20.iloc[0]


def classify_ghpr_signal(stats_row: pd.Series | None) -> str:
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


def build_trader_summary(latest: pd.Series | None, stats: pd.DataFrame) -> dict:
    stats_row = top20_stats_row(stats)
    status = classify_ghpr_signal(stats_row)
    copy = {
        "tailwind": {
            "signal_label": "綠燈順風 / Tailwind",
            "signal_color": "#16a34a",
            "plain_language_summary_zh": "歷史相似案例後續表現偏正向，環境較順風；仍只代表歷史樣本傾向。",
            "chase_long_advice_zh": "歷史樣本偏順風，但 GHPR 不提供進出場點，仍需價格結構確認。",
            "short_advice_zh": "不應僅因 GHPR 統計偏順風就建立反向假設；等待價格結構或其他市場確認。",
            "wait_for_zh": "等待價格結構、OGR / MMP、OI 回升或關鍵區間反應後，再作進一步判斷。",
        },
        "mixed": {
            "signal_label": "黃燈混亂 / Mixed",
            "signal_color": "#ca8a04",
            "plain_language_summary_zh": "歷史相似案例分歧，尚未形成明確風險方向，適合等待更多確認。",
            "chase_long_advice_zh": "追多風險未明顯改善，較適合降低假設強度並觀察後續資料。",
            "short_advice_zh": "尚不可直接視為 GHPR 放空訊號；需要價格結構或其他確認。",
            "wait_for_zh": "等待價格結構、OGR / MMP、OI 回升或跌破支撐後，再作進一步判斷。",
        },
        "risk_off_caution": {
            "signal_label": "黃燈偏紅 / Risk-off Caution",
            "signal_color": "#f97316",
            "plain_language_summary_zh": "目前歷史相似案例偏向後續弱勢，追多風險較高，尚不宜視為直接放空訊號。",
            "chase_long_advice_zh": "目前不適合高槓桿追多，因為歷史樣本後續表現偏弱。",
            "short_advice_zh": "尚不可直接視為 GHPR 放空訊號。GHPR 只提供歷史定位，仍需價格結構或其他確認。",
            "wait_for_zh": "等待價格結構、OGR / MMP、OI 回升或跌破支撐後，再作進一步判斷。",
        },
        "high_risk": {
            "signal_label": "紅燈高風險 / High Risk",
            "signal_color": "#dc2626",
            "plain_language_summary_zh": "歷史相似案例短中期後續表現偏弱，追多風險很高；仍不能單獨作為放空依據。",
            "chase_long_advice_zh": "目前追多風險偏高，尤其不適合把 GHPR 當作高槓桿追多依據。",
            "short_advice_zh": "即使風險偏高，也不可直接視為 GHPR 放空訊號；仍需價格結構或其他確認。",
            "wait_for_zh": "等待價格結構、OGR / MMP、OI 回升或跌破支撐後，再作進一步判斷。",
        },
        "na": {
            "signal_label": "資料不足 / N/A",
            "signal_color": "#64748b",
            "plain_language_summary_zh": "目前歷史相似案例統計不足，暫不做定位判讀。",
            "chase_long_advice_zh": "資料不足，GHPR 暫不提供追多風險濾網判讀。",
            "short_advice_zh": "資料不足，GHPR 暫不提供放空條件判讀。",
            "wait_for_zh": "等待資料更新完成後，再查看歷史統計研究結果。",
        },
    }
    stats_used = {
        "avg_1w": scalar_float(stats_row.get("avg_return_1w")) if stats_row is not None else None,
        "avg_2w": scalar_float(stats_row.get("avg_return_2w")) if stats_row is not None else None,
        "avg_4w": scalar_float(stats_row.get("avg_return_4w")) if stats_row is not None else None,
        "avg_8w": scalar_float(stats_row.get("avg_return_8w")) if stats_row is not None else None,
        "win_8w": scalar_float(stats_row.get("win_rate_8w")) if stats_row is not None else None,
    }
    return {**copy[status], "status_key": status, "stats_used": stats_used}


def data_freshness(latest_date: object) -> str:
    if latest_date is None or pd.isna(latest_date):
        return "N/A"
    age_days = (pd.Timestamp(datetime.now().date()) - pd.Timestamp(latest_date).normalize()).days
    if age_days <= 10:
        return "Fresh"
    if age_days <= 21:
        return "Slightly stale"
    return "Stale"


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


def html_table(rows: list[dict], columns: list[tuple[str, str]]) -> str:
    if not rows:
        return '<p class="muted">N/A</p>'
    header = "".join(f"<th>{escape(label)}</th>" for _, label in columns)
    body = []
    for row in rows:
        cells = "".join(f"<td>{escape(str(row.get(key, 'N/A')))}</td>" for key, _ in columns)
        body.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{header}</tr></thead><tbody>{''.join(body)}</tbody></table>"


def stats_rows(stats: pd.DataFrame) -> list[dict]:
    if stats.empty:
        return []
    rows = []
    for _, row in stats.iterrows():
        rows.append(
            {
                "group": row.get("group", "N/A"),
                "case_count": fmt_number(row.get("case_count"), 0),
                "avg_1w": fmt_percent(row.get("avg_return_1w")),
                "win_1w": fmt_percent(row.get("win_rate_1w"), input_scale="fraction"),
                "avg_2w": fmt_percent(row.get("avg_return_2w")),
                "win_2w": fmt_percent(row.get("win_rate_2w"), input_scale="fraction"),
                "avg_4w": fmt_percent(row.get("avg_return_4w")),
                "win_4w": fmt_percent(row.get("win_rate_4w"), input_scale="fraction"),
                "avg_8w": fmt_percent(row.get("avg_return_8w")),
                "win_8w": fmt_percent(row.get("win_rate_8w"), input_scale="fraction"),
            }
        )
    return rows


def historical_case_rows(report: pd.DataFrame) -> list[dict]:
    if report.empty:
        return []
    rows = []
    for _, row in report.head(20).iterrows():
        rows.append(
            {
                "date": fmt_date(row.get("historical_date")),
                "score": fmt_number(row.get("similarity_score"), 2),
                "gold": fmt_number(row.get("historical_gold_close")),
                "mm": fmt_number(row.get("historical_mm_percentile"), 2),
                "producer": fmt_number(row.get("historical_producer_percentile"), 2),
                "oi": fmt_number(row.get("historical_oi_percentile"), 2),
                "r1": fmt_percent(row.get("future_return_1w")),
                "r2": fmt_percent(row.get("future_return_2w")),
                "r4": fmt_percent(row.get("future_return_4w")),
                "r8": fmt_percent(row.get("future_return_8w")),
            }
        )
    return rows


def build_html(master: pd.DataFrame, report: pd.DataFrame, stats: pd.DataFrame) -> str:
    latest = latest_row(master)
    summary = build_trader_summary(latest, stats)
    source = GOLD_SOURCE_TEXT
    if latest is not None and "gold_price_source" in latest:
        source = str(latest.get("gold_price_source") or GOLD_SOURCE_TEXT)
    latest_date = latest.get("date") if latest is not None else None
    gold_close = latest.get("gold_close") if latest is not None else None
    mm = latest.get(MM_FACTOR) if latest is not None else None
    producer = latest.get("producer_net_percentile_156w") if latest is not None else None
    oi = latest.get("oi_percentile_156w") if latest is not None else None
    top20_stats = top20_stats_row(stats)

    stat_cards = [
        ("1W", fmt_percent(top20_stats.get("avg_return_1w")) if top20_stats is not None else "N/A"),
        ("2W", fmt_percent(top20_stats.get("avg_return_2w")) if top20_stats is not None else "N/A"),
        ("4W", fmt_percent(top20_stats.get("avg_return_4w")) if top20_stats is not None else "N/A"),
        ("8W", fmt_percent(top20_stats.get("avg_return_8w")) if top20_stats is not None else "N/A"),
        ("8W Win Rate", fmt_percent(top20_stats.get("win_rate_8w"), input_scale="fraction") if top20_stats is not None else "N/A"),
    ]
    stat_card_html = "".join(
        f'<div class="metric"><div class="metric-label">{escape(label)}</div><div class="metric-value">{escape(value)}</div></div>'
        for label, value in stat_cards
    )

    health_rows = [
        {
            "cot_date": fmt_date(latest_date),
            "latest_gold": fmt_number(gold_close),
            "source": source,
            "generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "freshness": data_freshness(latest_date),
        }
    ]

    current_rows = [
        {
            "date": fmt_date(latest_date),
            "gold": fmt_number(gold_close),
            "mm": fmt_percent(mm, input_scale="fraction"),
            "producer": fmt_percent(producer, input_scale="fraction"),
            "oi": fmt_percent(oi, input_scale="fraction"),
            "state": market_state(mm, oi),
        }
    ]
    current_table = html_table(
        current_rows,
        [
            ("date", "Current Snapshot Date"),
            ("gold", "Gold Price"),
            ("mm", "MM Percentile"),
            ("producer", "Producer Percentile"),
            ("oi", "OI Percentile"),
            ("state", "Market State"),
        ],
    )
    historical_cases_table = html_table(
        historical_case_rows(report),
        [
            ("date", "Historical Case Date"),
            ("score", "Similarity Score"),
            ("gold", "Historical Case Gold"),
            ("mm", "Historical MM Percentile"),
            ("producer", "Historical Producer Percentile"),
            ("oi", "Historical OI Percentile"),
            ("r1", "Historical Case Forward Return 1W"),
            ("r2", "Historical Case Forward Return 2W"),
            ("r4", "Historical Case Forward Return 4W"),
            ("r8", "Historical Case Forward Return 8W"),
        ],
    )
    stats_table = html_table(
        stats_rows(stats),
        [
            ("group", "Group"),
            ("case_count", "Case Count"),
            ("avg_1w", "Avg 1W"),
            ("win_1w", "Win Rate 1W"),
            ("avg_2w", "Avg 2W"),
            ("win_2w", "Win Rate 2W"),
            ("avg_4w", "Avg 4W"),
            ("win_4w", "Win Rate 4W"),
            ("avg_8w", "Avg 8W"),
            ("win_8w", "Win Rate 8W"),
        ],
    )
    health_table = html_table(
        health_rows,
        [
            ("cot_date", "Latest COT Date"),
            ("latest_gold", "Latest Gold Price"),
            ("source", "Gold Price Source"),
            ("generated", "Snapshot Generated At"),
            ("freshness", "Data Freshness"),
        ],
    )
    signal_label = escape(summary["signal_label"])
    signal_color = summary["signal_color"]
    plain_language_summary = escape(summary["plain_language_summary_zh"])
    chase_long_advice = escape(summary["chase_long_advice_zh"])
    short_advice = escape(summary["short_advice_zh"])
    wait_for = escape(summary["wait_for_zh"])

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GHPR Static Snapshot</title>
  <style>
    :root {{ color-scheme: light; --line:#e5e7eb; --text:#0f172a; --muted:#64748b; --bg:#f8fafc; }}
    body {{ margin:0; font-family: Arial, "Microsoft JhengHei", sans-serif; color:var(--text); background:var(--bg); }}
    main {{ max-width:1180px; margin:0 auto; padding:28px 18px 48px; }}
    section {{ margin-top:22px; padding:18px; background:#fff; border:1px solid var(--line); border-radius:8px; }}
    h1 {{ margin:0 0 6px; font-size:30px; line-height:1.25; }}
    h2 {{ margin:0 0 14px; font-size:22px; }}
    h3 {{ margin:0 0 8px; font-size:17px; }}
    p {{ line-height:1.65; }}
    .muted {{ color:var(--muted); }}
    .warning {{ color:#7c2d12; background:#fff7ed; border:1px solid #fed7aa; padding:12px; border-radius:8px; }}
    .summary {{ border-left:8px solid {signal_color}; }}
    .summary-badge {{ display:inline-block; font-weight:700; color:{signal_color}; margin-bottom:8px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(230px,1fr)); gap:12px; }}
    .box {{ border:1px solid var(--line); border-radius:8px; padding:14px; background:#fff; }}
    .metric-row {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:10px; }}
    .metric {{ border:1px solid var(--line); border-radius:8px; padding:12px; background:#f8fafc; }}
    .metric-label {{ color:var(--muted); font-size:13px; }}
    .metric-value {{ font-size:20px; font-weight:700; margin-top:4px; }}
    table {{ border-collapse:collapse; width:100%; font-size:14px; }}
    th, td {{ border-bottom:1px solid var(--line); padding:9px 8px; text-align:left; white-space:nowrap; }}
    th {{ background:#f1f5f9; color:#334155; }}
    .table-wrap {{ overflow-x:auto; }}
  </style>
</head>
<body>
<main>
  <section class="summary">
    <div class="summary-badge">GHPR 判讀摘要：{signal_label}</div>
    <h1>GHPR 判讀摘要 / Trader Summary</h1>
    <p><strong>GHPR 是大型資金籌碼結構的風險濾網，不是交易訊號。</strong></p>
    <p>{plain_language_summary}</p>
    <div class="grid">
      <div class="box"><h3>追多風險判讀</h3><p>{chase_long_advice}</p></div>
      <div class="box"><h3>放空條件判讀</h3><p>{short_advice}</p></div>
      <div class="box"><h3>等待確認條件</h3><p>{wait_for}</p></div>
    </div>
  </section>

  <section>
    <h2>Current Position</h2>
    <div class="table-wrap">
      {current_table}
    </div>
  </section>

  <section>
    <h2>Top20 Similar Cases Historical Statistics</h2>
    <div class="metric-row">{stat_card_html}</div>
  </section>

  <section>
    <h2>Historical Similar Cases</h2>
    <p class="muted">Current Snapshot Date 是目前資料快照日期；Historical Case Date 是歷史相似案例的發生日期。</p>
    <div class="table-wrap">
      {historical_cases_table}
    </div>
  </section>

  <section>
    <h2>Top 5 / Top 10 / Top 20 Statistics</h2>
    <div class="table-wrap">
      {stats_table}
    </div>
  </section>

  <section>
    <h2>Data Health</h2>
    <div class="table-wrap">
      {health_table}
    </div>
    <p><strong>Gold price source:</strong> {escape(GOLD_SOURCE_TEXT)}.</p>
    <p class="muted">{escape(FUTURES_PROXY_NOTE)}</p>
  </section>

  <section>
    <h2>如何使用 GHPR</h2>
    <ol>
      <li>先看 GHPR 判讀摘要，了解目前是順風、逆風還是混亂。</li>
      <li>再看 MM / Producer / OI percentile，判斷大型資金位置。</li>
      <li>再看 Top 20 Similar Cases，了解歷史樣本後續表現。</li>
      <li>GHPR 不提供進出場點，只提供追多或放空前的風險濾網。</li>
      <li>最後仍需結合價格結構、OGR / MMP、成交量或其他市場確認。</li>
    </ol>
  </section>

  <section class="warning">
    {escape(RESEARCH_WARNING_ZH)}
  </section>
</main>
</body>
</html>
"""


def main() -> None:
    master = read_csv(MASTER_PATH, ["date"])
    report = read_csv(HISTORICAL_REPORT_PATH, ["current_date", "historical_date"])
    stats = read_csv(HISTORICAL_STATS_PATH)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(build_html(master, report, stats), encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

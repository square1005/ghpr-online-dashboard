# Gold Price Source Audit

- Current `gold_close` source: COMEX GC futures proxy via Yahoo Finance GC=F
- Current status: GC futures proxy, not XAUUSD spot and not LBMA PM benchmark.
- Recommendation: Keep GC futures for COT/COMEX alignment; use licensed LBMA PM or reliable XAUUSD spot for benchmark-grade v0.2 pricing.
- Rationale: COT positioning is COMEX futures data, so GC futures are internally aligned for v0.1 research. For v0.2 benchmark-grade price research, prefer licensed LBMA PM or a stable XAUUSD spot feed.

## 2025-2026 Anomaly Flags

- Flagged rows: 47
- Rules: date >= 2025-01-01 and any of `level>=4000`, `level>=5000`, `abs_1w_return>=5pct`, `abs_return_zscore_52w>=2.5`, `level_zscore_156w>=2.5`.
- Detail CSV: gold_price_anomalies_2025_2026.csv

- Flagged interval: 2025-02-11 to 2026-05-26

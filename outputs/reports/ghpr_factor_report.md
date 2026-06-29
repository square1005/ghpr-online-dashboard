# GHPR Factor Research Report

## 1. 資料期間

- 資料期間：2009-09-01 至 2026-06-23

## 2. 資料筆數

- Master weekly rows: 878
- Single-factor result rows: 160

## 3. 缺值狀況

| column | missing_count | missing_pct |
|---|---:|---:|
| gold_anomaly_reason | 827 | 94.19% |
| gold_close_percentile_156w | 51 | 5.81% |
| swap_net_zscore_156w | 51 | 5.81% |
| oi_percentile_156w | 51 | 5.81% |
| gold_close_zscore_156w | 51 | 5.81% |
| mm_net_percentile_156w | 51 | 5.81% |
| swap_net_percentile_156w | 51 | 5.81% |
| producer_net_zscore_156w | 51 | 5.81% |
| producer_net_percentile_156w | 51 | 5.81% |
| mm_net_zscore_156w | 51 | 5.81% |
| oi_zscore_156w | 51 | 5.81% |
| gold_return_zscore_52w | 26 | 2.96% |
| gold_return_8w | 8 | 0.91% |
| gold_return_4w | 4 | 0.46% |
| gold_return_2w | 2 | 0.23% |
| gold_return_1w | 1 | 0.11% |
| mm_net_change | 1 | 0.11% |
| oi_change | 1 | 0.11% |

前幾週的 forward return、change 與 156-week rolling 指標出現缺值屬正常現象。

## 4. Gold Price Source 與 2025-2026 異常區間

- 目前 `gold_close` 來源：COMEX GC futures proxy via Yahoo Finance GC=F
- 判斷：目前欄位不應被解讀為 XAUUSD spot 或 LBMA PM。它是 COMEX GC futures proxy，和 COT/COMEX 籌碼資料在市場結構上較一致。
- 建議：Keep GC futures for COT/COMEX alignment; use licensed LBMA PM or reliable XAUUSD spot for benchmark-grade v0.2 pricing.
- v0.1 可保留 GC futures proxy 做籌碼研究；v0.2 若要做正式價格基準或跨市場比較，應新增可切換資料源，優先順序為 licensed LBMA PM，其次 reliable XAUUSD spot，最後才是 GC futures proxy。

- 標記筆數：51
- 標記規則：2025 年以後，符合 `level>=4000`、`level>=5000`、`abs_1w_return>=5pct`、`abs_return_zscore_52w>=2.5`、`level_zscore_156w>=2.5` 任一條件。
- 異常區間：
  - 2025-02-11 至 2025-02-18
  - 2025-03-18 至 2025-06-03
  - 2025-09-23 至 2025-10-21
  - 2025-11-10 至 2026-06-23

| date | gold_close | gold_return_1w | gold_return_zscore_52w | reason |
|---|---:|---:|---:|---|
| 2026-03-24 | 4399.30 | -12.03% | -3.68 | level>=4000; abs_1w_return>=5pct; abs_return_zscore_52w>=2.5 |
| 2025-04-15 | 3218.70 | 8.43% | 3.36 | abs_1w_return>=5pct; abs_return_zscore_52w>=2.5; level_zscore_156w>=2.5 |
| 2026-01-27 | 5079.90 | 6.73% | 2.01 | level>=4000; level>=5000; abs_1w_return>=5pct; level_zscore_156w>=2.5 |
| 2025-04-22 | 3400.80 | 5.66% | 2.05 | abs_1w_return>=5pct; level_zscore_156w>=2.5 |
| 2026-03-31 | 4647.60 | 5.64% | 1.36 | level>=4000; abs_1w_return>=5pct |
| 2026-02-24 | 5155.80 | 5.59% | 1.53 | level>=4000; level>=5000; abs_1w_return>=5pct; level_zscore_156w>=2.5 |
| 2026-06-09 | 4260.00 | -5.10% | -1.70 | level>=4000; abs_1w_return>=5pct |
| 2025-05-13 | 3240.30 | -5.02% | -2.22 | abs_1w_return>=5pct |

## 5. 每個因子的 1W / 2W / 4W / 8W 預測力

| factor | horizon | rank_corr | high_low_spread | best_bucket | best_avg | worst_bucket | worst_avg | assessment |
|---|---:|---:|---:|---|---:|---|---:|---|
| Managed Money Net Percentile | 1W | 0.079 | 0.19% | 50-60 percentile | 0.53% | 40-50 percentile | -0.29% | 無：暫無穩定單因子預測力 |
| Managed Money Net Percentile | 2W | 0.188 | 0.47% | 60-70 percentile | 0.95% | 30-40 percentile | -0.24% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Managed Money Net Percentile | 4W | 0.321 | 0.86% | 50-60 percentile | 1.83% | 30-40 percentile | -0.05% | 中：有可研究方向，但仍需樣本外驗證 |
| Managed Money Net Percentile | 8W | 0.758 | 1.14% | 60-70 percentile | 2.45% | 20-30 percentile | 0.08% | 強：bucket 報酬具明顯單調性與高低分位差 |
| Producer / Merchant Net Percentile | 1W | -0.176 | 0.03% | 50-60 percentile | 0.45% | 0-10 percentile | -0.07% | 無：暫無穩定單因子預測力 |
| Producer / Merchant Net Percentile | 2W | -0.248 | -0.20% | 30-40 percentile | 1.26% | 90-100 percentile | -0.13% | 無：暫無穩定單因子預測力 |
| Producer / Merchant Net Percentile | 4W | -0.285 | -0.49% | 30-40 percentile | 1.98% | 90-100 percentile | -0.21% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Producer / Merchant Net Percentile | 8W | -0.273 | -1.07% | 50-60 percentile | 2.85% | 90-100 percentile | -0.11% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Swap Net Percentile | 1W | 0.103 | 0.08% | 60-70 percentile | 0.47% | 30-40 percentile | -0.20% | 無：暫無穩定單因子預測力 |
| Swap Net Percentile | 2W | 0.127 | 0.23% | 20-30 percentile | 0.84% | 30-40 percentile | -0.26% | 無：暫無穩定單因子預測力 |
| Swap Net Percentile | 4W | 0.152 | 0.47% | 20-30 percentile | 1.47% | 30-40 percentile | -0.20% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Swap Net Percentile | 8W | -0.164 | 1.43% | 20-30 percentile | 3.17% | 60-70 percentile | 0.10% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Total Open Interest Percentile | 1W | 0.042 | 0.16% | 10-20 percentile | 0.59% | 60-70 percentile | -0.20% | 無：暫無穩定單因子預測力 |
| Total Open Interest Percentile | 2W | 0.030 | 0.13% | 10-20 percentile | 1.01% | 0-10 percentile | 0.01% | 無：暫無穩定單因子預測力 |
| Total Open Interest Percentile | 4W | 0.006 | 0.44% | 20-30 percentile | 1.41% | 30-40 percentile | 0.02% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Total Open Interest Percentile | 8W | -0.200 | 1.10% | 20-30 percentile | 2.90% | 80-90 percentile | 0.47% | 弱：有局部 bucket 現象，但方向不夠穩定 |

## 6. 樣本外測試：Train 2009-2018 / Test 2019-2026

| factor | horizon | train_rank_corr | test_rank_corr | train_spread | test_spread | train_best | test_best | stability |
|---|---:|---:|---:|---:|---:|---|---|---|
| Managed Money Net Percentile | 1W | -0.321 | 0.236 | 0.05% | -0.07% | 20-30 percentile | 70-80 percentile | weak |
| Managed Money Net Percentile | 2W | -0.297 | 0.479 | 0.07% | 0.32% | 10-20 percentile | 60-70 percentile | weak |
| Managed Money Net Percentile | 4W | -0.139 | 0.455 | 0.07% | 0.97% | 10-20 percentile | 50-60 percentile | weak |
| Managed Money Net Percentile | 8W | -0.103 | 0.709 | -0.67% | 1.87% | 0-10 percentile | 80-90 percentile | weak |
| Producer / Merchant Net Percentile | 1W | 0.176 | -0.782 | 0.27% | -0.52% | 50-60 percentile | 10-20 percentile | weak |
| Producer / Merchant Net Percentile | 2W | 0.164 | -0.903 | 0.28% | -1.42% | 50-60 percentile | 30-40 percentile | weak |
| Producer / Merchant Net Percentile | 4W | 0.430 | -0.867 | 0.59% | -3.22% | 50-60 percentile | 10-20 percentile | weak |
| Producer / Merchant Net Percentile | 8W | 0.333 | -0.867 | -0.22% | -4.53% | 50-60 percentile | 10-20 percentile | weak |
| Swap Net Percentile | 1W | 0.697 | -0.248 | 0.43% | -0.09% | 40-50 percentile | 60-70 percentile | weak |
| Swap Net Percentile | 2W | 0.733 | -0.042 | 0.99% | -0.20% | 90-100 percentile | 20-30 percentile | weak |
| Swap Net Percentile | 4W | 0.879 | -0.139 | 1.82% | -0.39% | 90-100 percentile | 80-90 percentile | weak |
| Swap Net Percentile | 8W | 0.758 | -0.212 | 3.53% | -0.08% | 90-100 percentile | 70-80 percentile | weak |
| Total Open Interest Percentile | 1W | -0.152 | 0.200 | -0.14% | 0.56% | 50-60 percentile | 70-80 percentile | weak |
| Total Open Interest Percentile | 2W | -0.212 | 0.212 | -0.16% | 0.51% | 50-60 percentile | 80-90 percentile | weak |
| Total Open Interest Percentile | 4W | -0.224 | 0.358 | 0.14% | 0.88% | 60-70 percentile | 70-80 percentile | weak |
| Total Open Interest Percentile | 8W | 0.164 | 0.006 | 0.87% | 1.46% | 20-30 percentile | 10-20 percentile | pass |

## 7. 牛市 / 熊市 / 震盪 Regime 切分

| regime | factor | horizon | rank_corr | high_low_spread | best_bucket | best_avg | assessment |
|---|---|---:|---:|---:|---|---:|---|
| bear | Managed Money Net Percentile | 1W | -0.905 | NA | 0-10 percentile | 1.84% | 無：暫無穩定單因子預測力 |
| bear | Managed Money Net Percentile | 2W | -0.929 | NA | 0-10 percentile | 2.46% | 無：暫無穩定單因子預測力 |
| bear | Managed Money Net Percentile | 4W | -0.714 | NA | 10-20 percentile | 10.08% | 無：暫無穩定單因子預測力 |
| bear | Managed Money Net Percentile | 8W | -0.786 | NA | 0-10 percentile | 4.91% | 無：暫無穩定單因子預測力 |
| bear | Total Open Interest Percentile | 1W | -0.103 | -1.30% | 10-20 percentile | 6.45% | 無：暫無穩定單因子預測力 |
| bear | Total Open Interest Percentile | 2W | -0.248 | -4.83% | 70-80 percentile | 5.24% | 無：暫無穩定單因子預測力 |
| bear | Total Open Interest Percentile | 4W | -0.018 | -4.51% | 80-90 percentile | 10.80% | 無：暫無穩定單因子預測力 |
| bear | Total Open Interest Percentile | 8W | 0.115 | -1.89% | 80-90 percentile | 9.53% | 無：暫無穩定單因子預測力 |
| bear | Producer / Merchant Net Percentile | 1W | 0.567 | NA | 90-100 percentile | 2.11% | 無：暫無穩定單因子預測力 |
| bear | Producer / Merchant Net Percentile | 2W | 0.533 | NA | 90-100 percentile | 2.62% | 無：暫無穩定單因子預測力 |
| bear | Producer / Merchant Net Percentile | 4W | 0.533 | NA | 80-90 percentile | 9.13% | 無：暫無穩定單因子預測力 |
| bear | Producer / Merchant Net Percentile | 8W | 0.483 | NA | 80-90 percentile | 7.11% | 無：暫無穩定單因子預測力 |
| bear | Swap Net Percentile | 1W | 0.855 | 4.47% | 90-100 percentile | 2.64% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bear | Swap Net Percentile | 2W | 0.745 | 7.67% | 80-90 percentile | 5.75% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bear | Swap Net Percentile | 4W | 0.903 | 11.26% | 80-90 percentile | 7.80% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bear | Swap Net Percentile | 8W | 0.915 | 16.40% | 80-90 percentile | 9.99% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bull | Managed Money Net Percentile | 1W | 0.382 | 0.03% | 60-70 percentile | 1.01% | 無：暫無穩定單因子預測力 |
| bull | Managed Money Net Percentile | 2W | 0.539 | 0.81% | 60-70 percentile | 2.05% | 中：有可研究方向，但仍需樣本外驗證 |
| bull | Managed Money Net Percentile | 4W | 0.564 | -0.01% | 60-70 percentile | 2.98% | 無：暫無穩定單因子預測力 |
| bull | Managed Money Net Percentile | 8W | 0.782 | 1.20% | 60-70 percentile | 5.32% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bull | Total Open Interest Percentile | 1W | 0.236 | 0.04% | 80-90 percentile | 1.04% | 無：暫無穩定單因子預測力 |
| bull | Total Open Interest Percentile | 2W | 0.091 | 0.04% | 10-20 percentile | 1.90% | 無：暫無穩定單因子預測力 |
| bull | Total Open Interest Percentile | 4W | 0.212 | 0.06% | 10-20 percentile | 3.67% | 無：暫無穩定單因子預測力 |
| bull | Total Open Interest Percentile | 8W | 0.006 | 0.36% | 10-20 percentile | 7.85% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| bull | Producer / Merchant Net Percentile | 1W | -0.527 | -0.02% | 10-20 percentile | 0.98% | 無：暫無穩定單因子預測力 |
| bull | Producer / Merchant Net Percentile | 2W | -0.503 | -0.82% | 30-40 percentile | 1.65% | 中：有可研究方向，但仍需樣本外驗證 |
| bull | Producer / Merchant Net Percentile | 4W | -0.588 | -1.04% | 30-40 percentile | 2.57% | 中：有可研究方向，但仍需樣本外驗證 |
| bull | Producer / Merchant Net Percentile | 8W | -0.321 | -1.59% | 40-50 percentile | 5.80% | 中：有可研究方向，但仍需樣本外驗證 |
| bull | Swap Net Percentile | 1W | 0.042 | -0.05% | 40-50 percentile | 1.48% | 無：暫無穩定單因子預測力 |
| bull | Swap Net Percentile | 2W | 0.067 | -0.05% | 80-90 percentile | 2.07% | 無：暫無穩定單因子預測力 |
| bull | Swap Net Percentile | 4W | -0.139 | -0.48% | 20-30 percentile | 3.09% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| bull | Swap Net Percentile | 8W | -0.103 | -0.98% | 70-80 percentile | 7.47% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| range | Managed Money Net Percentile | 1W | -0.503 | -1.64% | 20-30 percentile | 3.73% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Managed Money Net Percentile | 2W | -0.442 | -2.43% | 30-40 percentile | 4.35% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Managed Money Net Percentile | 4W | -0.333 | -2.34% | 60-70 percentile | 5.82% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Managed Money Net Percentile | 8W | 0.297 | 30.01% | 90-100 percentile | 29.05% | 無：暫無穩定單因子預測力 |
| range | Total Open Interest Percentile | 1W | -0.552 | -5.78% | 0-10 percentile | 2.40% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Total Open Interest Percentile | 2W | -0.236 | -1.96% | 0-10 percentile | 4.86% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| range | Total Open Interest Percentile | 4W | 0.055 | 6.01% | 90-100 percentile | 7.24% | 無：暫無穩定單因子預測力 |
| range | Total Open Interest Percentile | 8W | 0.358 | 10.20% | 90-100 percentile | 11.83% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Producer / Merchant Net Percentile | 1W | 0.467 | 0.66% | 70-80 percentile | 3.72% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Producer / Merchant Net Percentile | 2W | 0.297 | 0.87% | 70-80 percentile | 7.96% | 無：暫無穩定單因子預測力 |
| range | Producer / Merchant Net Percentile | 4W | 0.394 | 1.97% | 50-60 percentile | 8.95% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Producer / Merchant Net Percentile | 8W | 0.176 | 1.94% | 40-50 percentile | 10.09% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| range | Swap Net Percentile | 1W | 0.345 | 1.66% | 70-80 percentile | 3.89% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Swap Net Percentile | 2W | 0.382 | 2.55% | 60-70 percentile | 3.17% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Swap Net Percentile | 4W | 0.115 | 5.34% | 30-40 percentile | 5.73% | 無：暫無穩定單因子預測力 |
| range | Swap Net Percentile | 8W | 0.188 | 4.96% | 30-40 percentile | 8.92% | 無：暫無穩定單因子預測力 |

## 8. 明顯正報酬 percentile 區間

目前符合明顯正報酬規則的區間如下。

| factor | horizon | bucket | count | avg_forward_return | median_forward_return | win_rate |
|---|---:|---|---:|---:|---:|---:|
| Managed Money Net Percentile | 1W | 0-10 percentile | 166 | 0.13% | 0.19% | 55.42% |
| Managed Money Net Percentile | 1W | 10-20 percentile | 70 | 0.13% | 0.24% | 58.57% |
| Managed Money Net Percentile | 1W | 20-30 percentile | 83 | 0.45% | 0.38% | 59.04% |
| Managed Money Net Percentile | 1W | 50-60 percentile | 62 | 0.53% | 0.57% | 62.90% |
| Managed Money Net Percentile | 1W | 70-80 percentile | 46 | 0.42% | 0.66% | 58.70% |
| Managed Money Net Percentile | 2W | 10-20 percentile | 70 | 0.75% | 0.58% | 61.43% |
| Managed Money Net Percentile | 2W | 20-30 percentile | 83 | 0.45% | 0.78% | 59.04% |
| Managed Money Net Percentile | 2W | 50-60 percentile | 62 | 0.93% | 0.92% | 61.29% |
| Managed Money Net Percentile | 2W | 60-70 percentile | 62 | 0.95% | 0.42% | 59.68% |
| Managed Money Net Percentile | 4W | 0-10 percentile | 166 | 0.31% | 0.36% | 56.02% |
| Managed Money Net Percentile | 4W | 10-20 percentile | 70 | 1.51% | 2.02% | 64.29% |
| Managed Money Net Percentile | 4W | 60-70 percentile | 62 | 1.05% | 0.62% | 56.45% |
| Managed Money Net Percentile | 4W | 90-100 percentile | 110 | 1.17% | 0.99% | 63.64% |
| Managed Money Net Percentile | 8W | 50-60 percentile | 62 | 2.11% | 2.39% | 58.06% |
| Managed Money Net Percentile | 8W | 60-70 percentile | 62 | 2.45% | 1.12% | 61.29% |
| Managed Money Net Percentile | 8W | 80-90 percentile | 59 | 2.00% | 1.67% | 59.32% |
| Managed Money Net Percentile | 8W | 90-100 percentile | 110 | 2.19% | 1.92% | 63.64% |
| Total Open Interest Percentile | 1W | 10-20 percentile | 66 | 0.59% | 0.78% | 65.15% |
| Total Open Interest Percentile | 1W | 40-50 percentile | 75 | 0.25% | 0.23% | 56.00% |
| Total Open Interest Percentile | 1W | 50-60 percentile | 54 | 0.41% | 0.40% | 61.11% |
| Total Open Interest Percentile | 1W | 80-90 percentile | 62 | 0.36% | 0.62% | 58.06% |
| Total Open Interest Percentile | 1W | 90-100 percentile | 98 | 0.15% | 0.25% | 57.14% |
| Total Open Interest Percentile | 2W | 10-20 percentile | 66 | 1.01% | 0.95% | 65.15% |
| Total Open Interest Percentile | 2W | 20-30 percentile | 74 | 0.42% | 0.33% | 55.41% |
| Total Open Interest Percentile | 2W | 50-60 percentile | 54 | 0.66% | 0.31% | 57.41% |
| Total Open Interest Percentile | 2W | 80-90 percentile | 62 | 0.74% | 0.64% | 59.68% |
| Total Open Interest Percentile | 4W | 10-20 percentile | 66 | 1.13% | 1.09% | 59.09% |
| Total Open Interest Percentile | 4W | 20-30 percentile | 74 | 1.41% | 1.16% | 60.81% |
| Total Open Interest Percentile | 4W | 60-70 percentile | 79 | 1.05% | 0.39% | 55.70% |
| Total Open Interest Percentile | 4W | 70-80 percentile | 73 | 0.93% | 0.62% | 57.53% |
| Total Open Interest Percentile | 4W | 90-100 percentile | 98 | 0.67% | 0.50% | 62.24% |
| Total Open Interest Percentile | 8W | 10-20 percentile | 66 | 2.36% | 2.40% | 65.15% |
| Total Open Interest Percentile | 8W | 50-60 percentile | 54 | 1.88% | 1.82% | 64.81% |
| Total Open Interest Percentile | 8W | 70-80 percentile | 73 | 2.21% | 1.34% | 60.27% |
| Total Open Interest Percentile | 8W | 80-90 percentile | 62 | 0.47% | 0.47% | 56.45% |
| Total Open Interest Percentile | 8W | 90-100 percentile | 98 | 1.66% | 1.97% | 57.14% |
| Producer / Merchant Net Percentile | 1W | 10-20 percentile | 62 | 0.35% | 0.53% | 61.29% |
| Producer / Merchant Net Percentile | 1W | 20-30 percentile | 56 | 0.42% | 0.66% | 55.36% |
| Producer / Merchant Net Percentile | 1W | 30-40 percentile | 75 | 0.44% | 0.40% | 62.67% |
| Producer / Merchant Net Percentile | 1W | 40-50 percentile | 69 | 0.05% | 0.30% | 59.42% |
| Producer / Merchant Net Percentile | 1W | 50-60 percentile | 67 | 0.45% | 0.52% | 58.21% |
| Producer / Merchant Net Percentile | 1W | 60-70 percentile | 87 | 0.30% | 0.27% | 56.32% |
| Producer / Merchant Net Percentile | 1W | 80-90 percentile | 95 | 0.10% | 0.21% | 58.95% |
| Producer / Merchant Net Percentile | 2W | 10-20 percentile | 62 | 0.42% | 0.31% | 59.68% |
| Producer / Merchant Net Percentile | 2W | 20-30 percentile | 56 | 0.66% | 0.69% | 57.14% |
| Producer / Merchant Net Percentile | 2W | 30-40 percentile | 75 | 1.26% | 0.77% | 62.67% |
| Producer / Merchant Net Percentile | 2W | 50-60 percentile | 67 | 0.71% | 0.45% | 62.69% |
| Producer / Merchant Net Percentile | 2W | 70-80 percentile | 58 | 0.41% | 0.29% | 55.17% |
| Producer / Merchant Net Percentile | 4W | 10-20 percentile | 62 | 0.98% | 1.09% | 61.29% |
| Producer / Merchant Net Percentile | 4W | 30-40 percentile | 75 | 1.98% | 1.96% | 62.67% |
| Producer / Merchant Net Percentile | 4W | 40-50 percentile | 69 | 0.88% | 0.40% | 56.52% |
| Producer / Merchant Net Percentile | 4W | 50-60 percentile | 67 | 1.55% | 0.39% | 58.21% |
| Producer / Merchant Net Percentile | 4W | 60-70 percentile | 87 | 0.77% | 0.77% | 57.47% |
| Producer / Merchant Net Percentile | 4W | 70-80 percentile | 58 | 0.80% | 0.70% | 58.62% |
| Producer / Merchant Net Percentile | 8W | 10-20 percentile | 62 | 1.26% | 1.30% | 61.29% |
| Producer / Merchant Net Percentile | 8W | 20-30 percentile | 56 | 2.80% | 1.86% | 60.71% |
| Producer / Merchant Net Percentile | 8W | 30-40 percentile | 75 | 2.54% | 2.61% | 56.00% |
| Producer / Merchant Net Percentile | 8W | 40-50 percentile | 69 | 1.80% | 0.81% | 56.52% |
| Producer / Merchant Net Percentile | 8W | 50-60 percentile | 67 | 2.85% | 2.10% | 58.21% |
| Producer / Merchant Net Percentile | 8W | 60-70 percentile | 87 | 1.95% | 2.59% | 55.17% |
| Producer / Merchant Net Percentile | 8W | 80-90 percentile | 95 | 1.45% | 0.79% | 56.84% |
| Swap Net Percentile | 1W | 0-10 percentile | 150 | 0.24% | 0.36% | 56.00% |
| Swap Net Percentile | 1W | 20-30 percentile | 72 | 0.22% | 0.60% | 56.94% |
| Swap Net Percentile | 1W | 40-50 percentile | 54 | 0.37% | 0.59% | 59.26% |
| Swap Net Percentile | 1W | 60-70 percentile | 79 | 0.47% | 0.19% | 59.49% |
| Swap Net Percentile | 1W | 70-80 percentile | 57 | 0.14% | 0.52% | 57.89% |
| Swap Net Percentile | 1W | 90-100 percentile | 113 | 0.33% | 0.25% | 60.18% |
| Swap Net Percentile | 2W | 20-30 percentile | 72 | 0.84% | 0.72% | 55.56% |
| Swap Net Percentile | 2W | 60-70 percentile | 79 | 0.65% | 0.58% | 59.49% |
| Swap Net Percentile | 2W | 90-100 percentile | 113 | 0.60% | 0.62% | 62.83% |
| Swap Net Percentile | 4W | 0-10 percentile | 150 | 0.64% | 0.44% | 55.33% |
| Swap Net Percentile | 4W | 10-20 percentile | 74 | 0.89% | 0.37% | 55.41% |
| Swap Net Percentile | 4W | 20-30 percentile | 72 | 1.47% | 0.92% | 55.56% |
| Swap Net Percentile | 4W | 80-90 percentile | 67 | 1.16% | 0.46% | 58.21% |
| Swap Net Percentile | 4W | 90-100 percentile | 113 | 1.11% | 1.64% | 68.14% |
| Swap Net Percentile | 8W | 0-10 percentile | 150 | 1.50% | 1.37% | 56.00% |
| Swap Net Percentile | 8W | 20-30 percentile | 72 | 3.17% | 1.72% | 58.33% |
| Swap Net Percentile | 8W | 70-80 percentile | 56 | 1.17% | 0.32% | 55.36% |
| Swap Net Percentile | 8W | 90-100 percentile | 113 | 2.93% | 2.38% | 64.60% |

## 9. 明顯負報酬 percentile 區間

目前符合明顯負報酬規則的區間如下。

| factor | horizon | bucket | count | avg_forward_return | median_forward_return | win_rate |
|---|---:|---|---:|---:|---:|---:|
| Managed Money Net Percentile | 1W | 40-50 percentile | 90 | -0.29% | -0.23% | 44.44% |
| Managed Money Net Percentile | 2W | 40-50 percentile | 89 | -0.15% | -0.44% | 42.70% |

## 10. 目前沒有參考價值的因子

- Producer / Merchant Net Percentile：目前沒有穩定單因子參考價值。最大 |rank_corr|=0.285，最大 |90-100 vs 0-10 spread|=1.07%。
- Swap Net Percentile：目前沒有穩定單因子參考價值。最大 |rank_corr|=0.164，最大 |90-100 vs 0-10 spread|=1.43%。
- Total Open Interest Percentile：目前沒有穩定單因子參考價值。最大 |rank_corr|=0.200，最大 |90-100 vs 0-10 spread|=1.10%。

## 11. 是否建議進入 v0.2 綜合指數階段

- 不建議立即進入 v0.2 綜合指數階段。
- 目前可先擴充資料品質、改進 forward drawdown 定義，並做樣本外檢驗後再評估。

## 判定規則

- 明顯正報酬 bucket：count >= 30，avg_forward_return > 0，median_forward_return > 0，win_rate >= 55%。
- 明顯負報酬 bucket：count >= 30，avg_forward_return < 0，median_forward_return < 0，win_rate <= 45%。
- rank_corr：percentile bucket midpoint 與 avg_forward_return 的 Spearman 相關。
- high_low_spread：90-100 percentile bucket 平均 forward return 減 0-10 percentile bucket 平均 forward return。
- 預測力分級只代表 v0.1 單因子歷史研究結果，不代表交易訊號。

# GHPR Factor Research Report

## 1. 資料期間

- 資料期間：2009-09-01 至 2026-09-29

## 2. 資料筆數

- Master weekly rows: 892
- Single-factor result rows: 160

## 3. 缺值狀況

| column | missing_count | missing_pct |
|---|---:|---:|
| gold_anomaly_reason | 829 | 92.94% |
| gold_close_percentile_156w | 51 | 5.72% |
| swap_net_zscore_156w | 51 | 5.72% |
| oi_percentile_156w | 51 | 5.72% |
| gold_close_zscore_156w | 51 | 5.72% |
| mm_net_percentile_156w | 51 | 5.72% |
| swap_net_percentile_156w | 51 | 5.72% |
| producer_net_zscore_156w | 51 | 5.72% |
| producer_net_percentile_156w | 51 | 5.72% |
| mm_net_zscore_156w | 51 | 5.72% |
| oi_zscore_156w | 51 | 5.72% |
| gold_return_zscore_52w | 26 | 2.91% |
| gold_return_8w | 8 | 0.90% |
| gold_return_4w | 4 | 0.45% |
| gold_return_2w | 2 | 0.22% |
| gold_return_1w | 1 | 0.11% |
| mm_net_change | 1 | 0.11% |
| oi_change | 1 | 0.11% |

前幾週的 forward return、change 與 156-week rolling 指標出現缺值屬正常現象。

## 4. Gold Price Source 與 2025-2026 異常區間

- 目前 `gold_close` 來源：COMEX GC futures proxy via Yahoo Finance GC=F
- 判斷：目前欄位不應被解讀為 XAUUSD spot 或 LBMA PM。它是 COMEX GC futures proxy，和 COT/COMEX 籌碼資料在市場結構上較一致。
- 建議：Keep GC futures for COT/COMEX alignment; use licensed LBMA PM or reliable XAUUSD spot for benchmark-grade v0.2 pricing.
- v0.1 可保留 GC futures proxy 做籌碼研究；v0.2 若要做正式價格基準或跨市場比較，應新增可切換資料源，優先順序為 licensed LBMA PM，其次 reliable XAUUSD spot，最後才是 GC futures proxy。

- 標記筆數：63
- 標記規則：2025 年以後，符合 `level>=4000`、`level>=5000`、`abs_1w_return>=5pct`、`abs_return_zscore_52w>=2.5`、`level_zscore_156w>=2.5` 任一條件。
- 異常區間：
  - 2025-02-11 至 2025-02-18
  - 2025-03-18 至 2025-05-13
  - 2025-06-03 至 2025-06-03
  - 2025-09-23 至 2025-10-21
  - 2025-11-10 至 2026-09-29

| date | gold_close | gold_return_1w | gold_return_zscore_52w | reason |
|---|---:|---:|---:|---|
| 2026-03-24 | 4402.00 | -12.10% | -3.68 | level>=4000; abs_1w_return>=5pct; abs_return_zscore_52w>=2.5 |
| 2025-04-15 | 3240.40 | 8.37% | 3.28 | abs_1w_return>=5pct; abs_return_zscore_52w>=2.5; level_zscore_156w>=2.5 |
| 2026-08-11 | 4441.10 | 6.95% | 1.83 | level>=4000; abs_1w_return>=5pct |
| 2026-01-27 | 5082.60 | 6.65% | 1.94 | level>=4000; level>=5000; abs_1w_return>=5pct; level_zscore_156w>=2.5 |
| 2026-09-01 | 4396.40 | -6.35% | -1.87 | level>=4000; abs_1w_return>=5pct |
| 2026-08-25 | 4694.50 | 6.20% | 1.56 | level>=4000; abs_1w_return>=5pct |
| 2026-03-31 | 4647.60 | 5.58% | 1.34 | level>=4000; abs_1w_return>=5pct |
| 2025-04-22 | 3419.40 | 5.52% | 1.97 | abs_1w_return>=5pct; level_zscore_156w>=2.5 |

## 5. 每個因子的 1W / 2W / 4W / 8W 預測力

| factor | horizon | rank_corr | high_low_spread | best_bucket | best_avg | worst_bucket | worst_avg | assessment |
|---|---:|---:|---:|---|---:|---|---:|---|
| Managed Money Net Percentile | 1W | 0.127 | 0.20% | 50-60 percentile | 0.59% | 40-50 percentile | -0.31% | 無：暫無穩定單因子預測力 |
| Managed Money Net Percentile | 2W | 0.188 | 0.49% | 60-70 percentile | 0.91% | 30-40 percentile | -0.27% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Managed Money Net Percentile | 4W | 0.309 | 0.88% | 50-60 percentile | 1.86% | 30-40 percentile | -0.08% | 中：有可研究方向，但仍需樣本外驗證 |
| Managed Money Net Percentile | 8W | 0.758 | 1.14% | 60-70 percentile | 2.50% | 20-30 percentile | -0.21% | 強：bucket 報酬具明顯單調性與高低分位差 |
| Producer / Merchant Net Percentile | 1W | -0.188 | 0.07% | 30-40 percentile | 0.49% | 0-10 percentile | -0.08% | 無：暫無穩定單因子預測力 |
| Producer / Merchant Net Percentile | 2W | -0.248 | -0.19% | 30-40 percentile | 1.30% | 90-100 percentile | -0.14% | 無：暫無穩定單因子預測力 |
| Producer / Merchant Net Percentile | 4W | -0.248 | -0.48% | 30-40 percentile | 2.06% | 90-100 percentile | -0.23% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Producer / Merchant Net Percentile | 8W | -0.309 | -1.10% | 20-30 percentile | 2.85% | 90-100 percentile | -0.20% | 中：有可研究方向，但仍需樣本外驗證 |
| Swap Net Percentile | 1W | 0.164 | 0.13% | 60-70 percentile | 0.48% | 50-60 percentile | -0.13% | 無：暫無穩定單因子預測力 |
| Swap Net Percentile | 2W | 0.042 | 0.26% | 20-30 percentile | 0.89% | 70-80 percentile | -0.18% | 無：暫無穩定單因子預測力 |
| Swap Net Percentile | 4W | 0.176 | 0.53% | 20-30 percentile | 1.45% | 30-40 percentile | -0.08% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Swap Net Percentile | 8W | -0.188 | 1.42% | 20-30 percentile | 3.08% | 60-70 percentile | -0.17% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Total Open Interest Percentile | 1W | 0.042 | 0.15% | 10-20 percentile | 0.65% | 60-70 percentile | -0.22% | 無：暫無穩定單因子預測力 |
| Total Open Interest Percentile | 2W | 0.200 | 0.20% | 10-20 percentile | 1.04% | 0-10 percentile | -0.04% | 無：暫無穩定單因子預測力 |
| Total Open Interest Percentile | 4W | -0.018 | 0.66% | 10-20 percentile | 1.41% | 0-10 percentile | 0.04% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| Total Open Interest Percentile | 8W | -0.103 | 1.35% | 20-30 percentile | 2.98% | 0-10 percentile | 0.32% | 弱：有局部 bucket 現象，但方向不夠穩定 |

## 6. 樣本外測試：Train 2009-2018 / Test 2019-2026

| factor | horizon | train_rank_corr | test_rank_corr | train_spread | test_spread | train_best | test_best | stability |
|---|---:|---:|---:|---:|---:|---|---|---|
| Managed Money Net Percentile | 1W | -0.321 | 0.212 | 0.05% | -0.07% | 20-30 percentile | 70-80 percentile | weak |
| Managed Money Net Percentile | 2W | -0.297 | 0.479 | 0.07% | 0.36% | 10-20 percentile | 60-70 percentile | weak |
| Managed Money Net Percentile | 4W | -0.139 | 0.467 | 0.07% | 0.99% | 10-20 percentile | 50-60 percentile | weak |
| Managed Money Net Percentile | 8W | -0.103 | 0.818 | -0.67% | 1.88% | 0-10 percentile | 80-90 percentile | weak |
| Producer / Merchant Net Percentile | 1W | 0.176 | -0.721 | 0.27% | -0.42% | 50-60 percentile | 10-20 percentile | weak |
| Producer / Merchant Net Percentile | 2W | 0.164 | -0.867 | 0.28% | -1.35% | 50-60 percentile | 30-40 percentile | weak |
| Producer / Merchant Net Percentile | 4W | 0.430 | -0.806 | 0.59% | -3.15% | 50-60 percentile | 10-20 percentile | weak |
| Producer / Merchant Net Percentile | 8W | 0.333 | -0.867 | -0.22% | -4.52% | 50-60 percentile | 10-20 percentile | weak |
| Swap Net Percentile | 1W | 0.697 | -0.200 | 0.43% | -0.01% | 40-50 percentile | 60-70 percentile | weak |
| Swap Net Percentile | 2W | 0.733 | -0.079 | 0.99% | -0.14% | 90-100 percentile | 20-30 percentile | weak |
| Swap Net Percentile | 4W | 0.879 | -0.309 | 1.82% | -0.27% | 90-100 percentile | 20-30 percentile | weak |
| Swap Net Percentile | 8W | 0.758 | -0.273 | 3.53% | -0.10% | 90-100 percentile | 20-30 percentile | weak |
| Total Open Interest Percentile | 1W | -0.152 | 0.152 | -0.14% | 0.51% | 50-60 percentile | 70-80 percentile | weak |
| Total Open Interest Percentile | 2W | -0.212 | 0.248 | -0.16% | 0.66% | 50-60 percentile | 80-90 percentile | weak |
| Total Open Interest Percentile | 4W | -0.224 | 0.382 | 0.14% | 1.42% | 60-70 percentile | 70-80 percentile | weak |
| Total Open Interest Percentile | 8W | 0.164 | 0.006 | 0.87% | 2.19% | 20-30 percentile | 10-20 percentile | pass |

## 7. 牛市 / 熊市 / 震盪 Regime 切分

| regime | factor | horizon | rank_corr | high_low_spread | best_bucket | best_avg | assessment |
|---|---|---:|---:|---:|---|---:|---|
| bear | Managed Money Net Percentile | 1W | -0.833 | NA | 0-10 percentile | 1.82% | 無：暫無穩定單因子預測力 |
| bear | Managed Money Net Percentile | 2W | -0.810 | NA | 0-10 percentile | 3.57% | 無：暫無穩定單因子預測力 |
| bear | Managed Money Net Percentile | 4W | -0.714 | NA | 10-20 percentile | 9.97% | 無：暫無穩定單因子預測力 |
| bear | Managed Money Net Percentile | 8W | -0.905 | NA | 0-10 percentile | 12.83% | 無：暫無穩定單因子預測力 |
| bear | Total Open Interest Percentile | 1W | -0.139 | -1.38% | 10-20 percentile | 5.26% | 無：暫無穩定單因子預測力 |
| bear | Total Open Interest Percentile | 2W | -0.321 | -4.71% | 10-20 percentile | 5.70% | 中：有可研究方向，但仍需樣本外驗證 |
| bear | Total Open Interest Percentile | 4W | -0.297 | -8.73% | 80-90 percentile | 10.82% | 無：暫無穩定單因子預測力 |
| bear | Total Open Interest Percentile | 8W | -0.648 | -11.40% | 10-20 percentile | 11.10% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bear | Producer / Merchant Net Percentile | 1W | 0.567 | NA | 90-100 percentile | 2.02% | 無：暫無穩定單因子預測力 |
| bear | Producer / Merchant Net Percentile | 2W | 0.567 | NA | 90-100 percentile | 3.82% | 無：暫無穩定單因子預測力 |
| bear | Producer / Merchant Net Percentile | 4W | 0.633 | NA | 80-90 percentile | 14.44% | 無：暫無穩定單因子預測力 |
| bear | Producer / Merchant Net Percentile | 8W | 0.583 | NA | 80-90 percentile | 21.14% | 無：暫無穩定單因子預測力 |
| bear | Swap Net Percentile | 1W | 0.830 | 4.40% | 90-100 percentile | 2.60% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bear | Swap Net Percentile | 2W | 0.782 | 9.55% | 80-90 percentile | 5.76% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bear | Swap Net Percentile | 4W | 0.891 | 17.45% | 90-100 percentile | 10.79% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bear | Swap Net Percentile | 8W | 0.927 | 31.65% | 90-100 percentile | 24.04% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bull | Managed Money Net Percentile | 1W | 0.394 | 0.04% | 60-70 percentile | 0.99% | 無：暫無穩定單因子預測力 |
| bull | Managed Money Net Percentile | 2W | 0.576 | 0.88% | 60-70 percentile | 1.89% | 中：有可研究方向，但仍需樣本外驗證 |
| bull | Managed Money Net Percentile | 4W | 0.564 | -0.02% | 60-70 percentile | 2.97% | 無：暫無穩定單因子預測力 |
| bull | Managed Money Net Percentile | 8W | 0.782 | 1.26% | 60-70 percentile | 5.26% | 強：bucket 報酬具明顯單調性與高低分位差 |
| bull | Total Open Interest Percentile | 1W | 0.079 | -0.00% | 80-90 percentile | 0.97% | 無：暫無穩定單因子預測力 |
| bull | Total Open Interest Percentile | 2W | 0.091 | 0.14% | 10-20 percentile | 1.83% | 無：暫無穩定單因子預測力 |
| bull | Total Open Interest Percentile | 4W | 0.224 | 0.38% | 10-20 percentile | 3.57% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| bull | Total Open Interest Percentile | 8W | -0.079 | 0.89% | 10-20 percentile | 8.01% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| bull | Producer / Merchant Net Percentile | 1W | -0.467 | 0.01% | 10-20 percentile | 0.98% | 無：暫無穩定單因子預測力 |
| bull | Producer / Merchant Net Percentile | 2W | -0.503 | -0.79% | 30-40 percentile | 1.71% | 中：有可研究方向，但仍需樣本外驗證 |
| bull | Producer / Merchant Net Percentile | 4W | -0.527 | -1.07% | 30-40 percentile | 2.72% | 中：有可研究方向，但仍需樣本外驗證 |
| bull | Producer / Merchant Net Percentile | 8W | -0.273 | -1.16% | 40-50 percentile | 6.28% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| bull | Swap Net Percentile | 1W | 0.006 | -0.05% | 40-50 percentile | 1.66% | 無：暫無穩定單因子預測力 |
| bull | Swap Net Percentile | 2W | 0.030 | -0.13% | 80-90 percentile | 2.02% | 無：暫無穩定單因子預測力 |
| bull | Swap Net Percentile | 4W | -0.127 | -0.48% | 20-30 percentile | 3.22% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| bull | Swap Net Percentile | 8W | -0.103 | -1.01% | 70-80 percentile | 6.89% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| range | Managed Money Net Percentile | 1W | -0.418 | -1.54% | 40-50 percentile | 3.26% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Managed Money Net Percentile | 2W | -0.491 | -2.16% | 20-30 percentile | 3.85% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Managed Money Net Percentile | 4W | -0.442 | -2.23% | 50-60 percentile | 5.33% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Managed Money Net Percentile | 8W | -0.030 | -1.98% | 70-80 percentile | 10.04% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| range | Total Open Interest Percentile | 1W | -0.564 | -5.63% | 0-10 percentile | 2.25% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Total Open Interest Percentile | 2W | -0.297 | -3.01% | 0-10 percentile | 4.52% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| range | Total Open Interest Percentile | 4W | -0.188 | -1.80% | 0-10 percentile | 9.14% | 無：暫無穩定單因子預測力 |
| range | Total Open Interest Percentile | 8W | 0.115 | 3.74% | 90-100 percentile | 11.86% | 無：暫無穩定單因子預測力 |
| range | Producer / Merchant Net Percentile | 1W | 0.406 | 0.67% | 50-60 percentile | 7.80% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Producer / Merchant Net Percentile | 2W | 0.382 | 0.93% | 50-60 percentile | 8.69% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Producer / Merchant Net Percentile | 4W | 0.515 | 2.00% | 50-60 percentile | 8.68% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Producer / Merchant Net Percentile | 8W | 0.479 | 2.01% | 60-70 percentile | 13.13% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Swap Net Percentile | 1W | 0.394 | 1.87% | 70-80 percentile | 3.69% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Swap Net Percentile | 2W | 0.188 | 3.00% | 70-80 percentile | 6.52% | 弱：有局部 bucket 現象，但方向不夠穩定 |
| range | Swap Net Percentile | 4W | 0.552 | 5.37% | 70-80 percentile | 7.56% | 中：有可研究方向，但仍需樣本外驗證 |
| range | Swap Net Percentile | 8W | 0.552 | 4.96% | 30-40 percentile | 17.98% | 中：有可研究方向，但仍需樣本外驗證 |

## 8. 明顯正報酬 percentile 區間

目前符合明顯正報酬規則的區間如下。

| factor | horizon | bucket | count | avg_forward_return | median_forward_return | win_rate |
|---|---:|---|---:|---:|---:|---:|
| Managed Money Net Percentile | 1W | 0-10 percentile | 166 | 0.13% | 0.18% | 55.42% |
| Managed Money Net Percentile | 1W | 10-20 percentile | 70 | 0.11% | 0.24% | 57.14% |
| Managed Money Net Percentile | 1W | 20-30 percentile | 83 | 0.44% | 0.46% | 59.04% |
| Managed Money Net Percentile | 1W | 50-60 percentile | 66 | 0.59% | 0.59% | 63.64% |
| Managed Money Net Percentile | 1W | 70-80 percentile | 46 | 0.46% | 0.72% | 60.87% |
| Managed Money Net Percentile | 2W | 10-20 percentile | 70 | 0.73% | 0.58% | 60.00% |
| Managed Money Net Percentile | 2W | 20-30 percentile | 83 | 0.43% | 0.74% | 60.24% |
| Managed Money Net Percentile | 2W | 50-60 percentile | 66 | 0.88% | 0.83% | 60.61% |
| Managed Money Net Percentile | 2W | 60-70 percentile | 65 | 0.91% | 0.35% | 61.54% |
| Managed Money Net Percentile | 4W | 0-10 percentile | 166 | 0.31% | 0.36% | 56.02% |
| Managed Money Net Percentile | 4W | 10-20 percentile | 70 | 1.47% | 1.88% | 62.86% |
| Managed Money Net Percentile | 4W | 50-60 percentile | 64 | 1.86% | 1.05% | 56.25% |
| Managed Money Net Percentile | 4W | 90-100 percentile | 110 | 1.19% | 1.04% | 63.64% |
| Managed Money Net Percentile | 8W | 50-60 percentile | 63 | 2.17% | 2.28% | 61.90% |
| Managed Money Net Percentile | 8W | 60-70 percentile | 62 | 2.50% | 1.12% | 62.90% |
| Managed Money Net Percentile | 8W | 70-80 percentile | 46 | 1.81% | 1.12% | 56.52% |
| Managed Money Net Percentile | 8W | 80-90 percentile | 59 | 2.00% | 1.67% | 59.32% |
| Managed Money Net Percentile | 8W | 90-100 percentile | 110 | 2.19% | 1.94% | 62.73% |
| Total Open Interest Percentile | 1W | 10-20 percentile | 74 | 0.65% | 0.78% | 64.86% |
| Total Open Interest Percentile | 1W | 40-50 percentile | 75 | 0.25% | 0.22% | 56.00% |
| Total Open Interest Percentile | 1W | 50-60 percentile | 54 | 0.41% | 0.42% | 61.11% |
| Total Open Interest Percentile | 1W | 80-90 percentile | 62 | 0.32% | 0.62% | 58.06% |
| Total Open Interest Percentile | 1W | 90-100 percentile | 98 | 0.15% | 0.25% | 56.12% |
| Total Open Interest Percentile | 2W | 10-20 percentile | 74 | 1.04% | 0.94% | 62.16% |
| Total Open Interest Percentile | 2W | 50-60 percentile | 54 | 0.64% | 0.31% | 57.41% |
| Total Open Interest Percentile | 2W | 70-80 percentile | 73 | 0.44% | 0.11% | 56.16% |
| Total Open Interest Percentile | 2W | 80-90 percentile | 62 | 0.74% | 0.54% | 58.06% |
| Total Open Interest Percentile | 4W | 10-20 percentile | 72 | 1.41% | 1.28% | 58.33% |
| Total Open Interest Percentile | 4W | 20-30 percentile | 75 | 1.29% | 1.18% | 60.00% |
| Total Open Interest Percentile | 4W | 30-40 percentile | 90 | 0.08% | 0.58% | 55.56% |
| Total Open Interest Percentile | 4W | 70-80 percentile | 73 | 0.97% | 0.56% | 56.16% |
| Total Open Interest Percentile | 4W | 90-100 percentile | 98 | 0.70% | 0.56% | 62.24% |
| Total Open Interest Percentile | 8W | 10-20 percentile | 69 | 2.63% | 2.48% | 68.12% |
| Total Open Interest Percentile | 8W | 20-30 percentile | 74 | 2.98% | 0.89% | 56.76% |
| Total Open Interest Percentile | 8W | 50-60 percentile | 54 | 1.89% | 1.85% | 62.96% |
| Total Open Interest Percentile | 8W | 70-80 percentile | 73 | 2.21% | 1.38% | 60.27% |
| Total Open Interest Percentile | 8W | 80-90 percentile | 62 | 0.43% | 0.47% | 56.45% |
| Total Open Interest Percentile | 8W | 90-100 percentile | 98 | 1.67% | 2.03% | 57.14% |
| Producer / Merchant Net Percentile | 1W | 10-20 percentile | 62 | 0.35% | 0.50% | 59.68% |
| Producer / Merchant Net Percentile | 1W | 20-30 percentile | 56 | 0.39% | 0.61% | 55.36% |
| Producer / Merchant Net Percentile | 1W | 30-40 percentile | 75 | 0.49% | 0.40% | 64.00% |
| Producer / Merchant Net Percentile | 1W | 40-50 percentile | 69 | 0.06% | 0.22% | 59.42% |
| Producer / Merchant Net Percentile | 1W | 50-60 percentile | 67 | 0.44% | 0.48% | 58.21% |
| Producer / Merchant Net Percentile | 1W | 60-70 percentile | 87 | 0.33% | 0.26% | 57.47% |
| Producer / Merchant Net Percentile | 1W | 80-90 percentile | 99 | 0.07% | 0.20% | 57.58% |
| Producer / Merchant Net Percentile | 2W | 10-20 percentile | 62 | 0.43% | 0.35% | 61.29% |
| Producer / Merchant Net Percentile | 2W | 20-30 percentile | 56 | 0.64% | 0.66% | 57.14% |
| Producer / Merchant Net Percentile | 2W | 30-40 percentile | 75 | 1.30% | 0.83% | 62.67% |
| Producer / Merchant Net Percentile | 2W | 50-60 percentile | 67 | 0.69% | 0.36% | 61.19% |
| Producer / Merchant Net Percentile | 2W | 70-80 percentile | 63 | 0.32% | 0.26% | 55.56% |
| Producer / Merchant Net Percentile | 4W | 10-20 percentile | 62 | 0.97% | 1.09% | 61.29% |
| Producer / Merchant Net Percentile | 4W | 30-40 percentile | 75 | 2.06% | 2.25% | 62.67% |
| Producer / Merchant Net Percentile | 4W | 40-50 percentile | 69 | 0.85% | 0.48% | 56.52% |
| Producer / Merchant Net Percentile | 4W | 50-60 percentile | 67 | 1.51% | 0.15% | 58.21% |
| Producer / Merchant Net Percentile | 4W | 60-70 percentile | 87 | 0.84% | 0.78% | 56.32% |
| Producer / Merchant Net Percentile | 8W | 10-20 percentile | 62 | 1.21% | 1.30% | 61.29% |
| Producer / Merchant Net Percentile | 8W | 20-30 percentile | 56 | 2.85% | 2.18% | 62.50% |
| Producer / Merchant Net Percentile | 8W | 30-40 percentile | 75 | 2.60% | 2.61% | 57.33% |
| Producer / Merchant Net Percentile | 8W | 40-50 percentile | 69 | 1.81% | 0.81% | 55.07% |
| Producer / Merchant Net Percentile | 8W | 50-60 percentile | 67 | 2.78% | 2.16% | 58.21% |
| Producer / Merchant Net Percentile | 8W | 60-70 percentile | 87 | 2.02% | 2.61% | 56.32% |
| Producer / Merchant Net Percentile | 8W | 80-90 percentile | 97 | 1.58% | 1.06% | 58.76% |
| Swap Net Percentile | 1W | 0-10 percentile | 151 | 0.20% | 0.32% | 55.63% |
| Swap Net Percentile | 1W | 20-30 percentile | 73 | 0.22% | 0.58% | 56.16% |
| Swap Net Percentile | 1W | 40-50 percentile | 58 | 0.23% | 0.36% | 56.90% |
| Swap Net Percentile | 1W | 60-70 percentile | 79 | 0.48% | 0.30% | 59.49% |
| Swap Net Percentile | 1W | 70-80 percentile | 57 | 0.14% | 0.41% | 59.65% |
| Swap Net Percentile | 1W | 90-100 percentile | 113 | 0.33% | 0.25% | 60.18% |
| Swap Net Percentile | 2W | 20-30 percentile | 73 | 0.89% | 0.78% | 56.16% |
| Swap Net Percentile | 2W | 50-60 percentile | 93 | 0.15% | 0.36% | 56.99% |
| Swap Net Percentile | 2W | 60-70 percentile | 79 | 0.67% | 0.58% | 62.03% |
| Swap Net Percentile | 2W | 90-100 percentile | 113 | 0.60% | 0.62% | 61.95% |
| Swap Net Percentile | 4W | 80-90 percentile | 67 | 1.10% | 0.44% | 56.72% |
| Swap Net Percentile | 4W | 90-100 percentile | 113 | 1.12% | 1.64% | 68.14% |
| Swap Net Percentile | 8W | 0-10 percentile | 150 | 1.51% | 1.31% | 56.00% |
| Swap Net Percentile | 8W | 20-30 percentile | 72 | 3.08% | 1.74% | 56.94% |
| Swap Net Percentile | 8W | 70-80 percentile | 57 | 0.93% | 0.30% | 56.14% |
| Swap Net Percentile | 8W | 90-100 percentile | 113 | 2.92% | 2.38% | 64.60% |

## 9. 明顯負報酬 percentile 區間

目前符合明顯負報酬規則的區間如下。

| factor | horizon | bucket | count | avg_forward_return | median_forward_return | win_rate |
|---|---:|---|---:|---:|---:|---:|
| Managed Money Net Percentile | 1W | 40-50 percentile | 97 | -0.31% | -0.27% | 44.33% |

## 10. 目前沒有參考價值的因子

- Swap Net Percentile：目前沒有穩定單因子參考價值。最大 |rank_corr|=0.188，最大 |90-100 vs 0-10 spread|=1.42%。
- Total Open Interest Percentile：目前沒有穩定單因子參考價值。最大 |rank_corr|=0.200，最大 |90-100 vs 0-10 spread|=1.35%。

## 11. 是否建議進入 v0.2 綜合指數階段

- 建議進入 v0.2 綜合指數的研究階段，但只做 research prototype，不建議直接交易化。
- v0.2 初版候選因子：Managed Money Net Percentile, Producer / Merchant Net Percentile。
- 暫不納入或僅作觀察因子：Swap Net Percentile, Total Open Interest Percentile。
- v0.2 應加入樣本外驗證、走勢 regime 切分、訊號冷卻期與風險調整後報酬，再決定是否形成綜合指數。

## 判定規則

- 明顯正報酬 bucket：count >= 30，avg_forward_return > 0，median_forward_return > 0，win_rate >= 55%。
- 明顯負報酬 bucket：count >= 30，avg_forward_return < 0，median_forward_return < 0，win_rate <= 45%。
- rank_corr：percentile bucket midpoint 與 avg_forward_return 的 Spearman 相關。
- high_low_spread：90-100 percentile bucket 平均 forward return 減 0-10 percentile bucket 平均 forward return。
- 預測力分級只代表 v0.1 單因子歷史研究結果，不代表交易訊號。

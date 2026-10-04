# GHPR v0.3 Historical Similarity Engine

Historical Statistics / Research Reference.

This engine compares the latest GHPR weekly state with past weekly states. It does not connect to TradeDock, does not place orders, and does not produce trading instructions.

Hard scope limits: no TradeDock connection, no automated order placement, no trading recommendations, no Options / OGR / MMP inputs, no AI / ML, and no optimized weights.

Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile. Future candidates include MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.

## Current State

- Latest date: `2026-09-29`
- Latest gold_close: `4,179.70`
- Master rows: `892`
- Historical candidates after recent-row exclusion: `840`
- Complete feature candidates: `789`
- Dropped incomplete candidates: `51`
- Excluded latest rows: `52`

## Similarity Method

Version 0.3 uses a simple percentile-distance score. It does not use AI, machine learning, parameter fitting, or optimized weights.

Distance uses only three fields: `mm_net_percentile_156w`, `producer_net_percentile_156w`, and `oi_percentile_156w`.

`distance = abs(current_mm - historical_mm) + abs(current_producer - historical_producer) + abs(current_oi - historical_oi)`

`normalized_distance = distance / 300 * 100`

`similarity_score = 100 - normalized_distance`

The engine converts dataset percentiles to 0-100 percentile points before scoring. Higher score means a closer historical match.

## Current Feature Vector

| date       | feature                      | current_value   | candidate_mean   | candidate_std   |
|:-----------|:-----------------------------|:----------------|:-----------------|:----------------|
| 2026-09-29 | mm_net_percentile_156w       | 38.46%          | 45.22%           | 32.73%          |
| 2026-09-29 | producer_net_percentile_156w | 83.97%          | 56.49%           | 31.40%          |
| 2026-09-29 | oi_percentile_156w           | 15.38%          | 47.55%           | 31.29%          |

## Top Historical Matches

|   rank | date       |   gold_close |   similarity_score |   distance |   normalized_distance | mm_net_percentile_156w   | producer_net_percentile_156w   | oi_percentile_156w   | gold_return_1w   | gold_return_2w   | gold_return_4w   | gold_return_8w   | forward_return_1w   | forward_return_2w   | forward_return_4w   | forward_return_8w   |
|-------:|:-----------|-------------:|-------------------:|-----------:|----------------------:|:-------------------------|:-------------------------------|:---------------------|:-----------------|:-----------------|:-----------------|:-----------------|:--------------------|:--------------------|:--------------------|:--------------------|
|      1 | 2021-07-06 |       1794.2 |            98.9316 |     3.2051 |                1.0684 | 37.82%                   | 82.05%                         | 14.74%               | 1.74%            | 0.95%            | -5.29%           | -2.28%           | 0.88%               | 0.96%               | 1.11%               | 1.33%               |
|      2 | 2023-03-14 |       1910.9 |            98.2906 |     5.1282 |                1.7094 | 35.90%                   | 85.90%                         | 14.74%               | 4.99%            | 4.04%            | 2.44%            | 0.05%            | 1.58%               | 3.28%               | 5.66%               | 6.91%               |
|      3 | 2014-04-29 |       1296   |            97.0085 |     8.9744 |                2.9915 | 39.10%                   | 82.69%                         | 8.33%                | 1.20%            | -0.31%           | 1.28%            | -3.12%           | 0.95%               | -0.11%              | -2.36%              | 1.92%               |
|      4 | 2014-04-22 |       1280.6 |            95.9402 |    12.1795 |                4.0598 | 38.46%                   | 83.33%                         | 3.85%                | -1.49%           | -2.15%           | -2.35%           | -4.65%           | 1.20%               | 2.16%               | 1.09%               | -0.69%              |
|      5 | 2021-06-22 |       1777.4 |            95.7265 |    12.8205 |                4.2735 | 35.90%                   | 87.82%                         | 8.97%                | -4.26%           | -6.18%           | -6.35%           | -0.08%           | -0.78%              | 0.95%               | 1.91%               | 0.59%               |
|      6 | 2021-05-04 |       1776   |            95.7265 |    12.8205 |                4.2735 | 36.54%                   | 76.92%                         | 19.23%               | -0.16%           | -0.13%           | 1.89%            | 3.44%            | 3.38%               | 5.18%               | 7.26%               | -0.70%              |
|      7 | 2014-02-18 |       1324.7 |            95.5128 |    13.4615 |                4.4872 | 32.69%                   | 78.21%                         | 17.31%               | 2.68%            | 5.83%            | 6.63%            | 9.92%            | 1.38%               | 0.99%               | 2.59%               | -1.86%              |
|      8 | 2021-06-29 |       1763.6 |            95.2991 |    14.1026 |                4.7009 | 35.26%                   | 88.46%                         | 8.97%                | -0.78%           | -5.00%           | -7.42%           | -0.70%           | 1.74%               | 2.63%               | 2.05%               | 2.55%               |
|      9 | 2018-12-24 |       1267.5 |            95.0855 |    14.7436 |                4.9145 | 26.28%                   | 83.33%                         | 17.31%               | 1.46%            | 2.06%            | 4.65%            | 3.67%            | 0.85%               | 1.24%               | 1.18%               | 5.73%               |
|     10 | 2014-04-15 |       1300   |            94.4444 |    16.6667 |                5.5556 | 35.90%                   | 85.26%                         | 2.56%                | -0.66%           | 1.59%            | -4.34%           | -1.86%           | -1.49%              | -0.31%              | -0.42%              | -3.09%              |
|     11 | 2013-10-29 |       1345.2 |            94.4444 |    16.6667 |                5.5556 | 33.33%                   | 87.82%                         | 7.69%                | 0.20%            | 5.67%            | 4.60%            | -4.73%           | -2.77%              | -5.51%              | -7.72%              | -10.41%             |
|     12 | 2021-04-13 |       1747.6 |            93.5897 |    19.2308 |                6.4103 | 37.18%                   | 68.59%                         | 12.82%               | 0.26%            | 3.78%            | 0.96%            | -2.86%           | 1.76%               | 1.79%               | 5.06%               | 8.40%               |
|     13 | 2021-04-06 |       1743   |            93.5897 |    19.2308 |                6.4103 | 39.10%                   | 67.95%                         | 12.82%               | 3.51%            | 1.04%            | 1.52%            | -5.14%           | 0.26%               | 2.03%               | 1.89%               | 9.29%               |
|     14 | 2019-04-09 |       1303.5 |            93.5897 |    19.2308 |                6.4103 | 26.92%                   | 89.10%                         | 17.95%               | 1.05%            | -0.82%           | 0.56%            | -0.44%           | -2.37%              | -2.62%              | -1.53%              | 1.53%               |
|     15 | 2021-03-30 |       1683.9 |            93.3761 |    19.8718 |                6.6239 | 32.69%                   | 71.15%                         | 14.10%               | -2.39%           | -2.72%           | -2.87%           | -8.15%           | 3.51%               | 3.78%               | 5.64%               | 12.71%              |
|     16 | 2014-02-25 |       1343   |            93.3761 |    19.8718 |                6.6239 | 48.08%                   | 74.36%                         | 14.74%               | 1.38%            | 4.10%            | 7.35%            | 11.74%           | -0.39%              | 0.26%               | -2.35%              | -4.65%              |
|     17 | 2021-04-27 |       1778.8 |            93.3761 |    19.8718 |                6.6239 | 35.26%                   | 73.08%                         | 21.15%               | 0.02%            | 1.79%            | 5.64%            | 2.61%            | -0.16%              | 3.22%               | 6.70%               | -0.08%              |
|     18 | 2013-11-05 |       1308   |            93.3761 |    19.8718 |                6.6239 | 28.85%                   | 86.54%                         | 7.69%                | -2.77%           | -2.57%           | -1.22%           | -4.11%           | -2.82%              | -2.65%              | -6.60%              | -8.11%              |
|     19 | 2023-09-19 |       1953.7 |            93.3761 |    19.8718 |                6.6239 | 28.85%                   | 90.38%                         | 11.54%               | 0.96%            | 0.06%            | 1.44%            | -0.51%           | -1.74%              | -5.74%              | -0.92%              | 0.66%               |
|     20 | 2021-04-20 |       1778.4 |            92.9487 |    21.1538 |                7.0513 | 39.10%                   | 67.95%                         | 19.87%               | 1.76%            | 2.03%            | 3.09%            | -1.52%           | 0.02%               | -0.13%              | 5.04%               | 4.39%               |

## Similar Case Forward Return Summary

| horizon   |   similar_case_count | avg_forward_return   | median_forward_return   | win_rate   | worst_forward_return   | best_forward_return   |
|:----------|---------------------:|:---------------------|:------------------------|:-----------|:-----------------------|:----------------------|
| 1W        |                   20 | 0.25%                | 0.56%                   | 60.00%     | -2.82%                 | 3.51%                 |
| 2W        |                   20 | 0.57%                | 0.97%                   | 65.00%     | -5.74%                 | 5.18%                 |
| 4W        |                   20 | 1.26%                | 1.54%                   | 65.00%     | -7.72%                 | 7.26%                 |
| 8W        |                   20 | 1.32%                | 0.99%                   | 60.00%     | -10.41%                | 12.71%                |

## Output Files

- `outputs\reports\hse_current_similarity.csv`
- `outputs\reports\hse_current_feature_vector.csv`
- `outputs\reports\hse_current_similarity_summary.csv`
- `outputs\reports\historical_similarity_report.csv`
- `outputs\reports\historical_similarity_stats.csv`
- `outputs\reports\historical_similarity_summary.md`
- `outputs\charts\historical_similarity_cases.png`

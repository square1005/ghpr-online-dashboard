# GHPR v0.3 Historical Similarity Engine

Historical Statistics / Research Reference.

This engine compares the latest GHPR weekly state with past weekly states. It does not connect to TradeDock, does not place orders, and does not produce trading instructions.

Hard scope limits: no TradeDock connection, no automated order placement, no trading recommendations, no Options / OGR / MMP inputs, no AI / ML, and no optimized weights.

Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile. Future candidates include MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.

## Current State

- Latest date: `2026-10-06`
- Latest gold_close: `4,187.10`
- Master rows: `893`
- Historical candidates after recent-row exclusion: `841`
- Complete feature candidates: `790`
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
| 2026-10-06 | mm_net_percentile_156w       | 32.69%          | 45.24%           | 32.71%          |
| 2026-10-06 | producer_net_percentile_156w | 91.67%          | 56.44%           | 31.41%          |
| 2026-10-06 | oi_percentile_156w           | 12.82%          | 47.56%           | 31.27%          |

## Top Historical Matches

|   rank | date       |   gold_close |   similarity_score |   distance |   normalized_distance | mm_net_percentile_156w   | producer_net_percentile_156w   | oi_percentile_156w   | gold_return_1w   | gold_return_2w   | gold_return_4w   | gold_return_8w   | forward_return_1w   | forward_return_2w   | forward_return_4w   | forward_return_8w   |
|-------:|:-----------|-------------:|-------------------:|-----------:|----------------------:|:-------------------------|:-------------------------------|:---------------------|:-----------------|:-----------------|:-----------------|:-----------------|:--------------------|:--------------------|:--------------------|:--------------------|
|      1 | 2023-09-05 |       1952.6 |            98.0769 |     5.7692 |                1.9231 | 29.49%                   | 92.95%                         | 11.54%               | -0.64%           | 1.38%            | -0.37%           | 0.80%            | -0.90%              | 0.06%               | -5.69%              | 2.14%               |
|      2 | 2023-09-19 |       1953.7 |            97.8632 |     6.4103 |                2.1368 | 28.85%                   | 90.38%                         | 11.54%               | 0.96%            | 0.06%            | 1.44%            | -0.51%           | -1.74%              | -5.74%              | -0.92%              | 0.66%               |
|      3 | 2023-02-07 |       1884.8 |            97.2222 |     8.3333 |                2.7778 | 32.69%                   | 91.03%                         | 5.13%                | -2.32%           | -2.61%           | 0.44%            | 3.25%            | -1.03%              | -2.24%              | -3.44%              | 8.14%               |
|      4 | 2013-10-29 |       1345.2 |            96.7949 |     9.6154 |                3.2051 | 33.33%                   | 87.82%                         | 7.69%                | 0.20%            | 5.67%            | 4.60%            | -4.73%           | -2.77%              | -5.51%              | -7.72%              | -10.41%             |
|      5 | 2021-06-29 |       1763.6 |            96.7949 |     9.6154 |                3.2051 | 35.26%                   | 88.46%                         | 8.97%                | -0.78%           | -5.00%           | -7.42%           | -0.70%           | 1.74%               | 2.63%               | 2.05%               | 2.55%               |
|      6 | 2021-06-22 |       1777.4 |            96.3675 |    10.8974 |                3.6325 | 35.90%                   | 87.82%                         | 8.97%                | -4.26%           | -6.18%           | -6.35%           | -0.08%           | -0.78%              | 0.95%               | 1.91%               | 0.59%               |
|      7 | 2023-03-14 |       1910.9 |            96.3675 |    10.8974 |                3.6325 | 35.90%                   | 85.90%                         | 14.74%               | 4.99%            | 4.04%            | 2.44%            | 0.05%            | 1.58%               | 3.28%               | 5.66%               | 6.91%               |
|      8 | 2023-08-08 |       1959.9 |            96.1538 |    11.5385 |                3.8462 | 34.62%                   | 91.67%                         | 3.21%                | -0.96%           | -0.19%           | 1.18%            | 0.07%            | -1.26%              | -1.73%              | -0.37%              | -6.04%              |
|      9 | 2019-04-02 |       1290   |            95.5128 |    13.4615 |                4.4872 | 21.15%                   | 89.74%                         | 12.82%               | -1.85%           | -1.15%           | 0.62%            | -1.84%           | 1.05%               | -1.35%              | -0.56%              | -1.05%              |
|     10 | 2019-04-09 |       1303.5 |            95.5128 |    13.4615 |                4.4872 | 26.92%                   | 89.10%                         | 17.95%               | 1.05%            | -0.82%           | 0.56%            | -0.44%           | -2.37%              | -2.62%              | -1.53%              | 1.53%               |
|     11 | 2013-11-05 |       1308   |            95.2991 |    14.1026 |                4.7009 | 28.85%                   | 86.54%                         | 7.69%                | -2.77%           | -2.57%           | -1.22%           | -4.11%           | -2.82%              | -2.65%              | -6.60%              | -8.11%              |
|     12 | 2023-08-29 |       1965.1 |            95.2991 |    14.1026 |                4.7009 | 22.44%                   | 94.87%                         | 13.46%               | 2.03%            | 1.55%            | -0.69%           | 1.85%            | -0.64%              | -1.53%              | -2.31%              | 1.07%               |
|     13 | 2013-10-22 |       1342.5 |            94.4444 |    16.6667 |                5.5556 | 21.79%                   | 89.10%                         | 9.62%                | 5.46%            | 1.38%            | 2.01%            | -5.50%           | 0.20%               | -2.57%              | -5.15%              | -8.29%              |
|     14 | 2021-07-06 |       1794.2 |            94.4444 |    16.6667 |                5.5556 | 37.82%                   | 82.05%                         | 14.74%               | 1.74%            | 0.95%            | -5.29%           | -2.28%           | 0.88%               | 0.96%               | 1.11%               | 1.33%               |
|     15 | 2014-02-18 |       1324.7 |            94.0171 |    17.9487 |                5.9829 | 32.69%                   | 78.21%                         | 17.31%               | 2.68%            | 5.83%            | 6.63%            | 9.92%            | 1.38%               | 0.99%               | 2.59%               | -1.86%              |
|     16 | 2023-09-12 |       1935.1 |            94.0171 |    17.9487 |                5.9829 | 17.95%                   | 93.59%                         | 14.10%               | -0.90%           | -1.53%           | -0.01%           | -2.31%           | 0.96%               | -0.79%              | -3.09%              | 1.98%               |
|     17 | 2019-04-30 |       1282.8 |            93.8034 |    18.5897 |                6.1966 | 17.95%                   | 90.38%                         | 10.26%               | 1.06%            | 0.80%            | -0.56%           | 0.06%            | 0.05%               | 0.93%               | -0.49%              | 10.30%              |
|     18 | 2013-09-03 |       1412   |            93.5897 |    19.2308 |                6.4103 | 22.44%                   | 92.95%                         | 5.13%                | -0.61%           | 2.83%            | 10.04%           | 13.33%           | -3.39%              | -7.26%              | -8.92%              | -4.73%              |
|     19 | 2018-12-24 |       1267.5 |            93.5897 |    19.2308 |                6.4103 | 26.28%                   | 83.33%                         | 17.31%               | 1.46%            | 2.06%            | 4.65%            | 3.67%            | 0.85%               | 1.24%               | 1.18%               | 5.73%               |
|     20 | 2014-02-11 |       1290.1 |            93.3761 |    19.8718 |                6.6239 | 21.79%                   | 91.67%                         | 3.85%                | 3.07%            | 3.13%            | 3.61%            | 4.78%            | 2.68%               | 4.10%               | 4.37%               | 1.44%               |

## Similar Case Forward Return Summary

| horizon   |   similar_case_count | avg_forward_return   | median_forward_return   | win_rate   | worst_forward_return   | best_forward_return   |
|:----------|---------------------:|:---------------------|:------------------------|:-----------|:-----------------------|:----------------------|
| 1W        |                   20 | -0.32%               | -0.29%                  | 50.00%     | -3.39%                 | 2.68%                 |
| 2W        |                   20 | -0.94%               | -1.07%                  | 45.00%     | -7.26%                 | 4.10%                 |
| 4W        |                   20 | -1.40%               | -0.74%                  | 35.00%     | -8.92%                 | 5.66%                 |
| 8W        |                   20 | 0.19%                | 1.20%                   | 65.00%     | -10.41%                | 10.30%                |

## Output Files

- `outputs\reports\hse_current_similarity.csv`
- `outputs\reports\hse_current_feature_vector.csv`
- `outputs\reports\hse_current_similarity_summary.csv`
- `outputs\reports\historical_similarity_report.csv`
- `outputs\reports\historical_similarity_stats.csv`
- `outputs\reports\historical_similarity_summary.md`
- `outputs\charts\historical_similarity_cases.png`

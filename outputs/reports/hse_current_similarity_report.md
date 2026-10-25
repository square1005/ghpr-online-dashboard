# GHPR v0.3 Historical Similarity Engine

Historical Statistics / Research Reference.

This engine compares the latest GHPR weekly state with past weekly states. It does not connect to TradeDock, does not place orders, and does not produce trading instructions.

Hard scope limits: no TradeDock connection, no automated order placement, no trading recommendations, no Options / OGR / MMP inputs, no AI / ML, and no optimized weights.

Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile. Future candidates include MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.

## Current State

- Latest date: `2026-10-20`
- Latest gold_close: `4,142.60`
- Master rows: `895`
- Historical candidates after recent-row exclusion: `843`
- Complete feature candidates: `792`
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
| 2026-10-20 | mm_net_percentile_156w       | 24.36%          | 45.22%           | 32.67%          |
| 2026-10-20 | producer_net_percentile_156w | 99.36%          | 56.35%           | 31.42%          |
| 2026-10-20 | oi_percentile_156w           | 14.74%          | 47.58%           | 31.23%          |

## Top Historical Matches

|   rank | date       |   gold_close |   similarity_score |   distance |   normalized_distance | mm_net_percentile_156w   | producer_net_percentile_156w   | oi_percentile_156w   | gold_return_1w   | gold_return_2w   | gold_return_4w   | gold_return_8w   | forward_return_1w   | forward_return_2w   | forward_return_4w   | forward_return_8w   |
|-------:|:-----------|-------------:|-------------------:|-----------:|----------------------:|:-------------------------|:-------------------------------|:---------------------|:-----------------|:-----------------|:-----------------|:-----------------|:--------------------|:--------------------|:--------------------|:--------------------|
|      1 | 2023-08-29 |       1965.1 |            97.4359 |     7.6923 |                2.5641 | 22.44%                   | 94.87%                         | 13.46%               | 2.03%            | 1.55%            | -0.69%           | 1.85%            | -0.64%              | -1.53%              | -2.31%              | 1.07%               |
|      2 | 2011-02-15 |       1373.6 |            96.1427 |    11.5718 |                3.8573 | 15.58%                   | 97.40%                         | 15.58%               | 0.75%            | 2.54%            | 0.40%            | -1.05%           | 1.96%               | 4.16%               | 1.38%               | 5.77%               |
|      3 | 2023-09-12 |       1935.1 |            95.7265 |    12.8205 |                4.2735 | 17.95%                   | 93.59%                         | 14.10%               | -0.90%           | -1.53%           | -0.01%           | -2.31%           | 0.96%               | -0.79%              | -3.09%              | 1.98%               |
|      4 | 2019-04-23 |       1269.3 |            95.5128 |    13.4615 |                4.4872 | 12.82%                   | 99.36%                         | 12.82%               | -0.26%           | -2.62%           | -3.42%           | -4.21%           | 1.06%               | 1.12%               | 0.21%               | 6.09%               |
|      5 | 2019-04-02 |       1290   |            95.0855 |    14.7436 |                4.9145 | 21.15%                   | 89.74%                         | 12.82%               | -1.85%           | -1.15%           | 0.62%            | -1.84%           | 1.05%               | -1.35%              | -0.56%              | -1.05%              |
|      6 | 2023-09-05 |       1952.6 |            95.0855 |    14.7436 |                4.9145 | 29.49%                   | 92.95%                         | 11.54%               | -0.64%           | 1.38%            | -0.37%           | 0.80%            | -0.90%              | 0.06%               | -5.69%              | 2.14%               |
|      7 | 2021-10-05 |       1760.9 |            94.8718 |    15.3846 |                5.1282 | 26.92%                   | 97.44%                         | 25.64%               | 1.35%            | -0.97%           | -2.09%           | 1.69%            | -0.09%              | 0.55%               | 1.62%               | 0.72%               |
|      8 | 2019-04-09 |       1303.5 |            94.6581 |    16.0256 |                5.3419 | 26.92%                   | 89.10%                         | 17.95%               | 1.05%            | -0.82%           | 0.56%            | -0.44%           | -2.37%              | -2.62%              | -1.53%              | 1.53%               |
|      9 | 2023-09-19 |       1953.7 |            94.4444 |    16.6667 |                5.5556 | 28.85%                   | 90.38%                         | 11.54%               | 0.96%            | 0.06%            | 1.44%            | -0.51%           | -1.74%              | -5.74%              | -0.92%              | 0.66%               |
|     10 | 2013-09-03 |       1412   |            94.0171 |    17.9487 |                5.9829 | 22.44%                   | 92.95%                         | 5.13%                | -0.61%           | 2.83%            | 10.04%           | 13.33%           | -3.39%              | -7.26%              | -8.92%              | -4.73%              |
|     11 | 2013-10-22 |       1342.5 |            94.0171 |    17.9487 |                5.9829 | 21.79%                   | 89.10%                         | 9.62%                | 5.46%            | 1.38%            | 2.01%            | -5.50%           | 0.20%               | -2.57%              | -5.15%              | -8.29%              |
|     12 | 2019-04-16 |       1272.6 |            93.8034 |    18.5897 |                6.1966 | 13.46%                   | 92.95%                         | 13.46%               | -2.37%           | -1.35%           | -2.48%           | -5.04%           | -0.26%              | 0.80%               | 1.74%               | 4.23%               |
|     13 | 2011-02-08 |       1363.4 |            93.7584 |    18.7247 |                6.2416 | 6.58%                    | 98.68%                         | 14.47%               | 1.78%            | 2.33%            | -1.49%           | -2.86%           | 0.75%               | 2.72%               | 4.66%               | 6.48%               |
|     14 | 2011-07-05 |       1512.3 |            93.5721 |    19.2836 |                6.4279 | 19.59%                   | 86.60%                         | 16.49%               | 0.84%            | -2.18%           | -2.01%           | -0.28%           | 3.28%               | 5.86%               | 8.57%               | 20.79%              |
|     15 | 2019-04-30 |       1282.8 |            93.3761 |    19.8718 |                6.6239 | 17.95%                   | 90.38%                         | 10.26%               | 1.06%            | 0.80%            | -0.56%           | 0.06%            | 0.05%               | 0.93%               | -0.49%              | 10.30%              |
|     16 | 2021-08-10 |       1731.7 |            93.3761 |    19.8718 |                6.6239 | 21.79%                   | 91.67%                         | 24.36%               | -4.54%           | -3.78%           | -4.32%           | -6.72%           | 3.24%               | 4.43%               | 3.86%               | 1.69%               |
|     17 | 2021-10-12 |       1759.3 |            93.3761 |    19.8718 |                6.6239 | 28.21%                   | 94.23%                         | 25.64%               | -0.09%           | 1.25%            | -2.65%           | -1.59%           | 0.64%               | 1.94%               | 4.06%               | 1.44%               |
|     18 | 2013-10-01 |       1286   |            93.1624 |    20.5128 |                6.8376 | 17.95%                   | 98.08%                         | 1.92%                | -2.28%           | -1.79%           | -8.92%           | 0.22%            | 2.97%               | -1.01%              | 4.60%               | -3.47%              |
|     19 | 2018-12-24 |       1267.5 |            93.1624 |    20.5128 |                6.8376 | 26.28%                   | 83.33%                         | 17.31%               | 1.46%            | 2.06%            | 4.65%            | 3.67%            | 0.85%               | 1.24%               | 1.18%               | 5.73%               |
|     20 | 2013-04-30 |       1472.2 |            92.9487 |    21.1538 |                7.0513 | 4.49%                    | 100.00%                        | 15.38%               | 4.52%            | 6.16%            | -6.53%           | -6.50%           | -1.58%              | -3.23%              | -6.32%              | -13.41%             |

## Similar Case Forward Return Summary

| horizon   |   similar_case_count | avg_forward_return   | median_forward_return   | win_rate   | worst_forward_return   | best_forward_return   |
|:----------|---------------------:|:---------------------|:------------------------|:-----------|:-----------------------|:----------------------|
| 1W        |                   20 | 0.30%                | 0.42%                   | 60.00%     | -3.39%                 | 3.28%                 |
| 2W        |                   20 | -0.12%               | 0.30%                   | 55.00%     | -7.26%                 | 5.86%                 |
| 4W        |                   20 | -0.15%               | -0.14%                  | 50.00%     | -8.92%                 | 8.57%                 |
| 8W        |                   20 | 1.98%                | 1.61%                   | 75.00%     | -13.41%                | 20.79%                |

## Output Files

- `outputs\reports\hse_current_similarity.csv`
- `outputs\reports\hse_current_feature_vector.csv`
- `outputs\reports\hse_current_similarity_summary.csv`
- `outputs\reports\historical_similarity_report.csv`
- `outputs\reports\historical_similarity_stats.csv`
- `outputs\reports\historical_similarity_summary.md`
- `outputs\charts\historical_similarity_cases.png`

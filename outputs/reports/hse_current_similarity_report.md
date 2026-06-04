# GHPR v0.3 Historical Similarity Engine

Historical Statistics / Research Reference.

This engine compares the latest GHPR weekly state with past weekly states. It does not connect to TradeDock, does not place orders, and does not produce trading instructions.

Hard scope limits: no TradeDock connection, no automated order placement, no trading recommendations, no Options / OGR / MMP inputs, no AI / ML, and no optimized weights.

Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile. Future candidates include MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.

## Current State

- Latest date: `2026-05-26`
- Latest gold_close: `4,500.40`
- Master rows: `874`
- Historical candidates after recent-row exclusion: `866`
- Complete feature candidates: `815`
- Dropped incomplete candidates: `51`
- Excluded latest rows: `8`

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
| 2026-05-26 | mm_net_percentile_156w       | 30.13%          | 45.06%           | 32.30%          |
| 2026-05-26 | producer_net_percentile_156w | 94.87%          | 56.50%           | 31.39%          |
| 2026-05-26 | oi_percentile_156w           | 0.64%           | 47.06%           | 31.32%          |

## Top Historical Matches

|   rank | date       |   gold_close |   similarity_score |   distance |   normalized_distance | mm_net_percentile_156w   | producer_net_percentile_156w   | oi_percentile_156w   | gold_return_1w   | gold_return_2w   | gold_return_4w   | gold_return_8w   | forward_return_1w   | forward_return_2w   | forward_return_4w   | forward_return_8w   |
|-------:|:-----------|-------------:|-------------------:|-----------:|----------------------:|:-------------------------|:-------------------------------|:---------------------|:-----------------|:-----------------|:-----------------|:-----------------|:--------------------|:--------------------|:--------------------|:--------------------|
|      1 | 2026-02-17 |       4882.9 |            97.8632 |     6.4103 |                2.1368 | 27.56%                   | 97.44%                         | 1.92%                | -2.42%           | -0.42%           | 2.59%            | 8.93%            | 5.59%               | 4.60%               | 2.42%               | -1.19%              |
|      2 | 2026-03-03 |       5107.4 |            97.6496 |     7.0513 |                2.3504 | 27.56%                   | 96.79%                         | 3.21%                | -0.94%           | 4.60%            | 4.15%            | 13.95%           | 2.39%               | -2.08%              | -9.00%              | -10.10%             |
|      3 | 2026-02-03 |       4903.7 |            97.6496 |     7.0513 |                2.3504 | 24.36%                   | 95.51%                         | 1.28%                | -3.47%           | 3.03%            | 9.40%            | 16.57%           | 2.04%               | -0.42%              | 4.15%               | -5.22%              |
|      4 | 2026-03-17 |       5001   |            97.2222 |     8.3333 |                2.7778 | 30.13%                   | 99.36%                         | 4.49%                | -4.37%           | -2.08%           | 2.42%            | 5.07%            | -12.03%             | -7.07%              | -3.52%              | -6.47%              |
|      5 | 2013-10-08 |       1324.2 |            97.2222 |     8.3333 |                2.7778 | 23.72%                   | 92.95%                         | 0.64%                | 2.97%            | 0.62%            | -2.93%           | 0.23%            | -3.87%              | 1.38%               | -1.22%              | -7.74%              |
|      6 | 2026-03-31 |       4647.6 |            97.2222 |     8.3333 |                2.7778 | 23.08%                   | 96.15%                         | 0.64%                | 5.64%            | -7.07%           | -9.00%           | -5.22%           | 0.20%               | 3.82%               | -1.21%              | -3.17%              |
|      7 | 2026-03-10 |       5229.7 |            97.0085 |     8.9744 |                2.9915 | 28.21%                   | 98.08%                         | 4.49%                | 2.39%            | 1.43%            | 4.51%            | 13.96%           | -4.37%              | -15.88%             | -10.95%             | -12.89%             |
|      8 | 2026-02-10 |       5003.8 |            96.5812 |    10.2564 |                3.4188 | 23.72%                   | 98.72%                         | 0.64%                | 2.04%            | -1.50%           | 9.03%            | 16.25%           | -2.42%              | 3.04%               | 4.51%               | -6.93%              |
|      9 | 2023-08-08 |       1924.1 |            96.5812 |    10.2564 |                3.4188 | 34.62%                   | 91.67%                         | 3.21%                | -0.86%           | -1.94%           | -0.37%           | -1.05%           | -1.12%              | -1.44%              | 0.11%               | -5.17%              |
|     10 | 2023-02-07 |       1871.7 |            96.3675 |    10.8974 |                3.6325 | 32.69%                   | 91.03%                         | 5.13%                | -3.00%           | -3.22%           | 0.01%            | 3.19%            | -0.95%              | -2.07%              | -3.09%              | 8.04%               |
|     11 | 2026-03-24 |       4399.3 |            96.1538 |    11.5385 |                3.8462 | 20.51%                   | 92.95%                         | 0.64%                | -12.03%          | -15.88%          | -14.67%          | -13.40%          | 5.64%               | 5.86%               | 6.80%               | 2.43%               |
|     12 | 2026-02-24 |       5155.8 |            96.1538 |    11.5385 |                3.8462 | 27.56%                   | 98.08%                         | 6.41%                | 5.59%            | 3.04%            | 1.49%            | 17.98%           | -0.94%              | 1.43%               | -14.67%             | -8.87%              |
|     13 | 2013-08-27 |       1420.6 |            95.7265 |    12.8205 |                4.2735 | 20.51%                   | 93.59%                         | 2.56%                | 3.46%            | 7.52%            | 7.30%            | 14.23%           | -0.61%              | -3.98%              | -7.36%              | -5.50%              |
|     14 | 2023-09-05 |       1926.2 |            95.5128 |    13.4615 |                4.4872 | 29.49%                   | 92.95%                         | 11.54%               | -0.53%           | 1.57%            | 0.11%            | -0.26%           | -0.77%              | 0.30%               | -5.27%              | 3.06%               |
|     15 | 2023-02-14 |       1854   |            95.5128 |    13.4615 |                4.4872 | 20.51%                   | 91.67%                         | 1.28%                | -0.95%           | -3.91%           | -2.79%           | 2.10%            | -1.13%              | -1.35%              | 2.82%               | 8.13%               |
|     16 | 2013-09-03 |       1412   |            95.2991 |    14.1026 |                4.7009 | 22.44%                   | 92.95%                         | 5.13%                | -0.61%           | 2.83%            | 10.04%           | 13.33%           | -3.39%              | -7.26%              | -8.92%              | -4.73%              |
|     17 | 2013-09-10 |       1364.1 |            95.0855 |    14.7436 |                4.9145 | 17.95%                   | 94.87%                         | 3.21%                | -3.39%           | -3.98%           | 3.25%            | 5.68%            | -4.00%              | -3.53%              | -2.93%              | -4.11%              |
|     18 | 2014-02-11 |       1290.1 |            95.0855 |    14.7436 |                4.9145 | 21.79%                   | 91.67%                         | 3.85%                | 3.07%            | 3.13%            | 3.61%            | 4.78%            | 2.68%               | 4.10%               | 4.37%               | 1.44%               |
|     19 | 2013-09-24 |       1316   |            94.6581 |    16.0256 |                5.3419 | 17.95%                   | 96.79%                         | 2.56%                | 0.50%            | -3.53%           | -7.36%           | -0.60%           | -2.28%              | 0.62%               | 2.01%               | -3.24%              |
|     20 | 2023-09-19 |       1932   |            94.4444 |    16.6667 |                5.5556 | 28.85%                   | 90.38%                         | 11.54%               | 1.08%            | 0.30%            | 1.88%            | -1.53%           | -1.64%              | -5.56%              | -0.48%              | 1.54%               |

## Similar Case Forward Return Summary

| horizon   |   similar_case_count | avg_forward_return   | median_forward_return   | win_rate   | worst_forward_return   | best_forward_return   |
|:----------|---------------------:|:---------------------|:------------------------|:-----------|:-----------------------|:----------------------|
| 1W        |                   20 | -1.05%               | -1.03%                  | 30.00%     | -12.03%                | 5.64%                 |
| 2W        |                   20 | -1.27%               | -0.89%                  | 45.00%     | -15.88%                | 5.86%                 |
| 4W        |                   20 | -2.07%               | -1.22%                  | 40.00%     | -14.67%                | 6.80%                 |
| 8W        |                   20 | -3.03%               | -4.42%                  | 30.00%     | -12.89%                | 8.13%                 |

## Output Files

- `outputs\reports\hse_current_similarity.csv`
- `outputs\reports\hse_current_feature_vector.csv`
- `outputs\reports\hse_current_similarity_summary.csv`
- `outputs\reports\historical_similarity_report.csv`
- `outputs\reports\historical_similarity_stats.csv`
- `outputs\reports\historical_similarity_summary.md`
- `outputs\charts\historical_similarity_cases.png`

## Historical Case Viewer Warnings

- historical_date=2026-03-17: insufficient history around selected event

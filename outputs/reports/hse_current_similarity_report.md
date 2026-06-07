# GHPR v0.3 Historical Similarity Engine

Historical Statistics / Research Reference.

This engine compares the latest GHPR weekly state with past weekly states. It does not connect to TradeDock, does not place orders, and does not produce trading instructions.

Hard scope limits: no TradeDock connection, no automated order placement, no trading recommendations, no Options / OGR / MMP inputs, no AI / ML, and no optimized weights.

Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile. Future candidates include MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.

## Current State

- Latest date: `2026-06-02`
- Latest gold_close: `4,489.10`
- Master rows: `875`
- Historical candidates after recent-row exclusion: `823`
- Complete feature candidates: `772`
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
| 2026-06-02 | mm_net_percentile_156w       | 42.95%          | 44.70%           | 32.88%          |
| 2026-06-02 | producer_net_percentile_156w | 92.31%          | 57.01%           | 31.45%          |
| 2026-06-02 | oi_percentile_156w           | 0.64%           | 47.68%           | 31.38%          |

## Top Historical Matches

|   rank | date       |   gold_close |   similarity_score |   distance |   normalized_distance | mm_net_percentile_156w   | producer_net_percentile_156w   | oi_percentile_156w   | gold_return_1w   | gold_return_2w   | gold_return_4w   | gold_return_8w   | forward_return_1w   | forward_return_2w   | forward_return_4w   | forward_return_8w   |
|-------:|:-----------|-------------:|-------------------:|-----------:|----------------------:|:-------------------------|:-------------------------------|:---------------------|:-----------------|:-----------------|:-----------------|:-----------------|:--------------------|:--------------------|:--------------------|:--------------------|
|      1 | 2023-06-27 |       1914   |            98.0769 |     5.7692 |                1.9231 | 44.87%                   | 92.95%                         | 3.85%                | -1.11%           | -1.57%           | -2.25%           | -4.98%           | 0.40%               | 0.90%               | 2.51%               | -0.92%              |
|      2 | 2023-06-13 |       1944.6 |            97.2222 |     8.3333 |                2.7778 | 47.44%                   | 91.67%                         | 3.85%                | -1.06%           | -0.68%           | -2.20%           | -3.13%           | -0.47%              | -1.57%              | -0.68%              | -1.05%              |
|      3 | 2023-08-08 |       1924.1 |            96.1538 |    11.5385 |                3.8462 | 34.62%                   | 91.67%                         | 3.21%                | -0.86%           | -1.94%           | -0.37%           | -1.05%           | -1.12%              | -1.44%              | 0.11%               | -5.17%              |
|      4 | 2023-06-20 |       1935.5 |            95.5128 |    13.4615 |                4.4872 | 48.72%                   | 92.31%                         | 8.33%                | -0.47%           | -1.53%           | -1.87%           | -2.93%           | -1.11%              | -0.71%              | 2.15%               | -1.70%              |
|      5 | 2014-04-08 |       1308.7 |            95.2991 |    14.1026 |                4.7009 | 42.31%                   | 79.49%                         | 1.28%                | 2.27%            | -0.21%           | -2.81%           | 1.44%            | -0.66%              | -2.15%              | -0.03%              | -4.92%              |
|      6 | 2023-02-07 |       1871.7 |            94.6581 |    16.0256 |                5.3419 | 32.69%                   | 91.03%                         | 5.13%                | -3.00%           | -3.22%           | 0.01%            | 3.19%            | -0.95%              | -2.07%              | -3.09%              | 8.04%               |
|      7 | 2014-04-15 |       1300   |            94.6581 |    16.0256 |                5.3419 | 35.90%                   | 85.26%                         | 2.56%                | -0.66%           | 1.59%            | -4.34%           | -1.86%           | -1.49%              | -0.31%              | -0.42%              | -3.09%              |
|      8 | 2014-04-22 |       1280.6 |            94.4444 |    16.6667 |                5.5556 | 38.46%                   | 83.33%                         | 3.85%                | -1.49%           | -2.15%           | -2.35%           | -4.65%           | 1.20%               | 2.16%               | 1.09%               | -0.69%              |
|      9 | 2014-04-01 |       1279.6 |            94.4444 |    16.6667 |                5.5556 | 46.15%                   | 78.85%                         | 0.64%                | -2.42%           | -5.84%           | -4.35%           | 2.23%            | 2.27%               | 1.59%               | 1.28%               | -1.11%              |
|     10 | 2013-10-08 |       1324.2 |            93.3761 |    19.8718 |                6.6239 | 23.72%                   | 92.95%                         | 0.64%                | 2.97%            | 0.62%            | -2.93%           | 0.23%            | -3.87%              | 1.38%               | -1.22%              | -7.74%              |
|     11 | 2021-06-22 |       1776.3 |            93.3761 |    19.8718 |                6.6239 | 35.90%                   | 87.82%                         | 8.97%                | -4.22%           | -6.13%           | -6.42%           | -0.10%           | -0.76%              | 0.97%               | 1.95%               | 0.49%               |
|     12 | 2021-06-29 |       1762.8 |            93.3761 |    19.8718 |                6.6239 | 35.26%                   | 88.46%                         | 8.97%                | -0.76%           | -4.94%           | -7.36%           | -0.73%           | 1.74%               | 2.64%               | 2.08%               | 2.43%               |
|     13 | 2013-10-29 |       1345.2 |            92.9487 |    21.1538 |                7.0513 | 33.33%                   | 87.82%                         | 7.69%                | 0.20%            | 5.67%            | 4.60%            | -4.73%           | -2.77%              | -5.51%              | -7.72%              | -10.41%             |
|     14 | 2014-04-29 |       1296   |            92.9487 |    21.1538 |                7.0513 | 39.10%                   | 82.69%                         | 8.33%                | 1.20%            | -0.31%           | 1.28%            | -3.12%           | 0.95%               | -0.11%              | -2.36%              | 1.92%               |
|     15 | 2023-02-14 |       1854   |            92.094  |    23.7179 |                7.906  | 20.51%                   | 91.67%                         | 1.28%                | -0.95%           | -3.91%           | -2.79%           | 2.10%            | -1.13%              | -1.35%              | 2.82%               | 8.13%               |
|     16 | 2023-09-05 |       1926.2 |            91.6667 |    25      |                8.3333 | 29.49%                   | 92.95%                         | 11.54%               | -0.53%           | 1.57%            | 0.11%            | -0.26%           | -0.77%              | 0.30%               | -5.27%              | 3.06%               |
|     17 | 2014-02-11 |       1290.1 |            91.6667 |    25      |                8.3333 | 21.79%                   | 91.67%                         | 3.85%                | 3.07%            | 3.13%            | 3.61%            | 4.78%            | 2.68%               | 4.10%               | 4.37%               | 1.44%               |
|     18 | 2013-08-27 |       1420.6 |            91.453  |    25.641  |                8.547  | 20.51%                   | 93.59%                         | 2.56%                | 3.46%            | 7.52%            | 7.30%            | 14.23%           | -0.61%              | -3.98%              | -7.36%              | -5.50%              |
|     19 | 2013-09-03 |       1412   |            91.453  |    25.641  |                8.547  | 22.44%                   | 92.95%                         | 5.13%                | -0.61%           | 2.83%            | 10.04%           | 13.33%           | -3.39%              | -7.26%              | -8.92%              | -4.73%              |
|     20 | 2023-09-19 |       1932   |            91.0256 |    26.9231 |                8.9744 | 28.85%                   | 90.38%                         | 11.54%               | 1.08%            | 0.30%            | 1.88%            | -1.53%           | -1.64%              | -5.56%              | -0.48%              | 1.54%               |

## Similar Case Forward Return Summary

| horizon   |   similar_case_count | avg_forward_return   | median_forward_return   | win_rate   | worst_forward_return   | best_forward_return   |
|:----------|---------------------:|:---------------------|:------------------------|:-----------|:-----------------------|:----------------------|
| 1W        |                   20 | -0.57%               | -0.77%                  | 30.00%     | -3.87%                 | 2.68%                 |
| 2W        |                   20 | -0.90%               | -0.51%                  | 40.00%     | -7.26%                 | 4.10%                 |
| 4W        |                   20 | -0.96%               | -0.22%                  | 45.00%     | -8.92%                 | 4.37%                 |
| 8W        |                   20 | -1.00%               | -0.99%                  | 40.00%     | -10.41%                | 8.13%                 |

## Output Files

- `outputs\reports\hse_current_similarity.csv`
- `outputs\reports\hse_current_feature_vector.csv`
- `outputs\reports\hse_current_similarity_summary.csv`
- `outputs\reports\historical_similarity_report.csv`
- `outputs\reports\historical_similarity_stats.csv`
- `outputs\reports\historical_similarity_summary.md`
- `outputs\charts\historical_similarity_cases.png`

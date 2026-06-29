# Historical Similarity Summary

Historical Statistics / Research Reference.

Reminder: classification is historical positioning only, not a trading recommendation.

分類只是歷史定位，不是交易建議。

## Hard Scope Limits

- Does not connect to TradeDock.
- Does not place orders.
- Does not provide trading recommendations.
- Does not include Options, OGR, or MMP.
- Does not use AI or ML.
- Does not optimize weights.
- Version 0.3 similarity score uses only MM Percentile, Producer Percentile, and OI Percentile.

Future version candidates: MM Z-score, Producer Z-score, OI Z-score, Options, Max Pain, OGR, and MMP.

## Current Market State

- Latest data date: `2026-06-23`
- Latest gold close: `4,172.90`
- MM Percentile: `44.23%`
- Producer Percentile: `100.00%`
- OI Percentile: `2.56%`
- Temporary market-state classification: `Neutral / Transition`

## Top 10 Most Similar Historical Periods

| historical_date   |   similarity_score |   historical_gold_close | historical_mm_percentile   | historical_producer_percentile   | historical_oi_percentile   |
|:------------------|-------------------:|------------------------:|:---------------------------|:---------------------------------|:---------------------------|
| 2023-06-27        |              97.01 |                  1914   | 44.87%                     | 92.95%                           | 3.85%                      |
| 2023-06-13        |              95.73 |                  1944.6 | 47.44%                     | 91.67%                           | 3.85%                      |
| 2023-06-20        |              94.02 |                  1935.5 | 48.72%                     | 92.31%                           | 8.33%                      |
| 2023-08-08        |              93.8  |                  1924.1 | 34.62%                     | 91.67%                           | 3.21%                      |
| 2023-02-07        |              92.31 |                  1871.7 | 32.69%                     | 91.03%                           | 5.13%                      |
| 2014-04-15        |              92.31 |                  1300   | 35.90%                     | 85.26%                           | 2.56%                      |
| 2014-04-22        |              92.09 |                  1280.6 | 38.46%                     | 83.33%                           | 3.85%                      |
| 2014-04-08        |              92.09 |                  1308.7 | 42.31%                     | 79.49%                           | 1.28%                      |
| 2014-04-01        |              91.67 |                  1279.6 | 46.15%                     | 78.85%                           | 0.64%                      |
| 2021-06-22        |              91.03 |                  1776.3 | 35.90%                     | 87.82%                           | 8.97%                      |

## Top Similarity Outcome Statistics

| group   |   case_count | avg_return_1w   | win_rate_1w   | avg_return_2w   | win_rate_2w   | avg_return_4w   | win_rate_4w   | avg_return_8w   | win_rate_8w   |
|:--------|-------------:|:----------------|:--------------|:----------------|:--------------|:----------------|:--------------|:----------------|:--------------|
| Top 5   |            5 | -0.65%          | 20.00%        | -0.98%          | 20.00%        | 0.20%           | 60.00%        | -0.16%          | 20.00%        |
| Top 10  |           10 | -0.27%          | 30.00%        | -0.26%          | 40.00%        | 0.49%           | 60.00%        | -1.01%          | 20.00%        |
| Top 20  |           20 | -0.74%          | 30.00%        | -0.95%          | 40.00%        | -1.11%          | 45.00%        | -2.10%          | 25.00%        |

## 8W Extremes In Top 20 Similar Cases

- Best 8W case: `2023-02-07` with `8.04%`
- Worst 8W case: `2013-10-29` with `-10.41%`

## Classification Rules

- MM >= 80 and OI >= 60: Expansion / Momentum
- MM >= 80 and OI < 60: Euphoria / Thin Momentum
- MM 60-80: Healthy Bullish Positioning
- MM 40-60: Neutral / Transition
- MM 20-40: Accumulation / Weak Positioning
- MM <= 20: Extreme Low / Potential Reset

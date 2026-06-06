# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery

This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-05-26`.
- Latest date: `2026-05-26`.
- Latest MM percentile: `30.13%`.
- Latest MM lifecycle state: `MM_ACCUMULATION`.
- Latest MM velocity 8W: `7.05%`.
- Latest MM acceleration 8W: `8.33%`.
- Strongest velocity window summary: `mm_velocity_8w average absolute rank correlation 0.188`.
- State outcome note: MM_CROWDED_EXPANSION has the largest absolute 8W median following return (6.16%) in this sample.
- Lead-lag note: The strongest positive-lag row suggests MM lifecycle features have some historical lead-lag context, but it should be treated as sample evidence rather than a forecast.

## Required Research Questions

### 1. What does the current MM percentile lifecycle mean?

MM lifecycle treats `mm_net_percentile_156w` as a positioning phase variable. A low percentile with rising velocity is different from a low percentile still falling; a high percentile with rising velocity is different from a high percentile already rolling over.

### 2. What is MM Velocity?

MM Velocity measures the change in MM percentile over a trailing window. For example, `mm_velocity_8w = mm_percentile - mm_percentile.shift(8)`. Positive values mean MM positioning moved higher versus eight weeks earlier; negative values mean positioning moved lower.

### 3. What is MM Acceleration?

MM Acceleration measures whether velocity itself is increasing or fading. `mm_acceleration_8w = mm_velocity_8w - mm_velocity_8w.shift(8)`. It helps separate steady accumulation from a faster or slower positioning move.

### 4. Does MM lead gold, does gold lead MM, or is the relationship mixed?

The strongest positive-lag row suggests MM lifecycle features have some historical lead-lag context, but it should be treated as sample evidence rather than a forecast.

### 5. Which MM velocity window has the most information?

mm_velocity_8w average absolute rank correlation 0.188

### 6. Which MM Lifecycle State has the strongest historical sample tendency?

MM_CROWDED_EXPANSION has the largest absolute 8W median following return (6.16%) in this sample.

### 7. What does the current MM Lifecycle State mean?

The latest state is `MM_ACCUMULATION`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.

### 8. What does the current MM Velocity imply?

Latest 8W velocity is `7.05%`. It describes recent positioning movement only; it does not independently determine market direction.

### 9. What does the current MM Acceleration imply?

Latest 8W acceleration is `8.33%`. It describes whether the positioning movement is speeding up or slowing down.

### 10. Which historical MM trajectories are most similar now?

| window   | historical_start_date   | historical_end_date   |   similarity_score |   historical_gold_return_1w |   historical_gold_return_2w |   historical_gold_return_4w |   historical_gold_return_8w |
|:---------|:------------------------|:----------------------|-------------------:|----------------------------:|----------------------------:|----------------------------:|----------------------------:|
| 8W       | 2022-11-22              | 2023-01-17            |            89.7997 |                 0.0190211   |                 0.0366908   |                   0.0502781 |                   0.0971638 |
| 8W       | 2018-11-20              | 2019-01-15            |            88.3261 |                 0.00233791  |                 0.00618001  |                   0.029619  |                   0.0551271 |
| 8W       | 2011-12-27              | 2012-02-21            |            88.1842 |                 0.0240107   |                 0.00612686  |                   0.0558226 |                   0.102183  |
| 8W       | 2022-11-15              | 2023-01-10            |            88.0428 |                 0.0173398   |                 0.0312982   |                   0.0318099 |                   0.0551358 |
| 8W       | 2022-11-01              | 2022-12-27            |            87.9868 |                -0.000605747 |                 0.000496182 |                   0.0379776 |                   0.103222  |
| 8W       | 2022-11-29              | 2023-01-24            |            87.8012 |                 0.0139996   |                 0.0332871   |                   0.0656271 |                   0.106097  |
| 8W       | 2014-01-14              | 2014-03-11            |            87.4768 |                 0.00650318  |                 0.00260611  |                   0.0437176 |                   0.0813524 |
| 8W       | 2016-12-27              | 2017-02-21            |            87.364  |                 0.011112    |                 0.00267384  |                   0.0224737 |                   0.0881034 |
| 8W       | 2021-03-02              | 2021-04-27            |            87.2297 |                 0.000393828 |                 0.018211    |                   0.0558822 |                   0.0259073 |
| 8W       | 2018-10-30              | 2018-12-24            |            86.9717 |                 0.0146494   |                 0.0206136   |                   0.0464829 |                   0.036725  |

### 11. What happened after the most similar historical trajectories?

- 1W: avg `0.84%`, median `0.58%`, win rate `80.00%`.
- 2W: avg `1.29%`, median `1.20%`, win rate `85.00%`.
- 4W: avg `4.00%`, median `3.89%`, win rate `95.00%`.
- 8W: avg `7.00%`, median `7.79%`, win rate `95.00%`.

### 12. Should this replace MM Percentile in the Dashboard?

No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.

### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?

Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.

## MM Lifecycle State Analysis

| mm_lifecycle_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:---------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_RESET             |     209 |             -0.00603741 |                -0.00643463 |      0.363636 |             -0.0115586  |                -0.0115099  |      0.320574 |             -0.0204758  |               -0.0190912   |      0.258373 |              -0.0327947 |                -0.0337078  |      0.133971 |         0.17979  |        -0.141753  |
| MM_ACCUMULATION      |     134 |              0.00384024 |                 0.00496698 |      0.686567 |              0.006297   |                 0.0102498  |      0.626866 |              0.0063184  |                0.0139407   |      0.619403 |               0.0108877 |                 0.0119419  |      0.597015 |         0.142329 |        -0.135196  |
| MM_EXPANSION         |     145 |              0.00645231 |                 0.00608858 |      0.641379 |              0.0137331  |                 0.0126593  |      0.689655 |              0.0268568  |                0.0251306   |      0.731034 |               0.0469505 |                 0.0386469  |      0.827586 |         0.239115 |        -0.0456435 |
| MM_CROWDED_EXPANSION |     106 |              0.00839223 |                 0.00939511 |      0.669811 |              0.0172474  |                 0.0190197  |      0.764151 |              0.0367427  |                0.0345373   |      0.886792 |               0.0608284 |                 0.0616258  |      0.95283  |         0.179186 |        -0.0348419 |
| MM_DISTRIBUTION      |     212 |              0.00125058 |                 0.00161634 |      0.518868 |              0.00237314 |                -0.00052457 |      0.490566 |              0.00626583 |                0.000718803 |      0.509434 |               0.0177998 |                 0.00289419 |      0.509434 |         0.24908  |        -0.115905  |
| MM_NEUTRAL           |      68 |              0.00640746 |                 0.00915424 |      0.671642 |              0.0110329  |                 0.0167388  |      0.636364 |              0.0194682  |                0.0294857   |      0.71875  |               0.0362926 |                 0.0316098  |      0.666667 |         0.173598 |        -0.0843966 |

## Strongest Lead-Lag Rows

| mm_feature         | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                                              |   abs_rank_correlation |
|:-------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:------------------------------------------------------------|-----------------------:|
| mm_velocity_4w     | 4W             |           0 |      0.498068 |           0.580729 |            819 | same_week_positive_historical_alignment                     |               0.580729 |
| mm_acceleration_4w | 4W             |          -4 |     -0.444358 |          -0.514361 |            815 | gold_or_later_mm_alignment_4w_negative_historical_alignment |               0.514361 |
| mm_velocity_8w     | 8W             |           0 |      0.434444 |           0.488243 |            815 | same_week_positive_historical_alignment                     |               0.488243 |
| mm_acceleration_8w | 8W             |          -8 |     -0.431479 |          -0.485742 |            807 | gold_or_later_mm_alignment_8w_negative_historical_alignment |               0.485742 |
| mm_velocity_12w    | 8W             |           0 |      0.37564  |           0.428237 |            811 | same_week_positive_historical_alignment                     |               0.428237 |
| mm_velocity_4w     | 2W             |           0 |      0.340497 |           0.42486  |            819 | same_week_positive_historical_alignment                     |               0.42486  |
| mm_velocity_8w     | 8W             |           2 |      0.360662 |           0.412201 |            813 | mm_feature_leads_gold_2w_positive_historical_alignment      |               0.412201 |
| mm_velocity_8w     | 4W             |           0 |      0.363042 |           0.409711 |            815 | same_week_positive_historical_alignment                     |               0.409711 |

## Method Notes

- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.
- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.
- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.
- All outputs are historical statistics / research reference only.
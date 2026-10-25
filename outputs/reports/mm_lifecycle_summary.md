# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery

This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-10-20`.
- Latest date: `2026-10-20`.
- Latest MM percentile: `24.36%`.
- Latest MM lifecycle state: `MM_RESET`.
- Latest MM velocity 8W: `-41.03%`.
- Latest MM acceleration 8W: `-61.54%`.
- Strongest velocity window summary: `mm_velocity_8w average absolute rank correlation 0.183`.
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

mm_velocity_8w average absolute rank correlation 0.183

### 6. Which MM Lifecycle State has the strongest historical sample tendency?

MM_CROWDED_EXPANSION has the largest absolute 8W median following return (6.16%) in this sample.

### 7. What does the current MM Lifecycle State mean?

The latest state is `MM_RESET`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.

### 8. What does the current MM Velocity imply?

Latest 8W velocity is `-41.03%`. It describes recent positioning movement only; it does not independently determine market direction.

### 9. What does the current MM Acceleration imply?

Latest 8W acceleration is `-61.54%`. It describes whether the positioning movement is speeding up or slowing down.

### 10. Which historical MM trajectories are most similar now?

| window   | historical_start_date   | historical_end_date   |   similarity_score |   historical_gold_return_1w |   historical_gold_return_2w |   historical_gold_return_4w |   historical_gold_return_8w |
|:---------|:------------------------|:----------------------|-------------------:|----------------------------:|----------------------------:|----------------------------:|----------------------------:|
| 8W       | 2018-03-27              | 2018-05-22            |            94.8141 |                  0.00217234 |                 -0.0154726  |                 -0.0298183  |                  -0.0369791 |
| 8W       | 2020-06-30              | 2020-08-25            |            94.5427 |                 -0.0447072  |                 -0.0119201  |                 -0.0110563  |                   0.0680922 |
| 8W       | 2022-03-15              | 2022-05-10            |            94.2048 |                 -0.0158238  |                 -0.033139   |                 -0.068367   |                  -0.0459657 |
| 8W       | 2016-11-15              | 2017-01-10            |            93.9075 |                  0.0205101  |                  0.0412379  |                  0.0237745  |                  -0.0325164 |
| 8W       | 2020-04-14              | 2020-06-09            |            93.7156 |                 -0.00697807 |                  0.0100305  |                  0.0102675  |                  -0.0198098 |
| 8W       | 2014-07-29              | 2014-09-23            |            93.6351 |                 -0.0114961  |                 -0.020693   |                 -0.0489173  |                  -0.0595394 |
| 8W       | 2016-11-08              | 2017-01-03            |            93.6017 |                  0.0203112  |                  0.0255413  |                 -0.00616645 |                  -0.0887388 |
| 8W       | 2022-03-22              | 2022-05-17            |            93.4908 |                 -0.0120043  |                 -0.0276382  |                 -0.0715161  |                  -0.0533958 |
| 8W       | 2020-04-07              | 2020-06-02            |            93.3731 |                  0.0171281  |                 -0.00584793 |                  0.0173668  |                   0.0415665 |
| 8W       | 2014-07-22              | 2014-09-16            |            93.3495 |                 -0.0093039  |                 -0.0225528  |                 -0.0462513  |                  -0.0542838 |

### 11. What happened after the most similar historical trajectories?

- 1W: avg `-0.06%`, median `-0.52%`, win rate `45.00%`.
- 2W: avg `-0.57%`, median `-0.86%`, win rate `40.00%`.
- 4W: avg `-1.36%`, median `-1.59%`, win rate `30.00%`.
- 8W: avg `-0.66%`, median `-2.62%`, win rate `35.00%`.

### 12. Should this replace MM Percentile in the Dashboard?

No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.

### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?

Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.

## MM Lifecycle State Analysis

| mm_lifecycle_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:---------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_RESET             |     211 |             -0.00607152 |                -0.00643463 |      0.36019  |             -0.0115639  |               -0.0114943   |      0.312796 |             -0.0206107  |                -0.0201924  |      0.246445 |              -0.0332028 |                -0.0342944  |      0.14218  |         0.180106 |        -0.141753  |
| MM_ACCUMULATION      |     135 |              0.0034119  |                 0.00494877 |      0.674074 |              0.00594031 |                0.0100067   |      0.622222 |              0.00563109 |                 0.0138323  |      0.614815 |               0.0100166 |                 0.0106326  |      0.592593 |         0.142329 |        -0.135196  |
| MM_EXPANSION         |     160 |              0.00603311 |                 0.00581611 |      0.6375   |              0.0124044  |                0.010872    |      0.66875  |              0.0240605  |                 0.0247439  |      0.6875   |               0.0420188 |                 0.0386433  |      0.80625  |         0.239115 |        -0.116012  |
| MM_CROWDED_EXPANSION |     106 |              0.00844219 |                 0.00883771 |      0.669811 |              0.0171738  |                0.0184207   |      0.745283 |              0.0368913  |                 0.0345373  |      0.886792 |               0.0611155 |                 0.0616258  |      0.95283  |         0.18041  |        -0.0337237 |
| MM_DISTRIBUTION      |     214 |              0.00115306 |                 0.00206502 |      0.523364 |              0.00213953 |                0.000270562 |      0.509346 |              0.00569565 |                 0.00156096 |      0.504673 |               0.0170397 |                 0.00109799 |      0.518692 |         0.239587 |        -0.115905  |
| MM_NEUTRAL           |      69 |              0.00613398 |                 0.00818202 |      0.661765 |              0.0106738  |                0.0163343   |      0.626866 |              0.0189686  |                 0.0294586  |      0.723077 |               0.0340008 |                 0.030663   |      0.655738 |         0.173598 |        -0.106463  |

## Strongest Lead-Lag Rows

| mm_feature         | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                                              |   abs_rank_correlation |
|:-------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:------------------------------------------------------------|-----------------------:|
| mm_velocity_4w     | 4W             |           0 |      0.485926 |           0.569036 |            840 | same_week_positive_historical_alignment                     |               0.569036 |
| mm_acceleration_4w | 4W             |          -4 |     -0.433259 |          -0.503755 |            836 | gold_or_later_mm_alignment_4w_negative_historical_alignment |               0.503755 |
| mm_acceleration_8w | 8W             |          -8 |     -0.428692 |          -0.481933 |            828 | gold_or_later_mm_alignment_8w_negative_historical_alignment |               0.481933 |
| mm_velocity_8w     | 8W             |           0 |      0.419416 |           0.467196 |            836 | same_week_positive_historical_alignment                     |               0.467196 |
| mm_velocity_4w     | 2W             |           0 |      0.33879  |           0.421382 |            840 | same_week_positive_historical_alignment                     |               0.421382 |
| mm_velocity_12w    | 8W             |           0 |      0.359228 |           0.406613 |            832 | same_week_positive_historical_alignment                     |               0.406613 |
| mm_acceleration_4w | 4W             |           0 |      0.336294 |           0.39672  |            836 | same_week_positive_historical_alignment                     |               0.39672  |
| mm_velocity_8w     | 4W             |           0 |      0.353749 |           0.396714 |            836 | same_week_positive_historical_alignment                     |               0.396714 |

## Method Notes

- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.
- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.
- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.
- All outputs are historical statistics / research reference only.
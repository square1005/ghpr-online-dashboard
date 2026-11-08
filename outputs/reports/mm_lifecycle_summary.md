# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery

This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-11-03`.
- Latest date: `2026-11-03`.
- Latest MM percentile: `21.79%`.
- Latest MM lifecycle state: `MM_RESET`.
- Latest MM velocity 8W: `-33.33%`.
- Latest MM acceleration 8W: `-42.95%`.
- Strongest velocity window summary: `mm_velocity_8w average absolute rank correlation 0.185`.
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

mm_velocity_8w average absolute rank correlation 0.185

### 6. Which MM Lifecycle State has the strongest historical sample tendency?

MM_CROWDED_EXPANSION has the largest absolute 8W median following return (6.16%) in this sample.

### 7. What does the current MM Lifecycle State mean?

The latest state is `MM_RESET`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.

### 8. What does the current MM Velocity imply?

Latest 8W velocity is `-33.33%`. It describes recent positioning movement only; it does not independently determine market direction.

### 9. What does the current MM Acceleration imply?

Latest 8W acceleration is `-42.95%`. It describes whether the positioning movement is speeding up or slowing down.

### 10. Which historical MM trajectories are most similar now?

| window   | historical_start_date   | historical_end_date   |   similarity_score |   historical_gold_return_1w |   historical_gold_return_2w |   historical_gold_return_4w |   historical_gold_return_8w |
|:---------|:------------------------|:----------------------|-------------------:|----------------------------:|----------------------------:|----------------------------:|----------------------------:|
| 8W       | 2021-01-26              | 2021-03-23            |            95.021  |                -0.00335089  |                  0.00477602 |                 -0.0447423  |                 -0.067967   |
| 8W       | 2018-04-03              | 2018-05-29            |            93.9793 |                 0.00541922  |                  0.00760333 |                 -0.00391172 |                 -0.0255853  |
| 8W       | 2021-11-09              | 2022-01-04            |            93.8697 |                 0.00204316  |                  0.0144798  |                  0.0167535  |                 -0.00884863 |
| 8W       | 2012-09-25              | 2012-11-20            |            93.8675 |                -0.000579979 |                  0.00530889 |                  0.00872206 |                 -0.0230185  |
| 8W       | 2014-08-12              | 2014-10-07            |            93.6712 |                 0.000991286 |                 -0.00761675 |                 -0.0281521  |                 -0.0741902  |
| 8W       | 2018-03-27              | 2018-05-22            |            93.5278 |                 0.00217234  |                 -0.0154726  |                 -0.0298183  |                 -0.0369791  |
| 8W       | 2010-10-19              | 2010-12-14            |            93.2319 |                -0.00333741  |                  0.0134296  |                  0.0487932  |                  0.051307   |
| 8W       | 2021-11-16              | 2022-01-11            |            93.0271 |                 0.00214925  |                  0.00419679 |                  0.0260678  |                 -0.0192007  |
| 8W       | 2022-03-29              | 2022-05-24            |            93.0126 |                 0.0255649   |                  0.0132537  |                 -0.0203245  |                 -0.0244744  |
| 8W       | 2022-04-05              | 2022-05-31            |            92.9406 |                -0.012169    |                  0.0130848  |                 -0.014915   |                 -0.0439948  |

### 11. What happened after the most similar historical trajectories?

- 1W: avg `0.34%`, median `0.21%`, win rate `60.00%`.
- 2W: avg `0.47%`, median `0.50%`, win rate `70.00%`.
- 4W: avg `-0.79%`, median `-1.11%`, win rate `30.00%`.
- 8W: avg `-1.98%`, median `-2.91%`, win rate `25.00%`.

### 12. Should this replace MM Percentile in the Dashboard?

No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.

### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?

Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.

## MM Lifecycle State Analysis

| mm_lifecycle_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:---------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_RESET             |     213 |             -0.0062462  |                -0.00652892 |      0.356808 |             -0.0117999  |               -0.0115099   |      0.309859 |             -0.0208118  |                -0.0203245  |      0.244131 |              -0.033762  |                -0.0346812  |      0.140845 |         0.180106 |        -0.141753  |
| MM_ACCUMULATION      |     135 |              0.0034119  |                 0.00494877 |      0.674074 |              0.00594031 |                0.0100067   |      0.622222 |              0.00563109 |                 0.0138323  |      0.614815 |               0.0100166 |                 0.0106326  |      0.592593 |         0.142329 |        -0.135196  |
| MM_EXPANSION         |     160 |              0.00603311 |                 0.00581611 |      0.6375   |              0.0124044  |                0.010872    |      0.66875  |              0.0240605  |                 0.0247439  |      0.6875   |               0.0420188 |                 0.0386433  |      0.80625  |         0.239115 |        -0.116012  |
| MM_CROWDED_EXPANSION |     106 |              0.00844219 |                 0.00883771 |      0.669811 |              0.0171738  |                0.0184207   |      0.745283 |              0.0368913  |                 0.0345373  |      0.886792 |               0.0611155 |                 0.0616258  |      0.95283  |         0.18041  |        -0.0337237 |
| MM_DISTRIBUTION      |     214 |              0.00115306 |                 0.00206502 |      0.523364 |              0.00213953 |                0.000270562 |      0.509346 |              0.00569565 |                 0.00156096 |      0.504673 |               0.0170397 |                 0.00109799 |      0.518692 |         0.239587 |        -0.115905  |
| MM_NEUTRAL           |      69 |              0.00613398 |                 0.00818202 |      0.661765 |              0.0106738  |                0.0163343   |      0.626866 |              0.0189686  |                 0.0294586  |      0.723077 |               0.0340008 |                 0.030663   |      0.655738 |         0.173598 |        -0.106463  |

## Strongest Lead-Lag Rows

| mm_feature         | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                                              |   abs_rank_correlation |
|:-------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:------------------------------------------------------------|-----------------------:|
| mm_velocity_4w     | 4W             |           0 |      0.486362 |           0.569912 |            842 | same_week_positive_historical_alignment                     |               0.569912 |
| mm_acceleration_4w | 4W             |          -4 |     -0.433137 |          -0.503959 |            838 | gold_or_later_mm_alignment_4w_negative_historical_alignment |               0.503959 |
| mm_acceleration_8w | 8W             |          -8 |     -0.429979 |          -0.483788 |            830 | gold_or_later_mm_alignment_8w_negative_historical_alignment |               0.483788 |
| mm_velocity_8w     | 8W             |           0 |      0.422005 |           0.469709 |            838 | same_week_positive_historical_alignment                     |               0.469709 |
| mm_velocity_4w     | 2W             |           0 |      0.339584 |           0.422892 |            842 | same_week_positive_historical_alignment                     |               0.422892 |
| mm_velocity_12w    | 8W             |           0 |      0.361902 |           0.409092 |            834 | same_week_positive_historical_alignment                     |               0.409092 |
| mm_velocity_8w     | 4W             |           0 |      0.355674 |           0.398865 |            838 | same_week_positive_historical_alignment                     |               0.398865 |
| mm_velocity_8w     | 8W             |           2 |      0.350979 |           0.396363 |            836 | mm_feature_leads_gold_2w_positive_historical_alignment      |               0.396363 |

## Method Notes

- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.
- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.
- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.
- All outputs are historical statistics / research reference only.
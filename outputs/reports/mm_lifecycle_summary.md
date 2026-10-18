# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery

This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-10-13`.
- Latest date: `2026-10-13`.
- Latest MM percentile: `26.92%`.
- Latest MM lifecycle state: `MM_RESET`.
- Latest MM velocity 8W: `-35.26%`.
- Latest MM acceleration 8W: `-53.21%`.
- Strongest velocity window summary: `mm_velocity_8w average absolute rank correlation 0.182`.
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

mm_velocity_8w average absolute rank correlation 0.182

### 6. Which MM Lifecycle State has the strongest historical sample tendency?

MM_CROWDED_EXPANSION has the largest absolute 8W median following return (6.16%) in this sample.

### 7. What does the current MM Lifecycle State mean?

The latest state is `MM_RESET`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.

### 8. What does the current MM Velocity imply?

Latest 8W velocity is `-35.26%`. It describes recent positioning movement only; it does not independently determine market direction.

### 9. What does the current MM Acceleration imply?

Latest 8W acceleration is `-53.21%`. It describes whether the positioning movement is speeding up or slowing down.

### 10. Which historical MM trajectories are most similar now?

| window   | historical_start_date   | historical_end_date   |   similarity_score |   historical_gold_return_1w |   historical_gold_return_2w |   historical_gold_return_4w |   historical_gold_return_8w |
|:---------|:------------------------|:----------------------|-------------------:|----------------------------:|----------------------------:|----------------------------:|----------------------------:|
| 8W       | 2022-03-15              | 2022-05-10            |            94.4165 |                  -0.0158238 |                -0.033139    |                 -0.068367   |                  -0.0459657 |
| 8W       | 2020-04-07              | 2020-06-02            |            94.2939 |                   0.0171281 |                -0.00584793  |                  0.0173668  |                   0.0415665 |
| 8W       | 2020-06-30              | 2020-08-25            |            94.2054 |                  -0.0447072 |                -0.0119201   |                 -0.0110563  |                   0.0680922 |
| 8W       | 2020-03-31              | 2020-05-26            |            94.1875 |                  -0.0225891 |                 0.000234701 |                 -0.00333233 |                   0.0766705 |
| 8W       | 2018-03-20              | 2018-05-15            |            94.0928 |                  -0.0176067 |                -0.0114282   |                 -0.0432749  |                  -0.0169323 |
| 8W       | 2022-03-08              | 2022-05-03            |            94.0775 |                  -0.0175936 |                -0.0451251   |                 -0.0295201  |                  -0.0845202 |
| 8W       | 2020-06-23              | 2020-08-18            |            94.001  |                   0.0343215 |                -0.00390897  |                  0.091762   |                   0.129686  |
| 8W       | 2016-11-08              | 2017-01-03            |            93.9387 |                   0.0203112 |                 0.0255413   |                 -0.00616645 |                  -0.0887388 |
| 8W       | 2020-03-17              | 2020-05-12            |            93.6387 |                   0         |                -0.00356619  |                 -0.0297717  |                   0.117713  |
| 8W       | 2020-03-24              | 2020-05-19            |            93.5998 |                   0.0233513 |                 0.0233513   |                  0.0393279  |                   0.0505963 |

### 11. What happened after the most similar historical trajectories?

- 1W: avg `-0.32%`, median `-0.81%`, win rate `40.00%`.
- 2W: avg `-0.90%`, median `-1.17%`, win rate `30.00%`.
- 4W: avg `-1.48%`, median `-1.67%`, win rate `25.00%`.
- 8W: avg `-0.61%`, median `-2.01%`, win rate `35.00%`.

### 12. Should this replace MM Percentile in the Dashboard?

No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.

### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?

Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.

## MM Lifecycle State Analysis

| mm_lifecycle_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:---------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_RESET             |     210 |             -0.00606088 |                -0.00641665 |      0.361905 |             -0.0115684  |               -0.0115021   |      0.314286 |             -0.0204544  |                -0.0201396  |      0.247619 |              -0.0328011 |                -0.0340011  |      0.142857 |         0.180106 |        -0.141753  |
| MM_ACCUMULATION      |     135 |              0.0034119  |                 0.00494877 |      0.674074 |              0.00594031 |                0.0100067   |      0.622222 |              0.00563109 |                 0.0138323  |      0.614815 |               0.0100166 |                 0.0106326  |      0.592593 |         0.142329 |        -0.135196  |
| MM_EXPANSION         |     160 |              0.00603311 |                 0.00581611 |      0.6375   |              0.0124044  |                0.010872    |      0.66875  |              0.0240605  |                 0.0247439  |      0.6875   |               0.0420188 |                 0.0386433  |      0.80625  |         0.239115 |        -0.116012  |
| MM_CROWDED_EXPANSION |     106 |              0.00844219 |                 0.00883771 |      0.669811 |              0.0171738  |                0.0184207   |      0.745283 |              0.0368913  |                 0.0345373  |      0.886792 |               0.0611155 |                 0.0616258  |      0.95283  |         0.18041  |        -0.0337237 |
| MM_DISTRIBUTION      |     214 |              0.00115306 |                 0.00206502 |      0.523364 |              0.00213953 |                0.000270562 |      0.509346 |              0.00569565 |                 0.00156096 |      0.504673 |               0.0170397 |                 0.00109799 |      0.518692 |         0.239587 |        -0.115905  |
| MM_NEUTRAL           |      69 |              0.00613398 |                 0.00818202 |      0.661765 |              0.0106738  |                0.0163343   |      0.626866 |              0.0189686  |                 0.0294586  |      0.723077 |               0.0340008 |                 0.030663   |      0.655738 |         0.173598 |        -0.106463  |

## Strongest Lead-Lag Rows

| mm_feature         | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                                              |   abs_rank_correlation |
|:-------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:------------------------------------------------------------|-----------------------:|
| mm_velocity_4w     | 4W             |           0 |      0.48511  |           0.568154 |            839 | same_week_positive_historical_alignment                     |               0.568154 |
| mm_acceleration_4w | 4W             |          -4 |     -0.434229 |          -0.505214 |            835 | gold_or_later_mm_alignment_4w_negative_historical_alignment |               0.505214 |
| mm_acceleration_8w | 8W             |          -8 |     -0.426681 |          -0.480409 |            827 | gold_or_later_mm_alignment_8w_negative_historical_alignment |               0.480409 |
| mm_velocity_8w     | 8W             |           0 |      0.417404 |           0.465647 |            835 | same_week_positive_historical_alignment                     |               0.465647 |
| mm_velocity_4w     | 2W             |           0 |      0.338498 |           0.420873 |            839 | same_week_positive_historical_alignment                     |               0.420873 |
| mm_velocity_12w    | 8W             |           0 |      0.358819 |           0.405931 |            831 | same_week_positive_historical_alignment                     |               0.405931 |
| mm_acceleration_4w | 4W             |           0 |      0.336489 |           0.396655 |            835 | same_week_positive_historical_alignment                     |               0.396655 |
| mm_velocity_8w     | 4W             |           0 |      0.352228 |           0.395248 |            835 | same_week_positive_historical_alignment                     |               0.395248 |

## Method Notes

- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.
- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.
- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.
- All outputs are historical statistics / research reference only.
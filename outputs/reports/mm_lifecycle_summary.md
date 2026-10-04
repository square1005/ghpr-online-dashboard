# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery

This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-09-29`.
- Latest date: `2026-09-29`.
- Latest MM percentile: `38.46%`.
- Latest MM lifecycle state: `MM_DISTRIBUTION`.
- Latest MM velocity 8W: `-16.03%`.
- Latest MM acceleration 8W: `-34.62%`.
- Strongest velocity window summary: `mm_velocity_8w average absolute rank correlation 0.181`.
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

mm_velocity_8w average absolute rank correlation 0.181

### 6. Which MM Lifecycle State has the strongest historical sample tendency?

MM_CROWDED_EXPANSION has the largest absolute 8W median following return (6.16%) in this sample.

### 7. What does the current MM Lifecycle State mean?

The latest state is `MM_DISTRIBUTION`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.

### 8. What does the current MM Velocity imply?

Latest 8W velocity is `-16.03%`. It describes recent positioning movement only; it does not independently determine market direction.

### 9. What does the current MM Acceleration imply?

Latest 8W acceleration is `-34.62%`. It describes whether the positioning movement is speeding up or slowing down.

### 10. Which historical MM trajectories are most similar now?

| window   | historical_start_date   | historical_end_date   |   similarity_score |   historical_gold_return_1w |   historical_gold_return_2w |   historical_gold_return_4w |   historical_gold_return_8w |
|:---------|:------------------------|:----------------------|-------------------:|----------------------------:|----------------------------:|----------------------------:|----------------------------:|
| 8W       | 2020-03-17              | 2020-05-12            |            94.7597 |                  0          |                -0.00356619  |                 -0.0297717  |                   0.117713  |
| 8W       | 2014-02-25              | 2014-04-22            |            93.1345 |                 -0.0149231  |                -0.0214717   |                 -0.0234864  |                  -0.0464632 |
| 8W       | 2020-03-24              | 2020-05-19            |            92.7563 |                  0.0233513  |                 0.0233513   |                  0.0393279  |                   0.0505963 |
| 8W       | 2011-03-29              | 2011-05-24            |            92.5029 |                  0.0293282  |                 0.00435182  |                  0.0134398  |                   0.0757062 |
| 8W       | 2020-06-16              | 2020-08-11            |            92.4812 |                 -0.0369619  |                 0.000874253 |                  0.0732878  |                   0.120818  |
| 8W       | 2020-06-23              | 2020-08-18            |            92.3306 |                  0.0343215  |                -0.00390897  |                  0.091762   |                   0.129686  |
| 8W       | 2018-03-06              | 2018-05-01            |            91.6547 |                 -0.02073    |                -0.0322149   |                 -0.0217587  |                  -0.0223455 |
| 8W       | 2021-05-11              | 2021-07-06            |            91.6029 |                  0.0173509  |                 0.00945197  |                 -0.0528928  |                  -0.0228201 |
| 8W       | 2017-05-16              | 2017-07-11            |            91.0947 |                 -0.00353071 |                -0.0263158   |                 -0.0412388  |                  -0.017328  |
| 8W       | 2020-03-31              | 2020-05-26            |            90.8572 |                 -0.0225891  |                 0.000234701 |                 -0.00333233 |                   0.0766705 |

### 11. What happened after the most similar historical trajectories?

- 1W: avg `-0.54%`, median `-0.64%`, win rate `40.00%`.
- 2W: avg `-1.26%`, median `-0.89%`, win rate `30.00%`.
- 4W: avg `-0.84%`, median `-1.64%`, win rate `35.00%`.
- 8W: avg `0.85%`, median `-1.39%`, win rate `40.00%`.

### 12. Should this replace MM Percentile in the Dashboard?

No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.

### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?

Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.

## MM Lifecycle State Analysis

| mm_lifecycle_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:---------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_RESET             |     209 |             -0.00607868 |                -0.00643463 |      0.363636 |             -0.011621   |               -0.0115099   |      0.315789 |             -0.0203806  |                -0.0200868  |      0.248804 |              -0.0326947 |                -0.0337078  |      0.143541 |         0.180106 |        -0.141753  |
| MM_ACCUMULATION      |     135 |              0.0034119  |                 0.00494877 |      0.674074 |              0.00594031 |                0.0100067   |      0.622222 |              0.00563109 |                 0.0138323  |      0.614815 |               0.0100166 |                 0.0106326  |      0.592593 |         0.142329 |        -0.135196  |
| MM_EXPANSION         |     160 |              0.00603311 |                 0.00581611 |      0.6375   |              0.0124044  |                0.010872    |      0.66875  |              0.0240605  |                 0.0247439  |      0.6875   |               0.0420188 |                 0.0386433  |      0.80625  |         0.239115 |        -0.116012  |
| MM_CROWDED_EXPANSION |     106 |              0.00844219 |                 0.00883771 |      0.669811 |              0.0171738  |                0.0184207   |      0.745283 |              0.0368913  |                 0.0345373  |      0.886792 |               0.0611155 |                 0.0616258  |      0.95283  |         0.18041  |        -0.0337237 |
| MM_DISTRIBUTION      |     213 |              0.00115017 |                 0.00208689 |      0.521127 |              0.00235265 |                0.000306423 |      0.511737 |              0.00598881 |                 0.00228371 |      0.507042 |               0.0173882 |                 0.00137021 |      0.521127 |         0.239587 |        -0.115905  |
| MM_NEUTRAL           |      69 |              0.00613398 |                 0.00818202 |      0.661765 |              0.0106738  |                0.0163343   |      0.626866 |              0.0189686  |                 0.0294586  |      0.723077 |               0.0340008 |                 0.030663   |      0.655738 |         0.173598 |        -0.106463  |

## Strongest Lead-Lag Rows

| mm_feature         | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                                              |   abs_rank_correlation |
|:-------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:------------------------------------------------------------|-----------------------:|
| mm_velocity_4w     | 4W             |           0 |      0.483573 |           0.566401 |            837 | same_week_positive_historical_alignment                     |               0.566401 |
| mm_acceleration_4w | 4W             |          -4 |     -0.434895 |          -0.506938 |            833 | gold_or_later_mm_alignment_4w_negative_historical_alignment |               0.506938 |
| mm_acceleration_8w | 8W             |          -8 |     -0.426181 |          -0.479355 |            825 | gold_or_later_mm_alignment_8w_negative_historical_alignment |               0.479355 |
| mm_velocity_8w     | 8W             |           0 |      0.415641 |           0.463548 |            833 | same_week_positive_historical_alignment                     |               0.463548 |
| mm_velocity_4w     | 2W             |           0 |      0.337441 |           0.419732 |            837 | same_week_positive_historical_alignment                     |               0.419732 |
| mm_velocity_12w    | 8W             |           0 |      0.358074 |           0.404761 |            829 | same_week_positive_historical_alignment                     |               0.404761 |
| mm_acceleration_4w | 4W             |           0 |      0.33582  |           0.395149 |            833 | same_week_positive_historical_alignment                     |               0.395149 |
| mm_velocity_8w     | 4W             |           0 |      0.350212 |           0.392917 |            833 | same_week_positive_historical_alignment                     |               0.392917 |

## Method Notes

- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.
- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.
- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.
- All outputs are historical statistics / research reference only.
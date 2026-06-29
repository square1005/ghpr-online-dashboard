# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery

This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-06-23`.
- Latest date: `2026-06-23`.
- Latest MM percentile: `44.23%`.
- Latest MM lifecycle state: `MM_EXPANSION`.
- Latest MM velocity 8W: `23.72%`.
- Latest MM acceleration 8W: `30.77%`.
- Strongest velocity window summary: `mm_velocity_8w average absolute rank correlation 0.184`.
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

mm_velocity_8w average absolute rank correlation 0.184

### 6. Which MM Lifecycle State has the strongest historical sample tendency?

MM_CROWDED_EXPANSION has the largest absolute 8W median following return (6.16%) in this sample.

### 7. What does the current MM Lifecycle State mean?

The latest state is `MM_EXPANSION`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.

### 8. What does the current MM Velocity imply?

Latest 8W velocity is `23.72%`. It describes recent positioning movement only; it does not independently determine market direction.

### 9. What does the current MM Acceleration imply?

Latest 8W acceleration is `30.77%`. It describes whether the positioning movement is speeding up or slowing down.

### 10. Which historical MM trajectories are most similar now?

| window   | historical_start_date   | historical_end_date   |   similarity_score |   historical_gold_return_1w |   historical_gold_return_2w |   historical_gold_return_4w |   historical_gold_return_8w |
|:---------|:------------------------|:----------------------|-------------------:|----------------------------:|----------------------------:|----------------------------:|----------------------------:|
| 8W       | 2012-08-21              | 2012-10-16            |            94.2443 |                -0.0103801   |                -0.0157951   |                  -0.013402  |                   0.0639063 |
| 8W       | 2022-12-06              | 2023-01-31            |            93.4184 |                -0.00227521  |                 0.0116926   |                   0.0488123 |                   0.0905443 |
| 8W       | 2022-11-29              | 2023-01-24            |            92.7764 |                 0.0139996   |                 0.0332871   |                   0.0656271 |                   0.106097  |
| 8W       | 2014-01-21              | 2014-03-18            |            91.8413 |                 0.00928333  |                 0.0158469   |                   0.0258927 |                   0.0939386 |
| 8W       | 2012-08-14              | 2012-10-09            |            91.8346 |                -0.00547185  |                -0.000453594 |                   0.0180159 |                   0.102288  |
| 8W       | 2022-11-22              | 2023-01-17            |            91.0517 |                 0.0190211   |                 0.0366908   |                   0.0502781 |                   0.0971638 |
| 8W       | 2014-01-14              | 2014-03-11            |            90.9226 |                 0.00650318  |                 0.00260611  |                   0.0437176 |                   0.0813524 |
| 8W       | 2020-11-03              | 2020-12-29            |            90.8539 |                 0.000266071 |                 0.0147924   |                   0.0361612 |                  -0.0150904 |
| 8W       | 2020-11-10              | 2021-01-05            |            90.8313 |                 0.038836    |                 0.0391124   |                   0.043778  |                   0.0412178 |
| 8W       | 2016-12-27              | 2017-02-21            |            90.6765 |                 0.011112    |                 0.00267384  |                   0.0224737 |                   0.0881034 |

### 11. What happened after the most similar historical trajectories?

- 1W: avg `0.43%`, median `0.58%`, win rate `70.00%`.
- 2W: avg `0.97%`, median `1.24%`, win rate `75.00%`.
- 4W: avg `3.28%`, median `3.81%`, win rate `90.00%`.
- 8W: avg `6.77%`, median `7.70%`, win rate `95.00%`.

### 12. Should this replace MM Percentile in the Dashboard?

No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.

### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?

Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.

## MM Lifecycle State Analysis

| mm_lifecycle_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:---------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_RESET             |     209 |             -0.00603741 |                -0.00643463 |      0.363636 |             -0.0115586  |                -0.0115099  |      0.320574 |             -0.0204758  |               -0.0190912   |      0.258373 |             -0.0327947  |                -0.0337078  |      0.133971 |         0.17979  |        -0.141753  |
| MM_ACCUMULATION      |     135 |              0.00343376 |                 0.00496373 |      0.681481 |              0.00585467 |                 0.0100067  |      0.622222 |              0.00561029 |                0.0138323   |      0.614815 |              0.00993966 |                 0.011896   |      0.592593 |         0.142329 |        -0.135196  |
| MM_EXPANSION         |     148 |              0.0061705  |                 0.0059532  |      0.635135 |              0.0130527  |                 0.0119998  |      0.675676 |              0.0254588  |                0.024788    |      0.716216 |              0.0446105  |                 0.0383544  |      0.810811 |         0.239115 |        -0.0911685 |
| MM_CROWDED_EXPANSION |     106 |              0.00839223 |                 0.00939511 |      0.669811 |              0.0172474  |                 0.0190197  |      0.764151 |              0.0367427  |                0.0345373   |      0.886792 |              0.0608284  |                 0.0616258  |      0.95283  |         0.179186 |        -0.0348419 |
| MM_DISTRIBUTION      |     212 |              0.00125058 |                 0.00161634 |      0.518868 |              0.00237314 |                -0.00052457 |      0.490566 |              0.00626583 |                0.000718803 |      0.509434 |              0.0177998  |                 0.00289419 |      0.509434 |         0.24908  |        -0.115905  |
| MM_NEUTRAL           |      68 |              0.00640746 |                 0.00915424 |      0.671642 |              0.0110329  |                 0.0167388  |      0.636364 |              0.0194682  |                0.0294857   |      0.71875  |              0.0362926  |                 0.0316098  |      0.666667 |         0.173598 |        -0.0843966 |

## Strongest Lead-Lag Rows

| mm_feature         | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                                              |   abs_rank_correlation |
|:-------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:------------------------------------------------------------|-----------------------:|
| mm_velocity_4w     | 4W             |           0 |      0.491199 |           0.570629 |            823 | same_week_positive_historical_alignment                     |               0.570629 |
| mm_acceleration_4w | 4W             |          -4 |     -0.444399 |          -0.514699 |            819 | gold_or_later_mm_alignment_4w_negative_historical_alignment |               0.514699 |
| mm_acceleration_8w | 8W             |          -8 |     -0.432551 |          -0.48746  |            811 | gold_or_later_mm_alignment_8w_negative_historical_alignment |               0.48746  |
| mm_velocity_8w     | 8W             |           0 |      0.426347 |           0.477097 |            819 | same_week_positive_historical_alignment                     |               0.477097 |
| mm_velocity_12w    | 8W             |           0 |      0.369308 |           0.419202 |            815 | same_week_positive_historical_alignment                     |               0.419202 |
| mm_velocity_4w     | 2W             |           0 |      0.336525 |           0.417085 |            823 | same_week_positive_historical_alignment                     |               0.417085 |
| mm_velocity_8w     | 8W             |           2 |      0.354972 |           0.403621 |            817 | mm_feature_leads_gold_2w_positive_historical_alignment      |               0.403621 |
| mm_velocity_4w     | 2W             |          -2 |      0.353345 |           0.400953 |            823 | gold_or_later_mm_alignment_2w_positive_historical_alignment |               0.400953 |

## Method Notes

- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.
- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.
- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.
- All outputs are historical statistics / research reference only.
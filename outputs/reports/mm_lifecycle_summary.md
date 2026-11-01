# GHPR v0.5-B MM Lifecycle & Lead-Lag Discovery

This report is Historical Lifecycle Research only. It does not create execution logic, market instructions, or financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-10-27`.
- Latest date: `2026-10-27`.
- Latest MM percentile: `24.36%`.
- Latest MM lifecycle state: `MM_RESET`.
- Latest MM velocity 8W: `-33.97%`.
- Latest MM acceleration 8W: `-48.72%`.
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

The latest state is `MM_RESET`. This is a historical positioning label based on MM percentile and 8W velocity, not a directional instruction.

### 8. What does the current MM Velocity imply?

Latest 8W velocity is `-33.97%`. It describes recent positioning movement only; it does not independently determine market direction.

### 9. What does the current MM Acceleration imply?

Latest 8W acceleration is `-48.72%`. It describes whether the positioning movement is speeding up or slowing down.

### 10. Which historical MM trajectories are most similar now?

| window   | historical_start_date   | historical_end_date   |   similarity_score |   historical_gold_return_1w |   historical_gold_return_2w |   historical_gold_return_4w |   historical_gold_return_8w |
|:---------|:------------------------|:----------------------|-------------------:|----------------------------:|----------------------------:|----------------------------:|----------------------------:|
| 8W       | 2018-03-27              | 2018-05-22            |            95.0382 |                 0.00217234  |                 -0.0154726  |                 -0.0298183  |                 -0.0369791  |
| 8W       | 2020-06-30              | 2020-08-25            |            94.3862 |                -0.0447072   |                 -0.0119201  |                 -0.0110563  |                  0.0680922  |
| 8W       | 2012-09-25              | 2012-11-20            |            94.073  |                -0.000579979 |                  0.00530889 |                  0.00872206 |                 -0.0230185  |
| 8W       | 2021-01-26              | 2021-03-23            |            93.8872 |                -0.00335089  |                  0.00477602 |                 -0.0447423  |                 -0.067967   |
| 8W       | 2021-11-09              | 2022-01-04            |            93.5034 |                 0.00204316  |                  0.0144798  |                  0.0167535  |                 -0.00884863 |
| 8W       | 2018-04-03              | 2018-05-29            |            93.4314 |                 0.00541922  |                  0.00760333 |                 -0.00391172 |                 -0.0255853  |
| 8W       | 2022-03-29              | 2022-05-24            |            93.3986 |                 0.0255649   |                  0.0132537  |                 -0.0203245  |                 -0.0244744  |
| 8W       | 2020-07-07              | 2020-09-01            |            93.3974 |                 0.0290157   |                 -0.0169887  |                 -0.0208313  |                  0.0933753  |
| 8W       | 2016-11-15              | 2017-01-10            |            93.3817 |                 0.0205101   |                  0.0412379  |                  0.0237745  |                 -0.0325164  |
| 8W       | 2014-08-05              | 2014-09-30            |            93.3324 |                -0.00859951  |                 -0.0199967  |                 -0.0420986  |                 -0.057243   |

### 11. What happened after the most similar historical trajectories?

- 1W: avg `-0.04%`, median `0.02%`, win rate `50.00%`.
- 2W: avg `-0.14%`, median `-0.28%`, win rate `50.00%`.
- 4W: avg `-1.46%`, median `-1.57%`, win rate `30.00%`.
- 8W: avg `-1.16%`, median `-2.37%`, win rate `30.00%`.

### 12. Should this replace MM Percentile in the Dashboard?

No. v0.5-B adds lifecycle context around the existing 156W MM percentile. It does not replace the homepage MM definition.

### 13. Should GHPR enter a v0.6 Lifecycle Dashboard stage?

Yes, as a research page and monitoring layer. The lifecycle state, velocity, acceleration, and trajectory similarity are useful context fields, but they should stay clearly labeled as historical research.

## MM Lifecycle State Analysis

| mm_lifecycle_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:---------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_RESET             |     212 |             -0.00612031 |                -0.00648177 |      0.358491 |             -0.0116254  |               -0.0115021   |      0.311321 |             -0.0206321  |                -0.0202585  |      0.245283 |              -0.0333914 |                -0.0344878  |      0.141509 |         0.180106 |        -0.141753  |
| MM_ACCUMULATION      |     135 |              0.0034119  |                 0.00494877 |      0.674074 |              0.00594031 |                0.0100067   |      0.622222 |              0.00563109 |                 0.0138323  |      0.614815 |               0.0100166 |                 0.0106326  |      0.592593 |         0.142329 |        -0.135196  |
| MM_EXPANSION         |     160 |              0.00603311 |                 0.00581611 |      0.6375   |              0.0124044  |                0.010872    |      0.66875  |              0.0240605  |                 0.0247439  |      0.6875   |               0.0420188 |                 0.0386433  |      0.80625  |         0.239115 |        -0.116012  |
| MM_CROWDED_EXPANSION |     106 |              0.00844219 |                 0.00883771 |      0.669811 |              0.0171738  |                0.0184207   |      0.745283 |              0.0368913  |                 0.0345373  |      0.886792 |               0.0611155 |                 0.0616258  |      0.95283  |         0.18041  |        -0.0337237 |
| MM_DISTRIBUTION      |     214 |              0.00115306 |                 0.00206502 |      0.523364 |              0.00213953 |                0.000270562 |      0.509346 |              0.00569565 |                 0.00156096 |      0.504673 |               0.0170397 |                 0.00109799 |      0.518692 |         0.239587 |        -0.115905  |
| MM_NEUTRAL           |      69 |              0.00613398 |                 0.00818202 |      0.661765 |              0.0106738  |                0.0163343   |      0.626866 |              0.0189686  |                 0.0294586  |      0.723077 |               0.0340008 |                 0.030663   |      0.655738 |         0.173598 |        -0.106463  |

## Strongest Lead-Lag Rows

| mm_feature         | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                                              |   abs_rank_correlation |
|:-------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:------------------------------------------------------------|-----------------------:|
| mm_velocity_4w     | 4W             |           0 |      0.486205 |           0.569472 |            841 | same_week_positive_historical_alignment                     |               0.569472 |
| mm_acceleration_4w | 4W             |          -4 |     -0.433102 |          -0.503622 |            837 | gold_or_later_mm_alignment_4w_negative_historical_alignment |               0.503622 |
| mm_acceleration_8w | 8W             |          -8 |     -0.429183 |          -0.482712 |            829 | gold_or_later_mm_alignment_8w_negative_historical_alignment |               0.482712 |
| mm_velocity_8w     | 8W             |           0 |      0.420556 |           0.468425 |            837 | same_week_positive_historical_alignment                     |               0.468425 |
| mm_velocity_4w     | 2W             |           0 |      0.339224 |           0.422119 |            841 | same_week_positive_historical_alignment                     |               0.422119 |
| mm_velocity_12w    | 8W             |           0 |      0.360163 |           0.407593 |            833 | same_week_positive_historical_alignment                     |               0.407593 |
| mm_velocity_8w     | 4W             |           0 |      0.354361 |           0.397513 |            837 | same_week_positive_historical_alignment                     |               0.397513 |
| mm_acceleration_4w | 4W             |           0 |      0.336032 |           0.396153 |            837 | same_week_positive_historical_alignment                     |               0.396153 |

## Method Notes

- `lag_weeks > 0` means the MM feature is shifted earlier and compared with current gold following returns.
- `lag_weeks < 0` means later MM feature values are compared with current gold following returns.
- Similarity uses MM percentile trajectory paths and excludes the most recent 52 weeks by default.
- All outputs are historical statistics / research reference only.
# GHPR v0.6.2 MM Velocity Window Discovery

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-11-03`.
- Best Long velocity window: `2W`.
- Best Short velocity window: `2W`.
- Best Net velocity window: `26W`.
- Most stable feature/window: `short 4W` with average stability score `95.5`.
- Best 4W information row: `long 26W`.
- Best 8W information row: `short 2W`.
- Current 8W decision: `review alternative window before replacing anything`.

## Required Questions

### 1. Why not assume 8W is best?

8W is a reasonable swing window, but it is a design choice. A shorter window can react faster, while a longer window can reduce noise. This audit compares information, stability, train/test consistency, and interpretability before making any dashboard recommendation.

### 2. What market rhythm do 2W / 4W / 8W / 12W / 26W represent?

- 2W: very short-term positioning movement; responsive but noisy.
- 4W: short-term velocity; useful for faster shifts.
- 8W: swing velocity; current GHPR baseline.
- 12W: medium swing velocity; slower but often more stable than 4W.
- 26W: medium-term positioning cycle; more stable but slower to react.

### 3. Long Velocity best window

`2W` based on average 4W/8W total score.

### 4. Short Velocity best window

`2W` based on average 4W/8W total score.

### 5. Net Velocity best window

`26W` based on average 4W/8W total score.

### 6. Most stable window

`short 4W` has the highest stability score among feature/window pairs.

### 7. Best information for 4W following return

`long 26W` has the highest information score for 4W.

### 8. Best information for 8W following return

`short 2W` has the highest information score for 8W.

### 9. Train / Test consistency

Direction consistency rate: `100.00%` across all feature/window/horizon rows.

### 10. Should the Dashboard continue using 8W?

Do not replace the current 8W dashboard definition yet. If 8W remains near the top score, keep it as the baseline while reviewing this report. If an alternative clearly dominates, treat it as a v0.6.3 candidate rather than an automatic replacement.

### 11. If not 8W, should it be 4W / 12W / 26W?

The strongest overall candidate in this audit is `short 2W`. A formal replacement should wait for human review because each window captures a different market rhythm.

### 12. Should future Dashboard show short-term, swing, and medium-term velocity?

Yes, as a research layer. A compact view with 4W short-term, 8W swing, and 12W or 26W medium-term velocity can show whether positioning movement is accelerating across time scales.

### 13. Research limitations

- This audit uses historical weekly data only.
- It compares simple correlations, rank correlations, spreads, buckets, and train/test direction consistency.
- It does not include Producer, OI, Options, OGR, or MMP.
- It does not replace the existing dashboard definition.

## Recommended Window Summary

| feature_group   | window   |   avg_total_score |   avg_information_score |   avg_stability_score |   avg_train_test_score |
|:----------------|:---------|------------------:|------------------------:|----------------------:|-----------------------:|
| long            | 2W       |           61.6417 |                 50.0417 |              44.5     |                    100 |
| long            | 26W      |           61.5583 |                 45.875  |              46.8333  |                    100 |
| long            | 4W       |           60.8583 |                 30.5833 |              60.5     |                    100 |
| long            | 12W      |           60.225  |                 23.5833 |              67.1667  |                    100 |
| long            | 8W       |           50.9667 |                 14.5    |              42.6667  |                    100 |
| net             | 26W      |           52.8583 |                 39.75   |              21.8333  |                    100 |
| net             | 2W       |           51.1083 |                 43.9167 |              12.1667  |                    100 |
| net             | 4W       |           50.8667 |                 26.125  |              27.6667  |                    100 |
| net             | 12W      |           49.575  |                 27.375  |              18.5     |                    100 |
| net             | 8W       |           43.5583 |                 17.75   |               7.83333 |                    100 |
| short           | 2W       |           74.925  |                 61.7917 |              78.8333  |                    100 |
| short           | 4W       |           74.2417 |                 42.1667 |              95.5     |                    100 |
| short           | 8W       |           71.1083 |                 36.625  |              87.8333  |                    100 |
| short           | 12W      |           69.1583 |                 35.2917 |              84.1667  |                    100 |
| short           | 26W      |           65.0417 |                 42.2917 |              66.5     |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.110482 |          -0.147106 |                    0.147106 |       -0.00999543 |            869 |            0.123989 |              0.0787802 |            0.130815 |                   82 |           87.8333 |         -0.157403 |       -0.124153  |             -0.0086996  |            -0.00724749 | True                    |             92.75   |                100 |                       95 |       93.5583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.115678 |          -0.139413 |                    0.139413 |       -0.00878673 |            865 |            0.122647 |              0.0833333 |            0.132108 |                   78 |           84.1667 |         -0.157701 |       -0.113984  |             -0.00952048 |            -0.00300175 | True                    |             96.0833 |                100 |                       90 |       93.475  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.167842 |          -0.19535  |                    0.19535  |       -0.0120995  |            873 |            0.124402 |              0.0833333 |            0.142983 |                   78 |           95.5    |         -0.255315 |       -0.121543  |             -0.0155619  |            -0.00797665 | True                    |             84.5    |                100 |                       85 |       91.175  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.127429 |          -0.129053 |                    0.129053 |       -0.00711534 |            851 |            0.116301 |              0.0768867 |            0.120464 |                   72 |           66.5    |         -0.132635 |       -0.110002  |             -0.00639511 |            -0.00879319 | True                    |            100      |                100 |                       65 |       88.125  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.173279 |          -0.205258 |                    0.205258 |       -0.0179373  |            869 |            0.123989 |              0.0787802 |            0.130815 |                   82 |           87.8333 |         -0.250623 |       -0.140657  |             -0.0211944  |            -0.0123522  | True                    |             78.25   |                100 |                       95 |       87.7583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.123968 |           0.161716 |                    0.161716 |        0.00869133 |            865 |            0.111834 |              0.0705128 |            0.124428 |                   76 |           67.1667 |          0.143257 |        0.182209  |              0.00596931 |             0.0114813  | True                    |             91.25   |                100 |                       90 |       87.2917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.174276 |          -0.218053 |                    0.218053 |       -0.0184733  |            865 |            0.122647 |              0.0833333 |            0.132108 |                   78 |           84.1667 |         -0.265731 |       -0.15564   |             -0.019428   |            -0.013673   | True                    |             73.8333 |                100 |                       90 |       84.575  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.11566  |          -0.13243  |                    0.13243  |       -0.027101   |            875 |            0.116283 |              0.0733799 |            0.132374 |                   78 |           78.8333 |         -0.210588 |       -0.0471358 |             -0.0297236  |            -0.0182261  | True                    |             85.5    |                100 |                       55 |       84.4083 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.198416 |          -0.211785 |                    0.211785 |       -0.0404736  |            873 |            0.124402 |              0.0833333 |            0.142983 |                   78 |           95.5    |         -0.341137 |       -0.0599378 |             -0.0561075  |            -0.0183316  | True                    |             65.5    |                100 |                       85 |       83.575  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.140434 |           0.14885  |                    0.14885  |        0.00843829 |            851 |            0.109959 |              0.0769231 |            0.111106 |                   64 |           46.8333 |          0.141939 |        0.143628  |              0.00541405 |             0.0108926  | True                    |             94      |                100 |                       65 |       80.8083 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.19631  |          -0.196164 |                    0.196164 |       -0.0170618  |            851 |            0.116301 |              0.0768867 |            0.120464 |                   72 |           66.5    |         -0.234339 |       -0.139589  |             -0.0212859  |            -0.0124778  | True                    |             80.5    |                100 |                       65 |       80.325  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.272166 |          -0.307854 |                    0.307854 |       -0.0274525  |            873 |            0.124402 |              0.0833333 |            0.142983 |                   78 |           95.5    |         -0.417411 |       -0.166233  |             -0.0338571  |            -0.0167288  | True                    |             51.8333 |                100 |                       85 |       78.1083 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.215513 |           0.252552 |                    0.252552 |        0.0206477  |            865 |            0.111834 |              0.0705128 |            0.124428 |                   76 |           67.1667 |          0.238416 |        0.263675  |              0.0144699  |             0.0206447  | True                    |             67.25   |                100 |                       90 |       77.6917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.259467 |          -0.284207 |                    0.284207 |       -0.0395242  |            869 |            0.123989 |              0.0787802 |            0.130815 |                   82 |           87.8333 |         -0.379557 |       -0.15008   |             -0.0488568  |            -0.0146973  | True                    |             52      |                100 |                       95 |       77.2583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.220548 |          -0.274285 |                    0.274285 |       -0.0164399  |            875 |            0.116283 |              0.0733799 |            0.132374 |                   78 |           78.8333 |         -0.336663 |       -0.195863  |             -0.0179628  |            -0.0093026  | True                    |             67      |                100 |                       55 |       77.0083 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.218954 |           0.261258 |                    0.261258 |        0.0153722  |            873 |            0.111422 |              0.0734635 |            0.123831 |                   73 |           60.5    |          0.258117 |        0.263191  |              0.016024   |             0.0172413  | True                    |             70.3333 |                100 |                       85 |       76.7583 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.181159 |           0.222395 |                    0.222395 |        0.0113373  |            869 |            0.105126 |              0.0641026 |            0.116002 |                   58 |           42.6667 |          0.197534 |        0.250209  |              0.0116333  |             0.0128857  | True                    |             76.4167 |                100 |                       95 |       75.7333 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.115201 |           0.156306 |                    0.156306 |        0.00988245 |            834 |            0.10272  |              0.0705128 |            0.106314 |                   50 |           18.5    |          0.127902 |        0.179642  |              0.00341581 |             0.0127854  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.138641 |           0.144054 |                    0.144054 |        0.0110204  |            820 |            0.102755 |              0.0705128 |            0.100768 |                   47 |           21.8333 |          0.134141 |        0.142548  |              0.0076014  |             0.012236   | True                    |             93.25   |                100 |                       65 |       74.2583 | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 26W      | mm_long_velocity_26w  | 2W        |      0.226474 |           0.221305 |                    0.221305 |        0.0163424  |            851 |            0.109959 |              0.0769231 |            0.111106 |                   64 |           46.8333 |          0.230446 |        0.200233  |              0.0174786  |             0.016404   | True                    |             75.1667 |                100 |                       65 |       73.275  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
# GHPR v0.6.2 MM Velocity Window Discovery

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-10-06`.
- Best Long velocity window: `26W`.
- Best Short velocity window: `2W`.
- Best Net velocity window: `4W`.
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

`26W` based on average 4W/8W total score.

### 4. Short Velocity best window

`2W` based on average 4W/8W total score.

### 5. Net Velocity best window

`4W` based on average 4W/8W total score.

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
| long            | 26W      |           61.5583 |                 45.875  |              46.8333  |                    100 |
| long            | 2W       |           61.425  |                 49.5    |              44.5     |                    100 |
| long            | 4W       |           60.8583 |                 30.5833 |              60.5     |                    100 |
| long            | 12W      |           60.4417 |                 24.125  |              67.1667  |                    100 |
| long            | 8W       |           51.1833 |                 15.0417 |              42.6667  |                    100 |
| net             | 4W       |           52      |                 26.6667 |              31.3333  |                    100 |
| net             | 26W      |           51.8417 |                 39.5    |              18.1667  |                    100 |
| net             | 2W       |           51.325  |                 44.4583 |              12.1667  |                    100 |
| net             | 12W      |           49.575  |                 27.375  |              18.5     |                    100 |
| net             | 8W       |           43.5583 |                 17.75   |               7.83333 |                    100 |
| short           | 2W       |           75.9417 |                 62.0417 |              82.5     |                    100 |
| short           | 4W       |           74.1417 |                 41.9167 |              95.5     |                    100 |
| short           | 8W       |           71.325  |                 37.1667 |              87.8333  |                    100 |
| short           | 12W      |           69.375  |                 35.8333 |              84.1667  |                    100 |
| short           | 26W      |           64.0083 |                 42      |              62.8333  |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.108877 |          -0.144284 |                    0.144284 |       -0.00974914 |            865 |            0.124348 |              0.0822425 |            0.131007 |                   82 |           87.8333 |         -0.157403 |       -0.116128  |             -0.0086996  |            -0.00719616 | True                    |             93.8333 |                100 |                       95 |       93.9917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.11414  |          -0.13674  |                    0.13674  |       -0.00878569 |            861 |            0.123069 |              0.0833333 |            0.132266 |                   78 |           84.1667 |         -0.157701 |       -0.106567  |             -0.00952048 |            -0.00294197 | True                    |             96.0833 |                100 |                       90 |       93.475  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.166748 |          -0.19239  |                    0.19239  |       -0.0117205  |            869 |            0.124828 |              0.0833333 |            0.143172 |                   78 |           95.5    |         -0.255315 |       -0.11326   |             -0.0155619  |            -0.00737076 | True                    |             84.5    |                100 |                       85 |       91.175  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.171747 |          -0.202984 |                    0.202984 |       -0.0179537  |            865 |            0.124348 |              0.0822425 |            0.131007 |                   82 |           87.8333 |         -0.250623 |       -0.133798  |             -0.0211944  |            -0.01173    | True                    |             78.25   |                100 |                       95 |       87.7583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.121471 |           0.158081 |                    0.158081 |        0.00839477 |            861 |            0.112168 |              0.0705128 |            0.124602 |                   76 |           67.1667 |          0.143257 |        0.174306  |              0.00596931 |             0.0115461  | True                    |             91.8333 |                100 |                       90 |       87.525  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.128912 |          -0.131637 |                    0.131637 |       -0.00711534 |            847 |            0.11654  |              0.0769231 |            0.120666 |                   72 |           62.8333 |         -0.132635 |       -0.114434  |             -0.00639511 |            -0.0091122  | True                    |             98.9167 |                100 |                       65 |       86.775  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.114495 |          -0.129841 |                    0.129841 |       -0.0268315  |            871 |            0.116574 |              0.074056  |            0.132588 |                   78 |           82.5    |         -0.210588 |       -0.0392555 |             -0.0297236  |            -0.0176122  | True                    |             86      |                100 |                       55 |       85.525  | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.172787 |          -0.21585  |                    0.21585  |       -0.0184632  |            861 |            0.123069 |              0.0833333 |            0.132266 |                   78 |           84.1667 |         -0.265731 |       -0.149101  |             -0.019428   |            -0.0136129  | True                    |             73.8333 |                100 |                       90 |       84.575  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.195946 |          -0.207049 |                    0.207049 |       -0.0404645  |            869 |            0.124828 |              0.0833333 |            0.143172 |                   78 |           95.5    |         -0.341137 |       -0.0447941 |             -0.0561075  |            -0.0181538  | True                    |             65.5    |                100 |                       85 |       83.575  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.13973  |           0.147733 |                    0.147733 |        0.00857283 |            847 |            0.110206 |              0.0769231 |            0.111294 |                   64 |           46.8333 |          0.141939 |        0.139693  |              0.00541405 |             0.00980898 | True                    |             93.4167 |                100 |                       65 |       80.575  | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.198111 |          -0.198878 |                    0.198878 |       -0.0170618  |            847 |            0.11654  |              0.0769231 |            0.120666 |                   72 |           62.8333 |         -0.234339 |       -0.144773  |             -0.0212859  |            -0.0121165  | True                    |             80.5    |                100 |                       65 |       79.4083 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.271351 |          -0.305608 |                    0.305608 |       -0.0274305  |            869 |            0.124828 |              0.0833333 |            0.143172 |                   78 |           95.5    |         -0.417411 |       -0.158567  |             -0.0338571  |            -0.01692    | True                    |             51.8333 |                100 |                       85 |       78.1083 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.213167 |           0.249494 |                    0.249494 |        0.0205972  |            861 |            0.112168 |              0.0705128 |            0.124602 |                   76 |           67.1667 |          0.238416 |        0.256896  |              0.0144699  |             0.0209202  | True                    |             67.8333 |                100 |                       90 |       77.925  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.220267 |          -0.27328  |                    0.27328  |       -0.0164962  |            871 |            0.116574 |              0.074056  |            0.132588 |                   78 |           82.5    |         -0.336663 |       -0.193189  |             -0.0179628  |            -0.00910055 | True                    |             65.9167 |                100 |                       55 |       77.4917 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.257829 |          -0.28175  |                    0.28175  |       -0.039239   |            865 |            0.124348 |              0.0822425 |            0.131007 |                   82 |           87.8333 |         -0.379557 |       -0.140898  |             -0.0488568  |            -0.0133913  | True                    |             52      |                100 |                       95 |       77.2583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.178412 |           0.218433 |                    0.218433 |        0.0102218  |            865 |            0.105294 |              0.0641026 |            0.11624  |                   58 |           42.6667 |          0.197534 |        0.240951  |              0.0116333  |             0.0121261  | True                    |             79.1667 |                100 |                       95 |       76.8333 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.217937 |           0.258747 |                    0.258747 |        0.0151436  |            869 |            0.111758 |              0.0747104 |            0.124003 |                   73 |           60.5    |          0.258117 |        0.256806  |              0.016024   |             0.0172413  | True                    |             70.3333 |                100 |                       85 |       76.7583 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.112118 |           0.152276 |                    0.152276 |        0.00908894 |            830 |            0.102814 |              0.0705128 |            0.10654  |                   50 |           18.5    |          0.127902 |        0.169938  |              0.00341581 |             0.0123958  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| long            | 26W      | mm_long_velocity_26w  | 2W        |      0.225962 |           0.220597 |                    0.220597 |        0.0164303  |            847 |            0.110206 |              0.0769231 |            0.111294 |                   64 |           46.8333 |          0.230446 |        0.197752  |              0.0174786  |             0.0158279  | True                    |             74.0833 |                100 |                       65 |       72.8417 | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.13875  |           0.144536 |                    0.144536 |        0.0110204  |            816 |            0.102952 |              0.0705128 |            0.100939 |                   47 |           18.1667 |          0.134141 |        0.143177  |              0.0076014  |             0.0125442  | True                    |             91.5833 |                100 |                       65 |       72.675  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
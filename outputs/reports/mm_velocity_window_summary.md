# GHPR v0.6.2 MM Velocity Window Discovery

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-06-09`.
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
| long            | 2W       |           62.5583 |                 50.0417 |              48.1667  |                    100 |
| long            | 26W      |           62.425  |                 48.0417 |              46.8333  |                    100 |
| long            | 4W       |           60.6417 |                 30.0417 |              60.5     |                    100 |
| long            | 12W      |           60.2417 |                 23.625  |              67.1667  |                    100 |
| long            | 8W       |           50.9333 |                 16.7083 |              39       |                    100 |
| net             | 26W      |           53.8583 |                 42.25   |              21.8333  |                    100 |
| net             | 4W       |           50.7667 |                 25.875  |              27.6667  |                    100 |
| net             | 2W       |           50.3083 |                 41.9167 |              12.1667  |                    100 |
| net             | 12W      |           49.1583 |                 26.3333 |              18.5     |                    100 |
| net             | 8W       |           43.775  |                 18.2917 |               7.83333 |                    100 |
| short           | 2W       |           74.375  |                 60.4167 |              78.8333  |                    100 |
| short           | 4W       |           71.925  |                 36.375  |              95.5     |                    100 |
| short           | 8W       |           70.2417 |                 34.4583 |              87.8333  |                    100 |
| short           | 12W      |           69.175  |                 35.3333 |              84.1667  |                    100 |
| short           | 26W      |           63.9083 |                 39.4583 |              66.5     |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.116732 |          -0.139521 |                    0.139521 |       -0.00749883 |            843 |            0.124375 |              0.0833333 |            0.133131 |                   78 |           84.1667 |         -0.157701 |       -0.111773  |             -0.00952048 |            -0.00272907 | True                    |             98.9167 |                100 |                       90 |       94.6083 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.116755 |          -0.151921 |                    0.151921 |       -0.00988847 |            847 |            0.125584 |              0.0833333 |            0.131941 |                   82 |           87.8333 |         -0.157403 |       -0.133783  |             -0.0086996  |            -0.0102442  | True                    |             91.6667 |                100 |                       95 |       93.125  | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.171506 |          -0.194966 |                    0.194966 |       -0.0111888  |            851 |            0.12628  |              0.0833333 |            0.144198 |                   78 |           95.5    |         -0.255315 |       -0.113404  |             -0.0155619  |            -0.00580736 | True                    |             86.6667 |                100 |                       85 |       92.0417 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.131061 |          -0.131831 |                    0.131831 |       -0.00753627 |            829 |            0.11816  |              0.0769231 |            0.121387 |                   72 |           66.5    |         -0.132635 |       -0.115094  |             -0.00639511 |            -0.00686424 | True                    |             99.4167 |                100 |                       65 |       87.8917 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.125227 |           0.166014 |                    0.166014 |        0.00778932 |            843 |            0.113417 |              0.0705128 |            0.125522 |                   76 |           67.1667 |          0.143257 |        0.192604  |              0.00596931 |             0.00954525 | True                    |             91.25   |                100 |                       90 |       87.2917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.181907 |          -0.215636 |                    0.215636 |       -0.0199664  |            847 |            0.125584 |              0.0833333 |            0.131941 |                   82 |           87.8333 |         -0.250623 |       -0.160351  |             -0.0211944  |            -0.0157075  | True                    |             77.0833 |                100 |                       95 |       87.2917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.176984 |          -0.222177 |                    0.222177 |       -0.0184835  |            843 |            0.124375 |              0.0833333 |            0.133131 |                   78 |           84.1667 |         -0.265731 |       -0.157863  |             -0.019428   |            -0.011855   | True                    |             72.8333 |                100 |                       90 |       84.175  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.123068 |          -0.139766 |                    0.139766 |       -0.028695   |            853 |            0.117901 |              0.0769231 |            0.133552 |                   78 |           78.8333 |         -0.210588 |       -0.0572245 |             -0.0297236  |            -0.0195791  | True                    |             83.25   |                100 |                       55 |       83.5083 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.200605 |          -0.202727 |                    0.202727 |       -0.0170987  |            829 |            0.11816  |              0.0769231 |            0.121387 |                   72 |           66.5    |         -0.234339 |       -0.150452  |             -0.0212859  |            -0.0120437  | True                    |             82.1667 |                100 |                       65 |       80.9917 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.20955  |          -0.221213 |                    0.221213 |       -0.0453354  |            851 |            0.12628  |              0.0833333 |            0.144198 |                   78 |           95.5    |         -0.341137 |       -0.068073  |             -0.0561075  |            -0.0198357  | True                    |             58.75   |                100 |                       85 |       80.875  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.137406 |           0.146589 |                    0.146589 |        0.00836454 |            829 |            0.111247 |              0.0769231 |            0.112022 |                   64 |           46.8333 |          0.141939 |        0.136486  |              0.00541405 |             0.00764789 | True                    |             93.9167 |                100 |                       65 |       80.775  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.279661 |          -0.313364 |                    0.313364 |       -0.0285845  |            851 |            0.12628  |              0.0833333 |            0.144198 |                   78 |           95.5    |         -0.417411 |       -0.17049   |             -0.0338571  |            -0.016817   | True                    |             52.4167 |                100 |                       85 |       78.3417 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.218938 |           0.258141 |                    0.258141 |        0.0205388  |            843 |            0.113417 |              0.0705128 |            0.125522 |                   76 |           67.1667 |          0.238416 |        0.279118  |              0.0144699  |             0.0176688  | True                    |             67.8333 |                100 |                       90 |       77.925  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.227274 |          -0.275256 |                    0.275256 |       -0.0161409  |            853 |            0.117901 |              0.0769231 |            0.133552 |                   78 |           78.8333 |         -0.336663 |       -0.193553  |             -0.0179628  |            -0.00814319 | True                    |             67.5833 |                100 |                       55 |       77.2417 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.220834 |           0.263132 |                    0.263132 |        0.0155099  |            851 |            0.113182 |              0.0769231 |            0.1248   |                   73 |           60.5    |          0.258117 |        0.265697  |              0.016024   |             0.0167258  | True                    |             71.4167 |                100 |                       85 |       77.1917 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.277658 |          -0.300519 |                    0.300519 |       -0.0407888  |            847 |            0.125584 |              0.0833333 |            0.131941 |                   82 |           87.8333 |         -0.379557 |       -0.177017  |             -0.0488568  |            -0.0250052  | True                    |             50.4167 |                100 |                       95 |       76.625  | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.114109 |           0.157827 |                    0.157827 |        0.00890714 |            812 |            0.10346  |              0.0693834 |            0.107439 |                   50 |           18.5    |          0.127902 |        0.184419  |              0.00341581 |             0.0108754  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.18073  |           0.222955 |                    0.222955 |        0.0109569  |            847 |            0.106413 |              0.0641026 |            0.117113 |                   58 |           39      |          0.197534 |        0.252119  |              0.0116333  |             0.0143089  | True                    |             76.4167 |                100 |                       95 |       74.8167 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.135884 |           0.141526 |                    0.141526 |        0.00999985 |            798 |            0.103701 |              0.0705128 |            0.101423 |                   46 |           21.8333 |          0.134141 |        0.137546  |              0.0076014  |             0.0116609  | True                    |             93.25   |                100 |                       65 |       74.2583 | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 26W      | mm_long_velocity_26w  | 2W        |      0.221369 |           0.218035 |                    0.218035 |        0.017397   |            829 |            0.111247 |              0.0769231 |            0.112022 |                   64 |           46.8333 |          0.230446 |        0.190763  |              0.0174786  |             0.015426   | True                    |             76.1667 |                100 |                       65 |       73.675  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
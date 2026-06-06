# GHPR v0.6.2 MM Velocity Window Discovery

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-05-26`.
- Best Long velocity window: `26W`.
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

`26W` based on average 4W/8W total score.

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
| long            | 26W      |           62.5417 |                 48.3333 |              46.8333  |                    100 |
| long            | 2W       |           61.425  |                 49.5    |              44.5     |                    100 |
| long            | 4W       |           60.6417 |                 30.0417 |              60.5     |                    100 |
| long            | 12W      |           60.4583 |                 24.1667 |              67.1667  |                    100 |
| long            | 8W       |           51.9667 |                 17      |              42.6667  |                    100 |
| net             | 26W      |           53.8583 |                 42.25   |              21.8333  |                    100 |
| net             | 4W       |           50.7667 |                 25.875  |              27.6667  |                    100 |
| net             | 2W       |           50.0917 |                 41.375  |              12.1667  |                    100 |
| net             | 12W      |           49.1583 |                 26.3333 |              18.5     |                    100 |
| net             | 8W       |           43.775  |                 18.2917 |               7.83333 |                    100 |
| short           | 2W       |           74.1583 |                 59.875  |              78.8333  |                    100 |
| short           | 4W       |           71.7083 |                 35.8333 |              95.5     |                    100 |
| short           | 8W       |           69.7917 |                 33.3333 |              87.8333  |                    100 |
| short           | 12W      |           69.5083 |                 36.1667 |              84.1667  |                    100 |
| short           | 26W      |           64.125  |                 40      |              66.5     |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.116914 |          -0.139916 |                    0.139916 |       -0.00749883 |            842 |            0.12434  |              0.0833333 |            0.133206 |                   78 |           84.1667 |         -0.157701 |       -0.112384  |             -0.00952048 |            -0.00272907 | True                    |             98.9167 |                100 |                       90 |       94.6083 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.117168 |          -0.152711 |                    0.152711 |       -0.010151   |            846 |            0.125498 |              0.0833333 |            0.131995 |                   82 |           87.8333 |         -0.157403 |       -0.135759  |             -0.0086996  |            -0.0105156  | True                    |             91.0833 |                100 |                       95 |       92.8917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.171944 |          -0.195875 |                    0.195875 |       -0.011333   |            850 |            0.126391 |              0.0833333 |            0.144247 |                   78 |           95.5    |         -0.255315 |       -0.115773  |             -0.0155619  |            -0.00722515 | True                    |             86.6667 |                100 |                       85 |       92.0417 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.131023 |          -0.131742 |                    0.131742 |       -0.00753627 |            828 |            0.118264 |              0.0769231 |            0.121423 |                   72 |           66.5    |         -0.132635 |       -0.114623  |             -0.00639511 |            -0.00686424 | True                    |             99.4167 |                100 |                       65 |       87.8917 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.125313 |           0.166273 |                    0.166273 |        0.00778932 |            842 |            0.113544 |              0.0705128 |            0.125542 |                   76 |           67.1667 |          0.143257 |        0.193067  |              0.00596931 |             0.00954525 | True                    |             91.25   |                100 |                       90 |       87.2917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.182338 |          -0.216471 |                    0.216471 |       -0.0205117  |            846 |            0.125498 |              0.0833333 |            0.131995 |                   82 |           87.8333 |         -0.250623 |       -0.162598  |             -0.0211944  |            -0.0165198  | True                    |             77.0833 |                100 |                       95 |       87.2917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.177172 |          -0.222559 |                    0.222559 |       -0.0184835  |            842 |            0.12434  |              0.0833333 |            0.133206 |                   78 |           84.1667 |         -0.265731 |       -0.158577  |             -0.019428   |            -0.011855   | True                    |             73.9167 |                100 |                       90 |       84.6083 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.124433 |          -0.141804 |                    0.141804 |       -0.0290272  |            852 |            0.117889 |              0.0769231 |            0.13363  |                   78 |           78.8333 |         -0.210588 |       -0.0624536 |             -0.0297236  |            -0.0195791  | True                    |             82.1667 |                100 |                       55 |       83.075  | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.200574 |          -0.202636 |                    0.202636 |       -0.0170987  |            828 |            0.118264 |              0.0769231 |            0.121423 |                   72 |           66.5    |         -0.234339 |       -0.150149  |             -0.0212859  |            -0.0120437  | True                    |             83.25   |                100 |                       65 |       81.425  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.137272 |           0.146342 |                    0.146342 |        0.00833461 |            828 |            0.111366 |              0.0769231 |            0.112037 |                   64 |           46.8333 |          0.141939 |        0.135397  |              0.00541405 |             0.00764789 | True                    |             93.9167 |                100 |                       65 |       80.775  | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.210535 |          -0.222887 |                    0.222887 |       -0.0456054  |            850 |            0.126391 |              0.0833333 |            0.144247 |                   78 |           95.5    |         -0.341137 |       -0.072201  |             -0.0561075  |            -0.0204495  | True                    |             57.6667 |                100 |                       85 |       80.4417 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.280137 |          -0.314326 |                    0.314326 |       -0.028812   |            850 |            0.126391 |              0.0833333 |            0.144247 |                   78 |           95.5    |         -0.417411 |       -0.172904  |             -0.0338571  |            -0.0184772  | True                    |             52.4167 |                100 |                       85 |       78.3417 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.219032 |           0.258505 |                    0.258505 |        0.0205388  |            842 |            0.113544 |              0.0705128 |            0.125542 |                   76 |           67.1667 |          0.238416 |        0.279997  |              0.0144699  |             0.0176688  | True                    |             67.8333 |                100 |                       90 |       77.925  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.228008 |          -0.276496 |                    0.276496 |       -0.0168812  |            852 |            0.117889 |              0.0769231 |            0.13363  |                   78 |           78.8333 |         -0.336663 |       -0.196733  |             -0.0179628  |            -0.00814319 | True                    |             67.5833 |                100 |                       55 |       77.2417 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.220966 |           0.263569 |                    0.263569 |        0.0155415  |            850 |            0.1133   |              0.0769231 |            0.124826 |                   73 |           60.5    |          0.258117 |        0.266973  |              0.016024   |             0.0167258  | True                    |             71.4167 |                100 |                       85 |       77.1917 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.278367 |          -0.301774 |                    0.301774 |       -0.041368   |            846 |            0.125498 |              0.0833333 |            0.131995 |                   82 |           87.8333 |         -0.379557 |       -0.180079  |             -0.0488568  |            -0.0252156  | True                    |             48.75   |                100 |                       95 |       75.9583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.180935 |           0.223547 |                    0.223547 |        0.0109569  |            846 |            0.106539 |              0.0641026 |            0.117125 |                   58 |           42.6667 |          0.197534 |        0.253668  |              0.0116333  |             0.0143089  | True                    |             76.4167 |                100 |                       95 |       75.7333 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.11426  |           0.158295 |                    0.158295 |        0.00890714 |            811 |            0.103516 |              0.0695175 |            0.107493 |                   50 |           18.5    |          0.127902 |        0.185564  |              0.00341581 |             0.0108754  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.135731 |           0.141212 |                    0.141212 |        0.00999985 |            797 |            0.103815 |              0.0705128 |            0.101435 |                   46 |           21.8333 |          0.134141 |        0.136269  |              0.0076014  |             0.0116609  | True                    |             94.9167 |                100 |                       65 |       74.925  | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 26W      | mm_long_velocity_26w  | 2W        |      0.221251 |           0.217864 |                    0.217864 |        0.017394   |            828 |            0.111366 |              0.0769231 |            0.112037 |                   64 |           46.8333 |          0.230446 |        0.190071  |              0.0174786  |             0.015426   | True                    |             76.1667 |                100 |                       65 |       73.675  | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
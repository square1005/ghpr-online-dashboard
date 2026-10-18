# GHPR v0.6.2 MM Velocity Window Discovery

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-10-13`.
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
| long            | 26W      |           61.5583 |                 45.875  |              46.8333  |                    100 |
| long            | 2W       |           61.425  |                 49.5    |              44.5     |                    100 |
| long            | 4W       |           60.8583 |                 30.5833 |              60.5     |                    100 |
| long            | 12W      |           60.4417 |                 24.125  |              67.1667  |                    100 |
| long            | 8W       |           51.1833 |                 15.0417 |              42.6667  |                    100 |
| net             | 26W      |           52.6417 |                 39.2083 |              21.8333  |                    100 |
| net             | 2W       |           51.325  |                 44.4583 |              12.1667  |                    100 |
| net             | 4W       |           51.0833 |                 26.6667 |              27.6667  |                    100 |
| net             | 12W      |           49.575  |                 27.375  |              18.5     |                    100 |
| net             | 8W       |           43.5583 |                 17.75   |               7.83333 |                    100 |
| short           | 2W       |           75.025  |                 62.0417 |              78.8333  |                    100 |
| short           | 4W       |           74.025  |                 41.625  |              95.5     |                    100 |
| short           | 8W       |           71.325  |                 37.1667 |              87.8333  |                    100 |
| short           | 12W      |           69.375  |                 35.8333 |              84.1667  |                    100 |
| short           | 26W      |           65.0417 |                 42.2917 |              66.5     |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.108965 |          -0.144527 |                    0.144527 |       -0.00982857 |            866 |            0.124241 |              0.0816046 |            0.130968 |                   82 |           87.8333 |         -0.157403 |       -0.116995  |             -0.0086996  |            -0.00719616 | True                    |             92.75   |                100 |                       95 |       93.5583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.114202 |          -0.136873 |                    0.136873 |       -0.00878569 |            862 |            0.12297  |              0.0833333 |            0.132221 |                   78 |           84.1667 |         -0.157701 |       -0.107259  |             -0.00952048 |            -0.00294197 | True                    |             96.0833 |                100 |                       90 |       93.475  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.166844 |          -0.192721 |                    0.192721 |       -0.0120995  |            870 |            0.124743 |              0.0833333 |            0.143111 |                   78 |           95.5    |         -0.255315 |       -0.114343  |             -0.0155619  |            -0.00797665 | True                    |             84.5    |                100 |                       85 |       91.175  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.171796 |          -0.203128 |                    0.203128 |       -0.0176091  |            866 |            0.124241 |              0.0816046 |            0.130968 |                   82 |           87.8333 |         -0.250623 |       -0.134129  |             -0.0211944  |            -0.01173    | True                    |             78.8333 |                100 |                       95 |       87.9917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.128822 |          -0.131341 |                    0.131341 |       -0.00711534 |            848 |            0.11647  |              0.0769231 |            0.120611 |                   72 |           66.5    |         -0.132635 |       -0.113786  |             -0.00639511 |            -0.00879319 | True                    |             98.9167 |                100 |                       65 |       87.6917 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.121579 |           0.158266 |                    0.158266 |        0.00839477 |            862 |            0.112112 |              0.0705128 |            0.124541 |                   76 |           67.1667 |          0.143257 |        0.174832  |              0.00596931 |             0.011551   | True                    |             91.8333 |                100 |                       90 |       87.525  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.115297 |          -0.131309 |                    0.131309 |       -0.027101   |            872 |            0.116448 |              0.0736749 |            0.132564 |                   78 |           78.8333 |         -0.210588 |       -0.0435449 |             -0.0297236  |            -0.0182261  | True                    |             86      |                100 |                       55 |       84.6083 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.172826 |          -0.215923 |                    0.215923 |       -0.0184632  |            862 |            0.12297  |              0.0833333 |            0.132221 |                   78 |           84.1667 |         -0.265731 |       -0.149276  |             -0.019428   |            -0.0136129  | True                    |             73.8333 |                100 |                       90 |       84.575  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.196633 |          -0.208351 |                    0.208351 |       -0.0404736  |            870 |            0.124743 |              0.0833333 |            0.143111 |                   78 |           95.5    |         -0.341137 |       -0.0489562 |             -0.0561075  |            -0.0183316  | True                    |             65.5    |                100 |                       85 |       83.575  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.139772 |           0.147821 |                    0.147821 |        0.00857283 |            848 |            0.110197 |              0.0769231 |            0.111229 |                   64 |           46.8333 |          0.141939 |        0.140183  |              0.00541405 |             0.0108926  | True                    |             93.4167 |                100 |                       65 |       80.575  | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.198037 |          -0.198777 |                    0.198777 |       -0.0170618  |            848 |            0.11647  |              0.0769231 |            0.120611 |                   72 |           66.5    |         -0.234339 |       -0.144449  |             -0.0212859  |            -0.0129602  | True                    |             80.5    |                100 |                       65 |       80.325  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.27138  |          -0.305741 |                    0.305741 |       -0.0274525  |            870 |            0.124743 |              0.0833333 |            0.143111 |                   78 |           95.5    |         -0.417411 |       -0.159147  |             -0.0338571  |            -0.0167288  | True                    |             51.8333 |                100 |                       85 |       78.1083 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.213212 |           0.249529 |                    0.249529 |        0.0205972  |            862 |            0.112112 |              0.0705128 |            0.124541 |                   76 |           67.1667 |          0.238416 |        0.256859  |              0.0144699  |             0.0205434  | True                    |             67.8333 |                100 |                       90 |       77.925  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.258217 |          -0.282393 |                    0.282393 |       -0.0386933  |            866 |            0.124241 |              0.0816046 |            0.130968 |                   82 |           87.8333 |         -0.379557 |       -0.143245  |             -0.0488568  |            -0.0133913  | True                    |             52      |                100 |                       95 |       77.2583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.178514 |           0.218696 |                    0.218696 |        0.0103805  |            866 |            0.105261 |              0.0641026 |            0.116177 |                   58 |           42.6667 |          0.197534 |        0.241824  |              0.0116333  |             0.0119999  | True                    |             79.1667 |                100 |                       95 |       76.8333 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.218021 |           0.259038 |                    0.259038 |        0.0151436  |            870 |            0.111652 |              0.0742493 |            0.123972 |                   73 |           60.5    |          0.258117 |        0.257631  |              0.016024   |             0.0171869  | True                    |             70.3333 |                100 |                       85 |       76.7583 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.220348 |          -0.27352  |                    0.27352  |       -0.0164399  |            872 |            0.116448 |              0.0736749 |            0.132564 |                   78 |           78.8333 |         -0.336663 |       -0.194015  |             -0.0179628  |            -0.0093026  | True                    |             65.9167 |                100 |                       55 |       76.575  | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.112223 |           0.152463 |                    0.152463 |        0.00908894 |            831 |            0.102798 |              0.0705128 |            0.106477 |                   50 |           18.5    |          0.127902 |        0.170711  |              0.00341581 |             0.0123958  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.13874  |           0.144492 |                    0.144492 |        0.0110204  |            817 |            0.102959 |              0.0705128 |            0.100878 |                   47 |           21.8333 |          0.134141 |        0.143079  |              0.0076014  |             0.012236   | True                    |             92.6667 |                100 |                       65 |       74.025  | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 26W      | mm_long_velocity_26w  | 2W        |      0.225989 |           0.220607 |                    0.220607 |        0.0164303  |            848 |            0.110197 |              0.0769231 |            0.111229 |                   64 |           46.8333 |          0.230446 |        0.197832  |              0.0174786  |             0.0159071  | True                    |             74.0833 |                100 |                       65 |       72.8417 | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
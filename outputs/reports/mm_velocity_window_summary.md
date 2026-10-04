# GHPR v0.6.2 MM Velocity Window Discovery

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-09-29`.
- Best Long velocity window: `2W`.
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

`2W` based on average 4W/8W total score.

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
| long            | 2W       |           62.3417 |                 49.5    |              48.1667  |                    100 |
| long            | 26W      |           61.5583 |                 45.875  |              46.8333  |                    100 |
| long            | 4W       |           60.8583 |                 30.5833 |              60.5     |                    100 |
| long            | 12W      |           60.4417 |                 24.125  |              67.1667  |                    100 |
| long            | 8W       |           50.2667 |                 15.0417 |              39       |                    100 |
| net             | 4W       |           52      |                 26.6667 |              31.3333  |                    100 |
| net             | 26W      |           51.5083 |                 38.6667 |              18.1667  |                    100 |
| net             | 2W       |           51.325  |                 44.4583 |              12.1667  |                    100 |
| net             | 12W      |           49.575  |                 27.375  |              18.5     |                    100 |
| net             | 8W       |           43.4417 |                 17.4583 |               7.83333 |                    100 |
| short           | 2W       |           75.1417 |                 62.3333 |              78.8333  |                    100 |
| short           | 4W       |           74.025  |                 41.625  |              95.5     |                    100 |
| short           | 8W       |           71.325  |                 37.1667 |              87.8333  |                    100 |
| short           | 12W      |           69.5917 |                 36.375  |              84.1667  |                    100 |
| short           | 26W      |           64.825  |                 41.75   |              66.5     |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.108887 |          -0.144324 |                    0.144324 |       -0.00974914 |            864 |            0.124418 |              0.0828804 |            0.131066 |                   82 |           87.8333 |         -0.157403 |       -0.11602   |             -0.0086996  |            -0.00719616 | True                    |             93.8333 |                100 |                       95 |       93.9917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.114143 |          -0.136766 |                    0.136766 |       -0.00878569 |            860 |            0.123078 |              0.0833333 |            0.132343 |                   78 |           84.1667 |         -0.157701 |       -0.106532  |             -0.00952048 |            -0.00294197 | True                    |             96.0833 |                100 |                       90 |       93.475  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.166768 |          -0.19241  |                    0.19241  |       -0.0121326  |            868 |            0.124861 |              0.0833333 |            0.143251 |                   78 |           95.5    |         -0.255315 |       -0.11298   |             -0.0155619  |            -0.00737076 | True                    |             84.5    |                100 |                       85 |       91.175  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.171301 |          -0.202381 |                    0.202381 |       -0.0179537  |            864 |            0.124418 |              0.0828804 |            0.131066 |                   82 |           87.8333 |         -0.250623 |       -0.13168   |             -0.0211944  |            -0.01173    | True                    |             78.25   |                100 |                       95 |       87.7583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.128931 |          -0.131706 |                    0.131706 |       -0.00711534 |            846 |            0.11667  |              0.0769231 |            0.120678 |                   72 |           66.5    |         -0.132635 |       -0.114674  |             -0.00639511 |            -0.0091122  | True                    |             98.9167 |                100 |                       65 |       87.6917 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.121487 |           0.158135 |                    0.158135 |        0.00791095 |            860 |            0.112224 |              0.0705128 |            0.124664 |                   76 |           67.1667 |          0.143257 |        0.174341  |              0.00596931 |             0.0115461  | True                    |             91.8333 |                100 |                       90 |       87.525  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.172628 |          -0.215528 |                    0.215528 |       -0.0184632  |            860 |            0.123078 |              0.0833333 |            0.132343 |                   78 |           84.1667 |         -0.265731 |       -0.147664  |             -0.019428   |            -0.0136129  | True                    |             74.4167 |                100 |                       90 |       84.8083 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.113711 |          -0.128398 |                    0.128398 |       -0.0265619  |            870 |            0.11662  |              0.0736749 |            0.132657 |                   78 |           78.8333 |         -0.210588 |       -0.0350024 |             -0.0297236  |            -0.018558   | True                    |             86      |                100 |                       55 |       84.6083 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.195495 |          -0.206028 |                    0.206028 |       -0.0404645  |            868 |            0.124861 |              0.0833333 |            0.143251 |                   78 |           95.5    |         -0.341137 |       -0.0415374 |             -0.0561075  |            -0.0181538  | True                    |             65.5    |                100 |                       85 |       83.575  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.13973  |           0.147712 |                    0.147712 |        0.00857283 |            846 |            0.110245 |              0.0769231 |            0.111354 |                   64 |           46.8333 |          0.141939 |        0.139645  |              0.00541405 |             0.00980898 | True                    |             93.4167 |                100 |                       65 |       80.575  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.199321 |          -0.200529 |                    0.200529 |       -0.0170618  |            846 |            0.11667  |              0.0769231 |            0.120678 |                   72 |           66.5    |         -0.234339 |       -0.148025  |             -0.0212859  |            -0.0121165  | True                    |             80.5    |                100 |                       65 |       80.325  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.270924 |          -0.304683 |                    0.304683 |       -0.0279743  |            868 |            0.124861 |              0.0833333 |            0.143251 |                   78 |           95.5    |         -0.417411 |       -0.155505  |             -0.0338571  |            -0.01692    | True                    |             51.8333 |                100 |                       85 |       78.1083 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.212621 |           0.248502 |                    0.248502 |        0.0204832  |            860 |            0.112224 |              0.0705128 |            0.124664 |                   76 |           67.1667 |          0.238416 |        0.254714  |              0.0144699  |             0.0209202  | True                    |             67.8333 |                100 |                       90 |       77.925  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.257504 |          -0.281313 |                    0.281313 |       -0.039239   |            864 |            0.124418 |              0.0828804 |            0.131066 |                   82 |           87.8333 |         -0.379557 |       -0.138892  |             -0.0488568  |            -0.0133913  | True                    |             52      |                100 |                       95 |       77.2583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.218038 |           0.258912 |                    0.258912 |        0.0151436  |            868 |            0.111872 |              0.0751715 |            0.124029 |                   73 |           60.5    |          0.258117 |        0.256876  |              0.016024   |             0.0169725  | True                    |             70.3333 |                100 |                       85 |       76.7583 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.220324 |          -0.273446 |                    0.273446 |       -0.0168301  |            870 |            0.11662  |              0.0736749 |            0.132657 |                   78 |           78.8333 |         -0.336663 |       -0.193249  |             -0.0179628  |            -0.00876477 | True                    |             65.9167 |                100 |                       55 |       76.575  | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.178486 |           0.218625 |                    0.218625 |        0.0102218  |            864 |            0.10526  |              0.0641026 |            0.116303 |                   58 |           39      |          0.197534 |        0.2411    |              0.0116333  |             0.0130398  | True                    |             79.1667 |                100 |                       95 |       75.9167 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.112132 |           0.152329 |                    0.152329 |        0.00908894 |            829 |            0.102845 |              0.0700822 |            0.106601 |                   50 |           18.5    |          0.127902 |        0.169894  |              0.00341581 |             0.0123958  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| long            | 26W      | mm_long_velocity_26w  | 2W        |      0.22634  |           0.221233 |                    0.221233 |        0.0164303  |            846 |            0.110245 |              0.0769231 |            0.111354 |                   64 |           46.8333 |          0.230446 |        0.198657  |              0.0174786  |             0.0158279  | True                    |             74.0833 |                100 |                       65 |       72.8417 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.138756 |           0.144562 |                    0.144562 |        0.0112045  |            815 |            0.103039 |              0.0705128 |            0.100971 |                   47 |           18.1667 |          0.134141 |        0.14355   |              0.0076014  |             0.0125442  | True                    |             91.5833 |                100 |                       65 |       72.675  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
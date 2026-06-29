# GHPR v0.6.2 MM Velocity Window Discovery

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-06-23`.
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
| long            | 2W       |           62.3417 |                 49.5    |              48.1667  |                    100 |
| long            | 26W      |           62.2083 |                 47.5    |              46.8333  |                    100 |
| long            | 4W       |           60.425  |                 29.5    |              60.5     |                    100 |
| long            | 12W      |           60.2417 |                 23.625  |              67.1667  |                    100 |
| long            | 8W       |           50.3833 |                 15.3333 |              39       |                    100 |
| net             | 26W      |           52.5083 |                 41.1667 |              18.1667  |                    100 |
| net             | 4W       |           52.1167 |                 26.9583 |              31.3333  |                    100 |
| net             | 2W       |           50.625  |                 42.7083 |              12.1667  |                    100 |
| net             | 12W      |           49.375  |                 26.875  |              18.5     |                    100 |
| net             | 8W       |           43.775  |                 18.2917 |               7.83333 |                    100 |
| short           | 2W       |           74.7083 |                 61.25   |              78.8333  |                    100 |
| short           | 4W       |           73.6917 |                 40.7917 |              95.5     |                    100 |
| short           | 8W       |           70.3417 |                 34.7083 |              87.8333  |                    100 |
| short           | 12W      |           69.5083 |                 36.1667 |              84.1667  |                    100 |
| short           | 26W      |           64.125  |                 40      |              66.5     |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.11406  |          -0.136668 |                    0.136668 |       -0.00744807 |            846 |            0.124146 |              0.0833333 |            0.133023 |                   78 |           84.1667 |         -0.157701 |       -0.105833  |             -0.00952048 |            -0.00268188 | True                    |             97.8333 |                100 |                       90 |       94.175  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.112564 |          -0.148001 |                    0.148001 |       -0.0101211  |            850 |            0.125435 |              0.0833333 |            0.131812 |                   82 |           87.8333 |         -0.157403 |       -0.124586  |             -0.0086996  |            -0.010066   | True                    |             91.0833 |                100 |                       95 |       92.8917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.16769  |          -0.19085  |                    0.19085  |       -0.0110728  |            854 |            0.126174 |              0.0833333 |            0.143948 |                   78 |           95.5    |         -0.255315 |       -0.104757  |             -0.0155619  |            -0.00580736 | True                    |             86.6667 |                100 |                       85 |       92.0417 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.130251 |          -0.131175 |                    0.131175 |       -0.00753783 |            832 |            0.118019 |              0.0769231 |            0.121202 |                   72 |           66.5    |         -0.132635 |       -0.113839  |             -0.00639511 |            -0.00686424 | True                    |             99.4167 |                100 |                       65 |       87.8917 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.12367  |           0.164071 |                    0.164071 |        0.00807111 |            846 |            0.113204 |              0.0705128 |            0.125366 |                   76 |           67.1667 |          0.143257 |        0.188295  |              0.00596931 |             0.0102836  | True                    |             91.25   |                100 |                       90 |       87.2917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.17685  |          -0.208957 |                    0.208957 |       -0.0196966  |            850 |            0.125435 |              0.0833333 |            0.131812 |                   82 |           87.8333 |         -0.250623 |       -0.14519   |             -0.0211944  |            -0.0154288  | True                    |             77.0833 |                100 |                       95 |       87.2917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.173591 |          -0.216749 |                    0.216749 |       -0.0182182  |            846 |            0.124146 |              0.0833333 |            0.133023 |                   78 |           84.1667 |         -0.265731 |       -0.147087  |             -0.019428   |            -0.0115341  | True                    |             74.4167 |                100 |                       90 |       84.8083 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.11925  |          -0.134369 |                    0.134369 |       -0.0280969  |            856 |            0.117855 |              0.0769231 |            0.133364 |                   78 |           78.8333 |         -0.210588 |       -0.0446737 |             -0.0297236  |            -0.0172128  | True                    |             84.9167 |                100 |                       55 |       84.175  | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.202324 |          -0.212843 |                    0.212843 |       -0.0431496  |            854 |            0.126174 |              0.0833333 |            0.143948 |                   78 |           95.5    |         -0.341137 |       -0.0502303 |             -0.0561075  |            -0.0196453  | True                    |             64.3333 |                100 |                       85 |       83.1083 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.138331 |           0.147237 |                    0.147237 |        0.00865887 |            832 |            0.110968 |              0.0769231 |            0.111928 |                   64 |           46.8333 |          0.141939 |        0.138638  |              0.00541405 |             0.0076694  | True                    |             93.9167 |                100 |                       65 |       80.775  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.199621 |          -0.201414 |                    0.201414 |       -0.0170501  |            832 |            0.118019 |              0.0769231 |            0.121202 |                   72 |           66.5    |         -0.234339 |       -0.148503  |             -0.0212859  |            -0.0120437  | True                    |             81.0833 |                100 |                       65 |       80.5583 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.274268 |          -0.305834 |                    0.305834 |       -0.0283958  |            854 |            0.126174 |              0.0833333 |            0.143948 |                   78 |           95.5    |         -0.417411 |       -0.154262  |             -0.0338571  |            -0.0144469  | True                    |             51.8333 |                100 |                       85 |       78.1083 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.216956 |           0.254284 |                    0.254284 |        0.0204853  |            846 |            0.113204 |              0.0705128 |            0.125366 |                   76 |           67.1667 |          0.238416 |        0.269984  |              0.0144699  |             0.0182547  | True                    |             67.8333 |                100 |                       90 |       77.925  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.223582 |          -0.270839 |                    0.270839 |       -0.0167324  |            856 |            0.117855 |              0.0769231 |            0.133364 |                   78 |           78.8333 |         -0.336663 |       -0.184087  |             -0.0179628  |            -0.00759376 | True                    |             67.5833 |                100 |                       55 |       77.2417 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.219516 |           0.261858 |                    0.261858 |        0.0155099  |            854 |            0.112949 |              0.0769231 |            0.124651 |                   73 |           60.5    |          0.258117 |        0.262948  |              0.016024   |             0.0167258  | True                    |             71.4167 |                100 |                       85 |       77.1917 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.269845 |          -0.292535 |                    0.292535 |       -0.0402169  |            850 |            0.125435 |              0.0833333 |            0.131812 |                   82 |           87.8333 |         -0.379557 |       -0.159988  |             -0.0488568  |            -0.0221745  | True                    |             50.9167 |                100 |                       95 |       76.825  | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.112066 |           0.155288 |                    0.155288 |        0.00930831 |            815 |            0.103488 |              0.0700822 |            0.107302 |                   50 |           18.5    |          0.127902 |        0.178185  |              0.00341581 |             0.0113011  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.178976 |           0.220768 |                    0.220768 |        0.0105853  |            850 |            0.106256 |              0.0641026 |            0.116943 |                   58 |           39      |          0.197534 |        0.247262  |              0.0116333  |             0.0143089  | True                    |             76.4167 |                100 |                       95 |       74.8167 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.136687 |           0.142261 |                    0.142261 |        0.00965234 |            801 |            0.103504 |              0.0705128 |            0.101307 |                   46 |           18.1667 |          0.134141 |        0.139481  |              0.0076014  |             0.0123644  | True                    |             93.8333 |                100 |                       65 |       73.575  | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 12W      | mm_short_velocity_12w | 4W        |     -0.284139 |          -0.31993  |                    0.31993  |       -0.0399488  |            846 |            0.124146 |              0.0833333 |            0.133023 |                   78 |           84.1667 |         -0.386066 |       -0.221031  |             -0.0447451  |            -0.0274318  | True                    |             45      |                100 |                       90 |       73.0417 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
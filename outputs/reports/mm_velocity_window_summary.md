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
| long            | 26W      |           62.2083 |                 47.5    |              46.8333  |                    100 |
| long            | 4W       |           60.6417 |                 30.0417 |              60.5     |                    100 |
| long            | 12W      |           60.2417 |                 23.625  |              67.1667  |                    100 |
| long            | 8W       |           50.9333 |                 16.7083 |              39       |                    100 |
| net             | 26W      |           53.6417 |                 41.7083 |              21.8333  |                    100 |
| net             | 4W       |           50.9833 |                 26.4167 |              27.6667  |                    100 |
| net             | 2W       |           50.525  |                 42.4583 |              12.1667  |                    100 |
| net             | 12W      |           49.1583 |                 26.3333 |              18.5     |                    100 |
| net             | 8W       |           43.775  |                 18.2917 |               7.83333 |                    100 |
| short           | 2W       |           74.7083 |                 61.25   |              78.8333  |                    100 |
| short           | 4W       |           72.575  |                 38      |              95.5     |                    100 |
| short           | 8W       |           70.4583 |                 35      |              87.8333  |                    100 |
| short           | 12W      |           69.3917 |                 35.875  |              84.1667  |                    100 |
| short           | 26W      |           63.9083 |                 39.4583 |              66.5     |                    100 |

## Top Scorecard Rows

| feature_group   | window   | feature_name          | horizon   |   correlation |   rank_correlation |   absolute_rank_correlation |   high_low_spread |   sample_count |   weekly_change_avg |   weekly_change_median |   weekly_change_std |   extreme_jump_count |   stability_score |   train_rank_corr |   test_rank_corr |   train_high_low_spread |   test_high_low_spread | direction_consistency   |   information_score |   train_test_score |   interpretability_score |   total_score | recommended   | reason                                                                                                       |
|:----------------|:---------|:----------------------|:----------|--------------:|-------------------:|----------------------------:|------------------:|---------------:|--------------------:|-----------------------:|--------------------:|---------------------:|------------------:|------------------:|-----------------:|------------------------:|-----------------------:|:------------------------|--------------------:|-------------------:|-------------------------:|--------------:|:--------------|:-------------------------------------------------------------------------------------------------------------|
| short           | 12W      | mm_short_velocity_12w | 1W        |     -0.1166   |          -0.139034 |                    0.139034 |       -0.00749883 |            844 |            0.124303 |              0.0833333 |            0.133133 |                   78 |           84.1667 |         -0.157701 |       -0.110923  |             -0.00952048 |            -0.00272907 | True                    |             97.8333 |                100 |                       90 |       94.175  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 1W        |     -0.116602 |          -0.15153  |                    0.15153  |       -0.00988847 |            848 |            0.125572 |              0.0833333 |            0.131926 |                   82 |           87.8333 |         -0.157403 |       -0.132684  |             -0.0086996  |            -0.010197   | True                    |             91.6667 |                100 |                       95 |       93.125  | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 4W       | mm_short_velocity_4w  | 1W        |     -0.171289 |          -0.194547 |                    0.194547 |       -0.0111888  |            852 |            0.126252 |              0.0833333 |            0.144108 |                   78 |           95.5    |         -0.255315 |       -0.112013  |             -0.0155619  |            -0.00576723 | True                    |             86.6667 |                100 |                       85 |       92.0417 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 26W      | mm_short_velocity_26w | 1W        |     -0.131044 |          -0.131758 |                    0.131758 |       -0.00753627 |            830 |            0.118141 |              0.0769231 |            0.121305 |                   72 |           66.5    |         -0.132635 |       -0.115006  |             -0.00639511 |            -0.00686424 | True                    |             99.4167 |                100 |                       65 |       87.8917 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 12W      | mm_long_velocity_12w  | 1W        |      0.12523  |           0.165922 |                    0.165922 |        0.00778932 |            844 |            0.11332  |              0.0705128 |            0.125477 |                   76 |           67.1667 |          0.143257 |        0.192541  |              0.00596931 |             0.00954525 | True                    |             91.25   |                100 |                       90 |       87.2917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 8W       | mm_short_velocity_8w  | 2W        |     -0.181605 |          -0.215171 |                    0.215171 |       -0.0199664  |            848 |            0.125572 |              0.0833333 |            0.131926 |                   82 |           87.8333 |         -0.250623 |       -0.158874  |             -0.0211944  |            -0.0154377  | True                    |             77.0833 |                100 |                       95 |       87.2917 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| short           | 12W      | mm_short_velocity_12w | 2W        |     -0.176769 |          -0.221661 |                    0.221661 |       -0.0184835  |            844 |            0.124303 |              0.0833333 |            0.133133 |                   78 |           84.1667 |         -0.265731 |       -0.156657  |             -0.019428   |            -0.011855   | True                    |             72.8333 |                100 |                       90 |       84.175  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 8W        |     -0.121537 |          -0.137503 |                    0.137503 |       -0.0273548  |            854 |            0.117981 |              0.0769231 |            0.133491 |                   78 |           78.8333 |         -0.210588 |       -0.051947  |             -0.0297236  |            -0.0172128  | True                    |             84.9167 |                100 |                       55 |       84.175  | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| short           | 4W       | mm_short_velocity_4w  | 8W        |     -0.207755 |          -0.218682 |                    0.218682 |       -0.0451882  |            852 |            0.126252 |              0.0833333 |            0.144108 |                   78 |           95.5    |         -0.341137 |       -0.0624238 |             -0.0561075  |            -0.0197405  | True                    |             58.75   |                100 |                       85 |       80.875  | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 26W      | mm_long_velocity_26w  | 1W        |      0.13745  |           0.146672 |                    0.146672 |        0.00836454 |            830 |            0.111143 |              0.0769231 |            0.111995 |                   64 |           46.8333 |          0.141939 |        0.137054  |              0.00541405 |             0.00764789 | True                    |             93.9167 |                100 |                       65 |       80.775  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 26W      | mm_short_velocity_26w | 2W        |     -0.200589 |          -0.202735 |                    0.202735 |       -0.0170987  |            830 |            0.118141 |              0.0769231 |            0.121305 |                   72 |           66.5    |         -0.234339 |       -0.150335  |             -0.0212859  |            -0.0120437  | True                    |             81.0833 |                100 |                       65 |       80.5583 | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| short           | 4W       | mm_short_velocity_4w  | 2W        |     -0.279258 |          -0.312683 |                    0.312683 |       -0.0285845  |            852 |            0.126252 |              0.0833333 |            0.144108 |                   78 |           95.5    |         -0.417411 |       -0.168491  |             -0.0338571  |            -0.015632   | True                    |             51.8333 |                100 |                       85 |       78.1083 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| long            | 12W      | mm_long_velocity_12w  | 2W        |      0.218915 |           0.258058 |                    0.258058 |        0.0205388  |            844 |            0.11332  |              0.0705128 |            0.125477 |                   76 |           67.1667 |          0.238416 |        0.278706  |              0.0144699  |             0.0176688  | True                    |             67.8333 |                100 |                       90 |       77.925  | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| short           | 2W       | mm_short_velocity_2w  | 1W        |     -0.227106 |          -0.274901 |                    0.274901 |       -0.0161409  |            854 |            0.117981 |              0.0769231 |            0.133491 |                   78 |           78.8333 |         -0.336663 |       -0.192448  |             -0.0179628  |            -0.00759376 | True                    |             67.5833 |                100 |                       55 |       77.2417 | True          | short-term window; higher noise risk; train/test direction is consistent; historical structure research only |
| long            | 4W       | mm_long_velocity_4w   | 1W        |      0.220885 |           0.263404 |                    0.263404 |        0.0155099  |            852 |            0.113109 |              0.0769231 |            0.124748 |                   73 |           60.5    |          0.258117 |        0.266102  |              0.016024   |             0.0167258  | True                    |             71.4167 |                100 |                       85 |       77.1917 | False         | short-term velocity candidate; train/test direction is consistent; historical structure research only        |
| short           | 8W       | mm_short_velocity_8w  | 4W        |     -0.276284 |          -0.29855  |                    0.29855  |       -0.0407888  |            848 |            0.125572 |              0.0833333 |            0.131926 |                   82 |           87.8333 |         -0.379557 |       -0.172805  |             -0.0488568  |            -0.0233987  | True                    |             51.5    |                100 |                       95 |       77.0583 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 12W      | mm_net_velocity_12w   | 1W        |      0.114055 |           0.15758  |                    0.15758  |        0.00890714 |            813 |            0.103522 |              0.0700822 |            0.107364 |                   50 |           18.5    |          0.127902 |        0.183689  |              0.00341581 |             0.0108754  | True                    |             91.1667 |                100 |                       90 |       75.0917 | False         | medium swing velocity candidate; train/test direction is consistent; historical structure research only      |
| long            | 8W       | mm_long_velocity_8w   | 1W        |      0.180787 |           0.22307  |                    0.22307  |        0.0109569  |            848 |            0.106401 |              0.0641026 |            0.117039 |                   58 |           39      |          0.197534 |        0.252299  |              0.0116333  |             0.0143089  | True                    |             76.4167 |                100 |                       95 |       74.8167 | False         | current swing velocity baseline; train/test direction is consistent; historical structure research only      |
| net             | 26W      | mm_net_velocity_26w   | 1W        |      0.135888 |           0.141524 |                    0.141524 |        0.00999985 |            799 |            0.103748 |              0.0705128 |            0.101317 |                   46 |           21.8333 |          0.134141 |        0.137779  |              0.0076014  |             0.0116609  | True                    |             93.25   |                100 |                       65 |       74.2583 | True          | medium-term window; slower response; train/test direction is consistent; historical structure research only  |
| long            | 26W      | mm_long_velocity_26w  | 2W        |      0.221449 |           0.21808  |                    0.21808  |        0.017397   |            830 |            0.111143 |              0.0769231 |            0.111995 |                   64 |           46.8333 |          0.230446 |        0.191008  |              0.0174786  |             0.015426   | True                    |             76.1667 |                100 |                       65 |       73.675  | False         | medium-term window; slower response; train/test direction is consistent; historical structure research only  |

## Method Notes

- Information Score: rank correlation strength plus high-low spread strength.
- Stability Score: lower weekly velocity changes, lower volatility, and fewer >30 percentile-point jumps score higher.
- Train/Test Score: same sign rank correlation across 2009-2018 and 2019-latest scores higher.
- Interpretability Score: 4W/8W/12W score higher; 2W gets a noise penalty; 26W gets a slow-response penalty.
- Historical structure research only. Not a trading signal. Not financial advice.
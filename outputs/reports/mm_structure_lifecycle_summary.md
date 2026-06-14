# GHPR v0.6 MM Long / Short Structure Lifecycle Research

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-06-09`.
- Latest date: `2026-06-09`.
- Latest MM Long / Short / Net: `126,280` / `20,417` / `105,863`.
- Latest MM Long / Short / Net percentile: `25.00%` / `10.90%` / `35.90%`.
- Latest Long / Short / Net velocity 8W: `2.56%` / `-21.15%` / `10.26%`.
- Latest structure state: `MM_STRUCTURE_LOW_PARTICIPATION`.
- Latest contribution state: `SHORT_COVERING`.
- Structure state note: MM_STRUCTURE_CROWDED_LONG has the largest absolute 8W median following return (4.50%) in this sample.
- Contribution note: LONG_BUILDING has the largest absolute 8W median following return (5.29%) in this sample.

## Required Research Questions

### 1. Why is MM Net alone incomplete?

MM Net equals MM Long minus MM Short. A rising net position can come from new long exposure, short reduction, or both. A falling net position can come from long liquidation, short building, or both. The structure layer separates those paths.

### 2. What do MM Long / Short / Net each represent?

MM Long describes long-side exposure, MM Short describes short-side exposure, and MM Net summarizes their difference. The three series can move together or diverge, so Net should be read with its component structure.

### 3. When Net rises, is it driven by Long building or Short covering?

Latest 8W changes: Long `858`, Short `-9,864`, Net `10,722`. Latest contribution label is `SHORT_COVERING`.

### 4. When Net falls, is it driven by Long liquidation or Short building?

The contribution analysis table separates long-side reduction from short-side increase. This distinction matters because both can produce lower Net while describing different participation behavior.

### 5. Which has more information: Long Velocity, Short Velocity, or Net Velocity?

- Long: mm_long_velocity_4w vs 4W at lag 0W has rank correlation 0.576.
- Short: mm_short_velocity_4w vs 4W at lag 0W has rank correlation -0.432.
- Net: mm_net_velocity_4w vs 4W at lag 0W has rank correlation 0.578.

### 6. Does Long lead Gold?

mm_long_velocity_4w vs 4W at lag 0W has rank correlation 0.576.

### 7. Does Short lead Gold?

mm_short_velocity_4w vs 4W at lag 0W has rank correlation -0.432.

### 8. Is Net mainly a Long or Short outcome?

Net is a component outcome. The current 8W reconciliation confirms `mm_net_change_8w = mm_long_change_8w - mm_short_change_8w`, with any residual shown in `mm_net_change_8w_reconciliation_error`.

### 9. What is the current MM Structure State?

The current MM Structure State is `MM_STRUCTURE_LOW_PARTICIPATION`. This is a historical structure label, not a market instruction.

### 10. What do the current structure fields mean?

- MM Long Percentile: `25.00%`.
- MM Short Percentile: `10.90%`.
- MM Net Percentile: `35.90%`.
- Long Velocity 8W: `2.56%`.
- Short Velocity 8W: `-21.15%`.
- Net Velocity 8W: `10.26%`.

### 11. Should GHPR Dashboard v0.6 add Long / Short / Net structure?

Yes, as a research layer. It improves explainability of the existing MM Net signal by showing whether long-side or short-side positioning is driving the structure.

### 12. Should Producer / OI lifecycle be added next?

Potentially, but this v0.6 module intentionally stays MM-only. Producer and OI lifecycle research should be separate modules so their definitions do not blur the MM structure study.

### 13. Current research conclusion

MM structure adds useful decomposition around MM Net. The dashboard should display it as historical structure research, with the existing MM Net percentile preserved as the current core positioning reference.

## MM Structure State Analysis

| mm_structure_state                |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:----------------------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_STRUCTURE_ACCUMULATION         |     184 |             0.00491417  |                0.00584793  |      0.646739 |             0.0110112   |                0.0125264   |      0.695652 |              0.0210354  |                 0.0235206  |      0.733696 |               0.0393797 |                 0.0376427  |      0.842391 |        0.142329  |        -0.135196  |
| MM_STRUCTURE_SHORT_COVERING_RALLY |      54 |             0.000558779 |                0.00246879  |      0.592593 |             0.000116041 |               -0.00179082  |      0.462963 |             -0.00696774 |                -0.00754169 |      0.407407 |              -0.0066129 |                -0.00515305 |      0.351852 |        0.0816615 |        -0.119216  |
| MM_STRUCTURE_LONG_LIQUIDATION     |     292 |            -0.00268185  |               -0.00354845  |      0.431507 |            -0.00591395  |               -0.00675684  |      0.393836 |             -0.00966842 |                -0.0115302  |      0.35274  |              -0.014621  |                -0.0230957  |      0.280822 |        0.24908   |        -0.141753  |
| MM_STRUCTURE_SHORT_BUILDING       |      39 |            -0.0040514   |               -0.0015478   |      0.384615 |            -0.00623433  |               -0.00762389  |      0.307692 |             -0.0116967  |                -0.0189264  |      0.25641  |              -0.0220933 |                -0.0255492  |      0.153846 |        0.117368  |        -0.136609  |
| MM_STRUCTURE_CROWDED_LONG         |     156 |             0.00547001  |                0.00778209  |      0.615385 |             0.0118811   |                0.012684    |      0.666667 |              0.0258808  |                 0.0249279  |      0.788462 |               0.0467834 |                 0.0450474  |      0.820513 |        0.179186  |        -0.0721955 |
| MM_STRUCTURE_LOW_PARTICIPATION    |      46 |             0.00126035  |                0.000170738 |      0.5      |             0.0017302   |               -0.000329301 |      0.5      |              0.00727994 |                 0.00131666 |      0.521739 |               0.0262763 |                 0.00961297 |      0.521739 |        0.213371  |        -0.133979  |
| MM_STRUCTURE_NEUTRAL              |     105 |             0.00827494  |                0.00942395  |      0.730769 |             0.0142963   |                0.0175025   |      0.68932  |              0.0226129  |                 0.0291188  |      0.732673 |               0.0354311 |                 0.0286094  |      0.649485 |        0.239115  |        -0.1255    |

## MM Structure Contribution Analysis

| mm_structure_contribution_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:----------------------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| LONG_BUILDING                     |     183 |              0.00710035 |                 0.00820457 |      0.63388  |             0.0153856   |                 0.0171047  |      0.688525 |              0.0302392  |                 0.0318099  |      0.814208 |              0.0553304  |                 0.0528523  |      0.928962 |         0.207895 |        -0.135196  |
| SHORT_COVERING                    |      93 |              0.00506368 |                 0.0070031  |      0.698925 |             0.0123444   |                 0.0123865  |      0.784946 |              0.0227611  |                 0.023563   |      0.731183 |              0.0404222  |                 0.0349675  |      0.806452 |         0.142329 |        -0.0739689 |
| LONG_LIQUIDATION                  |     206 |             -0.00329015 |                -0.0037412  |      0.451456 |            -0.00452355  |                -0.00542077 |      0.383495 |             -0.00690003 |                -0.0102268  |      0.368932 |             -0.0105151  |                -0.0242189  |      0.281553 |         0.24908  |        -0.133979  |
| SHORT_BUILDING                    |     118 |             -0.00385201 |                -0.00434914 |      0.432203 |            -0.00969399  |                -0.0101794  |      0.355932 |             -0.0179187  |                -0.0163001  |      0.322034 |             -0.0263539  |                -0.0330494  |      0.194915 |         0.152911 |        -0.141753  |
| MIXED_LONG_AND_SHORT_UP           |     137 |              0.00614355 |                 0.00581202 |      0.627737 |             0.0106178   |                 0.0138563  |      0.59854  |              0.0208013  |                 0.0241584  |      0.686131 |              0.0306462  |                 0.0259073  |      0.642336 |         0.239115 |        -0.136609  |
| MIXED_LONG_AND_SHORT_DOWN         |     131 |              0.00137677 |                 0.00147674 |      0.541985 |            -0.000350679 |                 0.00191802 |      0.541985 |             -0.00210938 |                -0.00412392 |      0.473282 |              0.00682572 |                -0.00186023 |      0.480916 |         0.197196 |        -0.119216  |
| NEUTRAL_STRUCTURE                 |       8 |              0.0150236  |                 0.00915424 |      0.714286 |             0.0285532   |                 0.0212724  |      0.833333 |              0.0457257  |                 0.0418876  |      1        |            nan          |               nan          |    nan        |       nan        |       nan         |

## Strongest Lead-Lag Rows

| mm_feature           | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                          |   abs_rank_correlation |
|:---------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:----------------------------------------|-----------------------:|
| mm_net_velocity_4w   | 4W             |           0 |      0.496609 |           0.577588 |            821 | same_week_positive_historical_alignment |               0.577588 |
| mm_long_velocity_4w  | 4W             |           0 |      0.491585 |           0.576444 |            852 | same_week_positive_historical_alignment |               0.576444 |
| mm_long_velocity_8w  | 8W             |           0 |      0.432752 |           0.486859 |            848 | same_week_positive_historical_alignment |               0.486859 |
| mm_net_velocity_8w   | 8W             |           0 |      0.432016 |           0.483903 |            817 | same_week_positive_historical_alignment |               0.483903 |
| mm_long_velocity_4w  | 2W             |           0 |      0.352007 |           0.43336  |            852 | same_week_positive_historical_alignment |               0.43336  |
| mm_long_velocity_12w | 8W             |           0 |      0.384292 |           0.432935 |            844 | same_week_positive_historical_alignment |               0.432935 |
| mm_short_velocity_4w | 4W             |           0 |     -0.4156   |          -0.431763 |            852 | same_week_negative_historical_alignment |               0.431763 |
| mm_net_velocity_12w  | 8W             |           0 |      0.374132 |           0.425256 |            813 | same_week_positive_historical_alignment |               0.425256 |
| mm_net_velocity_4w   | 2W             |           0 |      0.340031 |           0.423563 |            821 | same_week_positive_historical_alignment |               0.423563 |
| mm_long_velocity_8w  | 4W             |           0 |      0.378286 |           0.423289 |            848 | same_week_positive_historical_alignment |               0.423289 |

## Method Notes

- MM Long and MM Short percentiles use prior-only rolling 156-week windows with a 20-observation minimum.
- MM Net percentile uses the existing `mm_net_percentile_156w` from the master weekly dataset.
- Positive lag means the MM feature is shifted earlier against gold following returns.
- All outputs are historical structure research only.
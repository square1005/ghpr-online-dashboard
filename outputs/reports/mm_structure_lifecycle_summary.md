# GHPR v0.6 MM Long / Short Structure Lifecycle Research

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-09-29`.
- Latest date: `2026-09-29`.
- Latest MM Long / Short / Net: `131,711` / `11,393` / `120,318`.
- Latest MM Long / Short / Net percentile: `21.79%` / `4.49%` / `38.46%`.
- Latest Long / Short / Net velocity 8W: `-11.54%` / `4.49%` / `-16.03%`.
- Latest structure state: `MM_STRUCTURE_LOW_PARTICIPATION`.
- Latest contribution state: `LONG_LIQUIDATION`.
- Structure state note: MM_STRUCTURE_CROWDED_LONG has the largest absolute 8W median following return (4.49%) in this sample.
- Contribution note: LONG_BUILDING has the largest absolute 8W median following return (5.33%) in this sample.

## Required Research Questions

### 1. Why is MM Net alone incomplete?

MM Net equals MM Long minus MM Short. A rising net position can come from new long exposure, short reduction, or both. A falling net position can come from long liquidation, short building, or both. The structure layer separates those paths.

### 2. What do MM Long / Short / Net each represent?

MM Long describes long-side exposure, MM Short describes short-side exposure, and MM Net summarizes their difference. The three series can move together or diverge, so Net should be read with its component structure.

### 3. When Net rises, is it driven by Long building or Short covering?

Latest 8W changes: Long `-8,098`, Short `2,350`, Net `-10,448`. Latest contribution label is `LONG_LIQUIDATION`.

### 4. When Net falls, is it driven by Long liquidation or Short building?

The contribution analysis table separates long-side reduction from short-side increase. This distinction matters because both can produce lower Net while describing different participation behavior.

### 5. Which has more information: Long Velocity, Short Velocity, or Net Velocity?

- Long: mm_long_velocity_4w vs 4W at lag 0W has rank correlation 0.566.
- Short: mm_short_velocity_4w vs 4W at lag 0W has rank correlation -0.419.
- Net: mm_net_velocity_4w vs 4W at lag 0W has rank correlation 0.566.

### 6. Does Long lead Gold?

mm_long_velocity_4w vs 4W at lag 0W has rank correlation 0.566.

### 7. Does Short lead Gold?

mm_short_velocity_4w vs 4W at lag 0W has rank correlation -0.419.

### 8. Is Net mainly a Long or Short outcome?

Net is a component outcome. The current 8W reconciliation confirms `mm_net_change_8w = mm_long_change_8w - mm_short_change_8w`, with any residual shown in `mm_net_change_8w_reconciliation_error`.

### 9. What is the current MM Structure State?

The current MM Structure State is `MM_STRUCTURE_LOW_PARTICIPATION`. This is a historical structure label, not a market instruction.

### 10. What do the current structure fields mean?

- MM Long Percentile: `21.79%`.
- MM Short Percentile: `4.49%`.
- MM Net Percentile: `38.46%`.
- Long Velocity 8W: `-11.54%`.
- Short Velocity 8W: `4.49%`.
- Net Velocity 8W: `-16.03%`.

### 11. Should GHPR Dashboard v0.6 add Long / Short / Net structure?

Yes, as a research layer. It improves explainability of the existing MM Net signal by showing whether long-side or short-side positioning is driving the structure.

### 12. Should Producer / OI lifecycle be added next?

Potentially, but this v0.6 module intentionally stays MM-only. Producer and OI lifecycle research should be separate modules so their definitions do not blur the MM structure study.

### 13. Current research conclusion

MM structure adds useful decomposition around MM Net. The dashboard should display it as historical structure research, with the existing MM Net percentile preserved as the current core positioning reference.

## MM Structure State Analysis

| mm_structure_state                |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:----------------------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_STRUCTURE_ACCUMULATION         |     187 |             0.00483206  |                 0.00581463 |      0.636364 |             0.0117224   |                0.0124645   |      0.68984  |              0.0220352  |                 0.0258927  |      0.737968 |              0.0394784  |                 0.0378672  |      0.850267 |        0.142329  |        -0.135196  |
| MM_STRUCTURE_SHORT_COVERING_RALLY |      54 |             0.000424144 |                 0.00244548 |      0.592593 |             2.68613e-05 |               -0.00179082  |      0.481481 |             -0.00701579 |                -0.00887337 |      0.407407 |             -0.00623099 |                -0.00400469 |      0.37037  |        0.0816615 |        -0.119216  |
| MM_STRUCTURE_LONG_LIQUIDATION     |     292 |            -0.00272497  |                -0.00375328 |      0.431507 |            -0.00601736  |               -0.006655    |      0.393836 |             -0.00977727 |                -0.0114109  |      0.342466 |             -0.0146133  |                -0.023045   |      0.291096 |        0.239587  |        -0.141753  |
| MM_STRUCTURE_SHORT_BUILDING       |      39 |            -0.00367702  |                -0.00146849 |      0.410256 |            -0.00524069  |               -0.00385505  |      0.333333 |             -0.0102687  |                -0.0189264  |      0.282051 |             -0.0211194  |                -0.0255492  |      0.179487 |        0.120818  |        -0.136609  |
| MM_STRUCTURE_CROWDED_LONG         |     156 |             0.00546397  |                 0.00772644 |      0.615385 |             0.0118098   |                0.0132346   |      0.660256 |              0.0257963  |                 0.0243997  |      0.788462 |              0.0467741  |                 0.044928   |      0.820513 |        0.18041   |        -0.0721955 |
| MM_STRUCTURE_LOW_PARTICIPATION    |      58 |            -0.0008744   |                 0.00187716 |      0.517241 |            -0.00347776  |               -0.000329301 |      0.5      |             -0.0027644  |                -0.00918914 |      0.431034 |              0.0106879  |                -0.00908824 |      0.482759 |        0.207895  |        -0.133908  |
| MM_STRUCTURE_NEUTRAL              |     106 |             0.00879391  |                 0.00956677 |      0.733333 |             0.0146332   |                0.0173229   |      0.692308 |              0.0237176  |                 0.0292887  |      0.735294 |              0.0370013  |                 0.0292694  |      0.653061 |        0.239115  |        -0.1255    |

## MM Structure Contribution Analysis

| mm_structure_contribution_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:----------------------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| LONG_BUILDING                     |     191 |              0.00689527 |                 0.00800128 |      0.628272 |             0.0152881   |                 0.0171047  |      0.675393 |              0.0296555  |                 0.0318246  |      0.801047 |              0.0526927  |                0.0532884   |      0.921466 |         0.207895 |         -0.135196 |
| SHORT_COVERING                    |      99 |              0.00374932 |                 0.00654504 |      0.686869 |             0.00932083  |                 0.0103795  |      0.737374 |              0.0176909  |                 0.0218626  |      0.686869 |              0.0348306  |                0.0338164   |      0.777778 |         0.142329 |         -0.116224 |
| LONG_LIQUIDATION                  |     207 |             -0.00357984 |                -0.00401823 |      0.449275 |            -0.00476509  |                -0.00572189 |      0.391304 |             -0.00716953 |                -0.0109772  |      0.362319 |             -0.0106101  |               -0.0230965   |      0.285024 |         0.239587 |         -0.133908 |
| SHORT_BUILDING                    |     118 |             -0.00395939 |                -0.00495307 |      0.432203 |            -0.0100396   |                -0.00944929 |      0.355932 |             -0.0182331  |                -0.0187409  |      0.29661  |             -0.0261855  |               -0.0330494   |      0.220339 |         0.152911 |         -0.141753 |
| MIXED_LONG_AND_SHORT_UP           |     138 |              0.00670791 |                 0.00585138 |      0.637681 |             0.011307    |                 0.0137941  |      0.615942 |              0.0222625  |                 0.0247547  |      0.695652 |              0.0318643  |                0.0255947   |      0.644928 |         0.239115 |         -0.136609 |
| MIXED_LONG_AND_SHORT_DOWN         |     131 |              0.00153915 |                 0.00208689 |      0.541985 |            -6.78328e-05 |                 0.00224127 |      0.549618 |             -0.00202867 |                -0.00363299 |      0.480916 |              0.00667488 |               -0.000661677 |      0.48855  |         0.197196 |         -0.119216 |
| NEUTRAL_STRUCTURE                 |       8 |              0.0150236  |                 0.00915424 |      0.714286 |             0.0285532   |                 0.0212724  |      0.833333 |              0.0457257  |                 0.0418876  |      1        |            nan          |              nan           |    nan        |       nan        |        nan        |

## Strongest Lead-Lag Rows

| mm_feature           | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                          |   abs_rank_correlation |
|:---------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:----------------------------------------|-----------------------:|
| mm_net_velocity_4w   | 4W             |           0 |      0.483573 |           0.566401 |            837 | same_week_positive_historical_alignment |               0.566401 |
| mm_long_velocity_4w  | 4W             |           0 |      0.478632 |           0.565672 |            868 | same_week_positive_historical_alignment |               0.565672 |
| mm_long_velocity_8w  | 8W             |           0 |      0.422451 |           0.473207 |            864 | same_week_positive_historical_alignment |               0.473207 |
| mm_net_velocity_8w   | 8W             |           0 |      0.415641 |           0.463548 |            833 | same_week_positive_historical_alignment |               0.463548 |
| mm_long_velocity_4w  | 2W             |           0 |      0.34649  |           0.428477 |            868 | same_week_positive_historical_alignment |               0.428477 |
| mm_net_velocity_4w   | 2W             |           0 |      0.337441 |           0.419732 |            837 | same_week_positive_historical_alignment |               0.419732 |
| mm_long_velocity_12w | 8W             |           0 |      0.37435  |           0.419694 |            860 | same_week_positive_historical_alignment |               0.419694 |
| mm_short_velocity_4w | 4W             |           0 |     -0.397219 |          -0.418657 |            868 | same_week_negative_historical_alignment |               0.418657 |
| mm_long_velocity_8w  | 4W             |           0 |      0.371448 |           0.418179 |            864 | same_week_positive_historical_alignment |               0.418179 |
| mm_net_velocity_12w  | 8W             |           0 |      0.358074 |           0.404761 |            829 | same_week_positive_historical_alignment |               0.404761 |

## Method Notes

- MM Long and MM Short percentiles use prior-only rolling 156-week windows with a 20-observation minimum.
- MM Net percentile uses the existing `mm_net_percentile_156w` from the master weekly dataset.
- Positive lag means the MM feature is shifted earlier against gold following returns.
- All outputs are historical structure research only.
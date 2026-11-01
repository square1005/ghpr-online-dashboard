# GHPR v0.6 MM Long / Short Structure Lifecycle Research

Historical structure research only. Not a trading signal. Not financial advice.

## Executive Summary

- Data period: `2009-09-01` to `2026-10-27`.
- Latest date: `2026-10-27`.
- Latest MM Long / Short / Net: `122,508` / `16,946` / `105,562`.
- Latest MM Long / Short / Net percentile: `8.97%` / `15.38%` / `24.36%`.
- Latest Long / Short / Net velocity 8W: `-32.69%` / `12.18%` / `-33.97%`.
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

Latest 8W changes: Long `-27,213`, Short `3,996`, Net `-31,209`. Latest contribution label is `LONG_LIQUIDATION`.

### 4. When Net falls, is it driven by Long liquidation or Short building?

The contribution analysis table separates long-side reduction from short-side increase. This distinction matters because both can produce lower Net while describing different participation behavior.

### 5. Which has more information: Long Velocity, Short Velocity, or Net Velocity?

- Long: mm_long_velocity_4w vs 4W at lag 0W has rank correlation 0.568.
- Short: mm_short_velocity_4w vs 4W at lag 0W has rank correlation -0.422.
- Net: mm_net_velocity_4w vs 4W at lag 0W has rank correlation 0.569.

### 6. Does Long lead Gold?

mm_long_velocity_4w vs 4W at lag 0W has rank correlation 0.568.

### 7. Does Short lead Gold?

mm_short_velocity_4w vs 4W at lag 0W has rank correlation -0.422.

### 8. Is Net mainly a Long or Short outcome?

Net is a component outcome. The current 8W reconciliation confirms `mm_net_change_8w = mm_long_change_8w - mm_short_change_8w`, with any residual shown in `mm_net_change_8w_reconciliation_error`.

### 9. What is the current MM Structure State?

The current MM Structure State is `MM_STRUCTURE_LOW_PARTICIPATION`. This is a historical structure label, not a market instruction.

### 10. What do the current structure fields mean?

- MM Long Percentile: `8.97%`.
- MM Short Percentile: `15.38%`.
- MM Net Percentile: `24.36%`.
- Long Velocity 8W: `-32.69%`.
- Short Velocity 8W: `12.18%`.
- Net Velocity 8W: `-33.97%`.

### 11. Should GHPR Dashboard v0.6 add Long / Short / Net structure?

Yes, as a research layer. It improves explainability of the existing MM Net signal by showing whether long-side or short-side positioning is driving the structure.

### 12. Should Producer / OI lifecycle be added next?

Potentially, but this v0.6 module intentionally stays MM-only. Producer and OI lifecycle research should be separate modules so their definitions do not blur the MM structure study.

### 13. Current research conclusion

MM structure adds useful decomposition around MM Net. The dashboard should display it as historical structure research, with the existing MM Net percentile preserved as the current core positioning reference.

## MM Structure State Analysis

| mm_structure_state                |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:----------------------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| MM_STRUCTURE_ACCUMULATION         |     187 |             0.00483206  |                0.00581463  |      0.636364 |             0.0117224   |                 0.0124645  |      0.68984  |              0.0220352  |                 0.0258927  |      0.737968 |              0.0394784  |                 0.0378672  |      0.850267 |        0.142329  |        -0.135196  |
| MM_STRUCTURE_SHORT_COVERING_RALLY |      54 |             0.000424144 |                0.00244548  |      0.592593 |             2.68613e-05 |                -0.00179082 |      0.481481 |             -0.00701579 |                -0.00887337 |      0.407407 |             -0.00623099 |                -0.00400469 |      0.37037  |        0.0816615 |        -0.119216  |
| MM_STRUCTURE_LONG_LIQUIDATION     |     292 |            -0.00272497  |               -0.00375328  |      0.431507 |            -0.00601736  |                -0.006655   |      0.393836 |             -0.00977727 |                -0.0114109  |      0.342466 |             -0.0146133  |                -0.023045   |      0.291096 |        0.239587  |        -0.141753  |
| MM_STRUCTURE_SHORT_BUILDING       |      39 |            -0.00367702  |               -0.00146849  |      0.410256 |            -0.00524069  |                -0.00385505 |      0.333333 |             -0.0102687  |                -0.0189264  |      0.282051 |             -0.0211194  |                -0.0255492  |      0.179487 |        0.120818  |        -0.136609  |
| MM_STRUCTURE_CROWDED_LONG         |     156 |             0.00546397  |                0.00772644  |      0.615385 |             0.0118098   |                 0.0132346  |      0.660256 |              0.0257963  |                 0.0243997  |      0.788462 |              0.0467741  |                 0.044928   |      0.820513 |        0.18041   |        -0.0721955 |
| MM_STRUCTURE_LOW_PARTICIPATION    |      62 |            -0.00122592  |               -0.000163327 |      0.5      |            -0.00452826  |                -0.00212747 |      0.467742 |             -0.00534741 |                -0.0105027  |      0.403226 |              0.00511145 |                -0.0127527  |      0.451613 |        0.207895  |        -0.133908  |
| MM_STRUCTURE_NEUTRAL              |     106 |             0.00879391  |                0.00956677  |      0.733333 |             0.0146332   |                 0.0173229  |      0.692308 |              0.0237176  |                 0.0292887  |      0.735294 |              0.0370013  |                 0.0292694  |      0.653061 |        0.239115  |        -0.1255    |

## MM Structure Contribution Analysis

| mm_structure_contribution_state   |   count |   avg_forward_return_1w |   median_forward_return_1w |   win_rate_1w |   avg_forward_return_2w |   median_forward_return_2w |   win_rate_2w |   avg_forward_return_4w |   median_forward_return_4w |   win_rate_4w |   avg_forward_return_8w |   median_forward_return_8w |   win_rate_8w |   best_return_8w |   worst_return_8w |
|:----------------------------------|--------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|------------------------:|---------------------------:|--------------:|-----------------:|------------------:|
| LONG_BUILDING                     |     191 |              0.00689527 |                 0.00800128 |      0.628272 |             0.0152881   |                 0.0171047  |      0.675393 |              0.0296555  |                 0.0318246  |      0.801047 |              0.0526927  |                0.0532884   |      0.921466 |         0.207895 |         -0.135196 |
| SHORT_COVERING                    |      99 |              0.00374932 |                 0.00654504 |      0.686869 |             0.00932083  |                 0.0103795  |      0.737374 |              0.0176909  |                 0.0218626  |      0.686869 |              0.0348306  |                0.0338164   |      0.777778 |         0.142329 |         -0.116224 |
| LONG_LIQUIDATION                  |     211 |             -0.00363184 |                -0.00401823 |      0.445498 |            -0.00504936  |                -0.00589668 |      0.383886 |             -0.00784501 |                -0.0110518  |      0.35545  |             -0.0118449  |               -0.0249944   |      0.279621 |         0.239587 |         -0.133908 |
| SHORT_BUILDING                    |     118 |             -0.00395939 |                -0.00495307 |      0.432203 |            -0.0100396   |                -0.00944929 |      0.355932 |             -0.0182331  |                -0.0187409  |      0.29661  |             -0.0261855  |               -0.0330494   |      0.220339 |         0.152911 |         -0.141753 |
| MIXED_LONG_AND_SHORT_UP           |     138 |              0.00670791 |                 0.00585138 |      0.637681 |             0.011307    |                 0.0137941  |      0.615942 |              0.0222625  |                 0.0247547  |      0.695652 |              0.0318643  |                0.0255947   |      0.644928 |         0.239115 |         -0.136609 |
| MIXED_LONG_AND_SHORT_DOWN         |     131 |              0.00153915 |                 0.00208689 |      0.541985 |            -6.78328e-05 |                 0.00224127 |      0.549618 |             -0.00202867 |                -0.00363299 |      0.480916 |              0.00667488 |               -0.000661677 |      0.48855  |         0.197196 |         -0.119216 |
| NEUTRAL_STRUCTURE                 |       8 |              0.0150236  |                 0.00915424 |      0.714286 |             0.0285532   |                 0.0212724  |      0.833333 |              0.0457257  |                 0.0418876  |      1        |            nan          |              nan           |    nan        |       nan        |        nan        |

## Strongest Lead-Lag Rows

| mm_feature           | gold_horizon   |   lag_weeks |   correlation |   rank_correlation |   sample_count | interpretation                          |   abs_rank_correlation |
|:---------------------|:---------------|------------:|--------------:|-------------------:|---------------:|:----------------------------------------|-----------------------:|
| mm_net_velocity_4w   | 4W             |           0 |      0.486205 |           0.569472 |            841 | same_week_positive_historical_alignment |               0.569472 |
| mm_long_velocity_4w  | 4W             |           0 |      0.480679 |           0.568268 |            872 | same_week_positive_historical_alignment |               0.568268 |
| mm_long_velocity_8w  | 8W             |           0 |      0.426685 |           0.477336 |            868 | same_week_positive_historical_alignment |               0.477336 |
| mm_net_velocity_8w   | 8W             |           0 |      0.420556 |           0.468425 |            837 | same_week_positive_historical_alignment |               0.468425 |
| mm_long_velocity_4w  | 2W             |           0 |      0.348045 |           0.430608 |            872 | same_week_positive_historical_alignment |               0.430608 |
| mm_long_velocity_12w | 8W             |           0 |      0.376499 |           0.42257  |            864 | same_week_positive_historical_alignment |               0.42257  |
| mm_long_velocity_8w  | 4W             |           0 |      0.374951 |           0.422124 |            868 | same_week_positive_historical_alignment |               0.422124 |
| mm_net_velocity_4w   | 2W             |           0 |      0.339224 |           0.422119 |            841 | same_week_positive_historical_alignment |               0.422119 |
| mm_short_velocity_4w | 4W             |           0 |     -0.398572 |          -0.421893 |            872 | same_week_negative_historical_alignment |               0.421893 |
| mm_net_velocity_12w  | 8W             |           0 |      0.360163 |           0.407593 |            833 | same_week_positive_historical_alignment |               0.407593 |

## Method Notes

- MM Long and MM Short percentiles use prior-only rolling 156-week windows with a 20-observation minimum.
- MM Net percentile uses the existing `mm_net_percentile_156w` from the master weekly dataset.
- Positive lag means the MM feature is shifted earlier against gold following returns.
- All outputs are historical structure research only.
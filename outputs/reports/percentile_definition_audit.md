# GHPR v0.5 Percentile Definition Audit

## Technical Summary

- Recommended formal v0.5 policy: factor-specific rolling percentile definitions (MM Net: `rolling_260w`, Producer Net: `rolling_156w`, Total Open Interest: `rolling_52w`). This preserves the strongest measured window for each positioning input.
- If GHPR must keep one unified rolling window for product simplicity, use `rolling_260w`. This is the best average production-safe rolling definition across the three audited factors, but it sacrifices some factor-level information content.
- Full-history percentile is included only as a research benchmark and is not production-safe because it uses future observations.
- Scores evaluate historical stability, all four forward horizons, and the 4W/8W long-horizon subset. This is historical statistics only, not a trading signal and not financial advice.
- Data period: `2009-09-01` to `2026-05-26` from `data/processed/ghpr_master_weekly.csv`.

## Recommended Definitions

| Factor | Recommended production-safe definition | Best rolling definition | Unified rolling recommendation |
|---|---|---|---|
| MM Net | `rolling_260w` | `rolling_260w` | `rolling_260w` |
| Producer Net | `rolling_156w` | `rolling_156w` | `rolling_260w` |
| Total Open Interest | `rolling_52w` | `rolling_52w` | `rolling_260w` |

## What Was Measured

- Factors audited: `mm_net`, `producer_net`, and `total_open_interest`.
- Rolling definitions audited: `rolling_52w`, `rolling_104w`, `rolling_156w`, `rolling_260w`.
- Additional definition audited: `full_history`.
- Percentile audit dataset output: `data\processed\ghpr_percentile_audit_dataset.csv`.
- Feature matrix output: `data\processed\ghpr_percentile_definition_audit.csv`.
- Information comparison output: `outputs\reports\percentile_definition_information_comparison.csv`.
- Bucket analysis output: `outputs\reports\percentile_definition_bucket_analysis.csv`.
- Train/test validation output: `outputs\reports\percentile_definition_train_test.csv`.
- Definition stability scorecard output: `outputs\reports\percentile_definition_scorecard.csv`.
- Feature matrix percentile fields use the same 0-1 scale as the existing GHPR master weekly percentile columns.
- Forward outcomes audited: `gold_return_1w`, `gold_return_2w`, `gold_return_4w`, and `gold_return_8w`.
- Audit note: the persisted master `gold_return_*` columns currently behave like trailing `pct_change` fields, so this script recomputes same-named forward outcome columns from `gold_close.shift(-h)` inside the audit dataframe.
- Rolling percentile minimum data requirement: `52` weekly observations.

## Scoring Method

- Stability score combines coverage, effective decile coverage, lower median weekly percentile change, and lower 95th percentile weekly change.
- Information score combines absolute Spearman rank correlation, absolute decile monotonicity, absolute top-minus-bottom decile t-stat, sample count, and non-empty decile count.
- Overall score is the equal-weight average of stability score, mean 1W/2W/4W/8W information score, and mean 4W/8W long-horizon information score.
- Higher scores mean the definition was more useful under this audit framework; they do not imply a market direction.

## Top Summary Rows

| display_name        | definition   | production_safe   |   coverage |   median_abs_weekly_change |   information_score_mean_all_horizons |   information_score_mean_4w_8w |   overall_score |
|:--------------------|:-------------|:------------------|-----------:|---------------------------:|--------------------------------------:|-------------------------------:|----------------:|
| MM Net              | full_history | False             |     1      |                     0.0378 |                                 0.65  |                           0.66 |          0.7367 |
| MM Net              | rolling_260w | True              |     0.9416 |                     0.0385 |                                 0.67  |                           0.66 |          0.6683 |
| MM Net              | rolling_156w | True              |     0.9416 |                     0.0385 |                                 0.635 |                           0.7  |          0.6367 |
| MM Net              | rolling_104w | True              |     0.9416 |                     0.0481 |                                 0.545 |                           0.54 |          0.52   |
| Producer Net        | full_history | False             |     1      |                     0.0263 |                                 0.59  |                           0.64 |          0.71   |
| Producer Net        | rolling_156w | True              |     0.9416 |                     0.0321 |                                 0.68  |                           0.7  |          0.6517 |
| Producer Net        | rolling_260w | True              |     0.9416 |                     0.0269 |                                 0.64  |                           0.6  |          0.6383 |
| Producer Net        | rolling_104w | True              |     0.9416 |                     0.0385 |                                 0.56  |                           0.5  |          0.5117 |
| Total Open Interest | full_history | False             |     1      |                     0.04   |                                 0.75  |                           0.74 |          0.78   |
| Total Open Interest | rolling_52w  | True              |     0.9416 |                     0.0577 |                                 0.795 |                           0.82 |          0.6633 |
| Total Open Interest | rolling_260w | True              |     0.9416 |                     0.0399 |                                 0.47  |                           0.44 |          0.545  |
| Total Open Interest | rolling_104w | True              |     0.9416 |                     0.0577 |                                 0.53  |                           0.54 |          0.515  |

## 1W / 2W / 4W / 8W Detail Leaders

| display_name        | definition   | horizon   |   sample_count |   spearman_ic |   decile_monotonicity |   tail_spread_top_minus_bottom |   tail_spread_tstat |   information_score |
|:--------------------|:-------------|:----------|---------------:|--------------:|----------------------:|-------------------------------:|--------------------:|--------------------:|
| MM Net              | rolling_260w | 1W        |            822 |        0.0318 |                0.4545 |                         0.0013 |              0.4289 |                0.74 |
| MM Net              | full_history | 1W        |            873 |        0.0279 |                0.1758 |                        -0.0013 |             -0.3948 |                0.68 |
| MM Net              | rolling_156w | 1W        |            822 |        0.0189 |                0.0788 |                         0.0019 |              0.7075 |                0.6  |
| MM Net              | rolling_52w  | 2W        |            821 |       -0.0383 |               -0.3455 |                        -0.0008 |             -0.2213 |                0.62 |
| MM Net              | rolling_104w | 2W        |            821 |       -0.0114 |                0.4061 |                         0.0033 |              0.8121 |                0.62 |
| MM Net              | rolling_260w | 2W        |            821 |        0.0277 |                0.5636 |                         0.0003 |              0.0721 |                0.62 |
| MM Net              | rolling_156w | 4W        |            819 |        0.0292 |                0.3091 |                         0.0086 |              1.6805 |                0.66 |
| MM Net              | rolling_260w | 4W        |            819 |        0.0545 |                0.5879 |                         0.0002 |              0.0392 |                0.66 |
| MM Net              | rolling_104w | 4W        |            819 |        0.005  |                0.3576 |                         0.0063 |              1.1798 |                0.58 |
| MM Net              | full_history | 8W        |            866 |        0.0581 |                0.3818 |                        -0.0168 |             -2.0223 |                0.76 |
| MM Net              | rolling_156w | 8W        |            815 |        0.0798 |                0.7576 |                         0.0114 |              1.6262 |                0.74 |
| MM Net              | rolling_260w | 8W        |            815 |        0.1068 |                0.6606 |                         0.0056 |              0.6829 |                0.66 |
| Producer Net        | rolling_104w | 1W        |            822 |       -0.0163 |               -0.1879 |                         0.0022 |              0.7764 |                0.66 |
| Producer Net        | rolling_260w | 1W        |            822 |       -0.0367 |                0.0303 |                         0.0039 |              1.2012 |                0.66 |
| Producer Net        | rolling_156w | 1W        |            822 |       -0.0336 |               -0.1758 |                         0.0007 |              0.2437 |                0.62 |
| Producer Net        | rolling_156w | 2W        |            821 |       -0.036  |               -0.2485 |                        -0.0014 |             -0.3434 |                0.7  |
| Producer Net        | rolling_260w | 2W        |            821 |       -0.039  |               -0.0909 |                         0.0067 |              1.5984 |                0.7  |
| Producer Net        | rolling_104w | 2W        |            821 |       -0.0144 |               -0.1273 |                         0.0027 |              0.6699 |                0.58 |
| Producer Net        | rolling_156w | 4W        |            819 |       -0.0411 |               -0.2848 |                        -0.0036 |             -0.6805 |                0.7  |
| Producer Net        | full_history | 4W        |            870 |        0.029  |                0.1758 |                         0.0053 |              0.7259 |                0.64 |
| Producer Net        | rolling_52w  | 4W        |            819 |        0.0408 |                0.3333 |                         0.0014 |              0.2524 |                0.62 |
| Producer Net        | rolling_156w | 8W        |            815 |       -0.075  |               -0.2727 |                        -0.0087 |             -1.2038 |                0.7  |
| Producer Net        | full_history | 8W        |            866 |        0.0405 |                0.297  |                         0.0079 |              0.8864 |                0.64 |
| Producer Net        | rolling_104w | 8W        |            815 |       -0.0462 |                0.2121 |                        -0.0065 |             -0.9079 |                0.58 |
| Total Open Interest | full_history | 1W        |            873 |        0.0189 |                0.1636 |                        -0.0014 |             -0.4071 |                0.84 |
| Total Open Interest | rolling_52w  | 1W        |            822 |       -0.0392 |               -0.0424 |                        -0.0037 |             -1.2814 |                0.72 |
| Total Open Interest | rolling_156w | 1W        |            822 |        0.0048 |                0.0424 |                         0.0011 |              0.3845 |                0.52 |
| Total Open Interest | rolling_52w  | 2W        |            821 |       -0.0659 |               -0.2242 |                        -0.0049 |             -1.2417 |                0.82 |
| Total Open Interest | full_history | 2W        |            872 |        0.0047 |                0.2    |                        -0.0019 |             -0.3924 |                0.68 |
| Total Open Interest | rolling_104w | 2W        |            821 |       -0.0238 |                0.0424 |                        -0.0011 |             -0.2798 |                0.58 |
| Total Open Interest | rolling_52w  | 4W        |            819 |       -0.0838 |               -0.4788 |                        -0.0088 |             -1.6625 |                0.82 |
| Total Open Interest | full_history | 4W        |            870 |        0.0212 |                0.2364 |                         0.0039 |              0.6084 |                0.76 |
| Total Open Interest | rolling_104w | 4W        |            819 |       -0.0219 |                0.0909 |                        -0.0017 |             -0.3125 |                0.58 |
| Total Open Interest | rolling_52w  | 8W        |            815 |       -0.092  |               -0.7212 |                        -0.0175 |             -2.2808 |                0.82 |
| Total Open Interest | full_history | 8W        |            866 |        0.0462 |                0.3091 |                         0.0111 |              1.3827 |                0.72 |
| Total Open Interest | rolling_104w | 8W        |            815 |       -0.011  |               -0.4303 |                        -0.0007 |             -0.1038 |                0.5  |

## Formal GHPR Adoption Recommendation

Adopt factor-specific rolling percentile definitions for v0.5: MM Net: `rolling_260w`, Producer Net: `rolling_156w`, Total Open Interest: `rolling_52w`. This is the strongest formal recommendation because MM, Producer, and OI do not share the same best information window.

If product simplicity requires a single unified window, use `rolling_260w` and document that it is a compromise definition. It improves cross-factor consistency but is not the strongest 4W/8W information definition for every factor.

Keep the current 156W definition only if continuity with v0.4 dashboards is more important than the measured v0.5 audit score. The audit intentionally does not assume 156W is optimal.

## Limitations And Robustness Notes

- This audit is descriptive and diagnostic. It does not establish causality or produce a trading rule.
- Full-history percentile is not eligible for production use because it uses future observations.
- Higher stability can reduce responsiveness. Very long windows may look cleaner but can underreact to regime changes.
- Forward returns use `gold_close`, currently a COMEX GC futures proxy aligned to the GHPR weekly dataset.
- Window scores are sensitive to the selected scoring weights. The CSV outputs preserve raw metrics for alternate weighting.
# MM Weekly Change Summary

Historical COT Weekly Change Research only. Not a trading signal. Not financial advice.

## Dataset

- Source: `data/processed/ghpr_master_weekly.csv`
- Output: `data/processed/mm_weekly_change_dataset.csv`
- Data period: `2009-09-01` to `2026-11-03`
- Rows: `897`

## Latest Weekly Change

- Latest date: `2026-11-03`
- Previous date: `2026-10-27`
- MM Long: `122,283`
- MM Short: `18,669`
- MM Net: `103,614`
- Long 1W change: `-225` (-0.18%)
- Short 1W change: `1,723` (10.17%)
- Net 1W change: `-1,948` (-1.85%)
- Weekly structure state: `LONG_LIQUIDATION_SHORT_BUILDING`

## Classification Rules

- `LONG_BUILDING_SHORT_COVERING`: long change > 0 and short change < 0.
- `LONG_BUILDING_SHORT_BUILDING`: long change > 0 and short change > 0.
- `LONG_LIQUIDATION_SHORT_COVERING`: long change < 0 and short change < 0.
- `LONG_LIQUIDATION_SHORT_BUILDING`: long change < 0 and short change > 0.
- `NET_UP`: net change > 0 when long/short structure is neutral.
- `NET_DOWN`: net change < 0 when long/short structure is neutral.
- `NEUTRAL`: other cases or insufficient prior-week data.

## State Counts

| State | Count |
| --- | ---: |
| `LONG_LIQUIDATION_SHORT_BUILDING` | 298 |
| `LONG_BUILDING_SHORT_COVERING` | 278 |
| `LONG_BUILDING_SHORT_BUILDING` | 172 |
| `LONG_LIQUIDATION_SHORT_COVERING` | 148 |
| `NEUTRAL` | 1 |

## Interpretation Limit

This layer shows the latest COT report versus the prior report. It is a weekly positioning-change lens, not a forecast and not an execution rule.

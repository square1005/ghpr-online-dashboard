# MM Weekly Change Summary

Historical COT Weekly Change Research only. Not a trading signal. Not financial advice.

## Dataset

- Source: `data/processed/ghpr_master_weekly.csv`
- Output: `data/processed/mm_weekly_change_dataset.csv`
- Data period: `2009-09-01` to `2026-10-13`
- Rows: `894`

## Latest Weekly Change

- Latest date: `2026-10-13`
- Previous date: `2026-10-06`
- MM Long: `124,747`
- MM Short: `17,658`
- MM Net: `107,089`
- Long 1W change: `-2,354` (-1.85%)
- Short 1W change: `1,544` (9.58%)
- Net 1W change: `-3,898` (-3.51%)
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
| `LONG_LIQUIDATION_SHORT_BUILDING` | 297 |
| `LONG_BUILDING_SHORT_COVERING` | 278 |
| `LONG_BUILDING_SHORT_BUILDING` | 171 |
| `LONG_LIQUIDATION_SHORT_COVERING` | 147 |
| `NEUTRAL` | 1 |

## Interpretation Limit

This layer shows the latest COT report versus the prior report. It is a weekly positioning-change lens, not a forecast and not an execution rule.

# MM Weekly Change Summary

Historical COT Weekly Change Research only. Not a trading signal. Not financial advice.

## Dataset

- Source: `data/processed/ghpr_master_weekly.csv`
- Output: `data/processed/mm_weekly_change_dataset.csv`
- Data period: `2009-09-01` to `2026-06-23`
- Rows: `878`

## Latest Weekly Change

- Latest date: `2026-06-23`
- Previous date: `2026-06-16`
- MM Long: `131,102`
- MM Short: `15,707`
- MM Net: `115,395`
- Long 1W change: `3,059` (2.39%)
- Short 1W change: `1,385` (9.67%)
- Net 1W change: `1,674` (1.47%)
- Weekly structure state: `LONG_BUILDING_SHORT_BUILDING`

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
| `LONG_LIQUIDATION_SHORT_BUILDING` | 294 |
| `LONG_BUILDING_SHORT_COVERING` | 275 |
| `LONG_BUILDING_SHORT_BUILDING` | 166 |
| `LONG_LIQUIDATION_SHORT_COVERING` | 142 |
| `NEUTRAL` | 1 |

## Interpretation Limit

This layer shows the latest COT report versus the prior report. It is a weekly positioning-change lens, not a forecast and not an execution rule.

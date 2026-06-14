# GHPR v0.6.4 MM Velocity Reading Layer

Historical structure research only. Not a trading signal. Not financial advice.

## 1. What Is This Reading Layer?

This layer compares the current 8W dashboard baseline with the research-candidate velocity windows from the v0.6.2 window discovery and v0.6.3 review layer. It is designed to make the velocity definition readable without replacing the existing dashboard baseline.

## 2. Why Compare 8W Baseline And Candidate Windows?

8W remains the continuity baseline because GHPR already uses it for the MM Structure Lifecycle page. Candidate windows can capture different historical rhythms: Long and Net may behave more like medium-term cycles, while Short can react faster. The comparison shows whether the baseline and candidate windows are aligned or diverging.

## 3. Long 8W vs 26W

Long 8W is the current swing baseline. Long 26W is the research candidate for medium-term position-building or reduction. When both point in the same direction, the short swing and medium-term Long readings are aligned. When they diverge, the current swing move may not yet be confirmed by the medium-term Long cycle.

## 4. Short 8W vs 2W / 4W

Short 2W / 4W is the research candidate for faster short-side stress or covering windows. The `short_candidate_fast_avg` field averages 2W and 4W to reduce single-window noise while preserving short-term sensitivity.

## 5. Net 8W vs 26W

Net 8W is the current swing baseline. Net 26W is the research candidate because Net behavior often resembles the broader Long-side cycle. Comparing the two helps identify whether the current Net swing is also visible in the medium-term structure.

## 6. Latest Reading Snapshot

| Field | Value |
|---|---|
| date | `2026-06-09` |
| gold_close | `4,468.10` |
| long_baseline_8w | `2.56 pct points` |
| long_candidate_26w | `-14.74 pct points` |
| long_alignment_status | `BASELINE_POSITIVE_CANDIDATE_NEGATIVE` |
| short_baseline_8w | `-21.15 pct points` |
| short_candidate_2w | `-11.54 pct points` |
| short_candidate_4w | `-18.59 pct points` |
| short_candidate_fast_avg | `-15.06 pct points` |
| short_alignment_status | `SAME_DIRECTION_NEGATIVE` |
| net_baseline_8w | `10.26 pct points` |
| net_candidate_26w | `-14.74 pct points` |
| net_alignment_status | `BASELINE_POSITIVE_CANDIDATE_NEGATIVE` |
| overall_velocity_reading | `MEDIUM_TERM_STRUCTURE_WEAKENING` |

## 7. Overall Reading Distribution

| Reading | Count |
|---|---:|
| MEDIUM_TERM_STRUCTURE_WEAKENING | 386 |
| MEDIUM_TERM_PARTICIPATION_BUILDING | 323 |
| MIXED_STRUCTURE | 108 |
| SHORT_TERM_RECOVERY_MEDIUM_TERM_UNCONFIRMED | 53 |
| SHORT_TERM_ONLY_REACTION | 6 |

## 8. Are Long / Short / Net Aligned?

- Long alignment: `BASELINE_POSITIVE_CANDIDATE_NEGATIVE`.
- Short alignment: `SAME_DIRECTION_NEGATIVE`.
- Net alignment: `BASELINE_POSITIVE_CANDIDATE_NEGATIVE`.
- Overall reading: `MEDIUM_TERM_STRUCTURE_WEAKENING`.

## 9. Should GHPR Replace 8W Now?

No formal replacement is made in v0.6.4. The dashboard should keep the 8W continuity baseline while displaying the candidate windows as historical research context. A later version can decide whether a formal definition change improves readability and stability.

## Research Limit

This report only describes historical velocity-window structure. It does not forecast price, does not rank actions, does not connect to execution systems, and does not provide financial advice.

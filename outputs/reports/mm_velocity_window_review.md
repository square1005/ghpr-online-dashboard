# GHPR v0.6.3 MM Velocity Window Review

Historical Research Definition Layer only. Not a trading signal. Not financial advice.

## Executive Conclusion

- Do not immediately replace the current formal 8W velocity definition.
- Show both the current dashboard baseline and the research candidate windows.
- Review Long 26W / Short 2W or 4W / Net 26W against the 8W continuity baseline before any v0.7 definition change.
- Use this layer to explain historical structure rhythm, not to create a market instruction.

## 1. Why Not Use One Window For All MM Velocity?

MM Long, MM Short, and MM Net do not necessarily move on the same time scale. Long positioning often reflects slower allocation and position-building behavior. Short positioning can move faster when positioning stress, event reaction, or covering behavior appears. Net positioning blends both sides, so it can inherit the slower Long cycle when Long dominates the net change.

Using one shared window is simple and readable, but it can hide these different rhythms. The v0.6.2 discovery layer showed that a single 8W window is useful as a continuity baseline, but not automatically optimal for every MM component.

## 2. Why Long Velocity Fits 26W

The v0.6.2 scorecard selected 26W as the strongest research candidate for MM Long Velocity. This suggests Long-side changes may be better understood as a medium-term lifecycle rather than a short burst.

Interpretation:

- 26W captures about half a year of positioning drift.
- It smooths short weekly noise.
- It is better suited for observing whether managed-money long exposure is being built or reduced over a broader historical structure cycle.

中文說明：MM Long Velocity 比較像中期建倉或減倉週期。目前研究顯示 26W 可能比 8W 更適合觀察 Long 的中期生命週期。

## 3. Why Short Velocity Fits 2W / 4W

The v0.6.2 scorecard selected 2W as the strongest Short Velocity candidate, while 4W had the strongest stability profile among the tested feature/window pairs. This points to a faster rhythm on the short side.

Interpretation:

- 2W is very responsive, but noisier.
- 4W is still short-term, but may be easier to monitor.
- Short-side movement may reflect event-driven repositioning, stress windows, or covering behavior more quickly than Long-side movement.

中文說明：MM Short Velocity 比較像短線避險、事件反應或空單回補週期。目前研究顯示 2W / 4W 可能比 8W 更適合觀察 Short 的快速變化。

## 4. Why Net Velocity Is Close To 26W

MM Net combines Long and Short behavior. In the v0.6.2 discovery scorecard, Net Velocity also selected 26W as the research candidate. This suggests that the net measure may be closer to a medium-term allocation cycle than to a short event window.

Interpretation:

- Net Velocity is not just a faster stress indicator.
- When Long-side behavior dominates the net shift, Net Velocity can resemble the Long medium-term lifecycle.
- 26W is therefore a useful research candidate for Net, while 8W remains useful for continuity.

中文說明：MM Net Velocity 是 Long 與 Short 的綜合結果。目前研究顯示 Net 的節奏比較接近 Long 的中期週期，因此 26W 值得作為候選主視窗。

## 5. Why Keep 8W As The Continuity Baseline?

8W remains useful because it is already the GHPR v0.6 dashboard baseline and is easy to interpret as a swing-cycle velocity window. Replacing it immediately would make historical dashboard comparisons harder and could overfit the latest audit.

Practical conclusion:

- Keep 8W as the current dashboard baseline.
- Display 26W and 2W / 4W as research candidates.
- Compare baseline and candidates visually before making a formal replacement decision.

## 6. How The Dashboard Should Read Long / Short / Net Velocity

| Component | Current Baseline | Research Candidate | Interpretation |
|---|---:|---:|---|
| Long Velocity | 8W | 26W | 中期建倉 / 減倉週期 |
| Short Velocity | 8W | 2W / 4W | 短線壓力 / 空單回補週期 |
| Net Velocity | 8W | 26W | 綜合中期資金週期 |

Dashboard reading guide:

- Long Velocity: use 26W as the research lens for medium-term position-building or reduction.
- Short Velocity: monitor 2W / 4W as short-term stress or covering windows.
- Net Velocity: use 26W as a candidate for broader capital-cycle interpretation.
- 8W: keep as the continuity baseline until GHPR formally changes the definition.

## 7. Why This Is Not A Trading Signal

This review only defines how to observe historical positioning velocity windows. It does not forecast price, does not rank trades, does not issue entry or exit instructions, and does not connect to any execution system.

All results should be read as historical structure research only. They are background context for understanding positioning rhythm, not financial advice.

## 8. Should The Next Stage Replace 8W?

Not yet. The recommended next stage is to keep 8W in place through v0.7 while adding the research-candidate layer:

- Long: compare 8W baseline with 26W candidate.
- Short: compare 8W baseline with 2W / 4W candidates.
- Net: compare 8W baseline with 26W candidate.

Formal replacement should wait until the team reviews whether the candidate windows improve dashboard readability, stability, and historical interpretation without making the system harder to understand.

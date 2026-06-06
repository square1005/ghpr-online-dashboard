# GHPR v0.5-A MM Percentile Definition Audit

Data period: `2009-09-01` to `2026-05-26`.
Rows: `874`.

This is historical statistics and research reference only. It does not create market instructions, execution logic, or financial advice.

## Executive Answer

- This MM-only audit is intentionally separate from the broader v0.5 multi-factor audit. It should be reviewed as one research lens before any v0.6 dashboard definition change.
- 156W is reasonable and wins at least one horizon, but the MM-only audit still favors a factor-specific comparison instead of assuming 156W is universally best.
- Best production-safe average score: `104W percentile` with `68.7`.
- Best production-safe 4W/8W average score: `260W percentile` with `70.3`.
- Best average 4W/8W information score: `104W percentile` with `70.0`.
- 156W average score: `62.9`; recommended horizons: `1`.
- Final dashboard decision: `暫不替換`. Keep `mm_net_percentile_156w` as the current dashboard main reference until v0.6 review, while tracking 104W and 260W as research candidates.
- Full History percentile is useful as a research benchmark, but it is not production-safe because historical rows use future observations.

## Required Questions

### 1. 目前 GHPR 使用的 156W MM Percentile 是什麼？

`mm_net_percentile_156w` 是把當週 MM net positioning 放到 156 週歷史窗口中做百分位定位。v0.5-A audit 使用 production-safe trailing definition：當週只和前 156 週資料比較，不使用未來資料。Dashboard 目前仍以 156W 作為 Current Position 的 MM reference。

### 2. 156W 的優點是什麼？

- 156W 約等於三年週資料，樣本數足夠，decile 不會太稀疏。
- 比 52W 更平滑，較不容易把短期 positioning 波動放大成極端狀態。
- 與目前 GHPR Dashboard 口徑一致，保留它能維持使用者解讀的連續性。
- 在本次 scorecard 中，156W 的平均 total score 為 `62.9`，且 8W horizon 被選為 recommended。

### 3. 156W 的缺點是什麼？

- 156W 不是所有 horizon 的最佳定義：1W/4W 偏向 104W，2W 偏向 52W，8W 才由 156W 勝出。
- 它比 52W/104W 反應慢，遇到 positioning regime 快速切換時可能較滯後。
- 156W 平均 total score `62.9` 低於 best average definition `104W percentile` 的 `68.7`。

### 4. 52W / 104W / 156W / 260W / full_history 各自差異是什麼？

- `52W percentile`：一年窗口，反應最快，但 weekly change 最大，interpretability 有 jumpiness penalty。
- `104W percentile`：兩年窗口，速度與穩定度較均衡，本次平均 total score 最高。
- `156W percentile`：三年窗口，現行 Dashboard reference，連續性佳，8W horizon 表現較強。
- `260W percentile`：五年窗口，更偏長週期 positioning，4W/8W average total score 較高。
- `full_history percentile`：全樣本歷史定位，適合研究 benchmark，但因為歷史列會使用未來觀測排序，不可作為即時 Dashboard 或 historical backtest 主定義。

### 5. 哪個定義最穩定？

若只看 weekly percentile change，最穩定的是 `Full History percentile`，平均 weekly change `0.0378`。但它若是 full_history，僅能作研究 benchmark。production-safe rolling 定義中，最穩定的是 `260W percentile`，平均 weekly change `0.0385`。

### 6. 哪個定義對 4W / 8W 最有資訊量？

依 information_score 的 4W/8W 平均值，最佳為 `104W percentile`，平均 information score `70.0`。拆開看，4W information score 最高是 `52W percentile`，8W information score 最高是 `156W percentile`。

### 7. Train / Test 是否一致？

Train/Test rank correlation 方向在本次 scorecard 中大致一致；所有 scorecard row 的 train/test rank_corr 方向一致。

### 8. 最終推薦 GHPR Dashboard 暫時採用哪個 MM Percentile 定義？

`暫時採用現行 156W`。理由是：它是既有 Dashboard reference、8W horizon 勝出，而且目前證據不是單一窗口全面勝出。v0.5-A 建議把 104W / 260W 放入研究觀察清單，不立即替換正式 Current Position 定義。

### 9. 是否建議保留 156W 作為主定義？

是，暫時保留。不是因為 156W 絕對最佳，而是因為它有連續性、穩定性與 8W 支持，同時避免 v0.5-A 單因子結果過早改動正式 Dashboard。

### 10. 如果不建議，應改成哪一個？原因是什麼？

本報告不建議立刻替換，因此沒有正式替換定義。若 v0.6 決定改版，候選方向是：`104W percentile` 作為 balanced/default candidate，因為平均 total score 最高；若 Dashboard 更重視 4W/8W historical positioning，則 `260W percentile` 是長週期候選；若只看 8W 單一 horizon，156W 仍有保留理由。

### 11. 如果資料不足以決定，也要明確說明「暫不替換」。

`暫不替換`。目前資料足以說明 156W 不是唯一最佳，但不足以支持直接把正式 Dashboard 主定義從 156W 改成單一新窗口。下一步應在 v0.6 同時評估 Dashboard 使用者解讀、HSE 相似度結果、以及多因子一致性。

## Recommended Definitions By Horizon

| horizon   | definition      |   total_score |   rank_corr |   high_low_spread |   weekly_change_avg |   train_rank_corr |   test_rank_corr | reason                                                                                                                                                                    |
|:----------|:----------------|--------------:|------------:|------------------:|--------------------:|------------------:|-----------------:|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1W        | 104W percentile |       67.7333 |      0.2068 |            0.0139 |              0.0481 |            0.1775 |           0.2257 | rolling percentile is suitable for an online dashboard                                                                                                                    |
| 2W        | 52W percentile  |       69      |      0.321  |            0.0294 |              0.0577 |            0.3312 |           0.3003 | rolling percentile is suitable for an online dashboard; 52W window is more reactive and gets a jumpiness penalty                                                          |
| 4W        | 104W percentile |       73.3333 |      0.4277 |            0.0559 |              0.0481 |            0.4371 |           0.3825 | rolling percentile is suitable for an online dashboard; 4W/8W information receives primary research weight                                                                |
| 8W        | 156W percentile |       76.6667 |      0.5363 |            0.0926 |              0.0385 |            0.5648 |           0.4527 | rolling percentile is suitable for an online dashboard; 156W remains useful for continuity with the current dashboard; 4W/8W information receives primary research weight |

## Average Score By Definition

| definition              |   avg_total_score |   avg_information_score |   avg_weekly_change |   avg_train_test_score |   recommended_horizon_count |   avg_4w_8w_score |   avg_4w_8w_information_score | production_safe   |
|:------------------------|------------------:|------------------------:|--------------------:|-----------------------:|----------------------------:|------------------:|------------------------------:|:------------------|
| 104W percentile         |           68.7333 |                    68.5 |              0.0481 |                    100 |                           2 |           69.3333 |                            70 | True              |
| 260W percentile         |           64.4667 |                    49.5 |              0.0385 |                    100 |                           0 |           70.2667 |                            64 | True              |
| 156W percentile         |           62.9067 |                    45.6 |              0.0385 |                    100 |                           1 |           67.0667 |                            56 | True              |
| 52W percentile          |           60.8    |                    64.5 |              0.0577 |                    100 |                           1 |           55.8    |                            52 | True              |
| Full History percentile |           54.6708 |                    41.9 |              0.0378 |                    100 |                           0 |           61.1108 |                            58 | False             |

## 156W Reasonableness Check

- 156W has enough observations for stable deciles and remains useful for continuity with the existing dashboard.
- The audit does not support treating 156W as automatically optimal for MM.
- A longer window can better preserve the full MM positioning cycle; a shorter window can react faster but may overstate short-cycle moves.

## Definition Construction Notes

- Rolling percentile fields use a trailing historical window and compare the current `mm_net` against prior observations only.
- Rolling z-score fields use the same prior-only trailing window: `(current_mm_net - prior_window_mean) / prior_window_std`.
- `mm_net_percentile_full_history` is a full-sample historical positioning field for research context only. It should not be used for real-time historical backtests because past rows are ranked with future observations.

## Train/Test Validation Snapshot

| sample_split   | definition      | horizon   |   rank_corr |   high_low_spread |   win_rate_extreme_high |   win_rate_extreme_low |   sample_count |
|:---------------|:----------------|:----------|------------:|------------------:|------------------------:|-----------------------:|---------------:|
| train          | 52W percentile  | 4W        |      0.4895 |            0.0624 |                  0.8889 |                 0.2075 |            436 |
| train          | 52W percentile  | 8W        |      0.6082 |            0.1029 |                  0.9683 |                 0.0943 |            436 |
| train          | 104W percentile | 4W        |      0.4371 |            0.0503 |                  0.8333 |                 0.254  |            436 |
| train          | 104W percentile | 8W        |      0.5702 |            0.0865 |                  0.8571 |                 0.127  |            436 |
| train          | 156W percentile | 4W        |      0.4264 |            0.0464 |                  0.8293 |                 0.2878 |            436 |
| train          | 156W percentile | 8W        |      0.5648 |            0.0877 |                  0.8293 |                 0.1799 |            436 |
| train          | 260W percentile | 4W        |      0.4259 |            0.0428 |                  0.8372 |                 0.2866 |            436 |
| train          | 260W percentile | 8W        |      0.5639 |            0.0701 |                  0.814  |                 0.172  |            436 |
| test           | 52W percentile  | 4W        |      0.3417 |            0.0441 |                  0.8904 |                 0.3704 |            386 |
| test           | 52W percentile  | 8W        |      0.3249 |            0.0509 |                  0.9589 |                 0.4074 |            386 |
| test           | 104W percentile | 4W        |      0.3825 |            0.056  |                  0.8462 |                 0.3208 |            386 |
| test           | 104W percentile | 8W        |      0.4323 |            0.0832 |                  0.9538 |                 0.2453 |            386 |
| test           | 156W percentile | 4W        |      0.3981 |            0.0508 |                  0.8235 |                 0.2759 |            386 |
| test           | 156W percentile | 8W        |      0.4527 |            0.0944 |                  0.8971 |                 0.069  |            386 |
| test           | 260W percentile | 4W        |      0.435  |            0.0816 |                  0.9722 |                 0.0769 |            386 |
| test           | 260W percentile | 8W        |      0.5168 |            0.1146 |                  0.9722 |                 0      |            386 |

## Final Research View

For MM only, keep `mm_net_percentile_156w` visible as the current dashboard reference while v0.5-A treats the higher-scoring rolling definition as the research candidate for v0.6 review.
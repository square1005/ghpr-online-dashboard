# GHPR v0.5 Percentile Definition Audit Report

Data period: `2009-09-01` to `2026-05-26`.
Latest weekly row: `2026-05-26`.

This report is historical statistics and research reference only. It is not a trading signal and not financial advice.

## Executive Conclusion

- The current 156W rolling percentile is a reasonable continuity baseline, but the audit does not support treating it as the best universal definition.
- Recommended dashboard policy: keep 156W as a legacy reference, but show factor-specific v0.5 primary definitions.
- MM primary: `260W percentile` for dashboard interpretability (average score 61.5); `260W zscore` is useful as a long-horizon support field.
- Producer production-safe primary: `156W percentile` (average score 60.0). `104W percentile` is useful for shorter-horizon readability (average score 81.4), and `52W zscore` (84.2) should be tracked as a research companion.
- OI primary: `52W percentile` (average score 78.8). OI should also show absolute level and change because OI has structural level effects.

## Scorecard Snapshot

Recommended definition by factor and horizon:

| factor   | horizon   | definition      |   stability_score |   train_score |   test_score |
|:---------|:----------|:----------------|------------------:|--------------:|-------------:|
| MM       | 1W        | 260W percentile |             69.07 |         44.11 |        67.51 |
| MM       | 2W        | 52W percentile  |             72.13 |         74.12 |        46.24 |
| MM       | 4W        | 260W percentile |             81.24 |         61.53 |        84.89 |
| MM       | 8W        | 260W zscore     |             74.23 |         47.69 |        78.67 |
| OI       | 1W        | 52W percentile  |             75.01 |         83.33 |        45.27 |
| OI       | 2W        | 52W percentile  |             74.4  |         87.63 |        39.24 |
| OI       | 4W        | 52W percentile  |             80.22 |         94.12 |        49.37 |
| OI       | 8W        | 52W percentile  |             85.38 |         89.44 |        68.79 |
| Producer | 1W        | 104W percentile |             86.62 |         66.34 |        95.44 |
| Producer | 2W        | 104W percentile |             89.08 |         69.95 |        98.85 |
| Producer | 4W        | 52W zscore      |             85.67 |         75.66 |        83.39 |
| Producer | 8W        | 52W percentile  |             89.12 |         78.71 |        90.21 |

Average stability score by factor and definition, top rows:

| factor   | definition              |   avg_stability_score |   avg_train_score |   avg_test_score |   recommended_horizon_count |
|:---------|:------------------------|----------------------:|------------------:|-----------------:|----------------------------:|
| MM       | 260W zscore             |               73.045  |           49.67   |          73.3075 |                           1 |
| MM       | 52W zscore              |               69.07   |           69.205  |          42.42   |                           0 |
| MM       | 52W percentile          |               63.975  |           74.5425 |          43.9525 |                           1 |
| MM       | 260W percentile         |               61.4825 |           53.99   |          78.82   |                           2 |
| Producer | 52W zscore              |               84.2125 |           71.95   |          82.94   |                           1 |
| Producer | 104W percentile         |               81.355  |           70.8775 |          97.28   |                           2 |
| Producer | 52W percentile          |               78.555  |           76.5775 |          83.5875 |                           1 |
| Producer | 156W zscore             |               76.01   |           39.135  |          92.325  |                           0 |
| OI       | 52W percentile          |               78.7525 |           88.63   |          50.6675 |                           4 |
| OI       | 52W zscore              |               74.4975 |           84.2225 |          42.9125 |                           0 |
| OI       | Full History percentile |               61.8925 |           47.105  |          65.445  |                           0 |
| OI       | 104W percentile         |               51.785  |           56.455  |          48.645  |                           0 |

## 1. GHPR 目前 156W rolling percentile 是什麼？

`156W rolling percentile` 是把當週的因子值放進最近 156 週觀察值中排序，計算它位於這段 rolling window 的百分位。GHPR 目前 dashboard 使用的 `mm_net_percentile_156w`、`producer_net_percentile_156w`、`oi_percentile_156w` 就是這個定義。資料檔中 percentile 儲存為 0-1；dashboard 顯示時可轉成 0-100%。

Example formula:

`percentile_t = count(value_i <= value_t, i in t-155..t) / valid_count`

## 2. 156W 的優點是什麼？

- 約等於 3 年市場資料，直覺上容易解釋，也比 52W 更平滑。
- 不使用未來資料，適合線上 dashboard 與歷史回測共同使用。
- 對 COT 週資料來說，156W 有足夠樣本形成 decile，不會像太短窗口那樣容易劇烈跳動。
- 目前 v0.4 dashboard 已採用 156W，因此保留它可維持歷史連續性與使用者熟悉度。

## 3. 156W 的缺點是什麼？

- v0.5 scorecard 顯示 156W 不是三個因子的通用最優解：MM 156W 平均分 55.4，Producer 156W 平均分 60.0，OI 156W 平均分 41.3。
- 156W 對 OI 特別弱，因為 OI 同時有市場參與度、合約規模、結構性週期變化，單純 3 年百分位可能不夠敏感。
- 156W 可能太慢，遇到 2024-2026 這類價格與持倉 regime 轉換時，會保留過多舊狀態。
- 對短期定位而言，52W/104W 有時更敏感；對長期定位而言，260W 有時更穩定。

## 4. MM 最適合用哪個定義？

MM 建議使用 `260W percentile` 作為 dashboard 主定義。它在 scorecard 中平均分 61.5，並在多個 horizon 被選為 recommended。

Rationale:

- MM 是趨勢與擁擠度型因子，過短窗口容易把短週期波動誤判成極端定位。
- 260W 約 5 年，能保留較完整的基金部位週期，適合做 historical positioning。
- `260W zscore` 在 4W/8W 長 horizon 表現也強，建議當輔助欄位，而不是完全取代 percentile。

MM top scorecard definitions:

| definition      |   avg_stability_score |   avg_train_score |   avg_test_score |   recommended_horizon_count |
|:----------------|----------------------:|------------------:|-----------------:|----------------------------:|
| 260W zscore     |               73.045  |           49.67   |          73.3075 |                           1 |
| 52W zscore      |               69.07   |           69.205  |          42.42   |                           0 |
| 52W percentile  |               63.975  |           74.5425 |          43.9525 |                           1 |
| 260W percentile |               61.4825 |           53.99   |          78.82   |                           2 |
| 104W zscore     |               55.55   |           67.8625 |          69.4225 |                           0 |

## 5. Producer 最適合用哪個定義？

Producer 若只選 production-safe dashboard 主欄位，建議先用 `156W percentile`。它在 overall summary 中是最佳 rolling production-safe 定義，平均 scorecard 分數為 60.0。
`104W percentile` 平均分 81.4，並在 1W/2W horizon 被 scorecard 選為 recommended，適合當較敏感的短週期研究參考。
`52W zscore` 平均分 84.2，代表 Producer 的變化幅度對研究有資訊量，但它是 zscore 輔助欄位，不應直接取代 production-safe percentile。

Practical decision:

- Production-safe dashboard primary: `producer_net_percentile_156w`。
- Short-horizon research companion: `producer_net_percentile_104w`。
- Magnitude research companion: `producer_net_zscore_52w`。

Producer top scorecard definitions:

| definition      |   avg_stability_score |   avg_train_score |   avg_test_score |   recommended_horizon_count |
|:----------------|----------------------:|------------------:|-----------------:|----------------------------:|
| 52W zscore      |               84.2125 |           71.95   |          82.94   |                           1 |
| 104W percentile |               81.355  |           70.8775 |          97.28   |                           2 |
| 52W percentile  |               78.555  |           76.5775 |          83.5875 |                           1 |
| 156W zscore     |               76.01   |           39.135  |          92.325  |                           0 |
| 260W zscore     |               75.145  |           38.305  |          90.68   |                           0 |

## 6. OI 最適合用哪個定義？

OI 最適合用 `52W percentile` 作為主 dashboard 定義。它平均分 78.8，並在 1W/2W/4W/8W 都被 scorecard 選為 recommended。

Reason:

- OI 是市場參與度變數，短到中期資金進出比長期歷史排序更有即時資訊。
- 52W percentile 對近期資金擁擠/退潮更敏感。
- OI 不應只看 percentile；absolute level、weekly change、zscore 都應同時呈現。

OI top scorecard definitions:

| definition              |   avg_stability_score |   avg_train_score |   avg_test_score |   recommended_horizon_count |
|:------------------------|----------------------:|------------------:|-----------------:|----------------------------:|
| 52W percentile          |               78.7525 |           88.63   |          50.6675 |                           4 |
| 52W zscore              |               74.4975 |           84.2225 |          42.9125 |                           0 |
| Full History percentile |               61.8925 |           47.105  |          65.445  |                           0 |
| 104W percentile         |               51.785  |           56.455  |          48.645  |                           0 |
| 104W zscore             |               44.8375 |           56.0575 |          50.62   |                           0 |

## 7. Full History Percentile 是否比 Rolling Percentile 更適合長期定位？

結論：適合作為研究 benchmark，不適合作為正式 dashboard 主定義。

Full History 在 summary 中分數偏高，尤其可提供長期歷史相對位置：

| display_name        |   overall_score |   information_score_mean_4w_8w | production_safe   |
|:--------------------|----------------:|-------------------------------:|:------------------|
| MM Net              |          0.7367 |                           0.66 | No                |
| Producer Net        |          0.71   |                           0.64 | No                |
| Total Open Interest |          0.78   |                           0.74 | No                |

但是它有兩個重大限制：

- Full History 使用全樣本排序，若直接用於歷史回測，會包含當時尚未發生的未來觀測。
- 隨著資料增加，過去日期的 full-history percentile 會被重新改寫，不適合做穩定的線上狀態欄位。

建議：

- Dashboard 可新增 `Full History Percentile` 作為 long-term context reference。
- 正式市場狀態與 historical similarity engine 仍應使用 rolling / expanding 類定義。
- 若要做 production-safe long-term 定位，下一版應測試 `expanding percentile`，而不是 full-sample percentile。

## 8. Producer 是否應該改用 Producer Net / OI 或 Hedging Ratio？

目前不建議直接替換。建議保持 `Producer Net` 作為 v0.5 主資料源，同時在 v0.6 加入 Hedging Ratio audit。

原因：

- Producer Net 仍是 COT 商業避險端的直接部位資訊，解釋性最高。
- 但 Producer Net 會受總 OI 規模變動影響；當 OI 很低或很高時，單看 net contracts 可能失真。
- `Producer Net / OI` 或 `abs(Producer Net) / OI` 可衡量商業端避險強度，可能比單純 net 更適合跨 regime 比較。
- 目前 v0.5 尚未正式 audit Hedging Ratio，因此不應把它放進正式 dashboard 主結論。

建議 v0.6 新增候選欄位：

- `producer_net_to_oi_ratio`
- `producer_abs_net_to_oi_ratio`
- `producer_short_to_oi_ratio`
- `producer_ratio_percentile_104w / 156w / 260w`

## 9. OI 是否適合用 percentile，還是應該用 absolute level / change / zscore？

OI 適合用 percentile，但不應只用 percentile。

`52W percentile` 是本次審計中 OI 的最佳主定義；不過 OI 本身是市場參與度與合約規模變數，absolute level 與 change 也很重要。

OI signal comparison, top rows:

| definition              | definition_type   |   avg_abs_rank_corr |   avg_abs_spread |   avg_monotonicity |
|:------------------------|:------------------|--------------------:|-----------------:|-------------------:|
| 52W percentile          | percentile        |              0.0702 |           0.0087 |             0.3667 |
| 52W zscore              | zscore            |              0.0652 |           0.0098 |             0.4182 |
| Full History percentile | percentile        |              0.0227 |           0.0046 |             0.2273 |
| 104W percentile         | percentile        |              0.016  |           0.0011 |             0.1424 |
| 104W zscore             | zscore            |              0.011  |           0.0043 |             0.1121 |

Dashboard 應同時顯示：

- `total_open_interest`：絕對持倉規模。
- `oi_change`：近期資金進出變化。
- `oi_percentile_52w`：近期市場參與度定位。
- `oi_zscore_52w`：偏離近期均值的標準化幅度。
- `oi_percentile_156w`：legacy comparison，不作為唯一主判斷。

## 10. GHPR Dashboard 最終應該顯示哪些欄位？

Recommended Current Market Snapshot fields:

- `date`
- `gold_close`
- `gold_source` / source note: COMEX GC futures proxy via Yahoo Finance GC=F
- `mm_net`
- `mm_net_percentile_260w`
- `mm_net_zscore_260w`
- `mm_net_percentile_156w` as legacy reference
- `producer_net`
- `producer_net_percentile_156w`
- `producer_net_percentile_104w` as short-horizon research companion
- `producer_net_zscore_52w`
- `total_open_interest`
- `oi_change`
- `oi_percentile_52w`
- `oi_zscore_52w`
- `oi_percentile_156w` as legacy reference
- `full_history_percentile` fields only in an advanced research panel, not as the default market-state driver

Recommended dashboard labels:

- `Primary Historical Positioning` for the v0.5 factor-specific definitions.
- `Legacy 156W Reference` for current v0.4 continuity.
- `Long-Term Historical Reference` for Full History fields.

## Final Adoption Recommendation

Use factor-specific definitions in v0.5:

- MM: `260W percentile` primary, `260W zscore` support.
- Producer: `156W percentile` production-safe primary, `104W percentile` short-horizon companion, `52W zscore` support.
- OI: `52W percentile` primary, plus absolute OI and OI change.

Keep 156W rolling percentile visible as a legacy reference during transition, but stop treating 156W as the universal GHPR standard.

This is a research definition audit. It does not create trade execution logic or external execution integration.
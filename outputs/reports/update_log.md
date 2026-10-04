# GHPR Update Log

- Status: `success`
- Update mode: `full`
- Started UTC: `2026-10-04T14:51:53.170534+00:00`
- Finished UTC: `2026-10-04T14:53:41.735270+00:00`
- Latest dataset date before update: `2026-06-23`
- Latest dataset date after update: `2026-09-29`
- Latest CFTC available date: `2026-09-29`
- Data is current: `true`
- Stale reason: `N/A`
- Runtime note: `Cloud runtime file writes may be ephemeral; commit refreshed outputs to GitHub for durable deployment data.`
- Scope: `Historical statistics / research reference only.`

## Steps

### Build master weekly dataset

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/build_master_dataset.py`
- Exit code: `0`
- Elapsed seconds: `28.04`

#### stdout

```text
Built 892 rows
Output: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\data\processed\ghpr_master_weekly.csv
```

#### stderr

```text
N/A
```

### Run single-factor analysis

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/factor_analysis.py`
- Exit code: `0`
- Elapsed seconds: `20.64`

#### stdout

```text
Built 160 factor bucket rows
CSV: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\single_factor_decile_analysis.csv
Markdown: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\single_factor_decile_analysis.md
Train/Test CSV: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\single_factor_train_test_analysis.csv
Regime CSV: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\single_factor_regime_analysis.csv
```

#### stderr

```text
N/A
```

### Regenerate charts

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/plot_engine.py`
- Exit code: `0`
- Elapsed seconds: `11.03`

#### stdout

```text
Created 6 charts
D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\charts\gold_price_vs_mm_net_percentile.png
D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\charts\gold_price_vs_producer_net_percentile.png
D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\charts\gold_price_vs_total_oi_percentile.png
D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\charts\forward_return_by_mm_percentile_bucket.png
D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\charts\forward_return_by_producer_percentile_bucket.png
D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\charts\forward_return_by_oi_percentile_bucket.png
```

#### stderr

```text
Matplotlib is building the font cache; this may take a moment.
```

### Generate factor research report

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/report_engine.py`
- Exit code: `0`
- Elapsed seconds: `11.19`

#### stdout

```text
Report: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\ghpr_factor_report.md
```

#### stderr

```text
N/A
```

### Run historical similarity engine

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/historical_similarity_engine.py`
- Exit code: `0`
- Elapsed seconds: `2.47`

#### stdout

```text
Wrote D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\hse_current_similarity.csv
Wrote D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\hse_current_similarity_report.md
```

#### stderr

```text
N/A
```

### Run MM lifecycle research

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_lifecycle_research.py`
- Exit code: `0`
- Elapsed seconds: `11.77`

#### stdout

```text
Wrote MM lifecycle dataset: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\data\processed\mm_lifecycle_dataset.csv
Wrote MM lifecycle summary: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\mm_lifecycle_summary.md
Rows: 892
Scope: historical statistics / research reference only
```

#### stderr

```text
N/A
```

### Run MM structure lifecycle research

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_structure_lifecycle_research.py`
- Exit code: `0`
- Elapsed seconds: `7.33`

#### stdout

```text
Wrote MM structure lifecycle dataset: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\data\processed\mm_structure_lifecycle_dataset.csv
Wrote MM structure lifecycle summary: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\mm_structure_lifecycle_summary.md
Rows: 892
Scope: historical structure research only
```

#### stderr

```text
N/A
```

### Run MM velocity window discovery

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_velocity_window_discovery.py`
- Exit code: `0`
- Elapsed seconds: `9.31`

#### stdout

```text
Wrote velocity window dataset: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\data\processed\mm_velocity_window_dataset.csv
Wrote velocity window summary: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\mm_velocity_window_summary.md
Rows: 892
Scope: historical structure research only
```

#### stderr

```text
N/A
```

### Run MM velocity reading layer

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_velocity_reading_layer.py`
- Exit code: `0`
- Elapsed seconds: `1.21`

#### stdout

```text
Wrote velocity reading layer dataset: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\data\processed\mm_velocity_reading_layer.csv
Wrote velocity reading layer report: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\mm_velocity_reading_layer.md
Rows: 892
Latest date: 2026-09-29
Scope: historical structure research only
```

#### stderr

```text
N/A
```

### Run MM weekly change layer

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_weekly_change_layer.py`
- Exit code: `0`
- Elapsed seconds: `1.28`

#### stdout

```text
Wrote weekly change dataset: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\data\processed\mm_weekly_change_dataset.csv
Wrote weekly change summary: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\mm_weekly_change_summary.md
Latest date: 2026-09-29
Scope: Historical COT Weekly Change Research only. Not a trading signal.
```

#### stderr

```text
N/A
```

### Export hub summary

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/export_hub_summary.py`
- Exit code: `0`
- Elapsed seconds: `1.46`

#### stdout

```text
Wrote hub summary: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\ghpr_summary_for_hub.json
Summary date: 2026-09-29
Scope: historical statistics / research reference only
```

#### stderr

```text
N/A
```

### Run data freshness diagnostics

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/data_freshness_diagnostics.py --strict`
- Exit code: `0`
- Elapsed seconds: `1.24`

#### stdout

```text
Wrote diagnostics: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\data_freshness_diagnostics.json
Wrote diagnostics: D:\Codex\GHPR_ReadOnly_Diagnosis_20261004\implementation\ghpr-engine-candidate\outputs\reports\data_freshness_diagnostics.md
Overall freshness status: OK
Expected latest date: 2026-09-29
```

#### stderr

```text
N/A
```

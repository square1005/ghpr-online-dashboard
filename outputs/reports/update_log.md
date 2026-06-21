# GHPR Update Log

- Status: `success`
- Update mode: `local`
- Started UTC: `2026-06-21T10:32:23.326613+00:00`
- Finished UTC: `2026-06-21T10:34:05.427597+00:00`
- Latest dataset date before update: `2026-06-09`
- Latest dataset date after update: `2026-06-09`
- Latest CFTC available date: `2026-06-09`
- Data is current: `true`
- Stale reason: `N/A`
- Runtime note: `Cloud runtime file writes may be ephemeral; commit refreshed outputs to GitHub for durable deployment data.`
- Scope: `Historical statistics / research reference only.`

## Steps

### Build master weekly dataset

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/build_master_dataset.py --no-download`
- Exit code: `0`
- Elapsed seconds: `17.65`

#### stdout

```text
Built 876 rows
Output: PROJECT_ROOT/data\processed\ghpr_master_weekly.csv
```

#### stderr

```text
N/A
```

### Run single-factor analysis

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/factor_analysis.py`
- Exit code: `0`
- Elapsed seconds: `29.18`

#### stdout

```text
Built 160 factor bucket rows
CSV: PROJECT_ROOT/outputs\reports\single_factor_decile_analysis.csv
Markdown: PROJECT_ROOT/outputs\reports\single_factor_decile_analysis.md
Train/Test CSV: PROJECT_ROOT/outputs\reports\single_factor_train_test_analysis.csv
Regime CSV: PROJECT_ROOT/outputs\reports\single_factor_regime_analysis.csv
```

#### stderr

```text
N/A
```

### Regenerate charts

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/plot_engine.py`
- Exit code: `0`
- Elapsed seconds: `6.67`

#### stdout

```text
Created 6 charts
PROJECT_ROOT/outputs\charts\gold_price_vs_mm_net_percentile.png
PROJECT_ROOT/outputs\charts\gold_price_vs_producer_net_percentile.png
PROJECT_ROOT/outputs\charts\gold_price_vs_total_oi_percentile.png
PROJECT_ROOT/outputs\charts\forward_return_by_mm_percentile_bucket.png
PROJECT_ROOT/outputs\charts\forward_return_by_producer_percentile_bucket.png
PROJECT_ROOT/outputs\charts\forward_return_by_oi_percentile_bucket.png
```

#### stderr

```text
N/A
```

### Generate factor research report

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/report_engine.py`
- Exit code: `0`
- Elapsed seconds: `5.00`

#### stdout

```text
Report: PROJECT_ROOT/outputs\reports\ghpr_factor_report.md
```

#### stderr

```text
N/A
```

### Run historical similarity engine

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/historical_similarity_engine.py`
- Exit code: `0`
- Elapsed seconds: `4.94`

#### stdout

```text
Wrote PROJECT_ROOT/outputs\reports\hse_current_similarity.csv
Wrote PROJECT_ROOT/outputs\reports\hse_current_similarity_report.md
```

#### stderr

```text
N/A
```

### Run MM lifecycle research

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_lifecycle_research.py`
- Exit code: `0`
- Elapsed seconds: `11.90`

#### stdout

```text
Wrote MM lifecycle dataset: PROJECT_ROOT/data\processed\mm_lifecycle_dataset.csv
Wrote MM lifecycle summary: PROJECT_ROOT/outputs\reports\mm_lifecycle_summary.md
Rows: 876
Scope: historical statistics / research reference only
```

#### stderr

```text
N/A
```

### Run MM structure lifecycle research

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_structure_lifecycle_research.py`
- Exit code: `0`
- Elapsed seconds: `8.70`

#### stdout

```text
Wrote MM structure lifecycle dataset: PROJECT_ROOT/data\processed\mm_structure_lifecycle_dataset.csv
Wrote MM structure lifecycle summary: PROJECT_ROOT/outputs\reports\mm_structure_lifecycle_summary.md
Rows: 876
Scope: historical structure research only
```

#### stderr

```text
N/A
```

### Run MM velocity window discovery

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_velocity_window_discovery.py`
- Exit code: `0`
- Elapsed seconds: `11.97`

#### stdout

```text
Wrote velocity window dataset: PROJECT_ROOT/data\processed\mm_velocity_window_dataset.csv
Wrote velocity window summary: PROJECT_ROOT/outputs\reports\mm_velocity_window_summary.md
Rows: 876
Scope: historical structure research only
```

#### stderr

```text
N/A
```

### Run MM velocity reading layer

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/mm_velocity_reading_layer.py`
- Exit code: `0`
- Elapsed seconds: `2.34`

#### stdout

```text
Wrote velocity reading layer dataset: PROJECT_ROOT/data\processed\mm_velocity_reading_layer.csv
Wrote velocity reading layer report: PROJECT_ROOT/outputs\reports\mm_velocity_reading_layer.md
Rows: 876
Latest date: 2026-06-09
Scope: historical structure research only
```

#### stderr

```text
N/A
```

### Export hub summary

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/export_hub_summary.py`
- Exit code: `0`
- Elapsed seconds: `1.42`

#### stdout

```text
Wrote hub summary: PROJECT_ROOT/outputs\reports\ghpr_summary_for_hub.json
Summary date: 2026-06-09
Scope: historical statistics / research reference only
```

#### stderr

```text
N/A
```

### Run data freshness diagnostics

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/data_freshness_diagnostics.py`
- Exit code: `0`
- Elapsed seconds: `2.33`

#### stdout

```text
Wrote diagnostics: PROJECT_ROOT/outputs\reports\data_freshness_diagnostics.json
Wrote diagnostics: PROJECT_ROOT/outputs\reports\data_freshness_diagnostics.md
Overall freshness status: OK
Expected latest date: 2026-06-09
```

#### stderr

```text
N/A
```

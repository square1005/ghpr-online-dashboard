# GHPR Update Log

- Status: `success`
- Started UTC: `2026-06-05T11:25:43.384426+00:00`
- Finished UTC: `2026-06-05T11:26:41.670568+00:00`
- Runtime note: `Cloud runtime file writes may be ephemeral; commit refreshed outputs to GitHub for durable deployment data.`
- Scope: `Historical statistics / research reference only.`

## Steps

### Fetch daily gold OHLC

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/fetch_gold_daily_ohlc.py`
- Exit code: `0`
- Elapsed seconds: `4.33`

#### stdout

```text
Wrote 4,382 daily OHLC rows to PROJECT_ROOT/data\processed\gold_daily_ohlc.csv
Source: Yahoo Finance GC=F futures proxy
```

#### stderr

```text
N/A
```

### Build master weekly dataset

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/build_master_dataset.py --no-download`
- Exit code: `0`
- Elapsed seconds: `17.02`

#### stdout

```text
Built 874 rows
Output: PROJECT_ROOT/data\processed\ghpr_master_weekly.csv
```

#### stderr

```text
N/A
```

### Run single-factor analysis

- Command: `C:\Users\Administrator\AppData\Local\Programs\Python\Python314\python.exe src/factor_analysis.py`
- Exit code: `0`
- Elapsed seconds: `18.80`

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
- Elapsed seconds: `4.69`

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
- Elapsed seconds: `11.05`

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
- Elapsed seconds: `2.39`

#### stdout

```text
Wrote PROJECT_ROOT/outputs\reports\hse_current_similarity.csv
Wrote PROJECT_ROOT/outputs\reports\hse_current_similarity_report.md
```

#### stderr

```text
N/A
```

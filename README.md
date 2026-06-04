# GHPR Engine

Gold Historical Positioning Research Engine. The dashboard is a historical statistics and research reference tool for gold price, COT positioning, and open interest research.

This project does not connect to TradeDock, does not use broker APIs, does not use account data, and does not place orders.

## Dashboard v0.4

Run locally from this directory:

```powershell
streamlit run dashboard.py
```

Open:

```text
http://localhost:8501
```

Dashboard pages:

- Current Position
- Historical Database
- Similar Cases
- Event Study
- Forward Statistics
- Research Report
- Historical Similarity Engine
- Update Log

Visible dashboard notice:

```text
此系統為歷史統計研究工具，不是交易訊號，不提供買賣建議。
```

## Gold Price Source

Current `gold_close` source:

```text
COMEX GC futures proxy via Yahoo Finance GC=F
```

Important note:

```text
This is a futures proxy, not official LBMA PM benchmark or broker XAUUSD spot.
```

## One-Click Update

In the dashboard sidebar, click:

```text
一鍵更新 GHPR 資料
```

The button runs:

```powershell
python src\build_master_dataset.py --no-download
python src\factor_analysis.py
python src\plot_engine.py
python src\report_engine.py
python src\historical_similarity_engine.py
```

The update flow is wrapped in:

```text
src/update_pipeline.py
```

Update log:

```text
outputs/reports/update_log.md
```

On hosted platforms, runtime file writes may be temporary. For durable deployed data, commit refreshed `data/` and `outputs/` files back to GitHub.

## Historical Similarity Engine

Run directly:

```powershell
python src\historical_similarity_engine.py
```

Similarity score uses only:

- `mm_net_percentile_156w`
- `producer_net_percentile_156w`
- `oi_percentile_156w`

No AI, machine learning, optimized weights, Options, OGR, or MMP are used in v0.3/v0.4.

## Local Full Refresh

Use existing raw files:

```powershell
python src\build_master_dataset.py --no-download
python src\factor_analysis.py
python src\plot_engine.py
python src\report_engine.py
python src\historical_similarity_engine.py
```

Allow downloads where supported:

```powershell
python src\build_master_dataset.py
python src\factor_analysis.py
python src\plot_engine.py
python src\report_engine.py
python src\historical_similarity_engine.py
```

## Streamlit Cloud Deployment

1. Push this `GHPR_Engine` project to GitHub.
2. Create or use this GitHub repo name:

```text
ghpr-online-dashboard
```

3. Go to Streamlit Community Cloud.
4. Click `New app`.
5. Repository: select `ghpr-online-dashboard`.
6. Branch: select your deployment branch, usually `main`.
7. Main file path:

```text
dashboard.py
```

8. Click `Deploy`.
9. After deployment, copy the generated `https://xxxxx.streamlit.app` URL and replace the placeholder below.

Dependency files:

- `requirements.txt`
- `packages.txt`
- `.streamlit/config.toml`

Public URL:

```text
Pending deployment. After deploy, replace with the generated https://xxxxx.streamlit.app URL.
```

Reference: Streamlit Community Cloud deploy docs: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

## Render Deployment

Create a Render Web Service from the GitHub repo.

If the service root is this `GHPR_Engine` directory:

```text
Build command: pip install -r requirements.txt
Start command: streamlit run dashboard.py --server.address=0.0.0.0 --server.port=$PORT
```

If the service root is the outer workspace directory:

```text
Root directory: GHPR_Engine
Build command: pip install -r requirements.txt
Start command: streamlit run dashboard.py --server.address=0.0.0.0 --server.port=$PORT
```

Reference: Render deploy docs: https://render.com/docs/deploys

## Core Outputs

- `data/processed/ghpr_master_weekly.csv`
- `outputs/reports/single_factor_decile_analysis.csv`
- `outputs/reports/ghpr_factor_report.md`
- `outputs/reports/historical_similarity_report.csv`
- `outputs/reports/historical_similarity_stats.csv`
- `outputs/charts/historical_similarity_cases.png`
- `outputs/reports/update_log.md`

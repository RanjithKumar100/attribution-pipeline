# Real-time Attribution Pipeline

GA4 → BigQuery → dbt → Streamlit dashboard showing First-Click and Last-Click attribution.

## Dataset
`bigquery-public-data.ga4_obfuscated_sample_ecommerce`

## Stack
- **BigQuery** — data warehouse
- **dbt Core** — transformation layer
- **Python** — streaming demo
- **Streamlit + Plotly** — dashboard

## Quick Start

### 1. Install dependencies
```bash
pip install dbt-bigquery google-cloud-bigquery streamlit plotly pandas
```

### 2. Add GCP credentials
Place your service account key at:
```
attribution-pipeline/gcp-key.json
```
Never commit this file — it is in .gitignore.

### 3. Run dbt models
```bash
cd attribution_pipeline
dbt run
dbt test
```

### 4. Load sample streaming events
```bash
cd ..
python stream_events.py
```

### 5. Launch dashboard
```bash
streamlit run app.py
```
Open http://localhost:8501

## dbt Model Layers
- `stg_ga4__events` — flattened raw GA4 events
- `stg_ga4__sessions` — session-grain aggregation
- `int_session_touchpoints` — channel mapping + window functions
- `mart_first_click_attribution` — first touch attribution
- `mart_last_click_attribution` — last touch attribution

## Assumptions
- Lookback window: 30 days
- Identity resolution: user_pseudo_id (no cross-device)
- Tie-breaker: earliest event_timestamp
- Conversion event: purchase
- Session timeout: 30 minutes

## Failure Handling
- BQ auth errors → regenerate service account key
- dbt model failure → run `dbt run --select <model>` to isolate
- Dashboard timeout → restart with `streamlit run app.py`

## Monitoring
- BQ: INFORMATION_SCHEMA.JOBS_BY_PROJECT for slot usage
- dbt: check target/run_results.json after each run

## Cost Notes
- GA4 public dataset: ~200MB scanned per full run ≈ $0.001
- Batch load jobs: free tier compatible
- Estimated total cost for this project: < $1
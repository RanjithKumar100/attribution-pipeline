# Worklog

## Entry 1 — Day 0
Set up project structure, installed dbt-bigquery, google-cloud-bigquery, streamlit.
Created GCP project `attribution-demo`, enabled BigQuery API, created service account.
Initialized Git repo and connected to GitHub.
Dataset chosen: bigquery-public-data.ga4_obfuscated_sample_ecommerce

## Entry 2 — Day 1
Created staging models: stg_ga4__events and stg_ga4__sessions.
Flattened GA4 event_params using UNNEST to extract session_id, page_location, traffic source.
Derived session grain by grouping on user_pseudo_id + session_id.

## Entry 3 — Day 1
Added schema.yml with dbt tests: not_null on user_pseudo_id, event_name, session_id.
Ran dbt test --select staging — all tests passed.
Assumption noted: using user_pseudo_id for identity resolution (no cross-device stitching).

## Entry 4 — Day 2
Built intermediate model: int_session_touchpoints.
Derived channel grouping from source/medium using CASE WHEN logic.
Used ROW_NUMBER() window function to rank touchpoints per user ascending and descending.
Assumption: 30-day lookback, user_pseudo_id as identity key, earliest timestamp wins tie-break.

## Entry 5 — Day 2
Built mart_first_click_attribution and mart_last_click_attribution.
First click = touch_number_asc = 1, Last click = touch_number_desc = 1.
Fixed GROUP BY error — BigQuery does not allow column position references with aggregations.
All 7 dbt models passing. PASS=7 WARN=0 ERROR=0.

## Entry 6 — Day 2
Built stream_events.py to generate and load 10 sample events into BigQuery.
BigQuery free tier does not support streaming inserts (insertAll API).
Used load_table_from_json() batch load job instead — latency ~2-5s, free tier compatible.
Deduplication handled via UUID event_id as unique row identifier.
Successfully loaded 10 events into dbt_attribution.streamed_events.

## Entry 7 — Day 3
Built Streamlit dashboard with 4 panels:
- Attribution totals: First-Click $29,602 vs Last-Click $29,279
- 14-day time series (showing full 2021 dataset)
- Channel breakdown bar chart
- Live streamed events table
Dashboard running at http://localhost:8501

## Entry 8 — Day 3
All deliverables complete:
- dbt: 7 models passing, stg + int + mart layers
- Attribution: First-click and Last-click models working
- Streaming: 10 events loaded via batch load job
- Dashboard: Streamlit with real BigQuery data
- README and runbook complete
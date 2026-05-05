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
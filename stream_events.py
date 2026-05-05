import uuid
import time
import random
import datetime
from google.cloud import bigquery
from google.oauth2 import service_account

# --- config ---
KEY_FILE   = r"C:\Users\TRG\Desktop\attribution-pipeline\gcp-key.json"
PROJECT_ID = "attribution-demo-495405"
DATASET    = "dbt_attribution"
TABLE      = "streamed_events"

CHANNELS = ["Organic Search", "Paid Search", "Direct", "Email", "Referral", "Social"]
EVENTS   = ["page_view", "add_to_cart", "purchase"]
SOURCES  = ["google", "facebook", "newsletter", "(direct)", "bing"]
MEDIUMS  = ["organic", "cpc", "email", "referral", "(none)"]

# --- setup client ---
credentials = service_account.Credentials.from_service_account_file(KEY_FILE)
client = bigquery.Client(project=PROJECT_ID, credentials=credentials)

table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE}"

# --- schema ---
schema = [
    bigquery.SchemaField("event_id",        "STRING"),
    bigquery.SchemaField("event_timestamp", "TIMESTAMP"),
    bigquery.SchemaField("user_pseudo_id",  "STRING"),
    bigquery.SchemaField("session_id",      "STRING"),
    bigquery.SchemaField("event_name",      "STRING"),
    bigquery.SchemaField("channel",         "STRING"),
    bigquery.SchemaField("source",          "STRING"),
    bigquery.SchemaField("medium",          "STRING"),
    bigquery.SchemaField("revenue",         "FLOAT"),
]

# --- create table if not exists ---
try:
    client.get_table(table_ref)
    print(f"Table {TABLE} already exists.")
except Exception:
    table = bigquery.Table(table_ref, schema=schema)
    client.create_table(table)
    print(f"Created table {TABLE}.")

# --- generate events ---
print("\nPreparing 10 sample events...\n")

rows = []
for i in range(10):
    row = {
        "event_id":        str(uuid.uuid4()),
        "event_timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        "user_pseudo_id":  f"user_{random.randint(1, 50)}",
        "session_id":      f"sess_{random.randint(100, 999)}",
        "event_name":      random.choice(EVENTS),
        "channel":         random.choice(CHANNELS),
        "source":          random.choice(SOURCES),
        "medium":          random.choice(MEDIUMS),
        "revenue":         round(random.uniform(10, 200), 2) if random.random() > 0.7 else 0.0,
    }
    rows.append(row)
    print(f"Event {i+1}: {row['event_name']} | {row['channel']} | user={row['user_pseudo_id']}")
    time.sleep(0.3)

# --- load via batch job (free tier compatible) ---
print("\nLoading into BigQuery via batch load job...")

job_config = bigquery.LoadJobConfig(
    schema=schema,
    write_disposition="WRITE_APPEND",
    source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
)

job = client.load_table_from_json(rows, table_ref, job_config=job_config)
job.result()  # wait for job to complete

table_obj = client.get_table(table_ref)
print(f"\nSuccess! {len(rows)} events loaded.")
print(f"Total rows in table: {table_obj.num_rows}")
print(f"\nCheck BigQuery: {DATASET}.{TABLE}")
print("\nNote: Using batch load job (free tier). Latency ~2-5s.")
print("Deduplication: event_id is unique per row (UUID).")
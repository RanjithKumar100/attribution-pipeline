import streamlit as st
import plotly.express as px
from google.cloud import bigquery
from google.oauth2 import service_account
import datetime

KEY_FILE   = r"C:\Users\TRG\Desktop\attribution-pipeline\gcp-key.json"
PROJECT_ID = "attribution-demo-495405"
DATASET    = "dbt_attribution"

st.set_page_config(page_title="Attribution Dashboard", page_icon="📊", layout="wide")

creds = service_account.Credentials.from_service_account_file(KEY_FILE)
client = bigquery.Client(project=PROJECT_ID, credentials=creds)

def run_query(sql):
    return client.query(sql).to_dataframe()

st.title("📊 Real-time Attribution Dashboard")
st.caption("First-Click vs Last-Click Attribution | GA4 Ecommerce Dataset")
st.divider()

# --- Panel 1: Totals ---
st.subheader("Attribution Totals")
col1, col2, col3, col4 = st.columns(4)

first = run_query(f"SELECT round(sum(attributed_revenue),2) as revenue, sum(attributed_users) as users FROM `{PROJECT_ID}.{DATASET}.mart_first_click_attribution`")
last  = run_query(f"SELECT round(sum(attributed_revenue),2) as revenue, sum(attributed_users) as users FROM `{PROJECT_ID}.{DATASET}.mart_last_click_attribution`")

col1.metric("First-Click Revenue", f"${first['revenue'].iloc[0]:,.2f}")
col2.metric("First-Click Users",   f"{int(first['users'].iloc[0]):,}")
col3.metric("Last-Click Revenue",  f"${last['revenue'].iloc[0]:,.2f}")
col4.metric("Last-Click Users",    f"{int(last['users'].iloc[0]):,}")

st.divider()

# --- Panel 2: Time series ---
st.subheader("14-Day Revenue Trend")

ts = run_query(f"""
    SELECT attribution_date, 'First Click' as model, sum(attributed_revenue) as revenue
    FROM `{PROJECT_ID}.{DATASET}.mart_first_click_attribution`
    WHERE attribution_date >= date_sub(current_date(), interval 14 day)
    GROUP BY attribution_date
    UNION ALL
    SELECT attribution_date, 'Last Click' as model, sum(attributed_revenue) as revenue
    FROM `{PROJECT_ID}.{DATASET}.mart_last_click_attribution`
    WHERE attribution_date >= date_sub(current_date(), interval 14 day)
    GROUP BY attribution_date
    ORDER BY attribution_date
""")

if not ts.empty:
    fig = px.line(ts, x="attribution_date", y="revenue", color="model", markers=True,
                  color_discrete_map={"First Click": "#636EFA", "Last Click": "#EF553B"})
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Showing all available data (dataset is from 2021).")
    ts2 = run_query(f"""
        SELECT attribution_date, 'First Click' as model, sum(attributed_revenue) as revenue
        FROM `{PROJECT_ID}.{DATASET}.mart_first_click_attribution`
        GROUP BY attribution_date
        UNION ALL
        SELECT attribution_date, 'Last Click' as model, sum(attributed_revenue) as revenue
        FROM `{PROJECT_ID}.{DATASET}.mart_last_click_attribution`
        GROUP BY attribution_date
        ORDER BY attribution_date
    """)
    fig = px.line(ts2, x="attribution_date", y="revenue", color="model", markers=True,
                  color_discrete_map={"First Click": "#636EFA", "Last Click": "#EF553B"})
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Panel 3: Channel breakdown ---
st.subheader("Channel Breakdown — First Click vs Last Click")

ch = run_query(f"""
    SELECT channel, 'First Click' as model, sum(attributed_revenue) as revenue
    FROM `{PROJECT_ID}.{DATASET}.mart_first_click_attribution`
    GROUP BY channel
    UNION ALL
    SELECT channel, 'Last Click' as model, sum(attributed_revenue) as revenue
    FROM `{PROJECT_ID}.{DATASET}.mart_last_click_attribution`
    GROUP BY channel
    ORDER BY channel
""")

fig2 = px.bar(ch, x="channel", y="revenue", color="model", barmode="group",
              color_discrete_map={"First Click": "#636EFA", "Last Click": "#EF553B"})
st.plotly_chart(fig2, use_container_width=True)

st.divider()

# --- Panel 4: Live events ---
st.subheader("Live Streamed Events")
st.caption("Last 20 events loaded into BigQuery")

live = run_query(f"""
    SELECT event_timestamp, event_name, channel, source, medium,
           user_pseudo_id, session_id,
           case when revenue > 0 then round(revenue,2) else null end as revenue
    FROM `{PROJECT_ID}.{DATASET}.streamed_events`
    ORDER BY event_timestamp DESC
    LIMIT 20
""")

st.dataframe(live, use_container_width=True)

st.divider()
st.caption(f"Last refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Source: GA4 Obfuscated Sample Ecommerce")
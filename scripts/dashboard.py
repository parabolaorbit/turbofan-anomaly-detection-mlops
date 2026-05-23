import sqlite3
import pandas as pd
import streamlit as st


DB_PATH = "logs/predictions.db"


@st.cache_data
def load_data():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT *
            FROM prediction_logs
            ORDER BY id DESC
            """,
            conn,
        )

    return df


df = load_data()

st.title("Anomaly Detection Monitoring Dashboard")


# =====================================
# metrics
# =====================================

total_predictions = len(df)

alert_count = int(df["alert"].sum()) if len(df) else 0

avg_latency = (
    round(df["latency_ms"].mean(), 2)
    if len(df)
    else 0
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Predictions",
    total_predictions,
)

col2.metric(
    "Alert Count",
    alert_count,
)

col3.metric(
    "Avg Latency (ms)",
    avg_latency,
)


# =====================================
# severity distribution
# =====================================

st.subheader("Severity Distribution")

severity_counts = (
    df["severity"]
    .value_counts()
)

st.bar_chart(severity_counts)


# =====================================
# anomaly score trend
# =====================================

st.subheader("Anomaly Score Trend")

if "anomaly_score" in df.columns:
    trend_df = df.sort_values("id")

    st.line_chart(
        trend_df["anomaly_score"]
    )


# =====================================
# recent predictions
# =====================================

st.subheader("Recent Predictions")

display_columns = [
    "timestamp",
    "unit_number",
    "anomaly_score",
    "threshold",
    "severity",
    "alert",
    "latency_ms",
]

existing_columns = [
    col
    for col in display_columns
    if col in df.columns
]

st.dataframe(
    df[existing_columns],
    use_container_width=True,
)
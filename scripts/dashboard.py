import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from core.config import settings
from db.database import SessionLocal
from repositories.prediction_log_repository import PredictionLogRepository

@st.cache_data(ttl=60)
def load_data():
    engine = create_engine(settings.database_url)
    df = pd.read_sql_query(
        """
        SELECT *
        FROM prediction_logs
        ORDER BY id DESC
        """,
        engine,
    )
    return df

if st.button("Refresh"):
    load_data.clear()
    st.rerun()

df = load_data()

st.title("Anomaly Detection Monitoring Dashboard")


# =====================================
# Prediction History
# =====================================
db = SessionLocal()
repository = PredictionLogRepository(db)
logs = repository.get_recent_logs(limit=20)

df1 = pd.DataFrame(
    [
        {
            "created_at": log.created_at,
            "predition": log.prediction,
            "threshold": log.threshold,
            "result": log.result,
        }
        for log in logs
    ]
)
st.dataframe(df1)

# =====================================
# metrics
# =====================================

total_predictions = len(df)

alert_count = int(df["alert"].fillna(False).sum()) if len(df) else 0

avg_latency = (
    round(df["latency_ms"].mean(), 2)
    if len(df)
    else 0
)

col1, col2, col3, col4 = st.columns(4)

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
# Monitoring Metrics
# =====================================
anomaly_rate = 0
col4.metric(
    "Anomaly Rate",
    f"{anomaly_rate:.1%}"
)

# =====================================
# Model Version
# =====================================
st.metric(
    "Model Version",
    "v1"
)

# =====================================
# Retraining Status
# =====================================
st.metric(
    "Last Retrain",
    "2026-06-17 02:00"
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

if "prediction" in df.columns:
    trend_df = df.sort_values("id")
    st.line_chart(trend_df["prediction"])


# =====================================
# recent predictions
# =====================================

st.subheader("Recent Predictions")

display_columns = [
    "created_at",
    "unit_number",
    "prediction",
    "threshold",
    "severity",
    "result",
    "alert",
    "final_alert",
    "latency_ms",
]

existing_columns = [
    col
    for col in display_columns
    if col in df.columns
]

st.dataframe(
    df[existing_columns],
    width="streach",
)




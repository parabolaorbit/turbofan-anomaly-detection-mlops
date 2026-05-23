import streamlit as st
import requests
import pandas as pd

st.title("Turbofan Anomaly Dashboard")

uploaded = st.file_uploader("Upload sensor sequence CSV")

if uploaded:
    df = pd.read_csv(uploaded)
    st.dataframe(df.tail())

    payload = {
        "sequence": df.to_dict(orient="records"),
        "seq_len": 10,
        "rolling_window": 10,
        "threshold": 0.8,
        "consecutive_window": 5
    }

    if st.button("Predict"):
        res = requests.post(
            "http://localhost:8080/predict",
            json=payload
        )

        result = res.json()
        st.json(result)

        st.metric("Severity", result["severity"])
        st.metric("Rolling Error", result["rolling_error"])
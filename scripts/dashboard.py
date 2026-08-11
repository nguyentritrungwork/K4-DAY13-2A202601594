import streamlit as st
import pandas as pd
import json
import time

st.set_page_config(page_title="Day 13 AI Observability Dashboard", layout="wide")

st.title("Day 13 AI Observability Dashboard")

# Auto-refresh mechanism
refresh_rate = 30 # seconds

@st.cache_data(ttl=refresh_rate)
def load_data():
    try:
        with open("data/logs.jsonl", "r") as f:
            data = [json.loads(line) for line in f]
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty and "ts" in df.columns and "timestamp" not in df.columns:
    df.rename(columns={"ts": "timestamp"}, inplace=True)

if df.empty:
    st.warning("No data found in data/logs.jsonl")
    st.stop()

if "timestamp" in df.columns:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    # filter for last 60 minutes
    one_hour_ago = pd.Timestamp.now(tz="UTC") - pd.Timedelta(minutes=60)
    # df = df[df["timestamp"] >= one_hour_ago]

# Split into two columns for layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Latency Percentiles (ms)")
    # event == "response_sent"
    response_df = df[df["event"] == "response_sent"]
    if not response_df.empty and "latency_ms" in response_df.columns:
        p50 = response_df["latency_ms"].quantile(0.50)
        p95 = response_df["latency_ms"].quantile(0.95)
        p99 = response_df["latency_ms"].quantile(0.99)
        
        st.metric(label="P95 Latency", value=f"{p95:.2f} ms")
        st.write(f"**P50:** {p50:.2f} ms | **P99:** {p99:.2f} ms | **SLO:** <= 3000 ms")
        
        # Line chart
        chart_data = response_df[["timestamp", "latency_ms"]].dropna().set_index("timestamp")
        st.line_chart(chart_data)
        if p95 > 3000:
            st.error("⚠️ P95 Latency SLO Violated (P95 > 3000ms)!")
        else:
            st.success("✅ Latency SLO OK")
    else:
        st.write("No latency data.")

    st.subheader("3. Error Rate & Breakdown (%)")
    req_received = len(df[df["event"] == "request_received"])
    req_failed = len(df[df["event"] == "request_failed"])
    if req_received > 0:
        error_rate = (req_failed / req_received) * 100
        st.metric(label="Error Rate", value=f"{error_rate:.2f} %")
        st.write("**SLO:** <= 2 %")
        if error_rate > 2:
            st.error("⚠️ Error Rate SLO Violated (> 2%)!")
        else:
            st.success("✅ Error Rate SLO OK")
        
        failed_df = df[df["event"] == "request_failed"]
        if not failed_df.empty and "error_type" in failed_df.columns:
            st.write("Error Breakdown:")
            st.dataframe(failed_df["error_type"].value_counts())
    else:
        st.write("No requests yet.")

    st.subheader("5. Input & Output Tokens")
    if not response_df.empty:
        tokens_in = response_df["tokens_in"].sum() if "tokens_in" in response_df.columns else 0
        tokens_out = response_df["tokens_out"].sum() if "tokens_out" in response_df.columns else 0
        total_tokens = tokens_in + tokens_out
        st.metric("Total Tokens", value=f"{total_tokens:,.0f}")
        st.write(f"Tokens In: {tokens_in:,.0f} | Tokens Out: {tokens_out:,.0f} | **SLO:** <= 50,000")
        if total_tokens > 50000:
            st.error("⚠️ Token Limit SLO Violated (> 50,000)!")
        else:
            st.success("✅ Tokens SLO OK")

with col2:
    st.subheader("2. Request Traffic (req/min)")
    received_df = df[df["event"] == "request_received"].copy()
    if not received_df.empty:
        received_df.set_index("timestamp", inplace=True)
        # resample by minute
        traffic_per_min = received_df.resample('1min').size()
        avg_traffic = traffic_per_min.mean() if not traffic_per_min.empty else 0
        st.metric("Avg Traffic (req/min)", value=f"{avg_traffic:.2f}")
        st.write("**SLO:** >= 1 req/min")
        st.line_chart(traffic_per_min)
        if avg_traffic < 1:
            st.error("⚠️ Traffic SLO Violated (< 1)!")
        else:
            st.success("✅ Traffic SLO OK")
    else:
        st.write("No traffic data.")

    st.subheader("4. Cost Over Time (USD)")
    if not response_df.empty and "cost_usd" in response_df.columns:
        total_cost = response_df["cost_usd"].sum()
        st.metric("Total Cost", value=f"${total_cost:.4f}")
        st.write("**SLO:** <= $2.5")
        cost_df = response_df.copy()
        cost_df.set_index("timestamp", inplace=True)
        cost_per_min = cost_df["cost_usd"].resample('1min').sum()
        st.line_chart(cost_per_min)
        if total_cost > 2.5:
            st.error("⚠️ Cost SLO Violated (> $2.5)!")
        else:
            st.success("✅ Cost SLO OK")
    else:
        st.write("No cost data.")

    st.subheader("6. Quality Proxy")
    if not response_df.empty and "quality_score" in response_df.columns:
        avg_quality = response_df["quality_score"].mean()
        st.metric("Avg Quality Score", value=f"{avg_quality:.2f}")
        st.write("**SLO:** >= 0.75")
        if avg_quality < 0.75:
            st.error("⚠️ Quality SLO Violated (< 0.75)!")
        else:
            st.success("✅ Quality SLO OK")
    else:
        st.write("No quality data.")

time.sleep(refresh_rate)
st.rerun()

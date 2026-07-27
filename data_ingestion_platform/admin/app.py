import pandas as pd
import streamlit as st
from core.database import SessionLocal
from core.models import IngestedData, IngestionLog
from workers.tasks import fetch_periodic_data

st.set_page_config(page_title="Ingestion Platform Dashboard", layout="wide")
st.title("📊 Data Ingestion Platform Admin Control Plane")

db = SessionLocal()

st.sidebar.header("System Control Plane")
if st.sidebar.button("Force Ingestion Synchronizer Run"):
    fetch_periodic_data.delay()
    st.sidebar.success("Dispatched ad-hoc execution queue signal.")

if st.sidebar.button("Refresh Live Telemetry"):
    st.rerun()

left_pane, right_pane = st.columns(2)

with left_pane:
    st.subheader("📥 Incoming Payloads Stream")
    data_rows = db.query(IngestedData).order_by(IngestedData.received_at.desc()).limit(15).all()
    if data_rows:
        df_data = pd.DataFrame([
            {"ID": r.id, "Source Type": r.source, "Payload Text Fragment": r.payload[:80], "Ingested At": r.received_at} 
            for r in data_rows
        ])
        st.dataframe(df_data, use_container_width=True)
    else:
        st.info("No metrics discovered in database streams.")

with right_pane:
    st.subheader("📜 Periodic Reconciliation Engine Logs")
    log_rows = db.query(IngestionLog).order_by(IngestionLog.timestamp.desc()).limit(15).all()
    if log_rows:
        df_logs = pd.DataFrame([
            {"ID": r.id, "Engine Component": r.task_name, "Execution Status": r.status, "Message Summary": r.message, "Timestamp": r.timestamp} 
            for r in log_rows
        ])
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.info("No worker orchestration entries logged yet.")

db.close()

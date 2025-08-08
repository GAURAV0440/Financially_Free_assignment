# app/components/data_source.py
import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
from src.data.storage import load_processed
from src.data.ingest_upload import parse_uploaded_csv

def select_data_source(default_parquet="registrations.parquet"):
    ss = st.session_state
    ss.setdefault("source_choice", "mock")   # "mock" | "uploaded"
    ss.setdefault("uploaded_df", None)
    ss.setdefault("uploaded_name", "")

    st.sidebar.markdown("### Data source")

    # Radio default follows session
    idx = 0 if ss["source_choice"] == "mock" else 1
    choice = st.sidebar.radio("Choose", ["Mock (processed)", "Upload CSV"], index=idx)
    ss["source_choice"] = "uploaded" if choice == "Upload CSV" else "mock"

    if ss["source_choice"] == "uploaded":
        up = st.sidebar.file_uploader(
            "Upload CSV with columns: date, category, manufacturer, registrations "
            "(optional: year, quarter OR year, month)",
            type=["csv"], key="upload_csv_widget"
        )
        if up is not None:
            try:
                df = parse_uploaded_csv(up)
                ss["uploaded_df"] = df
                ss["uploaded_name"] = up.name
            except Exception as e:
                st.sidebar.error(f"Upload parse failed: {e}")

        # Show persistent status + return cached upload if present
        if ss["uploaded_df"] is not None:
            st.sidebar.success(f"Using uploaded CSV: {ss['uploaded_name']}")
            return ss["uploaded_df"], "uploaded"

        st.sidebar.info("No upload yet; using mock processed data temporarily.")
        return load_processed(default_parquet), "mock"

    # Using mock
    st.sidebar.info("Using processed mock dataset.")
    return load_processed(default_parquet), "mock"
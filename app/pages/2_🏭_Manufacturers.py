# --- make 'src' importable when Streamlit runs this page ---
import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[2]  # project root
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import pandas as pd
from app.components.data_source import select_data_source
from src.viz.charts import line_trend, bar_growth

# Load data (Mock parquet or Uploaded CSV)
df, source = select_data_source("registrations.parquet")

st.title("Manufacturers")
st.caption("Drill-down by manufacturer with QoQ/YoY growth.")

# --- Filters ---
min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.slider(
    "Date range",
    min_value=min_date.to_pydatetime(),
    max_value=max_date.to_pydatetime(),
    value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
    format="YYYY-MM-DD",
)

cats = sorted(df["category"].unique().tolist())
sel_cats = st.multiselect("Vehicle categories", cats, default=cats)

mf_all = sorted(df[df["category"].isin(sel_cats)]["manufacturer"].unique().tolist())
mf_all = [m for m in mf_all if m != "TOTAL"]
default_mf = mf_all[:3] if len(mf_all) >= 3 else mf_all
sel_mfrs = st.multiselect("Manufacturers", mf_all, default=default_mf)

# Apply filters
f = df[
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1])) &
    (df["category"].isin(sel_cats)) &
    (df["manufacturer"].isin(sel_mfrs))
].copy()

if f.empty:
    st.info("No data for selected filters.")
    st.stop()

# Compute QoQ/YoY (per manufacturer within category)
f_sorted = f.sort_values("date").copy()
f_sorted["prev_q"] = f_sorted.groupby(["category", "manufacturer"])["registrations"].shift(1)
f_sorted["qoq_pct"] = (f_sorted["registrations"] - f_sorted["prev_q"]) / f_sorted["prev_q"] * 100
f_sorted["prev_y"] = f_sorted.groupby(["category", "manufacturer"])["registrations"].shift(4)
f_sorted["yoy_pct"] = (f_sorted["registrations"] - f_sorted["prev_y"]) / f_sorted["prev_y"] * 100

latest_date = f_sorted["date"].max()
latest = f_sorted[f_sorted["date"] == latest_date]

st.subheader("Registrations over time (selected manufacturers)")
fig1 = line_trend(f, x="date", y="registrations", color="manufacturer", title="Registrations over time")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("YoY % (latest quarter)")
yoy_latest = (
    latest.groupby("manufacturer", as_index=False)["yoy_pct"]
    .mean()
    .sort_values("yoy_pct", ascending=False)
)
fig2 = bar_growth(yoy_latest, x="manufacturer", y="yoy_pct", color=None, title="YoY % (latest)")
st.plotly_chart(fig2, use_container_width=True)

# --- Manufacturer snapshot (latest quarter) ---
st.subheader("Latest-quarter snapshot (selected manufacturers)")
snap_m = (
    latest[["manufacturer", "registrations", "qoq_pct", "yoy_pct"]]
    .rename(columns={
        "manufacturer": "Manufacturer",
        "registrations": "Registrations (latest qtr)",
        "qoq_pct": "QoQ %",
        "yoy_pct": "YoY %"
    })
    .sort_values("Registrations (latest qtr)", ascending=False)
)
snap_m["QoQ %"] = snap_m["QoQ %"].round(2)
snap_m["YoY %"] = snap_m["YoY %"].round(2)
st.dataframe(snap_m, use_container_width=True)

# Download current filtered data (selected manufacturers)
csv_bytes = f_sorted.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered manufacturer data (CSV)", csv_bytes, "manufacturers_filtered.csv", "text/csv")

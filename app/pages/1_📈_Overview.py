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

st.title("Overview")
st.caption("Totals by category (shows the TOTAL rollup; use Manufacturers page for brand drill-down).")

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

# Apply filters — use only TOTAL manufacturer here
f = df[
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1])) &
    (df["category"].isin(sel_cats)) &
    (df["manufacturer"] == "TOTAL")
].copy()

if f.empty:
    st.info("No data in selected range.")
    st.stop()

# --- KPIs for latest quarter (sum across selected categories) ---
latest_date = f["date"].max()
ts_total = f.groupby("date", as_index=True)["registrations"].sum().sort_index()

curr_val = int(ts_total.loc[latest_date])
prev_q_val = ts_total.shift(1).get(latest_date, None)
prev_y_val = ts_total.shift(4).get(latest_date, None)

def fmt_pct(new, old):
    if old is None or pd.isna(old) or old == 0:
        return "—"
    return f"{(new - old) / old * 100:.2f}%"

k1, k2, k3 = st.columns(3)
k1.metric("Total registrations (latest quarter)", f"{curr_val:,}", help=str(f[f['date']==latest_date]['quarter'].iloc[0]))
k2.metric("QoQ %", fmt_pct(curr_val, prev_q_val))
k3.metric("YoY %", fmt_pct(curr_val, prev_y_val))

st.divider()

# --- Trend: TOTAL by category
st.subheader("Trend — TOTAL by category")
fig1 = line_trend(f, x="date", y="registrations", color="category", title="TOTAL registrations over time")
st.plotly_chart(fig1, use_container_width=True)

# --- YoY growth by category (latest quarter)
st.subheader("YoY growth by category (latest quarter)")
f_sorted = f.sort_values("date")
f_sorted["prev_y"] = f_sorted.groupby("category")["registrations"].shift(4)
f_sorted["yoy_pct"] = (f_sorted["registrations"] - f_sorted["prev_y"]) / f_sorted["prev_y"] * 100
yoy_latest = (
    f_sorted[f_sorted["date"] == latest_date]
    .groupby("category", as_index=False)["yoy_pct"]
    .mean()
)
fig2 = bar_growth(yoy_latest, x="category", y="yoy_pct", color=None, title="YoY % by category (TOTAL)")
st.plotly_chart(fig2, use_container_width=True)

# --- Category snapshot (latest quarter) ---
st.subheader("Latest-quarter snapshot (by category)")
fs = f.sort_values("date").copy()
fs["prev_q"] = fs.groupby("category")["registrations"].shift(1)
fs["qoq_pct"] = (fs["registrations"] - fs["prev_q"]) / fs["prev_q"] * 100
fs["prev_y"] = fs.groupby("category")["registrations"].shift(4)
fs["yoy_pct"] = (fs["registrations"] - fs["prev_y"]) / fs["prev_y"] * 100

snap = (
    fs[fs["date"] == latest_date][["category", "registrations", "qoq_pct", "yoy_pct"]]
    .rename(columns={
        "category": "Category",
        "registrations": "Registrations (latest qtr)",
        "qoq_pct": "QoQ %",
        "yoy_pct": "YoY %"
    })
    .sort_values("Registrations (latest qtr)", ascending=False)
)

snap["QoQ %"] = snap["QoQ %"].round(2)
snap["YoY %"] = snap["YoY %"].round(2)
st.dataframe(snap, use_container_width=True)

# Download current TOTAL-filtered data
csv_bytes = f.to_csv(index=False).encode("utf-8")
st.download_button("Download filtered TOTAL data (CSV)", csv_bytes, "total_filtered.csv", "text/csv")

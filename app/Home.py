# --- make 'src' importable ---
import sys
from pathlib import Path
root_path = Path(__file__).resolve().parents[1]  # project root
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import streamlit as st
import pandas as pd

from app.components.data_source import select_data_source
from src.viz.charts import line_trend, bar_growth

st.set_page_config(page_title="Vahan Growth Dashboard", layout="wide")

# ---- HERO ----
st.markdown(
    """
    # 🚗 Vahan Growth Dashboard — *Investor View*
    **Track YoY & QoQ growth of vehicle registrations** by category and manufacturer.
    """
)

# ---- DATA SOURCE (same toggle as pages) ----
df, source = select_data_source("registrations.parquet")

# Ensure TOTAL rows exist (for category-wide KPIs)
if "TOTAL" not in df["manufacturer"].unique():
    tot = df.groupby(["date","year","quarter","category"], as_index=False)["registrations"].sum()
    tot["manufacturer"] = "TOTAL"
    df = pd.concat([df, tot], ignore_index=True)

# ---- KPI STRIP (latest quarter across all categories) ----
f = df[df["manufacturer"] == "TOTAL"].copy()
latest_date = f["date"].max()
ts_total = f.groupby("date", as_index=True)["registrations"].sum().sort_index()

def pct(new, old):
    if old is None or pd.isna(old) or old == 0: return None
    return (new - old) / old * 100

curr = int(ts_total.loc[latest_date])
qoq = pct(curr, ts_total.shift(1).get(latest_date))
yoy = pct(curr, ts_total.shift(4).get(latest_date))

c1, c2, c3, c4 = st.columns([1,1,1,1])
c1.metric("Total registrations (latest qtr)", f"{curr:,}", help=str(df.loc[df['date']==latest_date, 'quarter'].iloc[0]))
c2.metric("QoQ %", f"{qoq:.2f}%" if qoq is not None else "—")
c3.metric("YoY %", f"{yoy:.2f}%" if yoy is not None else "—")
c4.write(" ")  # spacer
c4.caption("Data source: " + ("Uploaded CSV" if source == "uploaded" else "Mock (processed)"))

st.divider()

# ---- QUICK VIEW: TOTAL trend by category ----
st.subheader("TOTAL registrations — quick trend by category")
f_cat = df[(df["manufacturer"]=="TOTAL") & (df["date"]<=latest_date)]
st.plotly_chart(
    line_trend(f_cat, x="date", y="registrations", color="category", title=""),
    use_container_width=True
)

# ---- INSIGHTS: top-growing category & manufacturer (latest quarter) ----
st.subheader("Quick insights (latest quarter)")

# Category YoY
f_cat_sorted = f_cat.sort_values("date").copy()
f_cat_sorted["prev_y"] = f_cat_sorted.groupby("category")["registrations"].shift(4)
f_cat_sorted["yoy_pct"] = (f_cat_sorted["registrations"] - f_cat_sorted["prev_y"]) / f_cat_sorted["prev_y"] * 100
cat_latest = (f_cat_sorted[f_cat_sorted["date"]==latest_date]
              .sort_values("yoy_pct", ascending=False)[["category","yoy_pct"]])

# Manufacturer YoY (within each category)
f_mfr = df[df["manufacturer"]!="TOTAL"].sort_values("date").copy()
f_mfr["prev_y"] = f_mfr.groupby(["category","manufacturer"])["registrations"].shift(4)
f_mfr["yoy_pct"] = (f_mfr["registrations"] - f_mfr["prev_y"]) / f_mfr["prev_y"] * 100
mfr_latest = (f_mfr[f_mfr["date"]==latest_date]
              .sort_values("yoy_pct", ascending=False)[["category","manufacturer","yoy_pct"]]
              .groupby("category", as_index=False).head(1))

colA, colB = st.columns(2)
with colA:
    st.markdown("**Fastest-growing category (YoY)**")
    if not cat_latest.empty and pd.notna(cat_latest.iloc[0]["yoy_pct"]):
        st.success(f"• {cat_latest.iloc[0]['category']} — {cat_latest.iloc[0]['yoy_pct']:.2f}% YoY")
    else:
        st.info("Insufficient last-year data for YoY.")

with colB:
    st.markdown("**Top manufacturer by YoY (per category)**")
    if not mfr_latest.empty and pd.notna(mfr_latest.iloc[0]["yoy_pct"]):
        bullets = "\n".join(
            f"- {r.category}: **{r.manufacturer}** ({r.yoy_pct:.2f}%)" for r in mfr_latest.itertuples()
        )
        st.markdown(bullets)
    else:
        st.info("Insufficient last-year data for YoY.")

st.divider()

# ---- HOW TO USE ----
st.markdown(
    """
    ### How to use
    - Go to **Overview** for category totals and growth.
    - Go to **Manufacturers** to compare brands and see QoQ/YoY.
    - Use the **Data source** switcher (left sidebar) to upload your own CSV or use the mock dataset.
    """
)

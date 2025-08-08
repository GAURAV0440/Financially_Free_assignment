# Vahan Growth Dashboard — Investor View

A simple Streamlit app that shows **YoY (year-over-year)** and **QoQ (quarter-over-quarter)** growth in Indian vehicle registrations — by **category** (2W/3W/4W) and **manufacturer**. Built to give investors a quick, clean view of trends.

---

## 🚀 Quick start

# 1) Create & activate venv
python3 -m venv .venv
source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Run the app
streamlit run app/Home.py

# How to use the data
Option A — Mock data (default)
Works out of the box.

In the sidebar, choose Mock (processed).

Option B — Upload your own CSV (quick test)
In the sidebar, choose Upload CSV and drop a file.

Required columns:

category, manufacturer, registrations

and one of: date or (year,month) or (year,quarter)

The app reads it and refreshes charts immediately (not saved to disk).

Example CSV

date,category,manufacturer,registrations
2025-03-31,2W,Honda,300000
2025-03-31,4W,Tata,70000
2025-06-30,2W,Honda,305000
2025-06-30,4W,Tata,72000

Option C — Persist a CSV (so it’s the default next time)
python -m scripts.04_process_csv data/raw/my_vahan_export.csv

# -> writes data/processed/registrations.parquet (used by the app)

Note: An optional Selenium script is included (scripts/03_fetch_vahan_selenium.py) if you want to try auto-fetching a table from the Vahan site. It may need small tweaks (clicks/XPaths) depending on the page.

What you get in the app
Home: headline KPIs (Total, QoQ, YoY), a quick trend, and a small “insights” section.

Overview: totals by category (via TOTAL rollup), trend lines, YoY bars, latest-quarter table, CSV download.

Manufacturers: filter by category and brand, see trends + YoY, snapshot table, CSV download.

Growth logic

QoQ = current quarter vs previous quarter.

YoY = current quarter vs same quarter last year (4 quarters back).

# Folder structure

vahan-growth-dashboard/
├─ .streamlit/
│  └─ config.toml                # Streamlit theme/settings
├─ app/
│  ├─ __init__.py
│  ├─ Home.py                    # Investor-style home (KPIs + insights)
│  ├─ components/
│  │  ├─ __init__.py
│  │  └─ data_source.py          # Sidebar data-source switch (mock / upload)
│  └─ pages/
│     ├─ 1_📈_Overview.py         # Category totals (YoY/QoQ)
│     └─ 2_🏭_Manufacturers.py     # Manufacturer drill-down (YoY/QoQ)
├─ data/
│  ├─ raw/                       # Input CSVs (mock/template/your exports)
│  └─ processed/                 # Output parquet used by the app
├─ notebooks/                    # (optional) scratch work
├─ scripts/
│  ├─ 01_bootstrap_mock.py       # Build mock data
│  ├─ 02_export_template.py      # Create a sample CSV template
│  ├─ 03_fetch_vahan_selenium.py # Optional: auto-fetch table (stub)
│  └─ 04_process_csv.py          # Persist any CSV -> processed parquet
├─ src/
│  ├─ config.py                  # Paths/env defaults
│  ├─ utils.py                   # Logger helpers
│  ├─ data/
│  │  ├─ ingest_upload.py        # CSV parser (date normalization)
│  │  ├─ clean.py                # Standardize schema
│  │  ├─ storage.py              # Load/save data
│  │  └─ fetch.py                # (reserved)
│  ├─ features/
│  │  └─ growth.py               # QoQ/YoY + TOTAL rollups
│  └─ viz/
│     └─ charts.py               # Plotly chart helpers
├─ tests/                        # (optional) room for tests
├─ .env                          # Local env (ignored)
├─ .gitignore
├─ README.md
└─ requirements.txt

# Common commands

Recreate mock data:
python -m scripts.01_bootstrap_mock

Export a tiny template CSV:
python -m scripts.02_export_template

Process your CSV and make it the default dataset:
python -m scripts.04_process_csv path/to/your.csv

# Investor notes (fill this with what you observe)
Example: “2W shows steady QoQ growth; 4W improving but slower YoY.”

Example: “In latest quarter, Maruti leads YoY in 4W.”

# Video
3–5 min walkthrough (Home → Overview → Manufacturers → CSV upload).

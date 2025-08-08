import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from src.config import RAW_DIR
from src.utils import get_logger

log = get_logger("fetch")

# ---- MOCK DATA (unblocks UI). Replace later with real fetch/scrape. ----
def generate_mock_quarterly(start_year=2023, end_year=2025) -> pd.DataFrame:
    rng = pd.period_range(f"{start_year}Q1", f"{end_year}Q4", freq="Q")
    rng = [p for p in rng if (p.start_time.year < end_year or p.quarter <= 2)]  # up to Q2 2025

    categories = ["2W", "3W", "4W"]
    manufacturers = {
        "2W": ["Hero", "Honda", "TVS", "Bajaj"],
        "3W": ["Piaggio", "Bajaj 3W", "Mahindra 3W"],
        "4W": ["Maruti", "Hyundai", "Tata", "Mahindra"]
    }

    rows = []
    rs = np.random.RandomState(42)

    for cat in categories:
        for mfr in manufacturers[cat]:
            level = rs.randint(20_000, 120_000) if cat == "2W" else rs.randint(5_000, 25_000) if cat == "3W" else rs.randint(15_000, 80_000)
            for p in rng:
                # deterministic trend + small noise
                growth = 1 + (0.02 if cat == "2W" else 0.015 if cat == "4W" else 0.012)
                level = int(level * growth + rs.randint(-1500, 1500))
                rows.append({
                    "date": p.end_time.normalize(),
                    "year": p.year,
                    "quarter": f"{p.year}Q{p.quarter}",
                    "category": cat,
                    "manufacturer": mfr,
                    "registrations": max(level, 0)
                })

    df = pd.DataFrame(rows)
    return df

def save_raw_snapshot(df: pd.DataFrame, name: str = None) -> Path:
    name = name or datetime.now().strftime("mock_%Y%m%d_%H%M%S")
    out = RAW_DIR / f"{name}.csv"
    df.to_csv(out, index=False)
    log.info(f"Raw snapshot saved: {out}")
    return out

# ---- Placeholder for REAL scraping/ingest (wire later) ----
def fetch_from_vahan_placeholder():
    """
    TODO: Implement Selenium/requests-based ingestion.
    Return a DataFrame with columns:
    ['date','year','quarter','category','manufacturer','registrations']
    """
    raise NotImplementedError("Implement real Vahan fetch later.")

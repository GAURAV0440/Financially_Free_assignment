import pandas as pd

REQUIRED_COLS = ["date", "year", "quarter", "category", "manufacturer", "registrations"]

def standardize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # enforce columns
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df["year"] = df["date"].dt.year
    # Ensure quarter is consistent string like '2025Q2'
    if "quarter" not in df or df["quarter"].isna().any():
        df["quarter"] = df["date"].dt.to_period("Q").astype(str).str.replace("Q", "Q", regex=False)
    df["category"] = df["category"].astype(str)
    df["manufacturer"] = df["manufacturer"].astype(str)
    df["registrations"] = pd.to_numeric(df["registrations"], errors="coerce").fillna(0).astype(int)
    return df

def ensure_quarter_order(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["category", "manufacturer", "date"]).reset_index(drop=True)
    return df

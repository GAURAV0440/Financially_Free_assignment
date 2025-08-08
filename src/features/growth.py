import pandas as pd

def add_qoq(df: pd.DataFrame, group_cols=("category","manufacturer")) -> pd.DataFrame:
    df = df.sort_values(["date"]).copy()
    df["prev_q"] = df.groupby(list(group_cols))["registrations"].shift(1)
    df["qoq_pct"] = (df["registrations"] - df["prev_q"]) / df["prev_q"] * 100
    return df

def add_yoy(df: pd.DataFrame, group_cols=("category","manufacturer")) -> pd.DataFrame:
    df = df.sort_values(["date"]).copy()
    df["prev_y"] = df.groupby(list(group_cols))["registrations"].shift(4)
    df["yoy_pct"] = (df["registrations"] - df["prev_y"]) / df["prev_y"] * 100
    return df

def add_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Add a 'TOTAL' manufacturer row per category for investor view."""
    base = df.copy()
    tot = (base
           .groupby(["date","year","quarter","category"], as_index=False)["registrations"].sum())
    tot["manufacturer"] = "TOTAL"
    return pd.concat([base, tot], ignore_index=True)

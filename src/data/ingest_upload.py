from typing import Union, IO
import pandas as pd


REQUIRED_CORE = ["category", "manufacturer", "registrations"]


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lower/strip col names and map common aliases to expected names."""
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]

    aliases = {
        "vehicle_category": "category",
        "vehicle_type": "category",
        "brand": "manufacturer",
        "maker": "manufacturer",
        "oem": "manufacturer",
        "regns": "registrations",
        "count": "registrations",
        "qty": "registrations",
        "units": "registrations",
    }
    for old, new in aliases.items():
        if old in df.columns and new not in df.columns:
            df = df.rename(columns={old: new})
    return df


def _ensure_quarter_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Path 1: explicit date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if df["date"].isna().any():
            bad = df[df["date"].isna()].index[:3].tolist()
            raise ValueError(f"Unparseable 'date' values at rows: {bad}...")
        q = df["date"].dt.to_period("Q")
        df["year"] = df["date"].dt.year
        df["quarter"] = q.astype(str)
        # quarter end as midnight
        df["date"] = q.dt.to_timestamp(how="end").dt.normalize()
        return df

    # Path 2: year + month
    if {"year", "month"}.issubset(df.columns):
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df["month"] = pd.to_numeric(df["month"], errors="coerce")
        dt = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1), errors="coerce")
        if dt.isna().any():
            raise ValueError("Failed to build dates from year/month.")
        q = dt.dt.to_period("Q")
        df["date"] = q.dt.to_timestamp(how="end").dt.normalize()
        df["year"] = df["date"].dt.year
        df["quarter"] = q.astype(str)
        return df

    # Path 3: year + quarter (1..4 or Q1..Q4)
    if {"year", "quarter"}.issubset(df.columns):
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        q_raw = df["quarter"].astype(str).str.strip().str.upper()
        q_norm = q_raw.where(q_raw.str.match(r"^Q[1-4]$"),
                             "Q" + q_raw.str.extract(r"([1-4])", expand=False).fillna(""))
        if (q_norm.str.match(r"^Q[1-4]$").sum() != len(q_norm)):
            raise ValueError("Invalid 'quarter' values. Use 1-4 or Q1-Q4.")

        qlabels = df["year"].astype(int).astype(str) + q_norm
        p = pd.PeriodIndex(qlabels, freq="Q")
        df["quarter"] = p.astype(str)
        # DatetimeIndex -> normalize to midnight
        df["date"] = p.to_timestamp(how="end").normalize()
        df["year"] = df["date"].year
        return df

    raise ValueError("Provide either 'date' OR ('year','month') OR ('year','quarter').")


def parse_uploaded_csv(file_like: Union[str, IO]) -> pd.DataFrame:
    """
    Read an uploaded CSV and return a standardized quarterly DataFrame.
    """
    df = pd.read_csv(file_like)
    df = _standardize_columns(df)

    # Core checks
    missing = [c for c in REQUIRED_CORE if c not in df.columns]
    if missing:
        raise ValueError(f"Missing core columns: {missing}. "
                         f"Need {REQUIRED_CORE} plus a date spec.")

    # Date/quarter normalization
    df = _ensure_quarter_cols(df)

    # Registrations as int
    df["registrations"] = pd.to_numeric(df["registrations"], errors="coerce").fillna(0).astype(int)

    # Final schema + sort
    out = (df[["date", "year", "quarter", "category", "manufacturer", "registrations"]]
           .sort_values(["category", "manufacturer", "date"])
           .reset_index(drop=True))
    return out
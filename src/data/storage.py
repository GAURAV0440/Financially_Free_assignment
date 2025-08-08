from pathlib import Path
import pandas as pd
from src.config import PROCESSED_DIR
from src.utils import ensure_dir, get_logger

log = get_logger("storage")

def save_processed(df: pd.DataFrame, name: str = "registrations.parquet") -> Path:
    ensure_dir(PROCESSED_DIR)
    out = PROCESSED_DIR / name
    df.to_parquet(out, index=False)
    log.info(f"Processed saved: {out}")
    return out

def load_processed(name: str = "registrations.parquet") -> pd.DataFrame:
    path = PROCESSED_DIR / name
    return pd.read_parquet(path)

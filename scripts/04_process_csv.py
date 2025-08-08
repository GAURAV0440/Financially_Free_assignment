import sys
from pathlib import Path
import pandas as pd

from src.data.ingest_upload import parse_uploaded_csv
from src.data.clean import standardize, ensure_quarter_order
from src.data.storage import save_processed
from src.features.growth import add_qoq, add_yoy, add_totals
from src.config import PROCESSED_DIR
from src.utils import get_logger

log = get_logger("process_csv")

def main(csv_path: str):
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(p)

    log.info(f"Parsing uploaded CSV: {p}")
    df = parse_uploaded_csv(p)

    # Clean + order + totals + growth
    df = standardize(df)
    df = ensure_quarter_order(df)
    df = add_totals(df)
    df = add_qoq(df)
    df = add_yoy(df)

    # Save processed parquet
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    save_processed(df, "registrations.parquet")
    log.info("Processed parquet updated.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/04_process_csv.py <path_to_csv>")
        sys.exit(1)
    main(sys.argv[1])

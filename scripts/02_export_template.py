from src.data.storage import load_processed
from pathlib import Path
import pandas as pd

def main():
    df = load_processed("registrations.parquet")
    # minimal template columns (you can edit/extend)
    tpl = df[["date","category","manufacturer","registrations"]].head(20)
    out = Path("data/raw/upload_template.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    tpl.to_csv(out, index=False)
    print(f"Template written: {out.resolve()}")

if __name__ == "__main__":
    main()

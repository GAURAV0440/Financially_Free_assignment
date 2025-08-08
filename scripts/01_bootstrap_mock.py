from src.data.fetch import generate_mock_quarterly, save_raw_snapshot
from src.data.clean import standardize, ensure_quarter_order
from src.data.storage import save_processed
from src.features.growth import add_qoq, add_yoy, add_totals

def main():
    # 1) generate mock
    df = generate_mock_quarterly(start_year=2023, end_year=2025)

    # 2) save raw snapshot (csv)
    save_raw_snapshot(df, name="mock_quarterly")

    # 3) clean + order
    df = standardize(df)
    df = ensure_quarter_order(df)

    # 4) add TOTAL rows & growth metrics
    df = add_totals(df)
    df = add_qoq(df)
    df = add_yoy(df)

    # 5) save processed parquet
    save_processed(df, "registrations.parquet")

if __name__ == "__main__":
    main()
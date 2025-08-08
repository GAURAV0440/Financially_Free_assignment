from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data")).resolve()
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

VAHAN_BASE_URL = os.getenv("VAHAN_BASE_URL")
DB_URL = os.getenv("DB_URL", "sqlite:///data/registrations.db")

# Ensure dirs exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
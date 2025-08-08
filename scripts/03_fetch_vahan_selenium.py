import time
from datetime import datetime
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from src.config import RAW_DIR, VAHAN_BASE_URL
from src.utils import get_logger

log = get_logger("fetch_vahan")

def setup_driver(headless: bool = True):
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1600,1000")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=opts)

def extract_biggest_table(html: str) -> pd.DataFrame:
    # Try pandas.read_html first
    tables = pd.read_html(html, flavor="bs4")
    if not tables:
        raise RuntimeError("No tables found on page.")
    # pick the widest/most rows table
    tables.sort(key=lambda d: (d.shape[0], d.shape[1]), reverse=True)
    df = tables[0]
    # Drop multiindex columns if any
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [" ".join([str(c) for c in col if str(c) != "nan"]).strip() for col in df.columns]
    return df

def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    url = VAHAN_BASE_URL or "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"

    log.info(f"Opening {url}")
    driver = setup_driver(headless=True)
    driver.get(url)

    # TODO: If page needs navigation/clicks, add them here
    # Example (uncomment and adjust):
    # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Some Tab')]"))).click()

    # Wait for any table to appear
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//table"))
    )
    time.sleep(2)  # small stability wait

    html = driver.page_source
    driver.quit()

    df = extract_biggest_table(html)

    # Save raw CSV
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = RAW_DIR / f"vahan_raw_{ts}.csv"
    df.to_csv(out, index=False)
    log.info(f"Saved raw CSV: {out.resolve()}")

if __name__ == "__main__":
    main()

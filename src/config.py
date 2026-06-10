from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURES_DIR = BASE_DIR / "reports" / "figures"
OUTPUT_DIR = BASE_DIR / "reports" / "output"

for directory in [
    DATA_RAW_DIR,
    DATA_PROCESSED_DIR,
    FIGURES_DIR,
    OUTPUT_DIR,
]:
    directory.mkdir(parents=True, exist_ok=True)


ETF_MAP = {
    "IE00BM67HS53": "XDWM.MI",
    "IE00BM67HM91": "XDW0.DE",
    "IE00BM67HV82": "XDWI.MI",
    "IE00BM67HQ30": "XDWU.MI",
    "IE00B5L01S80": "HPRD.L",
    "IE00BM67HL84": "XDWF.DE",
    "IE00BM67HK77": "XDWH.MI",
    "IE00BM67HN09": "XDWS.MI",
    "IE00BM67HT60": "XDWT.MI",
    "IE00BM67HP23": "XDWC.MI",
    "IE00BM67HR47": "XWTS.MI",
}

SECTOR_MAP = {
    "IE00BM67HS53": "Materials",
    "IE00BM67HM91": "Energy",
    "IE00BM67HV82": "Industrials",
    "IE00BM67HQ30": "Utilities",
    "IE00B5L01S80": "Real Estate",
    "IE00BM67HL84": "Financials",
    "IE00BM67HK77": "Health Care",
    "IE00BM67HN09": "Consumer Staples",
    "IE00BM67HT60": "Technology",
    "IE00BM67HP23": "Consumer Discretionary",
    "IE00BM67HR47": "Communication Services",
}
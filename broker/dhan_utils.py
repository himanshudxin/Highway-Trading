import csv, os, urllib.request
SCRIP_MASTER_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"
SCRIP_CACHE_PATH = os.path.expanduser("~/.dhan_scrip_master.csv")

def resolve_dhan_security_id(symbol: str):
    if not os.path.exists(SCRIP_CACHE_PATH):
        req = urllib.request.Request(SCRIP_MASTER_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r, open(SCRIP_CACHE_PATH, "wb") as f:
            f.write(r.read())
    sym = symbol.upper().replace(".NS", "")
    with open(SCRIP_CACHE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for row in csv.DictReader(f):
            if row.get("SEM_TRADING_SYMBOL") == sym and row.get("SEM_EXM_EXCH_ID") == "NSE" and row.get("SEM_INSTRUMENT_NAME") == "EQUITY":
                return row.get("SEM_SMST_SECURITY_ID")
    return None

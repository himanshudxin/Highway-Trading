import json, sys, urllib.request
def fetch(sym):
    req = urllib.request.Request(f"https://www.nseindia.com/api/corporates-pit?symbol={sym}", headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r: return json.loads(r.read().decode())
    except Exception as e: return {"error": str(e)}
if __name__ == "__main__": print(json.dumps(fetch(sys.argv[1] if len(sys.argv)>1 else "RELIANCE")))

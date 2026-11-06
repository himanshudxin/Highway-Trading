import json, urllib.request

def fetch_nse_daily_ohlc(ticker: str, range_period: str = "6mo") -> tuple:
    ticker_clean = ticker.strip().upper()
    if not (ticker_clean.startswith("^") or ticker_clean.endswith(".NS") or ticker_clean.endswith(".BO")):
        ticker_clean = f"{ticker_clean}.NS"
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_clean}?range={range_period}&interval=1d&includePrePost=false"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as response:
        payload = json.loads(response.read().decode("utf-8"))
    res = payload.get("chart", {}).get("result", [{}])[0]
    quotes = res.get("indicators", {}).get("quote", [{}])[0]
    candles = []
    for h, l, c, o in zip(quotes.get("high", []), quotes.get("low", []), quotes.get("close", []), quotes.get("open", [])):
        if None not in (h, l, c, o):
            candles.append({"high": float(h), "low": float(l), "close": float(c), "open": float(o)})
    return candles, ticker_clean

def compute_14_atr(candles: list, period: int = 14) -> float:
    if len(candles) <= period: raise ValueError("Insufficient candle history")
    tr_list = [candles[0]["high"] - candles[0]["low"]]
    for i in range(1, len(candles)):
        h, l, prev_c = candles[i]["high"], candles[i]["low"], candles[i - 1]["close"]
        tr_list.append(max(h - l, abs(h - prev_c), abs(l - prev_c)))
    atr = sum(tr_list[:period]) / period
    for tr in tr_list[period:]:
        atr = ((atr * (period - 1)) + tr) / period
    return round(atr, 2)

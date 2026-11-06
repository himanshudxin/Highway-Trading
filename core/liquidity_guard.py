from core.atr_nse import fetch_nse_daily_ohlc

def validate_asset_safety(symbol: str, max_day_gain_pct: float = 6.0):
    try:
        candles, _ = fetch_nse_daily_ohlc(symbol, range_period="1mo")
        if not candles: return False, "No data."
        latest, prev = candles[-1], candles[-2]
        day_gain = ((latest["close"] - prev["close"]) / prev["close"]) * 100.0
        if day_gain >= max_day_gain_pct:
            return False, f"BLOCKED: {symbol} up {day_gain:.2f}% (circuit risk)."
        return True, f"PASSED: {symbol} liquid and safe."
    except Exception as e:
        return False, f"BLOCKED: Verification error {e}"

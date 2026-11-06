from core.atr_nse import fetch_nse_daily_ohlc

def check_market_regime(max_drop_pct: float = 0.75):
    try:
        candles, _ = fetch_nse_daily_ohlc("^NSEI", range_period="3mo")
        latest, prev = candles[-1], candles[-2]
        change_pct = ((latest["close"] - prev["close"]) / prev["close"]) * 100.0
        sma_20 = sum([c["close"] for c in candles[-20:]]) / 20.0
        if change_pct < -abs(max_drop_pct):
            return False, f"BLOCKED: NIFTY 50 down {change_pct:.2f}%."
        if latest["close"] < sma_20:
            return False, f"BLOCKED: NIFTY 50 (₹{latest['close']:.2f}) below 20-SMA (₹{sma_20:.2f})."
        return True, "PASSED: Broad market healthy."
    except Exception as e:
        return True, f"WARNING: Macro check bypassed ({e})."

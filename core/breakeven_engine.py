def evaluate_breakeven_shield(entry_price: float, current_ltp: float, current_stop: float, atr_at_entry: float, brokerage_buffer_pct: float = 0.25):
    be_stop = round(entry_price * (1.0 + (brokerage_buffer_pct / 100.0)), 2)
    r_target = entry_price + (1.0 * atr_at_entry)
    if current_ltp >= r_target and current_stop < be_stop:
        return True, be_stop, f"PROTECTION ACTIVE: +1R gained. Stop moved to Breakeven (₹{be_stop:.2f})."
    return False, current_stop, "Holding current stop"

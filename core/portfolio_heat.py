from core.ledger import TradeLedger

SECTOR_MAP = {
    "TATAMOTORS": "AUTO", "MARUTI": "AUTO", "M&M": "AUTO", "BAJAJ-AUTO": "AUTO",
    "TCS": "IT", "INFY": "IT", "WIPRO": "IT", "HCLTECH": "IT",
    "HDFCBANK": "FINANCE", "ICICIBANK": "FINANCE", "SBIN": "FINANCE", "KOTAKBANK": "FINANCE",
    "NIFTYBEES": "BROAD_INDEX", "SENSEXBEES": "BROAD_INDEX"
}

def evaluate_portfolio_heat(new_symbol: str, new_risk_inr: float, total_capital: float = 100000.0, max_heat_pct: float = 2.0, max_trades: int = 3):
    open_trades = TradeLedger().get_open_trades()
    if len(open_trades) >= max_trades:
        return False, f"BLOCKED: Concurrent limit ({max_trades}) reached."
    new_sec = SECTOR_MAP.get(new_symbol.upper(), "OTHER")
    for t in open_trades:
        if new_sec != "OTHER" and new_sec == SECTOR_MAP.get(t["symbol"].upper(), "OTHER"):
            return False, f"BLOCKED: Sector [{new_sec}] collision with {t['symbol']}."
    open_risk = sum([(t['entry_price'] - t['current_stop']) * t['quantity'] for t in open_trades if t['current_stop'] < t['entry_price']])
    if (open_risk + new_risk_inr) > (total_capital * max_heat_pct / 100.0):
        return False, "BLOCKED: Exceeds 2.0% maximum portfolio risk heat."
    return True, "PASSED: Portfolio heat compliant."

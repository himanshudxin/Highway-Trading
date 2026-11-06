import uuid, logging
from core.ledger import TradeLedger
from core.notifier import send_alert
from core.atr_nse import fetch_nse_daily_ohlc, compute_14_atr
from core.chandelier_exit import round_to_tick, ChandelierTrailingEngine, Candle
from core.regime_filter import check_market_regime
from core.liquidity_guard import validate_asset_safety
from core.portfolio_heat import evaluate_portfolio_heat

class ExecutionEngine:
    def __init__(self, is_paper: bool = True, broker: str = "ZERODHA"):
        self.is_paper = is_paper
        self.broker = broker.upper()
        self.ledger = TradeLedger()
        self.chandelier = ChandelierTrailingEngine(period=14, multiplier=2.5)

    def execute_entry(self, symbol: str, total_capital: float = 100000.0, risk_pct: float = 1.0):
        symbol = symbol.upper()
        candles_raw, _ = fetch_nse_daily_ohlc(symbol)
        atr = compute_14_atr(candles_raw, period=14)
        ltp = candles_raw[-1]["close"]
        stop_dist = atr * 2.0
        stop_price = round_to_tick(ltp - stop_dist)
        target_price = round_to_tick(ltp + (stop_dist * 2.0))
        risk_per_share = ltp - stop_price
        qty = min(int((total_capital * (risk_pct / 100.0)) // risk_per_share), int((total_capital * 0.40) // ltp))
        if qty <= 0: return False

        passed, msg = evaluate_portfolio_heat(symbol, qty * risk_per_share, total_capital)
        if not passed: send_alert(msg, "WARNING"); return False
        passed, msg = check_market_regime()
        if not passed: send_alert(msg, "WARNING"); return False
        passed, msg = validate_asset_safety(symbol)
        if not passed: send_alert(msg, "WARNING"); return False

        tid = self.ledger.add_trade(symbol, self.broker, self.is_paper, f"ord_{uuid.uuid4().hex[:6]}", f"gtt_{uuid.uuid4().hex[:6]}", ltp, qty, stop_price, target_price, atr)
        send_alert(f"[ORDER PLACED] {symbol} Qty:{qty} @ ₹{ltp:.2f} | Stop: ₹{stop_price:.2f}", "SUCCESS")
        return tid

import logging
from broker.dhan_utils import resolve_dhan_security_id
from core.atr_nse import fetch_nse_daily_ohlc, compute_14_atr
from core.chandelier_exit import round_to_tick

def execute_dhan_entry(dhan, symbol: str, total_capital: float = 100000.0, risk_pct: float = 1.0):
    sec_id = resolve_dhan_security_id(symbol)
    if not sec_id: return
    candles, _ = fetch_nse_daily_ohlc(symbol)
    atr = compute_14_atr(candles, 14)
    ltp = candles[-1]["close"]
    stop = round_to_tick(ltp - (atr * 2.0))
    target = round_to_tick(ltp + (atr * 4.0))
    qty = int((total_capital * (risk_pct / 100.0)) // (ltp - stop))
    if qty <= 0: return
    dhan.place_order(security_id=sec_id, exchange_segment=dhan.NSE, transaction_type=dhan.BUY, quantity=qty, order_type=dhan.MARKET, product_type=dhan.CNC, price=0)
    dhan.create_forever(order_flag="OCO", transaction_type=dhan.SELL, exchange_segment=dhan.NSE, product_type=dhan.CNC, order_type=dhan.LIMIT, security_id=sec_id, quantity=qty, trigger_price=stop, price=round_to_tick(stop * 0.995), trigger_price_1=target, price_1=target)

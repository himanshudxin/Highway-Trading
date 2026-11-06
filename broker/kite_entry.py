from core.atr_nse import fetch_nse_daily_ohlc, compute_14_atr
from core.chandelier_exit import round_to_tick

def execute_kite_entry(kite, symbol: str, total_capital: float = 100000.0, risk_pct: float = 1.0):
    candles, _ = fetch_nse_daily_ohlc(symbol)
    atr = compute_14_atr(candles, 14)
    ltp = kite.quote(f"NSE:{symbol}")[f"NSE:{symbol}"]["last_price"]
    stop = round_to_tick(ltp - (atr * 2.0))
    target = round_to_tick(ltp + (atr * 4.0))
    qty = int((total_capital * (risk_pct / 100.0)) // (ltp - stop))
    if qty <= 0: return
    oid = kite.place_order(variety=kite.VARIETY_REGULAR, exchange="NSE", tradingsymbol=symbol, transaction_type=kite.TRANSACTION_TYPE_BUY, quantity=qty, order_type=kite.ORDER_TYPE_MARKET, product=kite.PRODUCT_CNC)
    kite.place_gtt(trigger_type=kite.GTT_TYPE_OCO, tradingsymbol=symbol, exchange="NSE", trigger_values=[stop, target], last_price=ltp, orders=[
        {"exchange": "NSE", "tradingsymbol": symbol, "transaction_type": kite.TRANSACTION_TYPE_SELL, "quantity": qty, "order_type": kite.ORDER_TYPE_LIMIT, "product": kite.PRODUCT_CNC, "price": round_to_tick(stop * 0.995)},
        {"exchange": "NSE", "tradingsymbol": symbol, "transaction_type": kite.TRANSACTION_TYPE_SELL, "quantity": qty, "order_type": kite.ORDER_TYPE_LIMIT, "product": kite.PRODUCT_CNC, "price": target}
    ])
    return oid

from broker.dhan_utils import resolve_dhan_security_id
from core.atr_nse import fetch_nse_daily_ohlc
from core.chandelier_exit import ChandelierTrailingEngine, Candle, round_to_tick

def sync_dhan_stop(dhan, symbol: str, entry_price: float):
    sec_id = resolve_dhan_security_id(symbol)
    candles_raw, _ = fetch_nse_daily_ohlc(symbol)
    candles = [Candle(f"d_{i}", c["open"], c["high"], c["low"], c["close"]) for i, c in enumerate(candles_raw)]
    calc_stop = round_to_tick(ChandelierTrailingEngine().init_trade(symbol, "LONG", entry_price, candles).current_stop)
    for fo in dhan.get_forever_orders().get("data", []):
        if fo.get("securityId") == sec_id and fo.get("orderStatus") == "CONFIRMED":
            if calc_stop > float(fo.get("triggerPrice", 0)):
                dhan.modify_forever(order_id=fo.get("orderId"), order_flag="OCO", order_type=dhan.LIMIT, leg_name="STOP_LOSS_LEG", quantity=fo.get("quantity"), price=round_to_tick(calc_stop * 0.995), trigger_price=calc_stop)

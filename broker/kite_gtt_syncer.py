from core.atr_nse import fetch_nse_daily_ohlc
from core.chandelier_exit import ChandelierTrailingEngine, Candle, round_to_tick

def sync_kite_stop(kite, symbol: str, entry_price: float, gtt_id: int):
    candles_raw, _ = fetch_nse_daily_ohlc(symbol)
    candles = [Candle(f"d_{i}", c["open"], c["high"], c["low"], c["close"]) for i, c in enumerate(candles_raw)]
    calc_stop = round_to_tick(ChandelierTrailingEngine().init_trade(symbol, "LONG", entry_price, candles).current_stop)
    gtt = kite.get_gtt(gtt_id)
    if calc_stop > gtt["condition"]["trigger_values"][0]:
        orders = gtt["orders"]
        orders[0]["price"] = round_to_tick(calc_stop * 0.995)
        triggers = gtt["condition"]["trigger_values"]
        triggers[0] = calc_stop
        kite.modify_gtt(trigger_id=gtt_id, trigger_type=gtt["type"], tradingsymbol=symbol, exchange="NSE", trigger_values=triggers, last_price=candles[-1]["close"], orders=orders)

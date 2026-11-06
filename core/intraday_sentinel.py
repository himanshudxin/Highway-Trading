import time, logging
from datetime import datetime, time as dtime
from core.breakeven_engine import evaluate_breakeven_shield
from core.chandelier_exit import round_to_tick
from core.ledger import TradeLedger
from core.notifier import send_alert
from core.atr_nse import fetch_nse_daily_ohlc

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class IntradaySentinel:
    def __init__(self, check_interval_sec: int = 300):
        self.interval = check_interval_sec
        self.ledger = TradeLedger()

    def scan_and_defend(self):
        for trade in self.ledger.get_open_trades():
            try:
                candles, _ = fetch_nse_daily_ohlc(trade["symbol"], range_period="5d")
                ltp = candles[-1]["close"]
            except Exception: continue
            should_move, be_stop, _ = evaluate_breakeven_shield(trade["entry_price"], ltp, trade["current_stop"], trade["atr_at_entry"])
            if should_move:
                self.ledger.ratchet_stop(trade["id"], round_to_tick(be_stop))
                send_alert(f"🛡️ *BREAKEVEN LOCKED:* {trade['symbol']} at ₹{be_stop:.2f}", "SUCCESS")

    def start(self):
        while True:
            self.scan_and_defend()
            time.sleep(self.interval)

if __name__ == "__main__":
    IntradaySentinel().start()

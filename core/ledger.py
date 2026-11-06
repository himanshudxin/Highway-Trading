import os, sqlite3
from typing import Dict, List, Optional

DB_PATH = os.path.expanduser("~/highway_trading.db")

class TradeLedger:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    broker TEXT NOT NULL,
                    is_paper INTEGER DEFAULT 1,
                    entry_order_id TEXT,
                    gtt_order_id TEXT,
                    entry_price REAL NOT NULL,
                    quantity INTEGER NOT NULL,
                    initial_stop REAL NOT NULL,
                    current_stop REAL NOT NULL,
                    target_price REAL NOT NULL,
                    atr_at_entry REAL,
                    status TEXT DEFAULT 'OPEN',
                    exit_price REAL,
                    realized_pnl REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_id INTEGER,
                    old_stop REAL,
                    new_stop REAL,
                    action TEXT,
                    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(trade_id) REFERENCES trades(id)
                )
            """)
            conn.commit()

    def add_trade(self, symbol, broker, is_paper, entry_order_id, gtt_order_id, entry_price, quantity, stop_loss, target_price, atr) -> int:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO trades (symbol, broker, is_paper, entry_order_id, gtt_order_id, entry_price, quantity, initial_stop, current_stop, target_price, atr_at_entry, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN')
            """, (symbol.upper(), broker.upper(), 1 if is_paper else 0, entry_order_id, str(gtt_order_id), entry_price, quantity, stop_loss, stop_loss, target_price, atr))
            conn.commit()
            return cur.lastrowid

    def get_open_trades(self, broker: Optional[str] = None) -> List[Dict]:
        with self._get_connection() as conn:
            cur = conn.cursor()
            if broker:
                cur.execute("SELECT * FROM trades WHERE status = 'OPEN' AND broker = ?", (broker.upper(),))
            else:
                cur.execute("SELECT * FROM trades WHERE status = 'OPEN'")
            return [dict(r) for r in cur.fetchall()]

    def ratchet_stop(self, trade_id: int, new_stop: float) -> bool:
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT current_stop FROM trades WHERE id = ?", (trade_id,))
            row = cur.fetchone()
            if not row or new_stop <= row["current_stop"]: return False
            cur.execute("UPDATE trades SET current_stop = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_stop, trade_id))
            cur.execute("INSERT INTO audit_logs (trade_id, old_stop, new_stop, action) VALUES (?, ?, ?, 'RATCHET_UP')", (trade_id, row["current_stop"], new_stop))
            conn.commit()
            return True

    def close_trade(self, trade_id: int, exit_price: float, reason: str):
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT entry_price, quantity FROM trades WHERE id = ?", (trade_id,))
            row = cur.fetchone()
            if row:
                pnl = round((exit_price - row["entry_price"]) * row["quantity"], 2)
                cur.execute("UPDATE trades SET status = ?, exit_price = ?, realized_pnl = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (reason, exit_price, pnl, trade_id))
                conn.commit()

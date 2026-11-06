import json, sqlite3, os

db_path = os.path.expanduser("~/highway_trading.db")
if not os.path.exists(db_path):
    db_path = "./highway_trading.db"

output = {"trades": []}
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT symbol, broker, is_paper, entry_price, current_stop, target_price, status FROM trades WHERE status='OPEN'")
    output["trades"] = [dict(r) for r in cur.fetchall()]
    conn.close()

with open("data.json", "w") as f:
    json.dump(output, f, indent=2)
print("Exported active ledger to data.json")

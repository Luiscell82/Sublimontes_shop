import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "lots_seen.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_lots (
            lot_id    TEXT PRIMARY KEY,
            brand     TEXT,
            model     TEXT,
            year      INTEGER,
            mileage   INTEGER,
            price     REAL,
            score     INTEGER,
            url       TEXT,
            notified  INTEGER DEFAULT 0,
            seen_at   TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS bot_runs (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            ran_at     TEXT DEFAULT CURRENT_TIMESTAMP,
            lots_found INTEGER,
            lots_new   INTEGER
        )
    """)
    conn.commit()
    conn.close()


def is_seen(lot_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT 1 FROM seen_lots WHERE lot_id = ?", (lot_id,)).fetchone()
    conn.close()
    return row is not None


def mark_seen(lot: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        INSERT OR IGNORE INTO seen_lots (lot_id, brand, model, year, mileage, price, score, url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (lot["id"], lot.get("brand"), lot.get("model"), lot.get("year"),
         lot.get("mileage"), lot.get("price"), lot.get("score", 0), lot.get("url")),
    )
    conn.commit()
    conn.close()


def log_run(lots_found: int, lots_new: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO bot_runs (ran_at, lots_found, lots_new) VALUES (?, ?, ?)",
        (datetime.now().isoformat(), lots_found, lots_new),
    )
    conn.commit()
    conn.close()


def get_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    total = conn.execute("SELECT COUNT(*) FROM seen_lots").fetchone()[0]
    runs = conn.execute("SELECT COUNT(*) FROM bot_runs").fetchone()[0]
    last_run = conn.execute("SELECT ran_at FROM bot_runs ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return {
        "total_lots_seen": total,
        "total_runs": runs,
        "last_run": last_run[0] if last_run else "nunca",
    }

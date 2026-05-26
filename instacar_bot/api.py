"""
API REST para que la app Flutter controle el bot y consulte los lotes.
Corre en un hilo separado junto al bucle de scraping.
"""
import json
import os
import threading
import logging
from flask import Flask, jsonify, request

import database
import config as cfg

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)   # silenciar logs de Flask en consola

# ── Estado del bot (compartido con main.py vía set_bot_ref) ──────────────────
_bot_running: threading.Event = threading.Event()
_bot_running.set()

OVERRIDE_FILE = os.path.join(os.path.dirname(__file__), "config_override.json")


def set_bot_ref(event: threading.Event):
    global _bot_running
    _bot_running = event


# ── Helpers ──────────────────────────────────────────────────────────────────
def _load_override() -> dict:
    if os.path.exists(OVERRIDE_FILE):
        with open(OVERRIDE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_override(data: dict):
    with open(OVERRIDE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/lots")
def get_lots():
    """Devuelve los últimos 100 lotes almacenados en la BD."""
    import sqlite3
    conn = sqlite3.connect(database.DB_PATH)
    rows = conn.execute(
        """SELECT lot_id, brand, model, year, mileage, price, score, url, seen_at
           FROM seen_lots ORDER BY seen_at DESC LIMIT 100"""
    ).fetchall()
    conn.close()
    keys = ["id", "brand", "model", "year", "mileage", "price", "score", "url", "seen_at"]
    return jsonify([dict(zip(keys, r)) for r in rows])


@app.get("/stats")
def get_stats():
    return jsonify(database.get_stats())


@app.get("/config")
def get_config():
    override = _load_override()
    return jsonify({
        "max_mileage_km":         override.get("max_mileage_km",         cfg.MAX_MILEAGE_KM),
        "min_year":               override.get("min_year",               cfg.MIN_YEAR),
        "max_price_mxn":          override.get("max_price_mxn",          cfg.MAX_PRICE_MXN),
        "min_score":              override.get("min_score",              cfg.MIN_SCORE),
        "brands_priority":        override.get("brands_priority",        cfg.BRANDS_PRIORITY),
        "check_interval_minutes": override.get("check_interval_minutes", cfg.CHECK_INTERVAL_MINUTES),
    })


@app.post("/config")
def update_config():
    data = request.get_json(force=True) or {}
    existing = _load_override()
    existing.update(data)
    _save_override(existing)
    return jsonify({"status": "ok"})


@app.get("/status")
def bot_status():
    return jsonify({
        "running": _bot_running.is_set(),
        "interval_minutes": cfg.CHECK_INTERVAL_MINUTES,
    })


@app.post("/start")
def start_bot():
    _bot_running.set()
    logger.info("Bot iniciado desde la app")
    return jsonify({"status": "started"})


@app.post("/stop")
def stop_bot():
    _bot_running.clear()
    logger.info("Bot detenido desde la app")
    return jsonify({"status": "stopped"})


# ── Arrancar servidor ─────────────────────────────────────────────────────────
def start_api_server(port: int = 8765):
    """Lanza Flask en un hilo daemon."""
    def _run():
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    t = threading.Thread(target=_run, daemon=True, name="api-server")
    t.start()
    logger.info(f"API REST corriendo en http://0.0.0.0:{port}")
    return t

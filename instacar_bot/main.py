#!/usr/bin/env python3
"""
Bot Instacar — monitorea lotes nuevos con bajo kilometraje y buen precio.
Envía alertas por Telegram cuando encuentra buenas oportunidades.

Uso:
    python main.py            # Corre el bot en bucle continuo
    python main.py --test     # Prueba la conexión de Telegram y hace un scrape único
    python main.py --stats    # Muestra estadísticas de lotes vistos
"""
import argparse
import logging
import sys
import time
from datetime import datetime

import config
import database
import notifier
from filters import filter_lots
from scraper import scrape_lots

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("instacar_bot")


def run_once() -> tuple[int, int]:
    """Un ciclo completo: scrape → filtrar → notificar. Devuelve (total, nuevos)."""
    logger.info("─── Iniciando ciclo de búsqueda ───")

    raw_lots = scrape_lots()
    if not raw_lots:
        logger.warning("No se obtuvieron lotes en este ciclo")
        return 0, 0

    good_lots = filter_lots(raw_lots)
    logger.info(f"Lotes totales: {len(raw_lots)} | Buenos: {len(good_lots)}")

    new_count = 0
    for lot in good_lots:
        if database.is_seen(lot["id"]):
            continue

        logger.info(
            f"  NUEVO LOTE → {lot.get('brand')} {lot.get('model')} {lot.get('year')} "
            f"| {lot.get('mileage', '?')} km | ${lot.get('price', '?')} | score={lot.get('score')}"
        )
        sent = notifier.notify_lot(lot)
        if sent:
            database.mark_seen(lot)
            new_count += 1
        else:
            logger.error(f"No se pudo notificar el lote {lot['id']}")

    database.log_run(len(raw_lots), new_count)

    if new_count > 0:
        notifier.notify_summary(new_count, len(raw_lots))

    logger.info(f"─── Ciclo finalizado: {new_count} lotes nuevos notificados ───")
    return len(raw_lots), new_count


def run_loop():
    interval_secs = config.CHECK_INTERVAL_MINUTES * 60
    logger.info(f"Bot iniciado — revisando cada {config.CHECK_INTERVAL_MINUTES} minutos")
    notifier.notify_startup()

    while True:
        try:
            run_once()
        except Exception as e:
            logger.error(f"Error inesperado en el ciclo: {e}", exc_info=True)
            notifier.notify_error(str(e))

        next_run = datetime.now().strftime("%H:%M:%S")
        logger.info(f"Esperando {config.CHECK_INTERVAL_MINUTES} min... (próxima revisión)")
        time.sleep(interval_secs)


def cmd_test():
    logger.info("Modo prueba: verificando configuración...")

    errors = config.validate()
    if errors:
        for err in errors:
            logger.error(f"  ✗ {err}")
        sys.exit(1)

    logger.info("Probando conexión Telegram...")
    if notifier.test_connection():
        logger.info("  ✓ Telegram conectado correctamente")
    else:
        logger.error("  ✗ Fallo en la conexión de Telegram")
        sys.exit(1)

    logger.info("Haciendo scrape de prueba (un solo ciclo)...")
    total, new = run_once()
    logger.info(f"Prueba completada: {total} lotes totales, {new} notificaciones enviadas")


def cmd_stats():
    stats = database.get_stats()
    print("\n─── Estadísticas del bot ───")
    print(f"  Lotes vistos en total : {stats['total_lots_seen']}")
    print(f"  Ciclos ejecutados     : {stats['total_runs']}")
    print(f"  Último ciclo          : {stats['last_run']}")
    print("────────────────────────────\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot de selección de lotes para Instacar")
    parser.add_argument("--test",  action="store_true", help="Prueba configuración y hace un scrape único")
    parser.add_argument("--stats", action="store_true", help="Muestra estadísticas de lotes vistos")
    args = parser.parse_args()

    database.init_db()

    if args.test:
        cmd_test()
    elif args.stats:
        cmd_stats()
    else:
        run_loop()

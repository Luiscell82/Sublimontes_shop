import requests
import logging
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"


def _send(text: str, parse_mode: str = "HTML") -> bool:
    try:
        resp = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": parse_mode},
            timeout=15,
        )
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error enviando Telegram: {e}")
        return False


def _score_bar(score: int) -> str:
    filled = round(score / 10)
    return "🟩" * filled + "⬜" * (10 - filled)


def notify_lot(lot: dict) -> bool:
    score = lot.get("score", 0)
    mileage = lot.get("mileage", 0)
    price = lot.get("price", 0)
    year = lot.get("year", "?")
    brand = lot.get("brand", "?")
    model = lot.get("model", "?")
    url = lot.get("url", "")
    lot_id = lot.get("id", "?")

    mileage_str = f"{mileage:,} km" if mileage else "N/D"
    price_str = f"${price:,.0f} MXN" if price else "N/D"

    emoji = "🔥" if score >= 80 else "✅" if score >= 65 else "🔔"

    text = (
        f"{emoji} <b>Nuevo lote encontrado!</b>\n\n"
        f"🚗 <b>{brand} {model} {year}</b>\n"
        f"📏 Kilometraje: <b>{mileage_str}</b>\n"
        f"💰 Precio: <b>{price_str}</b>\n"
        f"🏆 Puntuación: <b>{score}/100</b>\n"
        f"{_score_bar(score)}\n"
        f"🔑 Lote ID: <code>{lot_id}</code>\n"
    )
    if url:
        text += f'\n<a href="{url}">Ver lote en Instacar →</a>'

    return _send(text)


def notify_summary(new_count: int, total_checked: int):
    if new_count == 0:
        return
    text = (
        f"📊 <b>Resumen de búsqueda</b>\n\n"
        f"🔍 Lotes revisados: {total_checked}\n"
        f"✨ Lotes nuevos con buena puntuación: {new_count}\n"
    )
    _send(text)


def notify_error(message: str):
    _send(f"⚠️ <b>Error en el bot Instacar</b>\n\n{message}")


def notify_startup():
    _send(
        "🤖 <b>Bot Instacar iniciado</b>\n\n"
        "Monitoreando lotes nuevos con bajo kilometraje y buen precio.\n"
        "Te notificaré cuando encuentre buenas oportunidades."
    )


def test_connection() -> bool:
    """Verifica que el token y chat_id sean válidos."""
    try:
        resp = requests.get(f"{TELEGRAM_API}/getMe", timeout=10)
        if not resp.ok:
            return False
        resp2 = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": "✅ Bot Instacar conectado correctamente."},
            timeout=10,
        )
        return resp2.ok
    except Exception as e:
        logger.error(f"Test de conexión fallido: {e}")
        return False

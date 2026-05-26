import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Instacar credentials
INSTACAR_EMAIL = os.getenv("INSTACAR_EMAIL", "")
INSTACAR_PASSWORD = os.getenv("INSTACAR_PASSWORD", "")
INSTACAR_BASE_URL = "https://www.instacar.mx"
INSTACAR_LOTS_URL = f"{INSTACAR_BASE_URL}/comprar"

# Check interval in minutes
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", "15"))

# Lot filtering criteria
MAX_MILEAGE_KM = int(os.getenv("MAX_MILEAGE_KM", "80000"))
MIN_YEAR = int(os.getenv("MIN_YEAR", "2018"))
MAX_PRICE_MXN = float(os.getenv("MAX_PRICE_MXN", "0"))   # 0 = no limit
MIN_SCORE = int(os.getenv("MIN_SCORE", "50"))             # 0-100 scoring threshold

# Comma-separated brands to prioritize, empty = all brands
BRANDS_PRIORITY = [b.strip().upper() for b in os.getenv("BRANDS_PRIORITY", "TOYOTA,HONDA,NISSAN,MAZDA,KIA").split(",") if b.strip()]

# Headless browser (set False to debug visually)
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

# Puerto de la API REST para la app Flutter
API_PORT = int(os.getenv("API_PORT", "8765"))

def validate():
    errors = []
    if not TELEGRAM_TOKEN:
        errors.append("TELEGRAM_TOKEN no configurado")
    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID no configurado")
    if not INSTACAR_EMAIL:
        errors.append("INSTACAR_EMAIL no configurado")
    if not INSTACAR_PASSWORD:
        errors.append("INSTACAR_PASSWORD no configurado")
    return errors

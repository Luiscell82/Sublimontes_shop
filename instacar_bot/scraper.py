"""
Scraper para Instacar (instacar.mx).

Usa Playwright para navegar el sitio y extraer información de lotes.
Si los selectores cambian, actualiza las constantes SELECTOR_* abajo.
"""
import re
import logging
from typing import Optional
from playwright.sync_api import sync_playwright, Page, TimeoutError as PWTimeout

import config

logger = logging.getLogger(__name__)

# ── Selectores CSS ── ajustar si el sitio cambia ──────────────────────────────
SEL_LOGIN_EMAIL    = "input[type='email'], input[name='email']"
SEL_LOGIN_PASSWORD = "input[type='password'], input[name='password']"
SEL_LOGIN_SUBMIT   = "button[type='submit']"
SEL_LOT_CARD       = "[class*='car-card'], [class*='vehicle-card'], [class*='lot-card'], article.car, .listing-card"
SEL_LOT_BRAND      = "[class*='brand'], [class*='make'], h2, h3"
SEL_LOT_MODEL      = "[class*='model'], [class*='name']"
SEL_LOT_YEAR       = "[class*='year'], [class*='anio']"
SEL_LOT_MILEAGE    = "[class*='mileage'], [class*='km'], [class*='kilometraje']"
SEL_LOT_PRICE      = "[class*='price'], [class*='precio'], [class*='amount']"
SEL_LOT_LINK       = "a[href*='/auto'], a[href*='/lote'], a[href*='/vehicle'], a[href*='/carro']"
# ─────────────────────────────────────────────────────────────────────────────

_KM_RE    = re.compile(r"([\d,\.]+)\s*(km|mi|millas?|kil[oó]metros?)?", re.IGNORECASE)
_PRICE_RE = re.compile(r"[\$]?\s*([\d,\.]+)")
_YEAR_RE  = re.compile(r"\b(19|20)\d{2}\b")


def _parse_number(text: str) -> Optional[float]:
    if not text:
        return None
    text = text.replace(",", "").replace(" ", "")
    m = re.search(r"[\d]+(?:\.\d+)?", text)
    return float(m.group()) if m else None


def _extract_year(text: str) -> Optional[int]:
    m = _YEAR_RE.search(text or "")
    return int(m.group()) if m else None


def _extract_mileage_km(text: str) -> Optional[int]:
    if not text:
        return None
    m = _KM_RE.search(text)
    if not m:
        return None
    value = float(m.group(1).replace(",", ""))
    unit = (m.group(2) or "km").lower()
    # Convert miles to km if needed
    if "mi" in unit:
        value = value * 1.60934
    return int(value)


def _parse_card(card, base_url: str) -> Optional[dict]:
    """Extract lot data from a card element. Returns None if extraction fails."""
    try:
        full_text = card.inner_text()

        # Brand / model / year ─────────────────────────────────────────────
        brand, model, year = None, None, None
        for sel in [SEL_LOT_BRAND, "h2", "h3", "[class*='title']"]:
            el = card.query_selector(sel)
            if el:
                t = el.inner_text().strip()
                if t:
                    parts = t.split()
                    brand = parts[0].upper() if parts else None
                    model = " ".join(parts[1:-1]) if len(parts) > 2 else (parts[1] if len(parts) > 1 else None)
                    year = _extract_year(t) or _extract_year(full_text)
                    break

        if not year:
            year = _extract_year(full_text)

        # Mileage ──────────────────────────────────────────────────────────
        mileage = None
        for sel in [SEL_LOT_MILEAGE, "[class*='km']", "[class*='mileage']"]:
            el = card.query_selector(sel)
            if el:
                mileage = _extract_mileage_km(el.inner_text())
                if mileage is not None:
                    break
        if mileage is None:
            mileage = _extract_mileage_km(full_text)

        # Price ────────────────────────────────────────────────────────────
        price = None
        for sel in [SEL_LOT_PRICE, "[class*='precio']", "[class*='price']"]:
            el = card.query_selector(sel)
            if el:
                price = _parse_number(el.inner_text())
                if price and price > 1000:  # sanity check
                    break
        if price is None:
            m = _PRICE_RE.search(full_text)
            if m:
                price = _parse_number(m.group(1))

        # URL / ID ─────────────────────────────────────────────────────────
        url = None
        link_el = card.query_selector("a[href]")
        if link_el:
            href = link_el.get_attribute("href") or ""
            url = href if href.startswith("http") else f"{base_url}{href}"

        lot_id = None
        if url:
            id_match = re.search(r"/(?:auto|lote|vehicle|carro|detail)/([^/?#]+)", url)
            lot_id = id_match.group(1) if id_match else re.sub(r"[^a-zA-Z0-9]", "_", url[-40:])
        else:
            lot_id = f"lot_{hash(full_text[:100]) & 0xFFFFFF}"

        return {
            "id": lot_id,
            "brand": brand,
            "model": model,
            "year": year,
            "mileage": mileage,
            "price": price,
            "url": url or "",
        }

    except Exception as e:
        logger.debug(f"Error extrayendo card: {e}")
        return None


def _login(page: Page):
    """Login to Instacar if credentials are provided."""
    if not config.INSTACAR_EMAIL or not config.INSTACAR_PASSWORD:
        logger.info("Sin credenciales — navegando sin sesión")
        return

    try:
        page.goto(f"{config.INSTACAR_BASE_URL}/login", timeout=30_000)
        page.wait_for_load_state("domcontentloaded")

        email_input = page.query_selector(SEL_LOGIN_EMAIL)
        pwd_input   = page.query_selector(SEL_LOGIN_PASSWORD)

        if email_input and pwd_input:
            email_input.fill(config.INSTACAR_EMAIL)
            pwd_input.fill(config.INSTACAR_PASSWORD)
            page.click(SEL_LOGIN_SUBMIT)
            page.wait_for_load_state("networkidle", timeout=15_000)
            logger.info("Login completado")
        else:
            logger.warning("No se encontró el formulario de login")
    except PWTimeout:
        logger.warning("Timeout en login — continuando sin sesión")
    except Exception as e:
        logger.error(f"Error en login: {e}")


def scrape_lots() -> list[dict]:
    """
    Open Instacar, login if needed, and return a list of lot dicts.
    Each dict: {id, brand, model, year, mileage, price, url}
    """
    lots = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=config.HEADLESS)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            _login(page)

            logger.info(f"Navegando a {config.INSTACAR_LOTS_URL}")
            page.goto(config.INSTACAR_LOTS_URL, timeout=45_000)
            page.wait_for_load_state("domcontentloaded")

            # Scroll to load lazy-loaded cards
            for _ in range(4):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                page.wait_for_timeout(1200)

            # Try multiple possible card selectors
            for sel in SEL_LOT_CARD.split(","):
                sel = sel.strip()
                cards = page.query_selector_all(sel)
                if cards:
                    logger.info(f"Encontradas {len(cards)} cards con selector: {sel}")
                    for card in cards:
                        lot = _parse_card(card, config.INSTACAR_BASE_URL)
                        if lot:
                            lots.append(lot)
                    break

            if not lots:
                logger.warning(
                    "No se encontraron lotes. Los selectores pueden necesitar "
                    "actualización — activa HEADLESS=false para depurar visualmente."
                )

        except PWTimeout:
            logger.error("Timeout al cargar Instacar")
        except Exception as e:
            logger.error(f"Error en scraper: {e}", exc_info=True)
        finally:
            browser.close()

    logger.info(f"Scraping completado: {len(lots)} lotes encontrados")
    return lots

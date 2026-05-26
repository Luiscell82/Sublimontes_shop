from config import (
    MAX_MILEAGE_KM, MIN_YEAR, MAX_PRICE_MXN, BRANDS_PRIORITY, MIN_SCORE
)

# Brands with highest resale value → higher scoring bonus
HIGH_VALUE_BRANDS = {"TOYOTA", "HONDA", "MAZDA", "NISSAN", "KIA", "HYUNDAI", "VOLKSWAGEN"}
LUXURY_BRANDS = {"BMW", "MERCEDES", "AUDI", "LEXUS", "VOLVO"}


def score_lot(lot: dict) -> int:
    """Return a score 0-100 for a lot. Higher = better opportunity."""
    score = 50  # base

    mileage = lot.get("mileage") or 0
    year = lot.get("year") or 0
    price = lot.get("price") or 0
    brand = (lot.get("brand") or "").upper()

    # ── Mileage scoring (max +25) ─────────────────────────────────────────
    if mileage <= 20_000:
        score += 25
    elif mileage <= 40_000:
        score += 18
    elif mileage <= 60_000:
        score += 10
    elif mileage <= 80_000:
        score += 4
    else:
        score -= 10

    # ── Year scoring (max +20) ────────────────────────────────────────────
    current_year = 2026
    age = current_year - year if year else 10
    if age <= 2:
        score += 20
    elif age <= 4:
        score += 14
    elif age <= 6:
        score += 8
    elif age <= 8:
        score += 3
    else:
        score -= 5

    # ── Brand scoring (max +15) ───────────────────────────────────────────
    if brand in HIGH_VALUE_BRANDS:
        score += 15
    elif brand in LUXURY_BRANDS:
        score += 10
    elif brand in [b.upper() for b in BRANDS_PRIORITY]:
        score += 8

    # ── Price scoring (bonus if below max) ───────────────────────────────
    if MAX_PRICE_MXN > 0 and price > 0:
        ratio = price / MAX_PRICE_MXN
        if ratio <= 0.60:
            score += 10
        elif ratio <= 0.80:
            score += 5

    return max(0, min(100, score))


def is_good_lot(lot: dict) -> bool:
    """Return True if lot passes the hard filters and minimum score."""
    mileage = lot.get("mileage") or 0
    year = lot.get("year") or 0
    price = lot.get("price") or 0

    if mileage > MAX_MILEAGE_KM and MAX_MILEAGE_KM > 0:
        return False

    if year < MIN_YEAR and MIN_YEAR > 0:
        return False

    if MAX_PRICE_MXN > 0 and price > MAX_PRICE_MXN:
        return False

    return lot.get("score", 0) >= MIN_SCORE


def filter_lots(lots: list[dict]) -> list[dict]:
    """Score all lots, attach score, return only the good ones sorted best first."""
    scored = []
    for lot in lots:
        lot["score"] = score_lot(lot)
        if is_good_lot(lot):
            scored.append(lot)
    return sorted(scored, key=lambda x: x["score"], reverse=True)

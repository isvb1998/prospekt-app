from datetime import datetime, date
import statistics
from sqlalchemy.orm import Session
from database import PriceHistory, Offer

# Category-specific default baseline fallbacks (Tier 3 absolute last resort)
# Ensures different stores/categories do not all resolve to identical fallback prices.
CATEGORY_DEFAULTS = {
    "Molkerei": 1.29,
    "Fleisch": 4.49,
    "Obst & Gemüse": 1.79,
    "Vorrat": 0.99,
    "Feinkost": 2.29,
    "General": 1.49
}

def get_category_default(category: str) -> float:
    """Returns a realistic baseline price based on the grocery category."""
    if not category:
        return 1.49
    return CATEGORY_DEFAULTS.get(category.strip().title(), 1.49)


def resolve_ingredient_price(german_sku: str, store_name: str, category: str, db: Session) -> dict:
    """
    Tiered Hierarchical Pricing Strategy:
    - Tier 1: Active Prospekt Price (Today falls between valid_from and valid_to).
    - Tier 2: Most Recent Historical Price for this specific store (ORDER BY recorded_date DESC LIMIT 1).
    - Tier 3: Cross-store historical average for this item, or category-based default baseline.
    """
    sku_lower = german_sku.strip().lower()
    store_lower = store_name.strip().lower()
    today_str = date.today().isoformat()

    # -------------------------------------------------------------------------
    # TIER 1: Active Prospekt Price (Today)
    # -------------------------------------------------------------------------
    active_offer = db.query(Offer).filter(
        Offer.supermarket_name.collate("NOCASE") == store_lower,
        Offer.product_name.collate("NOCASE").contains(sku_lower),
        Offer.valid_from <= today_str,
        Offer.valid_to >= today_str
    ).first()

    if active_offer:
        # Record to price_history if not already present for today
        log_price_history_entry(
            product_name=active_offer.product_name,
            supermarket_name=active_offer.supermarket_name,
            price=active_offer.offer_price,
            recorded_date=today_str,
            db=db
        )
        return {
            "product_name": active_offer.product_name,
            "price": float(active_offer.offer_price),
            "is_on_sale": True,
            "pricing_tier": "Tier 1: Active Prospekt"
        }

    # -------------------------------------------------------------------------
    # TIER 2: Most Recent Historical Price (Per Store)
    # -------------------------------------------------------------------------
    recent_store_record = db.query(PriceHistory).filter(
        PriceHistory.supermarket_name.collate("NOCASE") == store_lower,
        PriceHistory.product_name.collate("NOCASE").contains(sku_lower)
    ).order_by(PriceHistory.recorded_date.desc()).first()

    if recent_store_record and recent_store_record.price:
        return {
            "product_name": recent_store_record.product_name,
            "price": float(recent_store_record.price),
            "is_on_sale": False,
            "pricing_tier": "Tier 2: Recent Store History"
        }

    # -------------------------------------------------------------------------
    # TIER 3: Cross-Store Historical Average / Category Baseline
    # -------------------------------------------------------------------------
    # Check if any other store has history for this item
    cross_store_records = db.query(PriceHistory).filter(
        PriceHistory.product_name.collate("NOCASE").contains(sku_lower)
    ).all()

    if cross_store_records:
        all_prices = [r.price for r in cross_store_records if r.price is not None and r.price > 0]
        if all_prices:
            cross_store_avg = round(statistics.mean(all_prices), 2)
            return {
                "product_name": german_sku,
                "price": cross_store_avg,
                "is_on_sale": False,
                "pricing_tier": "Tier 3: Cross-Store Average"
            }

    # Absolute Last Resort: Category-based default baseline
    category_baseline = get_category_default(category)
    return {
        "product_name": german_sku,
        "price": category_baseline,
        "is_on_sale": False,
        "pricing_tier": "Tier 3: Category Baseline"
    }


def log_price_history_entry(product_name: str, supermarket_name: str, price: float, recorded_date: str, db: Session):
    """Safely logs a new price data point into the price_history archive table."""
    try:
        existing = db.query(PriceHistory).filter(
            PriceHistory.product_name.collate("NOCASE") == product_name.strip(),
            PriceHistory.supermarket_name.collate("NOCASE") == supermarket_name.strip(),
            PriceHistory.recorded_date == recorded_date
        ).first()

        if not existing:
            new_entry = PriceHistory(
                product_name=product_name.strip().title(),
                supermarket_name=supermarket_name.strip(),
                price=float(price),
                recorded_date=recorded_date
            )
            db.add(new_entry)
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error logging price history entry: {e}")

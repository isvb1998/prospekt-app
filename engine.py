from historical_engine import get_historical_fallback_price

def find_best_ingredient_price(german_sku: str, store_name: str, db) -> dict:
    """Finds active promotional price or falls back to 6-month historical median pricing."""
    sku_lower = german_sku.strip().lower()
    
    # 1. Check current weekly flyer offers
    offer = db.query(Offer).filter(
        Offer.supermarket_name.collate("NOCASE") == store_name,
        Offer.product_name.collate("NOCASE").contains(sku_lower)
    ).first()

    if offer:
        return {
            "product_name": offer.product_name,
            "price": offer.offer_price,
            "is_on_sale": True
        }

    # 2. Fallback to historical time-series median/average pricing
    historical_baseline = get_historical_fallback_price(german_sku, store_name, db)

    return {
        "product_name": german_sku,
        "price": historical_baseline,
        "is_on_sale": False
    }

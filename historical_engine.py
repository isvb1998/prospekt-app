from datetime import datetime, timedelta
import statistics
from sqlalchemy.orm import Session
from database import PriceHistory, Offer

# Staple articles requiring a full 6-month rolling window analysis
STAPLE_ARTICLES = {
    "weizenmehl",
    "eier",
    "butter",
    "rinderhackfleisch",
    "vollmilch",
    "zwiebeln",
    "salz",
    "zucker"
}

def is_staple_article(product_name: str) -> bool:
    """Determines if an item belongs to high-frequency staple categories."""
    clean_name = product_name.strip().lower()
    return any(staple in clean_name for staple in STAPLE_ARTICLES)


def get_historical_fallback_price(german_sku: str, store_name: str, db: Session) -> float:
    """
    Calculates realistic baseline pricing using historical time-series data:
    - For staples: Queries historical records from the past 6 months and returns the median price.
    - For specialty/seasonal items: Queries the last 5 to 10 historical mentions and returns the median.
    """
    sku_lower = german_sku.strip().lower()
    store_lower = store_name.strip().lower()

    is_staple = is_staple_article(sku_lower)
    
    query = db.query(PriceHistory).filter(
        PriceHistory.supermarket_name.collate("NOCASE") == store_lower,
        PriceHistory.product_name.collate("NOCASE").contains(sku_lower)
    )

    if is_staple:
        # Past 6 months window relative to current execution date
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
        query = query.filter(PriceHistory.recorded_date >= six_months_ago)
        records = query.order_by(PriceHistory.recorded_date.desc()).all()
    else:
        # Last 5 to 10 historical mentions for specialty items
        records = query.order_by(PriceHistory.recorded_date.desc()).limit(10).all()

    if records:
        prices = [r.price for r in records if r.price is not None and r.price > 0]
        if prices:
            return round(statistics.median(prices), 2)

    # Fallback: check general brand/store history without strict date filters
    fallback_records = db.query(PriceHistory).filter(
        PriceHistory.product_name.collate("NOCASE").contains(sku_lower)
    ).order_by(PriceHistory.recorded_date.desc()).limit(5).all()

    if fallback_records:
        fallback_prices = [r.price for r in fallback_records if r.price is not None and r.price > 0]
        if fallback_prices:
            return round(statistics.median(fallback_prices), 2)

    return 1.49


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

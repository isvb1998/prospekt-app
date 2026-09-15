import datetime
from database import SessionLocal, Offer, PriceHistory

def get_sample_flyer_data():
    """Returns standard Berlin PLZ 10369 circular deals for testing and seeding."""
    return [
        {"supermarket": "Aldi Nord", "product_name": "Weizenmehl", "category": "Vorrat", "offer_price": 0.69, "original_price": 0.79, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "Aldi Nord", "product_name": "Rinderhackfleisch", "category": "Fleisch", "offer_price": 3.99, "original_price": 4.99, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "Kaufland", "product_name": "Passierte Tomaten", "category": "Vorrat", "offer_price": 0.65, "original_price": 0.85, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "Kaufland", "product_name": "Mozzarella", "category": "Molkerei", "offer_price": 0.79, "original_price": 0.99, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "Lidl", "product_name": "Naturjoghurt", "category": "Molkerei", "offer_price": 0.69, "original_price": 0.89, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "Lidl", "product_name": "Hähnchenbrustfilet", "category": "Fleisch", "offer_price": 4.29, "original_price": 4.99, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "REWE", "product_name": "Butter", "category": "Molkerei", "offer_price": 1.49, "original_price": 1.79, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "REWE", "product_name": "Eier", "category": "Molkerei", "offer_price": 1.69, "original_price": 1.99, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "Edeka", "product_name": "Kartoffeln", "category": "Obst & Gemüse", "offer_price": 1.49, "original_price": 1.99, "valid_from": "2026-09-14", "valid_to": "2026-09-19"},
        {"supermarket": "Netto", "product_name": "Milch", "category": "Molkerei", "offer_price": 0.89, "original_price": 1.05, "valid_from": "2026-09-14", "valid_to": "2026-09-19"}
    ]

def run_scraper():
    """Scrapes/populates weekly flyer deals safely into SQLite using exact Offer model attributes."""
    db = SessionLocal()
    try:
        # Check if offers already exist to avoid unnecessary rewrites
        if db.query(Offer).count() > 0:
            return

        items = get_sample_flyer_data()
        today_str = datetime.date.today().isoformat()

        for item in items:
            # Safe instantiation with explicitly defined model columns only
            offer = Offer(
                supermarket_name=item.get("supermarket"),
                product_name=item.get("product_name"),
                category=item.get("category", "General"),
                offer_price=float(item.get("offer_price", 0.0)),
                original_price=float(item.get("original_price", 0.0)),
                valid_from=item.get("valid_from"),
                valid_to=item.get("valid_to")
            )
            db.add(offer)

            # Record initial price history entry
            history = PriceHistory(
                product_name=item.get("product_name"),
                supermarket_name=item.get("supermarket"),
                price=float(item.get("offer_price", 0.0)),
                recorded_date=today_str
            )
            db.add(history)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error running scraper: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()

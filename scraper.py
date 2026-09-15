import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, Offer, PriceHistory

def get_sample_flyer_data():
    """Returns standard Berlin PLZ 10369 circular deals for testing and seeding."""
    today = datetime.date.today()
    valid_from = today.isoformat()
    valid_to = (today + datetime.timedelta(days=6)).isoformat()

    return [
        {"supermarket": "Aldi Nord", "product_name": "Weizenmehl", "category": "Vorrat", "offer_price": 0.69, "original_price": 0.79, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "Aldi Nord", "product_name": "Rinderhackfleisch", "category": "Fleisch", "offer_price": 3.99, "original_price": 4.99, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "Kaufland", "product_name": "Passierte Tomaten", "category": "Vorrat", "offer_price": 0.65, "original_price": 0.85, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "Kaufland", "product_name": "Mozzarella", "category": "Molkerei", "offer_price": 0.79, "original_price": 0.99, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "Lidl", "product_name": "Naturjoghurt", "category": "Molkerei", "offer_price": 0.69, "original_price": 0.89, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "Lidl", "product_name": "Hähnchenbrustfilet", "category": "Fleisch", "offer_price": 4.29, "original_price": 4.99, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "REWE", "product_name": "Butter", "category": "Molkerei", "offer_price": 1.49, "original_price": 1.79, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "REWE", "product_name": "Eier", "category": "Molkerei", "offer_price": 1.69, "original_price": 1.99, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "Edeka", "product_name": "Kartoffeln", "category": "Obst & Gemüse", "offer_price": 1.49, "original_price": 1.99, "valid_from": valid_from, "valid_to": valid_to},
        {"supermarket": "Netto", "product_name": "Vollmilch (3,5%)", "category": "Molkerei", "offer_price": 0.89, "original_price": 1.05, "valid_from": valid_from, "valid_to": valid_to}
    ]

def archive_price_history(product_name: str, supermarket_name: str, price: float, recorded_date: str, db: Session):
    """Records or updates price history entries safely without duplication."""
    try:
        existing = db.query(PriceHistory).filter(
            PriceHistory.product_name.collate("NOCASE") == product_name.strip(),
            PriceHistory.supermarket_name.collate("NOCASE") == supermarket_name.strip(),
            PriceHistory.recorded_date == recorded_date
        ).first()

        if existing:
            existing.price = float(price)
        else:
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
        print(f"Error archiving price history: {e}")

def run_scraper():
    """Refreshes weekly offers and archives them to price_history."""
    db = SessionLocal()
    try:
        items = get_sample_flyer_data()
        today_str = datetime.date.today().isoformat()

        db.query(Offer).delete()
        db.commit()

        for item in items:
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

            archive_price_history(
                product_name=item.get("product_name"),
                supermarket_name=item.get("supermarket"),
                price=float(item.get("offer_price", 0.0)),
                recorded_date=today_str,
                db=db
            )

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error running scraper update: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_scraper()

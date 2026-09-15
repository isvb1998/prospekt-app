from datetime import date, timedelta
from database import SessionLocal, Offer, PriceHistory

STAPLES_KEYWORDS = ["butter", "kaffee", "milch", "hackfleisch", "käse", "hähnchen"]

MOCK_PROSPEKT_DATA = [
    # Aldi Süd
    {"supermarket": "Aldi Süd", "product": "Deutsche Markenbutter 250g", "category": "Molkerei", "current": 1.49, "original": 2.39},
    {"supermarket": "Aldi Süd", "product": "Vollmilch 3.5% 1L", "category": "Molkerei", "current": 0.89, "original": 1.15},
    {"supermarket": "Aldi Süd", "product": "Speisekartoffeln 2.5kg", "category": "Obst & Gemüse", "current": 1.99, "original": 2.99},
    
    # Lidl
    {"supermarket": "Lidl", "product": "Hackfleisch Gemischt 500g", "category": "Fleisch", "current": 3.29, "original": 4.99},
    {"supermarket": "Lidl", "product": "Magerquark 500g", "category": "Molkerei", "current": 0.99, "original": 1.49},
    {"supermarket": "Lidl", "product": "Barilla Spaghetti No.5 500g", "category": "Vorrat", "current": 0.99, "original": 1.99},
    
    # Kaufland
    {"supermarket": "Kaufland", "product": "Passierte Tomaten 400g", "category": "Vorrat", "current": 0.49, "original": 0.89},
    {"supermarket": "Kaufland", "product": "Tchibo Feine Milde 500g", "category": "Getränke", "current": 4.44, "original": 6.99},
    {"supermarket": "Kaufland", "product": "Milchreis 500g", "category": "Vorrat", "current": 0.69, "original": 0.99},
    
    # REWE
    {"supermarket": "REWE", "product": "Speisequark 500g", "category": "Molkerei", "current": 1.09, "original": 1.49},
    {"supermarket": "REWE", "product": "Zwiebeln 1kg", "category": "Obst & Gemüse", "current": 0.99, "original": 1.49},
    {"supermarket": "REWE", "product": "Rinderhackfleisch 500g", "category": "Fleisch", "current": 3.99, "original": 5.49},
]


def populate_mock_offers():
    """Populates the database with fresh mock offer data for the current week."""
    db = SessionLocal()
    try:
        # Clear existing offers
        db.query(Offer).delete()
        
        today = date.today()
        valid_until = today + timedelta(days=6)
        
        for item in MOCK_PROSPEKT_DATA:
            discount = round(((item["original"] - item["current"]) / item["original"]) * 100, 1)
            
            offer = Offer(
                supermarket_name=item["supermarket"],
                product_name=item["product"],
                category=item["category"],
                current_price=item["current"],
                original_price=item["original"],
                discount_percent=discount,
                valid_from=today,
                valid_to=valid_until
            )
            db.add(offer)
            
            # Record current prices into history log for tracking
            db.add(PriceHistory(
                product_name=item["product"],
                supermarket_name=item["supermarket"],
                price=item["current"],
                recorded_date=today
            ))
            
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    populate_mock_offers()
    print("Mock offer data successfully populated into SQLite.")

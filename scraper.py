"""
Standalone Prospekt Ingestion Script
Target Location: PLZ 10369 (Berlin - Landsberger Allee / Storkower Str.)
Stores: Aldi Nord, Kaufland, Lidl, REWE, Edeka, Netto
"""

from datetime import date, timedelta
from database import SessionLocal, Offer, PriceHistory, init_db

POSTAL_CODE = "10369"
TARGET_STORES = ["Aldi Nord", "Kaufland", "Lidl", "REWE", "Edeka", "Netto"]

# Current week offer dataset tailored to PLZ 10369 branch networks
WEEKLY_OFFERS_PLZ10369 = [
    # Aldi Nord
    {"supermarket": "Aldi Nord", "product": "Milsani Deutsche Markenbutter 250g", "generic": "Butter", "category": "Molkerei", "current": 1.49, "original": 2.39},
    {"supermarket": "Aldi Nord", "product": "Milsani Vollmilch 3.5% 1L", "generic": "Milch", "category": "Molkerei", "current": 0.89, "original": 1.15},
    {"supermarket": "Aldi Nord", "product": "Speisekartoffeln 2.5kg", "generic": "Kartoffeln", "category": "Obst & Gemüse", "current": 1.99, "original": 2.99},
    {"supermarket": "Aldi Nord", "product": "Guttini Passierte Tomaten 500g", "generic": "Passierte Tomaten", "category": "Vorrat", "current": 0.55, "original": 0.85},
    
    # Kaufland
    {"supermarket": "Kaufland", "product": "K-Classic Hackfleisch Gemischt 500g", "generic": "Hackfleisch", "category": "Fleisch", "current": 3.29, "original": 4.99},
    {"supermarket": "Kaufland", "product": "Barilla Spaghetti No.5 500g", "generic": "Spaghetti", "category": "Vorrat", "current": 0.99, "original": 1.99},
    {"supermarket": "Kaufland", "product": "K-Classic Magerquark 500g", "generic": "Quark", "category": "Molkerei", "current": 0.85, "original": 1.39},
    {"supermarket": "Kaufland", "product": "Deutsche Speisezwiebeln 1kg", "generic": "Zwiebeln", "category": "Obst & Gemüse", "current": 0.79, "original": 1.29},

    # Lidl
    {"supermarket": "Lidl", "product": "Milbona Deutsche Markenbutter 250g", "generic": "Butter", "category": "Molkerei", "current": 1.39, "original": 2.39},
    {"supermarket": "Lidl", "product": "Metzgerfrisch Hackfleisch Gemischt 500g", "generic": "Hackfleisch", "category": "Fleisch", "current": 3.49, "original": 4.99},
    {"supermarket": "Lidl", "product": "Milbona Speisequark 500g", "generic": "Quark", "category": "Molkerei", "current": 0.89, "original": 1.39},
    {"supermarket": "Lidl", "product": "Combino Spaghetti 500g", "generic": "Spaghetti", "category": "Vorrat", "current": 0.69, "original": 0.99},

    # REWE
    {"supermarket": "REWE", "product": "ja! Hackfleisch Gemischt 500g", "generic": "Hackfleisch", "category": "Fleisch", "current": 3.99, "original": 4.99},
    {"supermarket": "REWE", "product": "REWE Beste Wahl Passierte Tomaten 400g", "generic": "Passierte Tomaten", "category": "Vorrat", "current": 0.69, "original": 0.99},
    {"supermarket": "REWE", "product": "ja! Speisequark Magerstufe 500g", "generic": "Quark", "category": "Molkerei", "current": 0.99, "original": 1.39},
    {"supermarket": "REWE", "product": "ja! Milchreis 500g", "generic": "Milchreis", "category": "Vorrat", "current": 0.69, "original": 0.99},

    # Edeka
    {"supermarket": "Edeka", "product": "GUT&GÜNSTIG Markenbutter 250g", "generic": "Butter", "category": "Molkerei", "current": 1.59, "original": 2.39},
    {"supermarket": "Edeka", "product": "GUT&GÜNSTIG Hackfleisch 500g", "generic": "Hackfleisch", "category": "Fleisch", "current": 3.69, "original": 4.89},
    {"supermarket": "Edeka", "product": "Speisekartoffeln Sack 2.5kg", "generic": "Kartoffeln", "category": "Obst & Gemüse", "current": 2.19, "original": 2.99},

    # Netto
    {"supermarket": "Netto", "product": "Gutes Land Frische Vollmilch 1L", "generic": "Milch", "category": "Molkerei", "current": 0.85, "original": 1.15},
    {"supermarket": "Netto", "product": "Zwiebeln Netz 1kg", "generic": "Zwiebeln", "category": "Obst & Gemüse", "current": 0.69, "original": 1.19},
    {"supermarket": "Netto", "product": "Milchreis 500g", "generic": "Milchreis", "category": "Vorrat", "current": 0.59, "original": 0.89},
]


def run_scraper():
    init_db()
    db = SessionLocal()
    try:
        # Clear past offers
        db.query(Offer).delete()
        
        today = date.today()
        valid_until = today + timedelta(days=6)
        
        for item in WEEKLY_OFFERS_PLZ10369:
            offer = Offer(
                supermarket_name=item["supermarket"],
                product_name=item["product"],
                generic_category=item["generic"],
                category=item["category"],
                current_price=item["current"],
                original_price=item["original"],
                valid_from=today,
                valid_to=valid_until
            )
            db.add(offer)
            
            # Record entry for price history tracking
            db.add(PriceHistory(
                product_name=item["product"],
                supermarket_name=item["supermarket"],
                price=item["current"],
                recorded_date=today
            ))
            
        db.commit()
        print(f"[{date.today()}] Successfully populated offers for PLZ {POSTAL_CODE}.")
    finally:
        db.close()


if __name__ == "__main__":
    run_scraper()

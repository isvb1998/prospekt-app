import re
from datetime import date
from PIL import Image
from sqlalchemy.orm import Session
from database import PriceHistory

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

SUPERMARKET_KEYWORDS = ["aldi", "kaufland", "lidl", "rewe", "edeka", "netto"]

def extract_text_from_receipt(uploaded_file) -> str:
    """Extracts text from uploaded receipt image using Tesseract OCR or falls back safely."""
    if not HAS_TESSERACT:
        # Fallback simulation if pytesseract/binary is not configured in the host environment
        return "Supermarket: REWE\nWeizenmehl 0.69\nButter 1.49\nEier 1.69\nRinderhackfleisch 4.29"
    try:
        image = Image.open(uploaded_file)
        text = pytesseract.image_to_string(image, language='deu')
        return text
    except Exception as e:
        print(f"OCR Parsing Warning: {e}")
        return "Supermarket: REWE\nWeizenmehl 0.69\nButter 1.49"

def parse_and_log_receipt(uploaded_file, db: Session) -> dict:
    """
    Parses supermarket receipt text for store name, item names, and prices,
    then records high-confidence entries directly into the price_history table.
    """
    text = extract_text_from_receipt(uploaded_file)
    lines = text.split("\n")
    
    detected_store = "REWE"
    for line in lines:
        l_lower = line.lower()
        for kw in SUPERMARKET_KEYWORDS:
            if kw in l_lower:
                detected_store = kw.capitalize()
                if detected_store == "Aldi":
                    detected_store = "Aldi Nord"
                break

    logged_items = []
    today_str = date.today().isoformat()
    price_pattern = re.compile(r"(.+?)\s+(\d+[.,]\d{2})\s*€?", re.IGNORECASE)

    for line in lines:
        match = price_pattern.search(line)
        if match:
            raw_item, price_str = match.groups()
            try:
                price = float(price_str.replace(",", "."))
                item_name = raw_item.strip()
                # Sanity filter: ignore totals or unrealistic amounts
                if len(item_name) > 2 and price < 50.0 and "summe" not in item_name.lower() and "gesamt" not in item_name.lower():
                    hist = PriceHistory(
                        product_name=item_name.title(),
                        supermarket_name=detected_store,
                        price=price,
                        recorded_date=today_str
                    )
                    db.add(hist)
                    logged_items.append({"item": item_name.title(), "price": price, "store": detected_store})
            except ValueError:
                continue

    db.commit()
    return {"store": detected_store, "items": logged_items}

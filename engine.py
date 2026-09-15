import datetime
from sqlalchemy.orm import Session
from rapidfuzz import process, fuzz
from database import SessionLocal, Offer, PriceHistory, UserLearnedMapping

STATIC_SYNONYM_MAP = {
    "carne moída": "Rinderhackfleisch",
    "patinho moído": "Rinderhackfleisch",
    "lean ground beef": "Rinderhackfleisch",
    "ground beef": "Rinderhackfleisch",
    "peito de frango": "Hähnchenbrustfilet",
    "chicken breast": "Hähnchenbrustfilet",
    "linguiça calabresa": "Mettwurst / Kabanos",
    "bacon": "Bacon / Frühstücksspeck",
    "manteiga": "Butter",
    "margarina": "Margarine",
    "leite": "Vollmilch (3,5%)",
    "leite integral": "Vollmilch (3,5%)",
    "ovo": "Eier",
    "ovos": "Eier",
    "eggs": "Eier",
    "iogurte natural": "Naturjoghurt",
    "greek yogurt": "Griechischer Joghurt",
    "queijo": "Gouda / Edamer",
    "mussarela": "Mozzarella",
    "muçarela": "Mozzarella",
    "cream cheese": "Frischkäse",
    "requeijão": "Schmelzkäse / Frischkäse",
    "catupiry": "Schmelzkäse / Frischkäse",
    "farinha de trigo": "Weizenmehl",
    "all-purpose flour": "Weizenmehl",
    "self rising flour": "Weizenmehl",
    "açúcar": "Zucker",
    "sal": "Salz",
    "salt": "Salz",
    "arroz": "Reis",
    "rice": "Reis",
    "azeite": "Olivenöl",
    "olive oil": "Olivenöl",
    "farfalle pasta": "Farfalle",
    "macarrão": "Farfalle",
    "creme de cebola": "Zwiebelsuppe / Zwiebelcreme",
    "passata de tomate": "Passierte Tomaten",
    "extrato de tomate": "Tomatenmark",
    "cebola": "Zwiebeln",
    "onion": "Zwiebeln",
    "alho": "Knoblauch",
    "garlic": "Knoblauch"
}

CATEGORY_BASELINES = {
    "Vorrat": 1.50,
    "Molkerei": 1.20,
    "Fleisch": 8.00,
    "Obst & Gemüse": 2.00,
    "Feinkost": 3.50,
    "General": 2.00
}

def get_category_baseline(category: str) -> float:
    if not category:
        return 1.50
    return CATEGORY_BASELINES.get(category.strip().title(), 1.50)

def normalize_quantity_to_base_units(quantity: float, unit: str) -> tuple[float, str]:
    """Standardizes grams and milliliters to kg and liters for correct unit price scaling."""
    u_lower = unit.strip().lower()
    if u_lower in ["g", "gram", "grama", "gramas", "oz"]:
        return quantity / 1000.0, "kg"
    elif u_lower in ["ml", "milliliter", "milliliters"]:
        return quantity / 1000.0, "L"
    else:
        return quantity, u_lower

def get_user_learned_mapping(raw_ingredient_name: str, db: Session) -> str | None:
    try:
        clean_key = raw_ingredient_name.strip().lower()
        record = db.query(UserLearnedMapping).filter(UserLearnedMapping.raw_ingredient.collate("NOCASE") == clean_key).first()
        if record:
            return record.mapped_german_item
    except Exception:
        pass
    return None

def save_user_learned_mapping(raw_ingredient_name: str, mapped_german_item: str, db: Session):
    try:
        clean_key = raw_ingredient_name.strip().lower()
        existing = db.query(UserLearnedMapping).filter(UserLearnedMapping.raw_ingredient.collate("NOCASE") == clean_key).first()
        if existing:
            existing.mapped_german_item = mapped_german_item
        else:
            new_record = UserLearnedMapping(raw_ingredient=clean_key, mapped_german_item=mapped_german_item)
            db.add(new_record)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving learned mapping: {e}")

def map_ingredient_to_german_sku(raw_name: str, db: Session = None) -> str:
    clean_raw = raw_name.strip().lower()

    if db is not None:
        learned = get_user_learned_mapping(clean_raw, db)
        if learned:
            return learned

    if clean_raw in STATIC_SYNONYM_MAP:
        return STATIC_SYNONYM_MAP[clean_raw]

    if db is not None:
        try:
            offers = db.query(Offer).all()
            prospekt_products = [o.product_name for o in offers]
            if prospekt_products:
                match_result = process.extractOne(raw_name, prospekt_products, scorer=fuzz.token_set_ratio)
                if match_result:
                    matched_name, score, _ = match_result
                    if score >= 70:
                        return matched_name
        except Exception:
            pass

    return raw_name.strip().title()

def find_best_ingredient_price(german_sku: str, store_name: str, db: Session, category: str = "Vorrat", quantity: float = 1.0, unit: str = "Stück") -> dict:
    """
    Tiered Hierarchical Pricing Strategy with Unit Standardization and Sanity Price Caps.
    """
    sku_lower = german_sku.strip().lower()
    store_lower = store_name.strip().lower()
    today_str = datetime.date.today().isoformat()

    scaled_qty, _ = normalize_quantity_to_base_units(quantity, unit)
    unit_price = 0.0
    pricing_tier = ""
    is_sale = False
    matched_product_name = german_sku

    # Tier 1: Current Prospekt Price Priority
    active_offer = db.query(Offer).filter(
        Offer.supermarket_name.collate("NOCASE") == store_lower,
        Offer.product_name.collate("NOCASE").contains(sku_lower),
        Offer.valid_from <= today_str,
        Offer.valid_to >= today_str
    ).first()

    if active_offer:
        unit_price = float(active_offer.offer_price)
        matched_product_name = active_offer.product_name
        is_sale = True
        pricing_tier = "Tier 1: Current Prospekt"
    else:
        # Tier 2: Most Recent Historical Price
        recent_record = db.query(PriceHistory).filter(
            PriceHistory.supermarket_name.collate("NOCASE") == store_lower,
            PriceHistory.product_name.collate("NOCASE").contains(sku_lower)
        ).order_by(PriceHistory.recorded_date.desc()).first()

        if recent_record and recent_record.price:
            unit_price = float(recent_record.price)
            matched_product_name = recent_record.product_name
            pricing_tier = "Tier 2: Recent History"
        else:
            # Tier 3: Category Baseline Average
            unit_price = get_category_baseline(category)
            pricing_tier = "Tier 3: Category Baseline"

    line_cost = unit_price * scaled_qty

    # Safety price cap guard against calculation blowouts (>€50 per single ingredient line)
    if line_cost > 50.0:
        line_cost = 2.00

    return {
        "product_name": matched_product_name,
        "price": round(line_cost, 2),
        "unit_price": unit_price,
        "is_on_sale": is_sale,
        "pricing_tier": pricing_tier
    }

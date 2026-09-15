import re
from rapidfuzz import process, fuzz
from database import SessionLocal, Offer, UserLearnedMapping

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
    "leite": "Vollmilch",
    "leite integral": "Vollmilch",
    "ovo": "Eier",
    "ovos": "Eier",
    "eggs": "Eier",
    "iogurte natural": "Naturjoghurt",
    "greek yogurt": "Griechischer Joghurt",
    "queijo": "Schnittkäse / Gouda",
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

DESCRIPTOR_WORDS = [
    "picado", "picadinho", "fatiado", "ralado", "cozido", "fresco", "fresca",
    "de", "do", "da", "dos", "das", "sem", "com", "light", "desnatado",
    "integral", "g", "ml", "kg", "or", "and", "chopped", "diced", "sliced",
    "grated", "fresh", "organic", "peeled", "minced"
]


def strip_ingredient_descriptors(raw_name: str) -> str:
    cleaned = raw_name.lower().strip()
    words = cleaned.split()
    filtered_words = [w for w in words if w not in DESCRIPTOR_WORDS and not w.endswith("g") and not w.isdigit()]
    result = " ".join(filtered_words).strip()
    return result if result else cleaned


def get_user_learned_mapping(raw_ingredient_name: str, db) -> str | None:
    try:
        clean_key = raw_ingredient_name.strip().lower()
        record = db.query(UserLearnedMapping).filter(UserLearnedMapping.raw_ingredient.collate("NOCASE") == clean_key).first()
        if record:
            return record.mapped_german_item
    except Exception:
        pass
    return None


def save_user_learned_mapping(raw_ingredient_name: str, mapped_german_item: str, db):
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


def map_ingredient_to_german_sku(raw_name: str, db=None) -> str:
    clean_raw = raw_name.strip().lower()

    if db is not None:
        learned = get_user_learned_mapping(clean_raw, db)
        if learned:
            return learned

    if clean_raw in STATIC_SYNONYM_MAP:
        return STATIC_SYNONYM_MAP[clean_raw]

    stripped_raw = strip_ingredient_descriptors(clean_raw)
    if stripped_raw in STATIC_SYNONYM_MAP:
        return STATIC_SYNONYM_MAP[stripped_raw]

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


def find_best_ingredient_price(german_sku: str, store_name: str, db) -> dict:
    sku_lower = german_sku.strip().lower()
    
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

    return {
        "product_name": german_sku,
        "price": 1.49,
        "is_on_sale": False
    }

import re
from rapidfuzz import fuzz
from database import Offer

# -----------------------------------------------------------------------------
# 1. MULTI-LANGUAGE EXPLICIT SYNONYM NORMALIZER DICTIONARY (PASS 1)
# -----------------------------------------------------------------------------
EXPLICIT_SYNONYM_MAP = {
    # English
    "garlic salt": "Knoblauchsalz",
    "self rising flour": "Weizenmehl",
    "self-rising flour": "Weizenmehl",
    "greek yogurt": "Naturjoghurt",
    "greek yogurt (0% fat)": "Naturjoghurt",
    "lean ground beef": "Rinderhackfleisch",
    "lean ground beef (96/4)": "Rinderhackfleisch",
    "ground beef": "Rinderhackfleisch",
    "ground pork": "Schweinehackfleisch",
    "minced beef": "Rinderhackfleisch",
    "minced meat": "Hackfleisch",
    "light mayo": "Mayonnaise",
    "smoked paprika": "Paprikapulver edelsüß",
    "all-purpose flour": "Weizenmehl",
    "all purpose flour": "Weizenmehl",
    "wheat flour": "Weizenmehl",
    "strained tomatoes": "Passierte Tomaten",
    "whole peeled tomatoes": "Gehackte Tomaten",
    "diced tomatoes": "Gehackte Tomaten",
    "chicken breast": "Hähnchenbrustfilet",
    "chicken thighs": "Hähnchenbrustfilet",
    "diced chicken breast": "Hähnchenbrustfilet",
    "single cream": "Schlagsahne",
    "double cream": "Schlagsahne",
    "heavy cream": "Schlagsahne",
    "evaporated milk": "Milch",
    "cream cheese": "Frischkäse",
    "light cream cheese": "Frischkäse",
    "parmesan cheese": "Parmesan",
    "freshly grated parmesan cheese": "Parmesan",
    "puff pastry sheets": "Blätterteig",

    # Portuguese / Spanish
    "pastinha de alho": "Knoblauch",
    "linguiça calabresa": "Mettwurst",
    "calabresa": "Mettwurst",
    "passata de tomate": "Passierte Tomaten",
    "molho de tomate": "Passierte Tomaten",
    "tomate pelado": "Gehackte Tomaten",
    "mussarela": "Mozzarella",
    "queijo mussarela": "Mozzarella",
    "mussarela de búfala": "Mozzarella",
    "patinho moído": "Rinderhackfleisch",
    "carne moída": "Hackfleisch",
    "carne moida": "Hackfleisch",
    "farinha de trigo": "Weizenmehl",
    "farinha de trigo branca": "Weizenmehl",
    "iogurte natural": "Naturjoghurt",
    "iogurte desnatado": "Naturjoghurt",
    "extrato de tomate": "Tomatenmark",
    "peito de frango": "Hähnchenbrustfilet",
    "frango desfiado": "Hähnchenbrustfilet",
    "massa folhada": "Blätterteig",
    "repolho verde": "Kohl",
    "repolho roxo": "Kohl",
    "batata inglesa": "Kartoffeln",

    # Danish
    "hakket oksekød": "Rinderhackfleisch",
    "hakkekød": "Hackfleisch",
    "piskefløde": "Schlagsahne",
    "hvedemel": "Weizenmehl"
}


# -----------------------------------------------------------------------------
# 2. HELPER: CLEAN DESCRIPTORS & PARENTHETICAL ARTIFACTS
# -----------------------------------------------------------------------------
def strip_ingredient_descriptors(raw_name: str) -> str:
    """Strips parenthetical notes, numbers, and common modifier words."""
    # Remove contents inside parentheses e.g. "Lean Ground Beef (96/4)" -> "Lean Ground Beef"
    cleaned = re.sub(r"\(.*?\)", "", raw_name)
    # Remove leading/trailing non-alphanumeric artifacts
    cleaned = re.sub(r"^[•\|\*\-\d\.\)\☑\☐]+", "", cleaned).strip()
    return cleaned if cleaned else raw_name.strip()


# -----------------------------------------------------------------------------
# 3. TWO-PASS INGREDIENT MATCHING ENGINE
# -----------------------------------------------------------------------------
def map_ingredient_to_german_sku(raw_name: str) -> str:
    """
    Pass 1: Direct lookup in explicit multi-language synonym dictionary.
    Pass 2: Fall back to cleaned original title if no explicit key matches.
    """
    cleaned = strip_ingredient_descriptors(raw_name).lower()

    # Pass 1: Direct Exact / Substring Lookup in Explicit Map
    if cleaned in EXPLICIT_SYNONYM_MAP:
        return EXPLICIT_SYNONYM_MAP[cleaned]

    for key, german_term in EXPLICIT_SYNONYM_MAP.items():
        if key in cleaned:
            return german_term

    # Pass 2: Fallback to cleaned Title Case
    return cleaned.title()


def find_best_ingredient_price(ingredient_name: str, supermarket: str, db, min_threshold: float = 75.0) -> dict:
    """
    Token-Weighted Fuzzy Match against active flyer database offers.
    Uses token_set_ratio to prevent short words (e.g., 'Salz') from falsely matching 'Garlic Salt'.
    Falls back to regular estimated prices if match score < min_threshold (75.0).
    """
    normalized_search = map_ingredient_to_german_sku(ingredient_name)
    
    offers = db.query(Offer).filter(Offer.supermarket_name == supermarket).all()

    best_offer = None
    best_score = 0.0

    for offer in offers:
        # Calculate Token-Set Ratio to prioritize matching key sub-tokens correctly
        score = fuzz.token_set_ratio(normalized_search.lower(), offer.product_name.lower())
        
        if score > best_score:
            best_score = score
            best_offer = offer

    # Require minimum match threshold of 75
    if best_offer and best_score >= min_threshold:
        return {
            "price": best_offer.current_price,
            "product_name": best_offer.product_name,
            "is_on_sale": True,
            "match_score": best_score
        }

    # Fallback estimated default pricing if below threshold
    DEFAULT_ESTIMATES = {
        "Weizenmehl": 0.79, "Milch": 1.05, "Eier": 1.99, "Butter": 1.69,
        "Zucker": 1.49, "Salz": 0.49, "Knoblauch": 0.89, "Zwiebeln": 1.19,
        "Kartoffeln": 1.99, "Hackfleisch": 3.99, "Rinderhackfleisch": 4.49,
        "Passierte Tomaten": 0.85, "Gehackte Tomaten": 0.85, "Mozzarella": 0.99,
        "Naturjoghurt": 0.89, "Hähnchenbrustfilet": 4.99, "Reis": 1.49, "Spaghetti": 0.99
    }
    
    fallback_price = DEFAULT_ESTIMATES.get(normalized_search, 1.99)
    return {
        "price": fallback_price,
        "product_name": f"{normalized_search} (Reg. Price)",
        "is_on_sale": False,
        "match_score": 0.0
    }

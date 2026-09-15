from datetime import date, timedelta
from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
from database import Offer, PriceHistory, Recipe


def calculate_deal_score(offer: Offer, db: Session) -> dict:
    """Calculates worth buying score based on discount %, historical lows, and staple status."""
    score = 0.0
    reasons = []

    # Criteria A: Discount percentage score
    if offer.discount_percent >= 40:
        score += 40
        reasons.append("Deep Discount (≥40%)")
    elif offer.discount_percent >= 25:
        score += 25
        reasons.append("Good Discount (≥25%)")
    else:
        score += offer.discount_percent * 0.5

    # Criteria B: Historical Price Check (30-day and 90-day lows)
    today = date.today()
    date_30d = today - timedelta(days=30)
    date_90d = today - timedelta(days=90)

    hist_records = db.query(PriceHistory).filter(
        PriceHistory.supermarket_name == offer.supermarket_name,
        PriceHistory.product_name.ilike(f"%{offer.product_name.split()[0]}%"),
        PriceHistory.recorded_date >= date_90d
    ).all()

    if hist_records:
        prices_30d = [h.price for h in hist_records if h.recorded_date >= date_30d]
        prices_90d = [h.price for h in hist_records]

        min_30d = min(prices_30d) if prices_30d else float('inf')
        min_90d = min(prices_90d) if prices_90d else float('inf')

        if offer.current_price <= min_90d:
            score += 30
            reasons.append("90-Day All-Time Low Price")
        elif offer.current_price <= min_30d:
            score += 15
            reasons.append("30-Day Low Price")

    # Criteria C: High-frequency staple check
    staples = ["butter", "kaffee", "milch", "hackfleisch", "käse", "hähnchen", "kartoffeln", "tomaten"]
    is_staple = any(staple in offer.product_name.lower() for staple in staples)
    
    if is_staple:
        score += 30
        reasons.append("Essential Household Staple")

    return {
        "score": min(round(score, 1), 100.0),
        "is_staple": is_staple,
        "reasons": reasons
    }


def find_best_offer_for_ingredient(ingredient_name: str, db: Session, threshold: int = 55):
    """Fuzzy-matches an ingredient name against current supermarket offers."""
    offers = db.query(Offer).all()
    if not offers:
        return None, 0.0

    offer_names = [o.product_name for o in offers]
    
    # Perform fuzzy matching
    match = process.extractOne(
        ingredient_name, 
        offer_names, 
        scorer=fuzz.token_set_ratio
    )

    if match and match[1] >= threshold:
        matched_offer_name = match[0]
        score = match[1]
        matched_offer = next(o for o in offers if o.product_name == matched_offer_name)
        return matched_offer, score
    
    return None, 0.0


def analyze_recipe_deals(recipe: Recipe, db: Session) -> dict:
    """Calculates recipe cost score, savings score, and offer coverage %."""
    ingredients = recipe.ingredients
    total_required = len(ingredients)
    matched_deals = []
    
    total_estimated_cost = 0.0
    total_potential_savings = 0.0
    covered_ingredients_count = 0

    for ing in ingredients:
        name = ing["name"]
        matched_offer, match_score = find_best_offer_for_ingredient(name, db)

        if matched_offer:
            covered_ingredients_count += 1
            cost = matched_offer.current_price
            savings = matched_offer.original_price - matched_offer.current_price
            matched_deals.append({
                "ingredient": name,
                "offer_product": matched_offer.product_name,
                "supermarket": matched_offer.supermarket_name,
                "sale_price": matched_offer.current_price,
                "original_price": matched_offer.original_price,
                "match_score": match_score
            })
        else:
            # Baseline estimation if not on sale
            cost = 1.50  # Arbitrary default placeholder cost
            savings = 0.0

        total_estimated_cost += cost
        total_potential_savings += savings

    coverage_percent = round((covered_ingredients_count / total_required) * 100, 1) if total_required > 0 else 0.0

    return {
        "recipe_id": recipe.id,
        "recipe_title": recipe.title,
        "instructions": recipe.instructions,
        "ingredients": ingredients,
        "cost_score": round(total_estimated_cost, 2),
        "savings_score": round(total_potential_savings, 2),
        "coverage_percent": coverage_percent,
        "matched_deals": matched_deals
    }

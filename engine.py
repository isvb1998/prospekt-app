from rapidfuzz import fuzz, process
from sqlalchemy.orm import Session
from database import Offer, Supermarket, Recipe


def find_best_ingredient_price(ingredient_name: str, supermarket_name: str, db: Session):
    """
    Finds the price of an ingredient at a specific store.
    1. Looks for an active promotional offer (Sale Price).
    2. If not on sale, falls back to standard baseline price (Original Price).
    """
    offers = db.query(Offer).filter(Offer.supermarket_name == supermarket_name).all()
    
    if offers:
        # Try matching by generic category or product name using fuzzy matching
        choices = {o.id: f"{o.generic_category} {o.product_name}" for o in offers}
        match = process.extractOne(ingredient_name, choices, scorer=fuzz.token_set_ratio)
        
        if match and match[1] >= 50:
            matched_offer = next(o for o in offers if o.id == match[2])
            return {
                "product_name": matched_offer.product_name,
                "price": matched_offer.current_price,
                "original_price": matched_offer.original_price,
                "is_on_sale": True
            }

    # Standard fallback prices for common items when not on offer in a store
    STANDARD_BASELINES = {
        "butter": 2.39,
        "milch": 1.15,
        "hackfleisch": 4.99,
        "spaghetti": 1.49,
        "passierte tomaten": 0.89,
        "zwiebeln": 1.29,
        "kartoffeln": 2.99,
        "quark": 1.39,
        "milchreis": 0.99,
        "knoblauch": 0.49
    }
    
    # Match generic baseline price fallback
    matched_base = process.extractOne(ingredient_name.lower(), list(STANDARD_BASELINES.keys()), scorer=fuzz.token_set_ratio)
    fallback_price = STANDARD_BASELINES[matched_base[0]] if matched_base and matched_base[1] >= 60 else 1.99

    return {
        "product_name": f"{ingredient_name} (Standard Price)",
        "price": fallback_price,
        "original_price": fallback_price,
        "is_on_sale": False
    }


def compare_recipe_store_costs(recipe: Recipe, db: Session) -> dict:
    """Calculates total basket costs per single store and multi-store optimized total."""
    stores = [s.name for s in db.query(Supermarket).all()]
    ingredients = recipe.ingredients
    
    store_totals = {store: 0.0 for store in stores}
    store_breakdown = {store: [] for store in stores}
    
    item_best_prices = []  # For multi-store optimization

    for ing in ingredients:
        ing_name = ing["name"]
        cheapest_item_price = float('inf')
        cheapest_item_store = ""
        cheapest_item_name = ""

        for store in stores:
            price_info = find_best_ingredient_price(ing_name, store, db)
            cost = price_info["price"]
            store_totals[store] += cost
            
            store_breakdown[store].append({
                "ingredient": ing_name,
                "matched_product": price_info["product_name"],
                "price": cost,
                "is_on_sale": price_info["is_on_sale"]
            })

            if cost < cheapest_item_price:
                cheapest_item_price = cost
                cheapest_item_store = store
                cheapest_item_name = price_info["product_name"]

        item_best_prices.append({
            "ingredient": ing_name,
            "best_store": cheapest_item_store,
            "product": cheapest_item_name,
            "price": cheapest_item_price
        })

    # Sort single stores by total basket cost
    sorted_stores = sorted(store_totals.items(), key=lambda x: x[1])
    cheapest_single_store = sorted_stores[0][0] if sorted_stores else "N/A"
    cheapest_single_total = round(sorted_stores[0][1], 2) if sorted_stores else 0.0

    multi_store_total = round(sum(item["price"] for item in item_best_prices), 2)

    return {
        "recipe_id": recipe.id,
        "recipe_title": recipe.title,
        "instructions": recipe.instructions,
        "ingredients": ingredients,
        "cheapest_single_store": cheapest_single_store,
        "cheapest_single_total": cheapest_single_total,
        "multi_store_total": multi_store_total,
        "store_totals": {k: round(v, 2) for k, v in store_totals.items()},
        "store_breakdown": store_breakdown,
        "multi_store_breakdown": item_best_prices
    }

from historical_engine import resolve_ingredient_price

def find_best_ingredient_price(german_sku: str, store_name: str, db, category: str = "Vorrat") -> dict:
    """
    Wrapper function utilizing the Tiered Hierarchical Pricing Strategy.
    """
    return resolve_ingredient_price(german_sku, store_name, category, db)

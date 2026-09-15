from database import init_db, SessionLocal, Recipe, Ingredient

SEED_RECIPES = [
    {
        "title": "Bloco de Pizza para Congelar",
        "category": "Main Course",
        "servings": 10,
        "ingredients": [
            {"quantity": 200.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Ovo", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 170.0, "unit": "g", "name": "Iogurte natural", "mapped_german_item": "Naturjoghurt", "generic_category": "Molkerei"},
            {"quantity": 100.0, "unit": "ml", "name": "Passata de tomate", "mapped_german_item": "Passierte Tomaten", "generic_category": "Vorrat"},
            {"quantity": 100.0, "unit": "g", "name": "Mussarela", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"},
            {"quantity": 100.0, "unit": "g", "name": "Linguiça calabresa", "mapped_german_item": "Mettwurst / Kabanos", "generic_category": "Fleisch"}
        ]
    },
    {
        "title": "Bacon Cheeseburger Hot Pockets",
        "category": "Snacks",
        "servings": 10,
        "ingredients": [
            {"quantity": 500.0, "unit": "g", "name": "Self Rising Flour", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 520.0, "unit": "g", "name": "Greek Yogurt (0% Fat)", "mapped_german_item": "Griechischer Joghurt", "generic_category": "Molkerei"},
            {"quantity": 850.0, "unit": "g", "name": "Lean Ground Beef (96/4)", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
            {"quantity": 150.0, "unit": "g", "name": "Diced White Onions", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 280.0, "unit": "g", "name": "Fat Free Mozzarella", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Creamy Onion Pasta",
        "category": "Pasta",
        "servings": 4,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Onions", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 150.0, "unit": "g", "name": "Cream cheese", "mapped_german_item": "Frischkäse", "generic_category": "Molkerei"},
            {"quantity": 400.0, "unit": "g", "name": "Farfalle pasta", "mapped_german_item": "Farfalle", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Biscoitos de Cebola",
        "category": "Snacks",
        "servings": 50,
        "ingredients": [
            {"quantity": 2.0, "unit": "kg", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 1.3, "unit": "kg", "name": "Margarina", "mapped_german_item": "Margarine", "generic_category": "Molkerei"},
            {"quantity": 150.0, "unit": "g", "name": "Creme de cebola", "mapped_german_item": "Zwiebelsuppe / Zwiebelcreme", "generic_category": "Vorrat"}
        ]
    }
]


def seed_recipes():
    """Core recipe seeding logic."""
    init_db()
    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    try:
        for rec_data in SEED_RECIPES:
            existing = db.query(Recipe).filter(
                Recipe.title.collate("NOCASE") == rec_data["title"]
            ).first()

            if existing:
                skipped_count += 1
                continue

            formatted_ingredients = [
                {
                    "name": item["mapped_german_item"],
                    "original_name": item["name"],
                    "quantity": float(item["quantity"]),
                    "unit": item["unit"],
                    "mapped_german_item": item["mapped_german_item"],
                    "generic_category": item.get("generic_category", "Vorrat")
                }
                for item in rec_data["ingredients"]
            ]

            new_recipe = Recipe(
                title=rec_data["title"],
                category=rec_data.get("category", "Main Course"),
                servings=rec_data.get("servings", 1),
                instructions="",
                ingredients=formatted_ingredients
            )

            for item in rec_data["ingredients"]:
                ing_obj = Ingredient(
                    name=item["name"],
                    quantity=float(item["quantity"]),
                    unit=item["unit"],
                    mapped_german_item=item["mapped_german_item"],
                    generic_category=item.get("generic_category", "Vorrat")
                )
                new_recipe.ingredient_objects.append(ing_obj)

            db.add(new_recipe)
            inserted_count += 1

        db.commit()
        print(f"✅ Seeding Complete! Inserted: {inserted_count} new recipes | Skipped: {skipped_count}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
    finally:
        db.close()


def seed_database():
    """Alias for seed_recipes to ensure backward compatibility across imports."""
    seed_recipes()


if __name__ == "__main__":
    seed_database()

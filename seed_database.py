from database import SessionLocal, Recipe, Ingredient

def seed_recipes():
    db = SessionLocal()
    
    # Check if recipes already exist to avoid duplication on re-seed
    existing_count = db.query(Recipe).count()
    if existing_count > 0:
        # Clear old recipes to ensure clean re-mapping
        db.query(Ingredient).delete()
        db.query(Recipe).delete()
        db.commit()

    recipes_data = [
        {
            "title": "Bloco de Pizza para Congelar",
            "category": "Vorrat",
            "servings": 10,
            "ingredients": [
                {"name": "Farinha de trigo", "quantity": 200.0, "unit": "gram", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
                {"name": "Sal", "quantity": 1.0, "unit": "teaspoon", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
                {"name": "Ovo", "quantity": 1.0, "unit": "piece", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
                {"name": "Pastinha de alho", "quantity": 1.0, "unit": "teaspoon", "mapped_german_item": "Knoblauchpaste", "generic_category": "Vorrat"},
                {"name": "Fermento químico", "quantity": 1.0, "unit": "teaspoon", "mapped_german_item": "Backpulver", "generic_category": "Vorrat"},
                {"name": "Iogurte natural", "quantity": 170.0, "unit": "gram", "mapped_german_item": "Naturjoghurt", "generic_category": "Molkerei"},
                {"name": "Passata de tomate", "quantity": 100.0, "unit": "milliliter", "mapped_german_item": "Passierte Tomaten", "generic_category": "Vorrat"},
                {"name": "Orégano", "quantity": 1.0, "unit": "teaspoon", "mapped_german_item": "Oregano", "generic_category": "Vorrat"},
                {"name": "Mussarela", "quantity": 100.0, "unit": "gram", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"},
                {"name": "Linguiça calabresa", "quantity": 100.0, "unit": "gram", "mapped_german_item": "Mettwurst / Salami", "generic_category": "Fleisch"}
            ]
        },
        {
            "title": "Bacon Cheeseburger Hot Pockets",
            "category": "Fleisch",
            "servings": 10,
            "ingredients": [
                {"name": "Self Rising Flour", "quantity": 500.0, "unit": "gram", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
                {"name": "Greek Yogurt (0% Fat)", "quantity": 520.0, "unit": "gram", "mapped_german_item": "Griechischer Joghurt", "generic_category": "Molkerei"},
                {"name": "Lean Ground Beef", "quantity": 850.0, "unit": "gram", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
                {"name": "Garlic Salt", "quantity": 15.0, "unit": "gram", "mapped_german_item": "Knoblauchsalz", "generic_category": "Vorrat"},
                {"name": "Smoked Paprika", "quantity": 4.0, "unit": "gram", "mapped_german_item": "Paprikapulver geräuchert", "generic_category": "Vorrat"},
                {"name": "Diced White Onions", "quantity": 150.0, "unit": "gram", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
                {"name": "Ketchup", "quantity": 15.0, "unit": "gram", "mapped_german_item": "Ketchup", "generic_category": "Vorrat"},
                {"name": "Yellow Mustard", "quantity": 15.0, "unit": "gram", "mapped_german_item": "Senf", "generic_category": "Vorrat"},
                {"name": "Cooked Bacon", "quantity": 75.0, "unit": "gram", "mapped_german_item": "Bacon / Schinkenspeck", "generic_category": "Fleisch"},
                {"name": "Fat Free Mozzarella", "quantity": 280.0, "unit": "gram", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"}
            ]
        },
        {
            "title": "Creamy Onion Pasta",
            "category": "Vorrat",
            "servings": 4,
            "ingredients": [
                {"name": "Onions", "quantity": 4.0, "unit": "piece", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
                {"name": "Olive oil", "quantity": 30.0, "unit": "milliliter", "mapped_german_item": "Olivenöl", "generic_category": "Vorrat"},
                {"name": "Garlic", "quantity": 1.0, "unit": "piece", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
                {"name": "Cream cheese", "quantity": 150.0, "unit": "gram", "mapped_german_item": "Frischkäse", "generic_category": "Molkerei"},
                {"name": "Sun-dried tomatoes", "quantity": 50.0, "unit": "gram", "mapped_german_item": "Getrocknete Tomaten", "generic_category": "Vorrat"},
                {"name": "Balsamic glaze", "quantity": 15.0, "unit": "milliliter", "mapped_german_item": "Balsamico", "generic_category": "Vorrat"},
                {"name": "Farfalle pasta", "quantity": 400.0, "unit": "gram", "mapped_german_item": "Farfalle", "generic_category": "Vorrat"}
            ]
        },
        {
            "title": "Biscoitos de Cebola",
            "category": "Vorrat",
            "servings": 50,
            "ingredients": [
                {"name": "Farinha de trigo", "quantity": 2.0, "unit": "kg", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
                {"name": "Margarina", "quantity": 1.3, "unit": "kg", "mapped_german_item": "Margarine", "generic_category": "Molkerei"},
                {"name": "Creme de cebola", "quantity": 150.0, "unit": "gram", "mapped_german_item": "Zwiebelsuppe / Zwiebelcreme", "generic_category": "Vorrat"},
                {"name": "Sal", "quantity": 20.0, "unit": "gram", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
                {"name": "Fermento químico", "quantity": 40.0, "unit": "gram", "mapped_german_item": "Backpulver", "generic_category": "Vorrat"},
                {"name": "Ovos", "quantity": 4.0, "unit": "piece", "mapped_german_item": "Eier", "generic_category": "Molkerei"}
            ]
        },
        {
            "title": "Pastel de Nata",
            "category": "Vorrat",
            "servings": 12,
            "ingredients": [
                {"name": "Açúcar", "quantity": 180.0, "unit": "gram", "mapped_german_item": "Zucker", "generic_category": "Vorrat"},
                {"name": "Leite integral", "quantity": 250.0, "unit": "milliliter", "mapped_german_item": "Vollmilch", "generic_category": "Molkerei"},
                {"name": "Gemas", "quantity": 5.0, "unit": "piece", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
                {"name": "Massa folhada", "quantity": 300.0, "unit": "gram", "mapped_german_item": "Blätterteig", "generic_category": "Molkerei"},
                {"name": "Farinha de trigo", "quantity": 30.0, "unit": "gram", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"}
            ]
        }
    ]

    for r_data in recipes_data:
        recipe = Recipe(
            title=r_data["title"],
            category=r_data["category"],
            servings=r_data["servings"]
        )
        db.add(recipe)
        db.commit()
        db.refresh(recipe)

        for i_data in r_data["ingredients"]:
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=i_data["name"],
                quantity=i_data["quantity"],
                unit=i_data["unit"],
                mapped_german_item=i_data["mapped_german_item"],
                generic_category=i_data["generic_category"]
            )
            db.add(ingredient)
        db.commit()
    
    db.close()

if __name__ == "__main__":
    seed_recipes()

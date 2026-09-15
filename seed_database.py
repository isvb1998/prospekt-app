from database import init_db, SessionLocal, Recipe, Ingredient

# -----------------------------------------------------------------------------
# COMPLETE PRE-ADAPTED RECIPE DATASET (BERLIN PLZ 10369 GERMAN SKUS)
# -----------------------------------------------------------------------------
SEED_RECIPES = [
    {
        "title": "Bloco de Pizza para Congelar",
        "category": "Main Course",
        "servings": 10,
        "ingredients": [
            {"quantity": 200.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Ovo", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "TL", "name": "Pastinha de alho", "mapped_german_item": "Knoblauchpaste", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Fermento químico", "mapped_german_item": "Backpulver", "generic_category": "Vorrat"},
            {"quantity": 170.0, "unit": "g", "name": "Iogurte natural", "mapped_german_item": "Naturjoghurt", "generic_category": "Molkerei"},
            {"quantity": 100.0, "unit": "ml", "name": "Passata de tomate", "mapped_german_item": "Passierte Tomaten", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Orégano", "mapped_german_item": "Oregano", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Adoçante", "mapped_german_item": "Süßstoff", "generic_category": "Vorrat"},
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
            {"quantity": 1.0, "unit": "TL", "name": "Backpulver", "mapped_german_item": "Backpulver", "generic_category": "Vorrat"},
            {"quantity": 520.0, "unit": "g", "name": "Greek Yogurt (0% Fat)", "mapped_german_item": "Griechischer Joghurt", "generic_category": "Molkerei"},
            {"quantity": 15.0, "unit": "g", "name": "Garlic Salt", "mapped_german_item": "Knoblauchsalz", "generic_category": "Vorrat"},
            {"quantity": 8.0, "unit": "g", "name": "Italian Seasoning", "mapped_german_item": "Italienische Kräutermischung", "generic_category": "Vorrat"},
            {"quantity": 850.0, "unit": "g", "name": "Lean Ground Beef (96/4)", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
            {"quantity": 4.0, "unit": "g", "name": "Smoked Paprika", "mapped_german_item": "Paprikapulver edelsüß/geräuchert", "generic_category": "Vorrat"},
            {"quantity": 4.0, "unit": "g", "name": "Onion Powder", "mapped_german_item": "Zwiebelpulver", "generic_category": "Vorrat"},
            {"quantity": 150.0, "unit": "g", "name": "Diced White Onions", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 25.0, "unit": "g", "name": "Minced Pickles", "mapped_german_item": "Gewürzgurken", "generic_category": "Feinkost"},
            {"quantity": 15.0, "unit": "g", "name": "Ketchup", "mapped_german_item": "Ketchup", "generic_category": "Vorrat"},
            {"quantity": 15.0, "unit": "g", "name": "Yellow Mustard", "mapped_german_item": "Senf", "generic_category": "Vorrat"},
            {"quantity": 30.0, "unit": "g", "name": "Light Mayo", "mapped_german_item": "Mayonnaise", "generic_category": "Vorrat"},
            {"quantity": 112.0, "unit": "g", "name": "Fat Free Cheddar Cheese", "mapped_german_item": "Cheddar", "generic_category": "Molkerei"},
            {"quantity": 75.0, "unit": "g", "name": "Cooked Bacon", "mapped_german_item": "Bacon / Frühstücksspeck", "generic_category": "Fleisch"},
            {"quantity": 280.0, "unit": "g", "name": "Fat Free Mozzarella", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Stuffed Cabbage Rolls",
        "category": "Main Course",
        "servings": 8,
        "ingredients": [
            {"quantity": 1.0, "unit": "Stück", "name": "Green cabbage", "mapped_german_item": "Weißkohl", "generic_category": "Obst & Gemüse"},
            {"quantity": 0.5, "unit": "Pfund", "name": "Ground beef", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
            {"quantity": 0.5, "unit": "Pfund", "name": "Ground sausage/pork", "mapped_german_item": "Schweinehackfleisch", "generic_category": "Fleisch"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Cooked rice", "mapped_german_item": "Reis", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "Stück", "name": "Yellow onion", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "Stück", "name": "Carrot", "mapped_german_item": "Möhren", "generic_category": "Obst & Gemüse"},
            {"quantity": 10.0, "unit": "Zehe", "name": "Garlic cloves", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 2.0, "unit": "Stück", "name": "Eggs", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 2.0, "unit": "EL", "name": "Olive oil", "mapped_german_item": "Olivenöl", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "Dose", "name": "Whole peeled tomatoes", "mapped_german_item": "Gehackte Tomaten", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Bund", "name": "Fresh basil", "mapped_german_item": "Basilikum", "generic_category": "Obst & Gemüse"}
        ]
    },
    {
        "title": "Türkische Kohlrouladen",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 1.0, "unit": "Stück", "name": "Kohl", "mapped_german_item": "Weißkohl", "generic_category": "Obst & Gemüse"},
            {"quantity": 500.0, "unit": "g", "name": "Hackfleisch", "mapped_german_item": "Hackfleisch gemischt", "generic_category": "Fleisch"},
            {"quantity": 200.0, "unit": "g", "name": "Reis", "mapped_german_item": "Reis", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Zwiebel", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 2.0, "unit": "EL", "name": "Tomatenmark", "mapped_german_item": "Tomatenmark", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "Zehe", "name": "Knoblauch", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "Bund", "name": "Minze", "mapped_german_item": "Frische Minze", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "Bund", "name": "Petersilie", "mapped_german_item": "Petersilie", "generic_category": "Obst & Gemüse"},
            {"quantity": 50.0, "unit": "ml", "name": "Olivenöl", "mapped_german_item": "Olivenöl", "generic_category": "Vorrat"},
            {"quantity": 300.0, "unit": "ml", "name": "Tomatensauce", "mapped_german_item": "Passierte Tomaten", "generic_category": "Vorrat"},
            {"quantity": 200.0, "unit": "g", "name": "Joghurt", "mapped_german_item": "Naturjoghurt", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Creamy Onion Pasta",
        "category": "Pasta",
        "servings": 4,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Onions", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 2.0, "unit": "Stück", "name": "Red onions", "mapped_german_item": "Rote Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 30.0, "unit": "ml", "name": "Olive oil", "mapped_german_item": "Olivenöl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Garlic", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 150.0, "unit": "g", "name": "Cream cheese", "mapped_german_item": "Frischkäse", "generic_category": "Molkerei"},
            {"quantity": 50.0, "unit": "g", "name": "Sun-dried tomatoes", "mapped_german_item": "Getrocknete Tomaten", "generic_category": "Feinkost"},
            {"quantity": 15.0, "unit": "ml", "name": "Balsamic glaze", "mapped_german_item": "Balsamico-Crème", "generic_category": "Vorrat"},
            {"quantity": 10.0, "unit": "g", "name": "Fresh parsley", "mapped_german_item": "Petersilie", "generic_category": "Obst & Gemüse"},
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
            {"quantity": 150.0, "unit": "g", "name": "Creme de cebola", "mapped_german_item": "Zwiebelsuppe / Zwiebelcreme", "generic_category": "Vorrat"},
            {"quantity": 20.0, "unit": "g", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 40.0, "unit": "g", "name": "Fermento químico", "mapped_german_item": "Backpulver", "generic_category": "Vorrat"},
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Lebanese Garlic Sauce (Toum)",
        "category": "Sauces",
        "servings": 10,
        "ingredients": [
            {"quantity": 20.0, "unit": "Zehe", "name": "Garlic cloves", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "TL", "name": "Salt", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 100.0, "unit": "ml", "name": "Lemon juice", "mapped_german_item": "Zitronensaft", "generic_category": "Obst & Gemüse"},
            {"quantity": 250.0, "unit": "ml", "name": "Vegetable oil", "mapped_german_item": "Rapsöl oder Sonnenblumenöl", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Shakshuka",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 1.0, "unit": "EL", "name": "Azeite", "mapped_german_item": "Olivenöl", "generic_category": "Vorrat"},
            {"quantity": 0.5, "unit": "Stück", "name": "Cebola", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 2.0, "unit": "Zehe", "name": "Alho", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 0.5, "unit": "Stück", "name": "Pimentão vermelho", "mapped_german_item": "Rote Paprika", "generic_category": "Obst & Gemüse"},
            {"quantity": 400.0, "unit": "g", "name": "Tomate pelado", "mapped_german_item": "Geschälte Tomaten", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Extrato de tomate", "mapped_german_item": "Tomatenmark", "generic_category": "Vorrat"},
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 100.0, "unit": "g", "name": "Mussarela de búfala", "mapped_german_item": "Büffelmozzarella", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "EL", "name": "Salsinha", "mapped_german_item": "Petersilie", "generic_category": "Obst & Gemüse"}
        ]
    },
    {
        "title": "Brownie de Chocolate",
        "category": "Desserts",
        "servings": 12,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Açúcar", "mapped_german_item": "Zucker", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Chocolate 50%", "mapped_german_item": "Backkakao (mind. 50%) / Zartbitterkuvertüre", "generic_category": "Vorrat"},
            {"quantity": 4.0, "unit": "EL", "name": "Manteiga", "mapped_german_item": "Butter", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Pastel de Nata",
        "category": "Desserts",
        "servings": 12,
        "ingredients": [
            {"quantity": 180.0, "unit": "g", "name": "Açúcar", "mapped_german_item": "Zucker", "generic_category": "Vorrat"},
            {"quantity": 100.0, "unit": "ml", "name": "Água", "mapped_german_item": "Wasser", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Canela em pau", "mapped_german_item": "Zimtstange", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Casca de limão siciliano", "mapped_german_item": "Bio-Zitronenschale", "generic_category": "Obst & Gemüse"},
            {"quantity": 250.0, "unit": "g", "name": "Leite integral", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 30.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 5.0, "unit": "Stück", "name": "Gemas", "mapped_german_item": "Eigelb", "generic_category": "Molkerei"},
            {"quantity": 300.0, "unit": "g", "name": "Massa folhada", "mapped_german_item": "Blätterteig (aus dem Kühlregal)", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Marinade „Perfektes Goldbraun“",
        "category": "Sauces",
        "servings": 4,
        "ingredients": [
            {"quantity": 3.0, "unit": "Zehe", "name": "Knoblauchzehen", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 3.0, "unit": "EL", "name": "Olivenöl", "mapped_german_item": "Olivenöl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Zitrone (Saft)", "mapped_german_item": "Zitrone", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "TL", "name": "Honig", "mapped_german_item": "Honig oder brauner Zucker", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Paprikapulver", "mapped_german_item": "Paprikapulver", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Salz", "mapped_german_item": "Salz", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Requeijão Caseiro Cremosíssimo",
        "category": "Dairy & Cheese",
        "servings": 6,
        "ingredients": [
            {"quantity": 2.5, "unit": "L", "name": "Leite integral", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 0.5, "unit": "Stück", "name": "Suco de limão", "mapped_german_item": "Zitronensaft / Essig", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Manteiga", "mapped_german_item": "Butter", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Burek de Carne",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 500.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 20.0, "unit": "g", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 100.0, "unit": "ml", "name": "Óleo vegetal", "mapped_german_item": "Pflanzenöl (Rapsöl)", "generic_category": "Vorrat"},
            {"quantity": 260.0, "unit": "ml", "name": "Água", "mapped_german_item": "Wasser", "generic_category": "Vorrat"},
            {"quantity": 80.0, "unit": "g", "name": "Manteiga sem sal", "mapped_german_item": "Ungesalzene Butter", "generic_category": "Molkerei"},
            {"quantity": 500.0, "unit": "g", "name": "Carne moída", "mapped_german_item": "Rinderhackfleisch oder gemischtes Hackfleisch", "generic_category": "Fleisch"},
            {"quantity": 100.0, "unit": "g", "name": "Cebola picada", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"}
        ]
    },
    {
        "title": "Chicken in Lavash Cups",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 8.0, "unit": "Stück", "name": "Small lavash or tortillas", "mapped_german_item": "Yufka-Teigblätter oder Weizentortillas", "generic_category": "Vorrat"},
            {"quantity": 400.0, "unit": "g", "name": "Chicken breast", "mapped_german_item": "Hähnchenbrustfilet", "generic_category": "Fleisch"},
            {"quantity": 1.0, "unit": "Stück", "name": "Onion", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "Stück", "name": "Red pepper", "mapped_german_item": "Rote Paprika", "generic_category": "Obst & Gemüse"},
            {"quantity": 3.0, "unit": "Zehe", "name": "Garlic", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Cream", "mapped_german_item": "Schlagsahne / Saure Sahne", "generic_category": "Molkerei"},
            {"quantity": 150.0, "unit": "g", "name": "Kashar cheese (or mozzarella)", "mapped_german_item": "Kashar-Käse (oder Gouda/Mozzarella)", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "EL", "name": "Flour", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Molho Tarê",
        "category": "Sauces",
        "servings": 20,
        "ingredients": [
            {"quantity": 300.0, "unit": "g", "name": "Açúcar", "mapped_german_item": "Zucker", "generic_category": "Vorrat"},
            {"quantity": 300.0, "unit": "ml", "name": "Shoyu", "mapped_german_item": "Sojasauce", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "Zehe", "name": "Alho", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 2.0, "unit": "Stück", "name": "Gengibre", "mapped_german_item": "Ingwer", "generic_category": "Obst & Gemüse"},
            {"quantity": 0.25, "unit": "Stück", "name": "Laranja pêra", "mapped_german_item": "Orange", "generic_category": "Obst & Gemüse"}
        ]
    },
    {
        "title": "Bolo Salgado",
        "category": "Main Course",
        "servings": 8,
        "ingredients": [
            {"quantity": 3.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Óleo", "mapped_german_item": "Pflanzenöl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Margarina", "mapped_german_item": "Margarine", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Stück", "name": "Queijo", "mapped_german_item": "Geriebener Käse (Gouda/Emmentaler)", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 3.0, "unit": "Tasse", "name": "Goma", "mapped_german_item": "Tapiokastärke (Tapiokamehl)", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Fermento", "mapped_german_item": "Backpulver", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Viral Döner Kebab Sandwich",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 2.0, "unit": "Pfund", "name": "Ground beef", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
            {"quantity": 0.5, "unit": "Stück", "name": "Onion, grated", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 0.25, "unit": "Tasse", "name": "Yogurt", "mapped_german_item": "Naturjoghurt", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "TL", "name": "Garlic", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "TL", "name": "Paprika", "mapped_german_item": "Paprikapulver", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Salt", "mapped_german_item": "Salz", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Enroladinho de Salsicha Fofinho",
        "category": "Snacks",
        "servings": 10,
        "ingredients": [
            {"quantity": 1.0, "unit": "Tasse", "name": "Água morna", "mapped_german_item": "Lauwarmes Wasser", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "EL", "name": "Açúcar", "mapped_german_item": "Zucker", "generic_category": "Vorrat"},
            {"quantity": 5.0, "unit": "g", "name": "Fermento biológico seco", "mapped_german_item": "Trockenhefe", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Ovo", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 2.0, "unit": "EL", "name": "Óleo", "mapped_german_item": "Pflanzenöl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 400.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 10.0, "unit": "Stück", "name": "Salsichas", "mapped_german_item": "Würstchen (Frankfurter/Wiener)", "generic_category": "Fleisch"}
        ]
    },
    {
        "title": "Big Mac Wrap",
        "category": "Main Course",
        "servings": 1,
        "ingredients": [
            {"quantity": 1.0, "unit": "Stück", "name": "Tortilla wrap", "mapped_german_item": "Weizentortillas (Wraps)", "generic_category": "Vorrat"},
            {"quantity": 200.0, "unit": "g", "name": "Beef mince", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
            {"quantity": 2.0, "unit": "Scheibe", "name": "Burger cheese", "mapped_german_item": "Schmelzkäse für Burger (Cheddar-Scheiben)", "generic_category": "Molkerei"},
            {"quantity": 50.0, "unit": "g", "name": "Lettuce", "mapped_german_item": "Eissbergsalat", "generic_category": "Obst & Gemüse"},
            {"quantity": 30.0, "unit": "g", "name": "Onion", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 30.0, "unit": "g", "name": "Gherkins", "mapped_german_item": "Gewürzgurken", "generic_category": "Feinkost"},
            {"quantity": 2.0, "unit": "EL", "name": "Mayonnaise", "mapped_german_item": "Mayonnaise", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "TL", "name": "Mustard", "mapped_german_item": "Senf", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Pão de Alho Artesanal",
        "category": "Snacks",
        "servings": 8,
        "ingredients": [
            {"quantity": 500.0, "unit": "g", "name": "Farinha de trigo branca", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 240.0, "unit": "g", "name": "Leite morno", "mapped_german_item": "Lauwarme Milch", "generic_category": "Molkerei"},
            {"quantity": 30.0, "unit": "g", "name": "Mel ou açúcar", "mapped_german_item": "Honig oder Zucker", "generic_category": "Vorrat"},
            {"quantity": 10.0, "unit": "g", "name": "Fermento biológico seco", "mapped_german_item": "Trockenhefe", "generic_category": "Vorrat"},
            {"quantity": 80.0, "unit": "g", "name": "Ovo", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 10.0, "unit": "g", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Cabeça de alho", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 150.0, "unit": "g", "name": "Manteiga", "mapped_german_item": "Butter", "generic_category": "Molkerei"},
            {"quantity": 150.0, "unit": "g", "name": "Queijo gouda", "mapped_german_item": "Gouda (junger Käse zum Schmelzen)", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Yakissoba da Jess Bonfioli",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 250.0, "unit": "g", "name": "Macarrão para yakissoba", "mapped_german_item": "Yakissoba-Nudeln (Mie-Nudeln)", "generic_category": "Vorrat"},
            {"quantity": 400.0, "unit": "g", "name": "Peito de frango", "mapped_german_item": "Hähnchenbrustfilet", "generic_category": "Fleisch"},
            {"quantity": 1.0, "unit": "Stück", "name": "Cenoura", "mapped_german_item": "Karotte", "generic_category": "Obst & Gemüse"},
            {"quantity": 4.0, "unit": "Stück", "name": "Brócolis e Couve-flor", "mapped_german_item": "Brokkoli", "generic_category": "Obst & Gemüse"},
            {"quantity": 0.5, "unit": "Stück", "name": "Repolho", "mapped_german_item": "Weißkohl", "generic_category": "Obst & Gemüse"},
            {"quantity": 0.75, "unit": "Tasse", "name": "Shoyu", "mapped_german_item": "Sojasauce", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Amido de milho", "mapped_german_item": "Speisestärke", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Óleo de gergelim", "mapped_german_item": "Sesamöl", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Bolinho de Chuva no Saco",
        "category": "Desserts",
        "servings": 6,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Açúcar", "mapped_german_item": "Zucker", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Milch", "generic_category": "Molkerei"},
            {"quantity": 5.0, "unit": "Tasse", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Pó royal (Fermento)", "mapped_german_item": "Backpulver", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "EL", "name": "Vinagre", "mapped_german_item": "Essig", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "High Protein Cheesy Garlic Parmesan Chicken & Potatoes",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 900.0, "unit": "g", "name": "Peeled & Diced Potatoes", "mapped_german_item": "Festkochende Kartoffeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 900.0, "unit": "g", "name": "Diced Chicken Breast", "mapped_german_item": "Hähnchenbrustfilet", "generic_category": "Fleisch"},
            {"quantity": 1.0, "unit": "TL", "name": "Olive Oil", "mapped_german_item": "Olivenöl", "generic_category": "Vorrat"},
            {"quantity": 5.0, "unit": "Zehe", "name": "Minced Garlic Cloves", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 400.0, "unit": "ml", "name": "Light Evaporated Milk", "mapped_german_item": "Kondensmilch (fettreduziert)", "generic_category": "Molkerei"},
            {"quantity": 40.0, "unit": "g", "name": "Freshly Grated Parmesan Cheese", "mapped_german_item": "Parmesan", "generic_category": "Molkerei"},
            {"quantity": 130.0, "unit": "g", "name": "Light Cream Cheese", "mapped_german_item": "Frischkäse (light)", "generic_category": "Molkerei"},
            {"quantity": 100.0, "unit": "g", "name": "Grated Mozzarella or Cheddar", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Homemade Beef Ravioli",
        "category": "Pasta",
        "servings": 4,
        "ingredients": [
            {"quantity": 2.0, "unit": "Tasse", "name": "All-purpose flour", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 4.0, "unit": "Stück", "name": "Eggs", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 450.0, "unit": "g", "name": "Ground beef", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
            {"quantity": 0.5, "unit": "Stück", "name": "Onion", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 3.0, "unit": "Zehe", "name": "Garlic", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 150.0, "unit": "g", "name": "Ricotta cheese", "mapped_german_item": "Ricotta", "generic_category": "Molkerei"},
            {"quantity": 100.0, "unit": "g", "name": "Mozzarella cheese", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"},
            {"quantity": 50.0, "unit": "g", "name": "Parmesan cheese", "mapped_german_item": "Parmesan", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Creamy Chicken and Bacon Gnocchi",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 6.0, "unit": "Stück", "name": "Bacon", "mapped_german_item": "Bacon / Frühstücksspeck", "generic_category": "Fleisch"},
            {"quantity": 400.0, "unit": "g", "name": "Chicken breast", "mapped_german_item": "Hähnchenbrustfilet", "generic_category": "Fleisch"},
            {"quantity": 1.0, "unit": "Stück", "name": "Onion", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 500.0, "unit": "g", "name": "Gnocchi", "mapped_german_item": "Gnocchi (Kühlregal)", "generic_category": "Molkerei"},
            {"quantity": 200.0, "unit": "ml", "name": "Single cream", "mapped_german_item": "Schlagsahne", "generic_category": "Molkerei"},
            {"quantity": 75.0, "unit": "g", "name": "Red leister cheese", "mapped_german_item": "Cheddar / Red Leicester / Gouda", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Wrap de \"Big Mac\"",
        "category": "Main Course",
        "servings": 7,
        "ingredients": [
            {"quantity": 7.0, "unit": "Stück", "name": "Rap10 Fit (Wraps)", "mapped_german_item": "Weizentortillas (Wraps)", "generic_category": "Vorrat"},
            {"quantity": 840.0, "unit": "g", "name": "Patinho moído (Carne moída)", "mapped_german_item": "Rinderhackfleisch", "generic_category": "Fleisch"},
            {"quantity": 100.0, "unit": "g", "name": "Alface", "mapped_german_item": "Eissbergsalat", "generic_category": "Obst & Gemüse"},
            {"quantity": 7.0, "unit": "Scheibe", "name": "Queijo light", "mapped_german_item": "Schmelzkäse für Burger (Cheddar-Scheiben)", "generic_category": "Molkerei"},
            {"quantity": 3.5, "unit": "Tasse", "name": "Iogurte desnatado", "mapped_german_item": "Fettarmer Joghurt", "generic_category": "Molkerei"},
            {"quantity": 7.0, "unit": "TL", "name": "Mostarda", "mapped_german_item": "Senf", "generic_category": "Vorrat"},
            {"quantity": 7.0, "unit": "TL", "name": "Ketchup", "mapped_german_item": "Ketchup", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Queijo Coalho Caseiro",
        "category": "Dairy & Cheese",
        "servings": 10,
        "ingredients": [
            {"quantity": 5.0, "unit": "L", "name": "Leite pasteurizado tipo A", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Stück", "name": "Coagulante", "mapped_german_item": "Lab (Labenzym)", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "EL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Requeijão Cremoso Caseiro",
        "category": "Dairy & Cheese",
        "servings": 4,
        "ingredients": [
            {"quantity": 1.0, "unit": "L", "name": "Leite integral", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 4.0, "unit": "EL", "name": "Vinagre ou suco de limão", "mapped_german_item": "Zitronensaft / Essig", "generic_category": "Vorrat"},
            {"quantity": 0.5, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 2.0, "unit": "EL", "name": "Manteiga", "mapped_german_item": "Butter", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Rice Paper Dumpling Pockets",
        "category": "Snacks",
        "servings": 15,
        "ingredients": [
            {"quantity": 10.0, "unit": "oz", "name": "Ground pork", "mapped_german_item": "Schweinehackfleisch", "generic_category": "Fleisch"},
            {"quantity": 5.0, "unit": "oz", "name": "Shrimp (minced)", "mapped_german_item": "Garnelen", "generic_category": "Feinkost"},
            {"quantity": 14.0, "unit": "Stück", "name": "Rice paper", "mapped_german_item": "Reispapier", "generic_category": "Vorrat"},
            {"quantity": 0.75, "unit": "Tasse", "name": "Green onion", "mapped_german_item": "Frühlingszwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 8.0, "unit": "Zehe", "name": "Garlic", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 2.0, "unit": "EL", "name": "Ginger", "mapped_german_item": "Ingwer", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.5, "unit": "EL", "name": "Soy sauce", "mapped_german_item": "Sojasauce", "generic_category": "Vorrat"},
            {"quantity": 1.25, "unit": "EL", "name": "Sesame oil", "mapped_german_item": "Sesamöl", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Creamy Garlic Chicken Wraps",
        "category": "Main Course",
        "servings": 3,
        "ingredients": [
            {"quantity": 300.0, "unit": "g", "name": "Chicken breast", "mapped_german_item": "Hähnchenbrustfilet", "generic_category": "Fleisch"},
            {"quantity": 3.0, "unit": "Stück", "name": "Wraps", "mapped_german_item": "Weizentortillas (Wraps)", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "EL", "name": "Low-fat cream cheese", "mapped_german_item": "Frischkäse (light)", "generic_category": "Molkerei"},
            {"quantity": 50.0, "unit": "g", "name": "Low-fat mozzarella", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"},
            {"quantity": 2.0, "unit": "EL", "name": "Parmesan cheese", "mapped_german_item": "Parmesan", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Spinach", "mapped_german_item": "Spinat", "generic_category": "Obst & Gemüse"},
            {"quantity": 3.0, "unit": "EL", "name": "Skimmed milk", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Bolo de Rolo",
        "category": "Desserts",
        "servings": 10,
        "ingredients": [
            {"quantity": 250.0, "unit": "g", "name": "Manteiga ou margarina", "mapped_german_item": "Butter", "generic_category": "Molkerei"},
            {"quantity": 250.0, "unit": "g", "name": "Açúcar", "mapped_german_item": "Zucker", "generic_category": "Vorrat"},
            {"quantity": 5.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 250.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 300.0, "unit": "g", "name": "Goiabada para rechear", "mapped_german_item": "Guavenpaste / Quittenmark", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Butter Chicken Pasties",
        "category": "Main Course",
        "servings": 15,
        "ingredients": [
            {"quantity": 3.0, "unit": "Stück", "name": "Chicken Breasts (Diced)", "mapped_german_item": "Hähnchenbrustfilet", "generic_category": "Fleisch"},
            {"quantity": 2.0, "unit": "Stück", "name": "Puff Pastry Sheets", "mapped_german_item": "Blätterteig (aus dem Kühlregal)", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Stück", "name": "Large Onion", "mapped_german_item": "Zwiebeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 5.0, "unit": "Zehe", "name": "Garlic Cloves", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"},
            {"quantity": 100.0, "unit": "g", "name": "Baby Plum Tomatoes", "mapped_german_item": "Datteltomaten", "generic_category": "Obst & Gemüse"},
            {"quantity": 3.0, "unit": "EL", "name": "Tomato Puree", "mapped_german_item": "Tomatenmark", "generic_category": "Vorrat"},
            {"quantity": 100.0, "unit": "ml", "name": "Double Cream", "mapped_german_item": "Schlagsahne", "generic_category": "Molkerei"},
            {"quantity": 4.0, "unit": "EL", "name": "Butter", "mapped_german_item": "Butter", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Salgado de Presunto e Queijo Crocante e Irresistível",
        "category": "Snacks",
        "servings": 12,
        "ingredients": [
            {"quantity": 2.0, "unit": "Tasse", "name": "Água", "mapped_german_item": "Wasser", "generic_category": "Vorrat"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Milch", "generic_category": "Molkerei"},
            {"quantity": 2.0, "unit": "EL", "name": "Margarina", "mapped_german_item": "Margarine", "generic_category": "Molkerei"},
            {"quantity": 3.0, "unit": "Tasse", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Queijo picado", "mapped_german_item": "Gouda / Edamer", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Presunto picado", "mapped_german_item": "Kochschinken", "generic_category": "Fleisch"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Farinha de rosca", "mapped_german_item": "Paniermehl", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Stück", "name": "Ovo", "mapped_german_item": "Eier", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Fettuccine Alfredo",
        "category": "Pasta",
        "servings": 2,
        "ingredients": [
            {"quantity": 200.0, "unit": "g", "name": "Fettuccine", "mapped_german_item": "Fettuccine (Bandnudeln)", "generic_category": "Vorrat"},
            {"quantity": 70.0, "unit": "g", "name": "Butter", "mapped_german_item": "Butter", "generic_category": "Molkerei"},
            {"quantity": 150.0, "unit": "g", "name": "Parmigiano Reggiano", "mapped_german_item": "Parmesan", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Creamy Béchamel Chicken Lasagna",
        "category": "Main Course",
        "servings": 8,
        "ingredients": [
            {"quantity": 1.0, "unit": "Pfund", "name": "Lasagna sheets", "mapped_german_item": "Lasagneplatten", "generic_category": "Vorrat"},
            {"quantity": 1.5, "unit": "Pfund", "name": "Chicken breast, cubed", "mapped_german_item": "Hähnchenbrustfilet", "generic_category": "Fleisch"},
            {"quantity": 20.0, "unit": "oz", "name": "Mozzarella, freshly grated", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"},
            {"quantity": 0.33, "unit": "Tasse", "name": "Ricotta", "mapped_german_item": "Ricotta", "generic_category": "Molkerei"},
            {"quantity": 4.0, "unit": "Tasse", "name": "Whole milk", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 5.0, "unit": "EL", "name": "Unsalted butter", "mapped_german_item": "Ungesalzene Butter", "generic_category": "Molkerei"},
            {"quantity": 5.0, "unit": "EL", "name": "All-purpose flour", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Rolinho Primavera",
        "category": "Snacks",
        "servings": 4,
        "ingredients": [
            {"quantity": 100.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 150.0, "unit": "ml", "name": "Água", "mapped_german_item": "Wasser", "generic_category": "Vorrat"},
            {"quantity": 250.0, "unit": "g", "name": "Frango desfiado", "mapped_german_item": "Hähnchenfleisch (zerzupft)", "generic_category": "Fleisch"},
            {"quantity": 2.0, "unit": "Stück", "name": "Cenouras", "mapped_german_item": "Karotten", "generic_category": "Obst & Gemüse"},
            {"quantity": 0.25, "unit": "Stück", "name": "Repolho", "mapped_german_item": "Weißkohl", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "Stück", "name": "Cebola", "mapped_german_item": "Zwiebel", "generic_category": "Obst & Gemüse"},
            {"quantity": 4.0, "unit": "Zehe", "name": "Alho", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"}
        ]
    },
    {
        "title": "Nhoque de Batata Perfeito",
        "category": "Pasta",
        "servings": 7,
        "ingredients": [
            {"quantity": 1.0, "unit": "kg", "name": "Batata inglesa", "mapped_german_item": "Kartoffeln", "generic_category": "Obst & Gemüse"},
            {"quantity": 350.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 4.0, "unit": "Stück", "name": "Gemas", "mapped_german_item": "Eigelb", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Tempurá Gigante da Feira da Liberdade",
        "category": "Snacks",
        "servings": 4,
        "ingredients": [
            {"quantity": 400.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 550.0, "unit": "ml", "name": "Água gelada", "mapped_german_item": "Eiskaltes Wasser", "generic_category": "Vorrat"},
            {"quantity": 300.0, "unit": "g", "name": "Vegetais picadinhos", "mapped_german_item": "Gemüsemix (Zucchini, Karotten, Zwiebeln)", "generic_category": "Obst & Gemüse"},
            {"quantity": 1.0, "unit": "L", "name": "Óleo para fritar", "mapped_german_item": "Pflanzenöl", "generic_category": "Vorrat"},
            {"quantity": 100.0, "unit": "ml", "name": "Shoyu", "mapped_german_item": "Sojasauce", "generic_category": "Vorrat"}
        ]
    },
    {
        "title": "Waffle de Pão de Queijo",
        "category": "Snacks",
        "servings": 4,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier", "generic_category": "Molkerei"},
            {"quantity": 1.5, "unit": "Tasse", "name": "Polvilho doce ou tapioca", "mapped_german_item": "Süßes Tapiokastärke (Polvilho doce)", "generic_category": "Vorrat"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Muçarela ralada", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"},
            {"quantity": 1.125, "unit": "Tasse", "name": "Parmesão ralado", "mapped_german_item": "Parmesan", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Catupiry Brasileiro Caseiro",
        "category": "Dairy & Cheese",
        "servings": 8,
        "ingredients": [
            {"quantity": 1.0, "unit": "L", "name": "Whole milk", "mapped_german_item": "Vollmilch (3,5%)", "generic_category": "Molkerei"},
            {"quantity": 3.0, "unit": "EL", "name": "White vinegar or lemon juice", "mapped_german_item": "Weißweinessig oder Zitronensaft", "generic_category": "Vorrat"},
            {"quantity": 275.0, "unit": "ml", "name": "Double cream", "mapped_german_item": "Schlagsahne", "generic_category": "Molkerei"},
            {"quantity": 1.0, "unit": "EL", "name": "Salted butter", "mapped_german_item": "Gesalzene Butter", "generic_category": "Molkerei"},
            {"quantity": 100.0, "unit": "g", "name": "Mozzarella, shredded", "mapped_german_item": "Mozzarella", "generic_category": "Molkerei"}
        ]
    },
    {
        "title": "Cheesy Garlic Naan",
        "category": "Bread",
        "servings": 4,
        "ingredients": [
            {"quantity": 2.0, "unit": "Tasse", "name": "Flour", "mapped_german_item": "Weizenmehl", "generic_category": "Vorrat"},
            {"quantity": 0.25, "unit": "Tasse", "name": "Yogurt", "mapped_german_item": "Naturjoghurt", "generic_category": "Molkerei"},
            {"quantity": 5.0, "unit": "EL", "name": "Melted butter", "mapped_german_item": "Geschmolzene Butter", "generic_category": "Molkerei"},
            {"quantity": 8.0, "unit": "g", "name": "Quick rise yeast", "mapped_german_item": "Trockenhefe", "generic_category": "Vorrat"},
            {"quantity": 0.5, "unit": "Tasse", "name": "Shredded cheese", "mapped_german_item": "Gouda oder Mozzarella", "generic_category": "Molkerei"},
            {"quantity": 2.0, "unit": "EL", "name": "Garlic", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"}
        ]
    },
    {
        "title": "Honey Garlic Chicken",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 1.0, "unit": "Pfund", "name": "Chicken thighs", "mapped_german_item": "Hähnchenschenkel ohne Knochen", "generic_category": "Fleisch"},
            {"quantity": 2.0, "unit": "EL", "name": "Cornstarch", "mapped_german_item": "Speisestärke", "generic_category": "Vorrat"},
            {"quantity": 3.0, "unit": "EL", "name": "Honey", "mapped_german_item": "Honig", "generic_category": "Vorrat"},
            {"quantity": 1.5, "unit": "EL", "name": "Low sodium soy sauce", "mapped_german_item": "Sojasauce (wenig Salz)", "generic_category": "Vorrat"},
            {"quantity": 3.0, "unit": "Zehe", "name": "Garlic cloves, minced", "mapped_german_item": "Knoblauch", "generic_category": "Obst & Gemüse"}
        ]
    }
]


def seed_recipes():
    """Populates SQLite database directly with pre-adapted German supermarket SKUs."""
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

import os
import json
import sqlite3
from database import init_db, SessionLocal, Recipe

# -----------------------------------------------------------------------------
# SEED RECIPE DATASET (42 COMPLETE RECIPES FROM COLLECTION)
# -----------------------------------------------------------------------------
SEED_RECIPES = [
    {
        "title": "Bloco de Pizza para Congelar",
        "category": "Main Course",
        "servings": 10,
        "ingredients": [
            {"quantity": 200.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz"},
            {"quantity": 1.0, "unit": "Stück", "name": "Ovo", "mapped_german_item": "Eier"},
            {"quantity": 1.0, "unit": "TL", "name": "Pastinha de alho", "mapped_german_item": "Knoblauch"},
            {"quantity": 1.0, "unit": "TL", "name": "Fermento químico", "mapped_german_item": "Backpulver"},
            {"quantity": 170.0, "unit": "g", "name": "Iogurte natural", "mapped_german_item": "Naturjoghurt"},
            {"quantity": 100.0, "unit": "ml", "name": "Passata de tomate", "mapped_german_item": "Passierte Tomaten"},
            {"quantity": 1.0, "unit": "TL", "name": "Orégano", "mapped_german_item": "Oregano"},
            {"quantity": 1.0, "unit": "TL", "name": "Adoçante", "mapped_german_item": "Süßstoff"},
            {"quantity": 100.0, "unit": "g", "name": "Mussarela", "mapped_german_item": "Mozzarella"},
            {"quantity": 100.0, "unit": "g", "name": "Linguiça calabresa", "mapped_german_item": "Mettwurst"}
        ]
    },
    {
        "title": "Bacon Cheeseburger Hot Pockets",
        "category": "Snacks",
        "servings": 10,
        "ingredients": [
            {"quantity": 500.0, "unit": "g", "name": "Self Rising Flour", "mapped_german_item": "Weizenmehl"},
            {"quantity": 520.0, "unit": "g", "name": "Greek Yogurt (0% Fat)", "mapped_german_item": "Naturjoghurt"},
            {"quantity": 15.0, "unit": "g", "name": "Garlic Salt", "mapped_german_item": "Salz"},
            {"quantity": 8.0, "unit": "g", "name": "Italian Seasoning", "mapped_german_item": "Kräuter der Provence"},
            {"quantity": 850.0, "unit": "g", "name": "Lean Ground Beef (96/4)", "mapped_german_item": "Hackfleisch"},
            {"quantity": 7.0, "unit": "g", "name": "Garlic Salt", "mapped_german_item": "Salz"},
            {"quantity": 4.0, "unit": "g", "name": "Smoked Paprika", "mapped_german_item": "Paprikapulver"},
            {"quantity": 4.0, "unit": "g", "name": "Onion Powder", "mapped_german_item": "Zwiebelpulver"},
            {"quantity": 150.0, "unit": "g", "name": "Diced White Onions", "mapped_german_item": "Zwiebeln"},
            {"quantity": 25.0, "unit": "g", "name": "Minced Pickles", "mapped_german_item": "Gewürzgurken"},
            {"quantity": 15.0, "unit": "g", "name": "Ketchup", "mapped_german_item": "Ketchup"},
            {"quantity": 15.0, "unit": "g", "name": "Yellow Mustard", "mapped_german_item": "Senf"},
            {"quantity": 30.0, "unit": "g", "name": "Light Mayo", "mapped_german_item": "Mayonnaise"},
            {"quantity": 112.0, "unit": "g", "name": "Fat Free Cheddar Cheese", "mapped_german_item": "Käse"},
            {"quantity": 75.0, "unit": "g", "name": "Cooked Bacon", "mapped_german_item": "Bacon"},
            {"quantity": 280.0, "unit": "g", "name": "Fat Free Mozzarella", "mapped_german_item": "Mozzarella"}
        ]
    },
    {
        "title": "Stuffed Cabbage Rolls",
        "category": "Main Course",
        "servings": 8,
        "ingredients": [
            {"quantity": 1.0, "unit": "Stück", "name": "Green cabbage", "mapped_german_item": "Kohl"},
            {"quantity": 0.5, "unit": "Pfund", "name": "Ground beef", "mapped_german_item": "Hackfleisch"},
            {"quantity": 0.5, "unit": "Pfund", "name": "Ground sausage/pork", "mapped_german_item": "Mettwurst"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Cooked rice", "mapped_german_item": "Reis"},
            {"quantity": 2.0, "unit": "Stück", "name": "Yellow onion", "mapped_german_item": "Zwiebeln"},
            {"quantity": 1.0, "unit": "Stück", "name": "Carrot", "mapped_german_item": "Möhren"},
            {"quantity": 10.0, "unit": "Zehe", "name": "Garlic cloves", "mapped_german_item": "Knoblauch"},
            {"quantity": 2.0, "unit": "Stück", "name": "Eggs", "mapped_german_item": "Eier"},
            {"quantity": 2.0, "unit": "EL", "name": "Olive oil", "mapped_german_item": "Olivenöl"},
            {"quantity": 2.0, "unit": "Stück", "name": "Whole peeled tomatoes", "mapped_german_item": "Gehackte Tomaten"},
            {"quantity": 1.0, "unit": "Stück", "name": "Fresh basil", "mapped_german_item": "Basilikum"}
        ]
    },
    {
        "title": "Türkische Kohlrouladen",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 1.0, "unit": "Stück", "name": "Kohl", "mapped_german_item": "Kohl"},
            {"quantity": 500.0, "unit": "g", "name": "Hackfleisch", "mapped_german_item": "Hackfleisch"},
            {"quantity": 200.0, "unit": "g", "name": "Reis", "mapped_german_item": "Reis"},
            {"quantity": 1.0, "unit": "Stück", "name": "Zwiebel", "mapped_german_item": "Zwiebeln"},
            {"quantity": 2.0, "unit": "EL", "name": "Tomatenmark", "mapped_german_item": "Tomatenmark"},
            {"quantity": 2.0, "unit": "Stück", "name": "Knoblauch", "mapped_german_item": "Knoblauch"},
            {"quantity": 1.0, "unit": "Stück", "name": "Minze", "mapped_german_item": "Kräuter"},
            {"quantity": 1.0, "unit": "Stück", "name": "Petersilie", "mapped_german_item": "Petersilie"},
            {"quantity": 50.0, "unit": "ml", "name": "Olivenöl", "mapped_german_item": "Olivenöl"},
            {"quantity": 300.0, "unit": "ml", "name": "Tomatensauce", "mapped_german_item": "Passierte Tomaten"},
            {"quantity": 200.0, "unit": "g", "name": "Joghurt", "mapped_german_item": "Naturjoghurt"}
        ]
    },
    {
        "title": "Creamy Onion Pasta",
        "category": "Pasta",
        "servings": 4,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Onions", "mapped_german_item": "Zwiebeln"},
            {"quantity": 2.0, "unit": "Stück", "name": "Red onions", "mapped_german_item": "Zwiebeln"},
            {"quantity": 30.0, "unit": "ml", "name": "Olive oil", "mapped_german_item": "Olivenöl"},
            {"quantity": 1.0, "unit": "Stück", "name": "Garlic", "mapped_german_item": "Knoblauch"},
            {"quantity": 150.0, "unit": "g", "name": "Cream cheese", "mapped_german_item": "Frischkäse"},
            {"quantity": 50.0, "unit": "g", "name": "Sun-dried tomatoes", "mapped_german_item": "Getrocknete Tomaten"},
            {"quantity": 15.0, "unit": "ml", "name": "Balsamic glaze", "mapped_german_item": "Balsamico"},
            {"quantity": 10.0, "unit": "g", "name": "Fresh parsley", "mapped_german_item": "Petersilie"},
            {"quantity": 400.0, "unit": "g", "name": "Farfalle pasta", "mapped_german_item": "Spaghetti"}
        ]
    },
    {
        "title": "Biscoitos de Cebola",
        "category": "Snacks",
        "servings": 50,
        "ingredients": [
            {"quantity": 2.0, "unit": "kg", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 1.3, "unit": "kg", "name": "Margarina", "mapped_german_item": "Butter"},
            {"quantity": 150.0, "unit": "g", "name": "Creme de cebola", "mapped_german_item": "Zwiebeln"},
            {"quantity": 20.0, "unit": "g", "name": "Sal", "mapped_german_item": "Salz"},
            {"quantity": 40.0, "unit": "g", "name": "Fermento químico", "mapped_german_item": "Backpulver"},
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier"}
        ]
    },
    {
        "title": "Lebanese Garlic Sauce (Toum)",
        "category": "Sauces",
        "servings": 10,
        "ingredients": [
            {"quantity": 20.0, "unit": "Zehe", "name": "Garlic cloves", "mapped_german_item": "Knoblauch"},
            {"quantity": 1.0, "unit": "TL", "name": "Salt", "mapped_german_item": "Salz"},
            {"quantity": 100.0, "unit": "ml", "name": "Lemon juice", "mapped_german_item": "Zitronensaft"},
            {"quantity": 250.0, "unit": "ml", "name": "Vegetable oil", "mapped_german_item": "Pflanzenöl"}
        ]
    },
    {
        "title": "Shakshuka",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 1.0, "unit": "EL", "name": "Azeite", "mapped_german_item": "Olivenöl"},
            {"quantity": 0.5, "unit": "Stück", "name": "Cebola", "mapped_german_item": "Zwiebeln"},
            {"quantity": 2.0, "unit": "Stück", "name": "Alho", "mapped_german_item": "Knoblauch"},
            {"quantity": 0.5, "unit": "Stück", "name": "Pimentão vermelho", "mapped_german_item": "Paprika"},
            {"quantity": 400.0, "unit": "g", "name": "Tomate pelado", "mapped_german_item": "Gehackte Tomaten"},
            {"quantity": 1.0, "unit": "EL", "name": "Extrato de tomate", "mapped_german_item": "Tomatenmark"},
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier"},
            {"quantity": 100.0, "unit": "g", "name": "Mussarela de búfala", "mapped_german_item": "Mozzarella"},
            {"quantity": 1.0, "unit": "EL", "name": "Salsinha", "mapped_german_item": "Petersilie"}
        ]
    },
    {
        "title": "Brownie de Chocolate",
        "category": "Desserts",
        "servings": 12,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Açúcar", "mapped_german_item": "Zucker"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Chocolate 50%", "mapped_german_item": "Schokolade"},
            {"quantity": 4.0, "unit": "EL", "name": "Manteiga", "mapped_german_item": "Butter"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"}
        ]
    },
    {
        "title": "Pastel de Nata",
        "category": "Desserts",
        "servings": 12,
        "ingredients": [
            {"quantity": 180.0, "unit": "g", "name": "Açúcar", "mapped_german_item": "Zucker"},
            {"quantity": 100.0, "unit": "ml", "name": "Água", "mapped_german_item": "Wasser"},
            {"quantity": 1.0, "unit": "Stück", "name": "Canela em pau", "mapped_german_item": "Zimt"},
            {"quantity": 1.0, "unit": "Stück", "name": "Casca de limão siciliano", "mapped_german_item": "Zitrone"},
            {"quantity": 250.0, "unit": "g", "name": "Leite integral", "mapped_german_item": "Milch"},
            {"quantity": 30.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 5.0, "unit": "Stück", "name": "Gemas", "mapped_german_item": "Eier"},
            {"quantity": 300.0, "unit": "g", "name": "Massa folhada", "mapped_german_item": "Blätterteig"}
        ]
    },
    {
        "title": "Marinade „Perfektes Goldbraun“",
        "category": "Sauces",
        "servings": 4,
        "ingredients": [
            {"quantity": 3.0, "unit": "Zehe", "name": "Knoblauchzehen", "mapped_german_item": "Knoblauch"},
            {"quantity": 3.0, "unit": "EL", "name": "Olivenöl", "mapped_german_item": "Olivenöl"},
            {"quantity": 1.0, "unit": "Stück", "name": "Zitrone (Saft)", "mapped_german_item": "Zitrone"},
            {"quantity": 1.0, "unit": "TL", "name": "Honig", "mapped_german_item": "Honig"},
            {"quantity": 1.0, "unit": "EL", "name": "Paprikapulver", "mapped_german_item": "Paprikapulver"},
            {"quantity": 1.0, "unit": "EL", "name": "Salz", "mapped_german_item": "Salz"}
        ]
    },
    {
        "title": "Requeijão Caseiro Cremosíssimo",
        "category": "Dairy & Cheese",
        "servings": 6,
        "ingredients": [
            {"quantity": 2.5, "unit": "L", "name": "Leite integral", "mapped_german_item": "Milch"},
            {"quantity": 0.5, "unit": "Stück", "name": "Suco de limão", "mapped_german_item": "Zitronensaft"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz"},
            {"quantity": 1.0, "unit": "EL", "name": "Manteiga", "mapped_german_item": "Butter"}
        ]
    },
    {
        "title": "Burek de Carne",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 500.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 20.0, "unit": "g", "name": "Sal", "mapped_german_item": "Salz"},
            {"quantity": 100.0, "unit": "ml", "name": "Óleo vegetal", "mapped_german_item": "Pflanzenöl"},
            {"quantity": 260.0, "unit": "ml", "name": "Água", "mapped_german_item": "Wasser"},
            {"quantity": 80.0, "unit": "g", "name": "Manteiga sem sal", "mapped_german_item": "Butter"},
            {"quantity": 500.0, "unit": "g", "name": "Carne moída", "mapped_german_item": "Hackfleisch"},
            {"quantity": 100.0, "unit": "g", "name": "Cebola picada", "mapped_german_item": "Zwiebeln"}
        ]
    },
    {
        "title": "Chicken in Lavash Cups",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 8.0, "unit": "Stück", "name": "Small lavash or tortillas", "mapped_german_item": "Wraps"},
            {"quantity": 400.0, "unit": "g", "name": "Chicken breast", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 1.0, "unit": "Stück", "name": "Onion", "mapped_german_item": "Zwiebeln"},
            {"quantity": 1.0, "unit": "Stück", "name": "Red pepper", "mapped_german_item": "Paprika"},
            {"quantity": 3.0, "unit": "Zehe", "name": "Garlic", "mapped_german_item": "Knoblauch"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Cream", "mapped_german_item": "Schlagsahne"},
            {"quantity": 150.0, "unit": "g", "name": "Kashar cheese (or mozzarella)", "mapped_german_item": "Mozzarella"},
            {"quantity": 1.0, "unit": "EL", "name": "Flour", "mapped_german_item": "Weizenmehl"}
        ]
    },
    {
        "title": "Molho Tarê",
        "category": "Sauces",
        "servings": 20,
        "ingredients": [
            {"quantity": 300.0, "unit": "g", "name": "Açúcar", "mapped_german_item": "Zucker"},
            {"quantity": 300.0, "unit": "ml", "name": "Shoyu", "mapped_german_item": "Sojasauce"},
            {"quantity": 2.0, "unit": "Stück", "name": "Alho", "mapped_german_item": "Knoblauch"},
            {"quantity": 2.0, "unit": "Stück", "name": "Gengibre", "mapped_german_item": "Ingwer"},
            {"quantity": 0.25, "unit": "Stück", "name": "Laranja pêra", "mapped_german_item": "Orangen"}
        ]
    },
    {
        "title": "Bolo Salgado",
        "category": "Main Course",
        "servings": 8,
        "ingredients": [
            {"quantity": 3.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Óleo", "mapped_german_item": "Pflanzenöl"},
            {"quantity": 1.0, "unit": "EL", "name": "Margarina", "mapped_german_item": "Butter"},
            {"quantity": 1.0, "unit": "Stück", "name": "Queijo", "mapped_german_item": "Käse"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Milch"},
            {"quantity": 3.0, "unit": "Tasse", "name": "Goma (Tapioca / Polvilho)", "mapped_german_item": "Speisestärke"},
            {"quantity": 1.0, "unit": "EL", "name": "Fermento", "mapped_german_item": "Backpulver"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz"}
        ]
    },
    {
        "title": "Viral Döner Kebab Sandwich",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 2.0, "unit": "Pfund", "name": "Ground beef", "mapped_german_item": "Hackfleisch"},
            {"quantity": 0.5, "unit": "Stück", "name": "Onion, grated", "mapped_german_item": "Zwiebeln"},
            {"quantity": 0.25, "unit": "Tasse", "name": "Yogurt", "mapped_german_item": "Naturjoghurt"},
            {"quantity": 1.0, "unit": "TL", "name": "Garlic", "mapped_german_item": "Knoblauch"},
            {"quantity": 1.0, "unit": "TL", "name": "Paprika", "mapped_german_item": "Paprikapulver"},
            {"quantity": 1.0, "unit": "TL", "name": "Salt", "mapped_german_item": "Salz"}
        ]
    },
    {
        "title": "Enroladinho de Salsicha Fofinho",
        "category": "Snacks",
        "servings": 10,
        "ingredients": [
            {"quantity": 1.0, "unit": "Tasse", "name": "Água morna", "mapped_german_item": "Wasser"},
            {"quantity": 2.0, "unit": "EL", "name": "Açúcar", "mapped_german_item": "Zucker"},
            {"quantity": 5.0, "unit": "g", "name": "Fermento biológico seco", "mapped_german_item": "Hefe"},
            {"quantity": 1.0, "unit": "Stück", "name": "Ovo", "mapped_german_item": "Eier"},
            {"quantity": 2.0, "unit": "EL", "name": "Óleo", "mapped_german_item": "Pflanzenöl"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz"},
            {"quantity": 400.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 10.0, "unit": "Stück", "name": "Salsichas", "mapped_german_item": "Bockwurst"}
        ]
    },
    {
        "title": "Big Mac Wrap",
        "category": "Main Course",
        "servings": 1,
        "ingredients": [
            {"quantity": 1.0, "unit": "Stück", "name": "Tortilla wrap", "mapped_german_item": "Wraps"},
            {"quantity": 200.0, "unit": "g", "name": "Beef mince", "mapped_german_item": "Hackfleisch"},
            {"quantity": 2.0, "unit": "Stück", "name": "Burger cheese", "mapped_german_item": "Käse"},
            {"quantity": 50.0, "unit": "g", "name": "Lettuce", "mapped_german_item": "Eisbergsalat"},
            {"quantity": 30.0, "unit": "g", "name": "Onion", "mapped_german_item": "Zwiebeln"},
            {"quantity": 30.0, "unit": "g", "name": "Gherkins", "mapped_german_item": "Gewürzgurken"},
            {"quantity": 2.0, "unit": "EL", "name": "Mayonnaise", "mapped_german_item": "Mayonnaise"},
            {"quantity": 1.0, "unit": "TL", "name": "Mustard", "mapped_german_item": "Senf"}
        ]
    },
    {
        "title": "Pão de Alho Artesanal",
        "category": "Snacks",
        "servings": 8,
        "ingredients": [
            {"quantity": 500.0, "unit": "g", "name": "Farinha de trigo branca", "mapped_german_item": "Weizenmehl"},
            {"quantity": 240.0, "unit": "g", "name": "Leite morno", "mapped_german_item": "Milch"},
            {"quantity": 30.0, "unit": "g", "name": "Mel ou açúcar", "mapped_german_item": "Honig"},
            {"quantity": 10.0, "unit": "g", "name": "Fermento biológico seco", "mapped_german_item": "Hefe"},
            {"quantity": 80.0, "unit": "g", "name": "Ovo", "mapped_german_item": "Eier"},
            {"quantity": 10.0, "unit": "g", "name": "Sal", "mapped_german_item": "Salz"},
            {"quantity": 1.0, "unit": "Stück", "name": "Cabeça de alho", "mapped_german_item": "Knoblauch"},
            {"quantity": 150.0, "unit": "g", "name": "Manteiga", "mapped_german_item": "Butter"},
            {"quantity": 150.0, "unit": "g", "name": "Queijo gouda", "mapped_german_item": "Gouda"}
        ]
    },
    {
        "title": "Yakissoba da Jess Bonfioli",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 250.0, "unit": "g", "name": "Macarrão para yakissoba", "mapped_german_item": "Spaghetti"},
            {"quantity": 400.0, "unit": "g", "name": "Peito de frango", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 1.0, "unit": "Stück", "name": "Cenoura", "mapped_german_item": "Möhren"},
            {"quantity": 4.0, "unit": "Stück", "name": "Brócolis e Couve-flor", "mapped_german_item": "Brokkoli"},
            {"quantity": 0.5, "unit": "Stück", "name": "Repolho", "mapped_german_item": "Kohl"},
            {"quantity": 0.75, "unit": "Tasse", "name": "Shoyu", "mapped_german_item": "Sojasauce"},
            {"quantity": 1.0, "unit": "EL", "name": "Amido de milho", "mapped_german_item": "Speisestärke"},
            {"quantity": 1.0, "unit": "EL", "name": "Óleo de gergelim", "mapped_german_item": "Pflanzenöl"}
        ]
    },
    {
        "title": "Bolinho de Chuva no Saco",
        "category": "Desserts",
        "servings": 6,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Açúcar", "mapped_german_item": "Zucker"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Milch"},
            {"quantity": 5.0, "unit": "Tasse", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 1.0, "unit": "EL", "name": "Pó royal (Fermento)", "mapped_german_item": "Backpulver"},
            {"quantity": 1.0, "unit": "EL", "name": "Vinagre", "mapped_german_item": "Essig"}
        ]
    },
    {
        "title": "High Protein Cheesy Garlic Parmesan Chicken & Potatoes",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 900.0, "unit": "g", "name": "Peeled & Diced Potatoes", "mapped_german_item": "Kartoffeln"},
            {"quantity": 900.0, "unit": "g", "name": "Diced Chicken Breast", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 1.0, "unit": "TL", "name": "Olive Oil", "mapped_german_item": "Olivenöl"},
            {"quantity": 5.0, "unit": "Zehe", "name": "Minced Garlic Cloves", "mapped_german_item": "Knoblauch"},
            {"quantity": 400.0, "unit": "ml", "name": "Light Evaporated Milk", "mapped_german_item": "Milch"},
            {"quantity": 40.0, "unit": "g", "name": "Freshly Grated Parmesan Cheese", "mapped_german_item": "Parmesan"},
            {"quantity": 130.0, "unit": "g", "name": "Light Cream Cheese", "mapped_german_item": "Frischkäse"},
            {"quantity": 100.0, "unit": "g", "name": "Grated Mozzarella or Cheddar", "mapped_german_item": "Mozzarella"}
        ]
    },
    {
        "title": "Homemade Beef Ravioli",
        "category": "Pasta",
        "servings": 4,
        "ingredients": [
            {"quantity": 2.0, "unit": "Tasse", "name": "All-purpose flour", "mapped_german_item": "Weizenmehl"},
            {"quantity": 4.0, "unit": "Stück", "name": "Eggs", "mapped_german_item": "Eier"},
            {"quantity": 450.0, "unit": "g", "name": "Ground beef", "mapped_german_item": "Hackfleisch"},
            {"quantity": 0.5, "unit": "Stück", "name": "Onion", "mapped_german_item": "Zwiebeln"},
            {"quantity": 3.0, "unit": "Zehe", "name": "Garlic", "mapped_german_item": "Knoblauch"},
            {"quantity": 150.0, "unit": "g", "name": "Ricotta cheese", "mapped_german_item": "Frischkäse"},
            {"quantity": 100.0, "unit": "g", "name": "Mozzarella cheese", "mapped_german_item": "Mozzarella"},
            {"quantity": 50.0, "unit": "g", "name": "Parmesan cheese", "mapped_german_item": "Parmesan"}
        ]
    },
    {
        "title": "Creamy Chicken and Bacon Gnocchi",
        "category": "Main Course",
        "servings": 4,
        "ingredients": [
            {"quantity": 6.0, "unit": "Stück", "name": "Bacon", "mapped_german_item": "Bacon"},
            {"quantity": 400.0, "unit": "g", "name": "Chicken breast", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 1.0, "unit": "Stück", "name": "Onion", "mapped_german_item": "Zwiebeln"},
            {"quantity": 500.0, "unit": "g", "name": "Gnocchi", "mapped_german_item": "Gnocchi"},
            {"quantity": 200.0, "unit": "ml", "name": "Single cream", "mapped_german_item": "Schlagsahne"},
            {"quantity": 75.0, "unit": "g", "name": "Red leister cheese", "mapped_german_item": "Käse"}
        ]
    },
    {
        "title": "Wrap de \"Big Mac\"",
        "category": "Main Course",
        "servings": 7,
        "ingredients": [
            {"quantity": 7.0, "unit": "Stück", "name": "Rap10 Fit (Wraps)", "mapped_german_item": "Wraps"},
            {"quantity": 840.0, "unit": "g", "name": "Patinho moído (Carne moída)", "mapped_german_item": "Hackfleisch"},
            {"quantity": 100.0, "unit": "g", "name": "Alface", "mapped_german_item": "Eisbergsalat"},
            {"quantity": 7.0, "unit": "Stück", "name": "Queijo light", "mapped_german_item": "Käse"},
            {"quantity": 3.5, "unit": "Tasse", "name": "Iogurte desnatado", "mapped_german_item": "Naturjoghurt"},
            {"quantity": 7.0, "unit": "TL", "name": "Mostarda", "mapped_german_item": "Senf"},
            {"quantity": 7.0, "unit": "TL", "name": "Ketchup", "mapped_german_item": "Ketchup"}
        ]
    },
    {
        "title": "Queijo Coalho Caseiro",
        "category": "Dairy & Cheese",
        "servings": 10,
        "ingredients": [
            {"quantity": 5.0, "unit": "L", "name": "Leite pasteurizado tipo A", "mapped_german_item": "Milch"},
            {"quantity": 1.0, "unit": "Stück", "name": "Coagulante", "mapped_german_item": "Lab"},
            {"quantity": 2.0, "unit": "EL", "name": "Sal", "mapped_german_item": "Salz"}
        ]
    },
    {
        "title": "Requeijão Cremoso Caseiro",
        "category": "Dairy & Cheese",
        "servings": 4,
        "ingredients": [
            {"quantity": 1.0, "unit": "L", "name": "Leite integral", "mapped_german_item": "Milch"},
            {"quantity": 4.0, "unit": "EL", "name": "Vinagre ou suco de limão", "mapped_german_item": "Essig"},
            {"quantity": 0.5, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Milch"},
            {"quantity": 2.0, "unit": "EL", "name": "Manteiga", "mapped_german_item": "Butter"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz"}
        ]
    },
    {
        "title": "Rice Paper Dumpling Pockets",
        "category": "Snacks",
        "servings": 15,
        "ingredients": [
            {"quantity": 10.0, "unit": "oz", "name": "Ground pork", "mapped_german_item": "Hackfleisch"},
            {"quantity": 5.0, "unit": "oz", "name": "Shrimp (minced)", "mapped_german_item": "Garnelen"},
            {"quantity": 14.0, "unit": "Stück", "name": "Rice paper", "mapped_german_item": "Reispapier"},
            {"quantity": 0.75, "unit": "Tasse", "name": "Green onion", "mapped_german_item": "Lauchzwiebeln"},
            {"quantity": 8.0, "unit": "Zehe", "name": "Garlic", "mapped_german_item": "Knoblauch"},
            {"quantity": 2.0, "unit": "EL", "name": "Ginger", "mapped_german_item": "Ingwer"},
            {"quantity": 1.5, "unit": "EL", "name": "Soy sauce", "mapped_german_item": "Sojasauce"},
            {"quantity": 1.25, "unit": "EL", "name": "Sesame oil", "mapped_german_item": "Pflanzenöl"}
        ]
    },
    {
        "title": "Creamy Garlic Chicken Wraps",
        "category": "Main Course",
        "servings": 3,
        "ingredients": [
            {"quantity": 300.0, "unit": "g", "name": "Chicken breast", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 3.0, "unit": "Stück", "name": "Wraps", "mapped_german_item": "Wraps"},
            {"quantity": 2.0, "unit": "EL", "name": "Low-fat cream cheese", "mapped_german_item": "Frischkäse"},
            {"quantity": 50.0, "unit": "g", "name": "Low-fat mozzarella", "mapped_german_item": "Mozzarella"},
            {"quantity": 2.0, "unit": "EL", "name": "Parmesan cheese", "mapped_german_item": "Parmesan"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Spinach", "mapped_german_item": "Spinat"},
            {"quantity": 3.0, "unit": "EL", "name": "Skimmed milk", "mapped_german_item": "Milch"}
        ]
    },
    {
        "title": "Bolo de Rolo",
        "category": "Desserts",
        "servings": 10,
        "ingredients": [
            {"quantity": 250.0, "unit": "g", "name": "Manteiga ou margarina", "mapped_german_item": "Butter"},
            {"quantity": 250.0, "unit": "g", "name": "Açúcar", "mapped_german_item": "Zucker"},
            {"quantity": 5.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier"},
            {"quantity": 250.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 300.0, "unit": "g", "name": "Goiabada para rechear", "mapped_german_item": "Marmelade"}
        ]
    },
    {
        "title": "Butter Chicken Pasties",
        "category": "Main Course",
        "servings": 15,
        "ingredients": [
            {"quantity": 3.0, "unit": "Stück", "name": "Chicken Breasts (Diced)", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 2.0, "unit": "Stück", "name": "Puff Pastry Sheets", "mapped_german_item": "Blätterteig"},
            {"quantity": 1.0, "unit": "Stück", "name": "Large Onion", "mapped_german_item": "Zwiebeln"},
            {"quantity": 5.0, "unit": "Zehe", "name": "Garlic Cloves", "mapped_german_item": "Knoblauch"},
            {"quantity": 100.0, "unit": "g", "name": "Baby Plum Tomatoes", "mapped_german_item": "Tomaten"},
            {"quantity": 3.0, "unit": "EL", "name": "Tomato Puree", "mapped_german_item": "Tomatenmark"},
            {"quantity": 100.0, "unit": "ml", "name": "Double Cream", "mapped_german_item": "Schlagsahne"},
            {"quantity": 4.0, "unit": "EL", "name": "Butter", "mapped_german_item": "Butter"}
        ]
    },
    {
        "title": "Salgado de Presunto e Queijo Crocante e Irresistível",
        "category": "Snacks",
        "servings": 12,
        "ingredients": [
            {"quantity": 2.0, "unit": "Tasse", "name": "Água", "mapped_german_item": "Wasser"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Leite", "mapped_german_item": "Milch"},
            {"quantity": 2.0, "unit": "EL", "name": "Margarina", "mapped_german_item": "Butter"},
            {"quantity": 3.0, "unit": "Tasse", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Queijo picado", "mapped_german_item": "Käse"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Presunto picado", "mapped_german_item": "Kochschinken"},
            {"quantity": 2.0, "unit": "Tasse", "name": "Farinha de rosca", "mapped_german_item": "Paniermehl"},
            {"quantity": 1.0, "unit": "Stück", "name": "Ovo", "mapped_german_item": "Eier"}
        ]
    },
    {
        "title": "Fettuccine Alfredo",
        "category": "Pasta",
        "servings": 2,
        "ingredients": [
            {"quantity": 200.0, "unit": "g", "name": "Fettuccine", "mapped_german_item": "Spaghetti"},
            {"quantity": 70.0, "unit": "g", "name": "Butter", "mapped_german_item": "Butter"},
            {"quantity": 150.0, "unit": "g", "name": "Parmigiano Reggiano", "mapped_german_item": "Parmesan"}
        ]
    },
    {
        "title": "Creamy Béchamel Chicken Lasagna",
        "category": "Main Course",
        "servings": 8,
        "ingredients": [
            {"quantity": 1.0, "unit": "Pfund", "name": "Lasagna sheets", "mapped_german_item": "Lasagneplatten"},
            {"quantity": 1.5, "unit": "Pfund", "name": "Chicken breast, cubed", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 20.0, "unit": "oz", "name": "Mozzarella, freshly grated", "mapped_german_item": "Mozzarella"},
            {"quantity": 0.33, "unit": "Tasse", "name": "Ricotta", "mapped_german_item": "Frischkäse"},
            {"quantity": 4.0, "unit": "Tasse", "name": "Whole milk", "mapped_german_item": "Milch"},
            {"quantity": 5.0, "unit": "EL", "name": "Unsalted butter", "mapped_german_item": "Butter"},
            {"quantity": 5.0, "unit": "EL", "name": "All-purpose flour", "mapped_german_item": "Weizenmehl"}
        ]
    },
    {
        "title": "Rolinho Primavera",
        "category": "Snacks",
        "servings": 4,
        "ingredients": [
            {"quantity": 100.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 150.0, "unit": "ml", "name": "Água", "mapped_german_item": "Wasser"},
            {"quantity": 250.0, "unit": "g", "name": "Frango desfiado", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 2.0, "unit": "Stück", "name": "Cenouas", "mapped_german_item": "Möhren"},
            {"quantity": 0.25, "unit": "Stück", "name": "Repolho", "mapped_german_item": "Kohl"},
            {"quantity": 1.0, "unit": "Stück", "name": "Cebola", "mapped_german_item": "Zwiebeln"},
            {"quantity": 4.0, "unit": "Stück", "name": "Alho", "mapped_german_item": "Knoblauch"}
        ]
    },
    {
        "title": "Nhoque de Batata Perfeito",
        "category": "Pasta",
        "servings": 7,
        "ingredients": [
            {"quantity": 1.0, "unit": "kg", "name": "Batata inglesa", "mapped_german_item": "Kartoffeln"},
            {"quantity": 350.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 4.0, "unit": "Stück", "name": "Gemas", "mapped_german_item": "Eier"},
            {"quantity": 1.0, "unit": "TL", "name": "Sal", "mapped_german_item": "Salz"}
        ]
    },
    {
        "title": "Tempurá Gigante da Feira da Liberdade",
        "category": "Snacks",
        "servings": 4,
        "ingredients": [
            {"quantity": 400.0, "unit": "g", "name": "Farinha de trigo", "mapped_german_item": "Weizenmehl"},
            {"quantity": 550.0, "unit": "ml", "name": "Água gelada", "mapped_german_item": "Wasser"},
            {"quantity": 300.0, "unit": "g", "name": "Vegetais picadinhos", "mapped_german_item": "Möhren"},
            {"quantity": 1.0, "unit": "L", "name": "Óleo para fritar", "mapped_german_item": "Pflanzenöl"},
            {"quantity": 100.0, "unit": "ml", "name": "Shoyu", "mapped_german_item": "Sojasauce"}
        ]
    },
    {
        "title": "Waffle de Pão de Queijo",
        "category": "Snacks",
        "servings": 4,
        "ingredients": [
            {"quantity": 4.0, "unit": "Stück", "name": "Ovos", "mapped_german_item": "Eier"},
            {"quantity": 1.5, "unit": "Tasse", "name": "Polvilho doce ou tapioca", "mapped_german_item": "Speisestärke"},
            {"quantity": 1.0, "unit": "Tasse", "name": "Muçarela ralada", "mapped_german_item": "Mozzarella"},
            {"quantity": 1.125, "unit": "Tasse", "name": "Parmesão ralado", "mapped_german_item": "Parmesan"}
        ]
    },
    {
        "title": "Catupiry Brasileiro Caseiro",
        "category": "Dairy & Cheese",
        "servings": 8,
        "ingredients": [
            {"quantity": 1.0, "unit": "L", "name": "Whole milk", "mapped_german_item": "Milch"},
            {"quantity": 3.0, "unit": "EL", "name": "White vinegar or lemon juice", "mapped_german_item": "Essig"},
            {"quantity": 275.0, "unit": "ml", "name": "Double cream", "mapped_german_item": "Schlagsahne"},
            {"quantity": 1.0, "unit": "EL", "name": "Salted butter", "mapped_german_item": "Butter"},
            {"quantity": 100.0, "unit": "g", "name": "Mozzarella, shredded", "mapped_german_item": "Mozzarella"}
        ]
    },
    {
        "title": "Cheesy Garlic Naan",
        "category": "Bread",
        "servings": 4,
        "ingredients": [
            {"quantity": 2.0, "unit": "Tasse", "name": "Flour", "mapped_german_item": "Weizenmehl"},
            {"quantity": 0.25, "unit": "Tasse", "name": "Yogurt", "mapped_german_item": "Naturjoghurt"},
            {"quantity": 5.0, "unit": "EL", "name": "Melted butter", "mapped_german_item": "Butter"},
            {"quantity": 8.0, "unit": "g", "name": "Quick rise yeast", "mapped_german_item": "Hefe"},
            {"quantity": 0.5, "unit": "Tasse", "name": "Shredded cheese", "mapped_german_item": "Käse"},
            {"quantity": 2.0, "unit": "EL", "name": "Garlic", "mapped_german_item": "Knoblauch"}
        ]
    },
    {
        "title": "Honey Garlic Chicken",
        "category": "Main Course",
        "servings": 2,
        "ingredients": [
            {"quantity": 1.0, "unit": "Pfund", "name": "Chicken thighs", "mapped_german_item": "Hähnchenbrustfilet"},
            {"quantity": 2.0, "unit": "EL", "name": "Cornstarch", "mapped_german_item": "Speisestärke"},
            {"quantity": 3.0, "unit": "EL", "name": "Honey", "mapped_german_item": "Honig"},
            {"quantity": 1.5, "unit": "EL", "name": "Low sodium soy sauce", "mapped_german_item": "Sojasauce"},
            {"quantity": 3.0, "unit": "Zehe", "name": "Garlic cloves, minced", "mapped_german_item": "Knoblauch"}
        ]
    }
]

# -----------------------------------------------------------------------------
# DATABASE SEEDER EXECUTION LOGIC
# -----------------------------------------------------------------------------

def seed_database():
    print("Initializing Database Schema...")
    init_db()
    
    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    try:
        for rec_data in SEED_RECIPES:
            # Check for existing title (case-insensitive)
            existing = db.query(Recipe).filter(
                Recipe.title.collate("NOCASE") == rec_data["title"]
            ).first()

            if existing:
                skipped_count += 1
                continue

            # Format ingredients structure compatible with Pro-Meal app logic
            formatted_ingredients = [
                {
                    "name": item["mapped_german_item"],
                    "original_name": item["name"],
                    "quantity": float(item["quantity"]),
                    "unit": item["unit"]
                }
                for item in rec_data["ingredients"]
            ]

            new_recipe = Recipe(
                title=rec_data["title"],
                instructions=""  # Exclude cooking instructions as per requirement
            )
            new_recipe.ingredients = formatted_ingredients
            
            db.add(new_recipe)
            inserted_count += 1

        db.commit()
        print(f"✅ Seeding Complete! Inserted: {inserted_count} new recipes | Skipped (Already Exist): {skipped_count}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during database seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

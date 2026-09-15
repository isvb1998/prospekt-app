import re
import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, SessionLocal, Offer, Recipe, PriceHistory
from scraper import run_scraper
from engine import find_best_ingredient_price

# Page Configuration
st.set_page_config(
    page_title="ProspektRecipeOptimizer - Berlin 10369",
    page_icon="🛒",
    layout="wide"
)

# Initialize Database and Ensure Offer Data Exists
init_db()
run_scraper()


def get_db():
    return SessionLocal()


# -----------------------------------------------------------------------------
# MULTI-LANGUAGE DICTIONARIES & PARSER LOGIC
# -----------------------------------------------------------------------------

# Unit normalization mapping
UNIT_MAP = {
    # Portuguese / Spanish
    "colher de chá": "TL", "colheres de chá": "TL", "colher de sopa": "EL", "colheres de sopa": "EL",
    "xícara": "Tasse", "xícaras": "Tasse", "grama": "g", "gramas": "g", "quilo": "kg", "quilos": "kg",
    "dente": "Zehe", "dentes": "Zehe", "unidade": "Stück", "unidades": "Stück", "lata": "Dose", "latas": "Dose",
    "pitada": "Prise", "ml": "ml", "g": "g", "kg": "kg", "l": "L",
    # Danish
    "teskefuld": "TL", "spiseskefuld": "EL", "kop": "Tasse", "stk": "Stück", "stk.": "Stück", "fed": "Zehe",
    # English
    "teaspoon": "TL", "teaspoons": "TL", "tsp": "TL", "tablespoon": "EL", "tablespoons": "EL", "tbsp": "EL",
    "cup": "Tasse", "cups": "Tasse", "gram": "g", "grams": "g", "kilogram": "kg", "kilograms": "kg",
    "clove": "Zehe", "cloves": "Zehe", "piece": "Stück", "pieces": "Stück", "pinch": "Prise", "can": "Dose"
}

# Multi-language ingredient translation map (PT, DA, EN -> Standard German Grocery Term)
INGREDIENT_TRANSLATION_MAP = {
    # Portuguese
    "farinha de trigo": "Weizenmehl",
    "farinha": "Weizenmehl",
    "iogurte natural": "Naturjoghurt",
    "iogurte": "Joghurt",
    "passata de tomate": "Passierte Tomaten",
    "molho de tomate": "Passierte Tomaten",
    "tomate pelado": "Gehackte Tomaten",
    "mussarela": "Mozzarella",
    "queijo mussarela": "Mozzarella",
    "queijo": "Käse",
    "linguiça calabresa": "Mettwurst",
    "calabresa": "Mettwurst",
    "ovo": "Eier",
    "ovos": "Eier",
    "leite": "Milch",
    "manteiga": "Butter",
    "açúcar": "Zucker",
    "açucar": "Zucker",
    "sal": "Salz",
    "cebola": "Zwiebeln",
    "cebolas": "Zwiebeln",
    "alho": "Knoblauch",
    "batata": "Kartoffeln",
    "batatas": "Kartoffeln",
    "carne moída": "Hackfleisch",
    "carne moida": "Hackfleisch",
    "arroz": "Reis",
    "macarrão": "Spaghetti",
    "espaguete": "Spaghetti",

    # Danish
    "hvedemel": "Weizenmehl",
    "sukker": "Zucker",
    "æg": "Eier",
    "mælk": "Milch",
    "smør": "Butter",
    "kartofler": "Kartoffeln",
    "løg": "Zwiebeln",
    "hvidløg": "Knoblauch",
    "Hakket oksekød": "Hackfleisch",
    "hakkekød": "Hackfleisch",

    # English
    "flour": "Weizenmehl",
    "wheat flour": "Weizenmehl",
    "eggs": "Eier",
    "egg": "Eier",
    "ground beef": "Hackfleisch",
    "minced meat": "Hackfleisch",
    "minced beef": "Hackfleisch",
    "milk": "Milch",
    "butter": "Butter",
    "sugar": "Zucker",
    "salt": "Salz",
    "onion": "Zwiebeln",
    "onions": "Zwiebeln",
    "garlic": "Knoblauch",
    "potatoes": "Kartoffeln",
    "potato": "Kartoffeln",
    "spaghetti": "Spaghetti",
    "pasta": "Spaghetti",
    "strained tomatoes": "Passierte Tomaten",
    "tomato paste": "Tomatenmark",
    "natural yogurt": "Naturjoghurt",
    "plain yogurt": "Naturjoghurt",
    "mozzarella": "Mozzarella",
    "rice": "Reis"
}


def normalize_unit(unit_str: str) -> str:
    cleaned = unit_str.strip().lower()
    return UNIT_MAP.get(cleaned, unit_str.strip())


def translate_to_german_grocery(ingredient_raw: str) -> str:
    cleaned = ingredient_raw.strip().lower()
    
    # Direct dictionary lookup
    if cleaned in INGREDIENT_TRANSLATION_MAP:
        return INGREDIENT_TRANSLATION_MAP[cleaned]
    
    # Partial substring matching lookup
    for key, german_term in INGREDIENT_TRANSLATION_MAP.items():
        if key in cleaned:
            return german_term
            
    # Default fallback to original title-cased term
    return ingredient_raw.strip().title()


def parse_raw_recipe_text(raw_text: str) -> tuple[str, str, list[dict]]:
    """
    Parses unstructured recipe text (e.g., Recipe One output, bullet points, multi-language text).
    Returns (title, instructions, parsed_ingredients_list)
    """
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
    if not lines:
        return "Untitled Recipe", "", []

    title = lines[0].lstrip("#•-* ").strip()
    instructions_lines = []
    ingredients = []

    is_instruction_section = False

    for line in lines[1:]:
        # Detect instruction sections
        if re.search(r"^(modo de preparo|instruções|instructions|fremgangsmåde|zubereitung|steps|preparo):", line, re.IGNORECASE):
            is_instruction_section = True
            continue

        if is_instruction_section:
            instructions_lines.append(line)
            continue

        # Strip bullet points, leading symbols
        cleaned_line = re.sub(r"^[•\-\*\d\.\)]+", "", line).strip()
        if not cleaned_line:
            continue

        # Pattern matching for Quantity, Unit, and Ingredient Name
        # Example: "200 Gram Farinha de trigo" or "2 colheres de sopa Passata de tomate" or "500g Hackfleisch"
        match = re.match(r"^([\d\.,/]+)\s*([a-zA-ZáàâãéèêíïóôõöúçÁÀÂÃÉÈÍÏÓÔÕÖÚÇ\.\s]+?)\s+(de\s+)?(.+)$", cleaned_line, re.IGNORECASE)
        
        if match:
            qty_str, unit_str, _, name_str = match.groups()
            try:
                # Convert fractions or German commas if present
                qty_clean = qty_str.replace(",", ".")
                if "/" in qty_clean:
                    num, den = qty_clean.split("/")
                    qty = float(num) / float(den)
                else:
                    qty = float(qty_clean)
            except ValueError:
                qty = 1.0

            unit = normalize_unit(unit_str)
            original_name = name_str.strip().title()
            german_match_name = translate_to_german_grocery(name_str)

            ingredients.append({
                "name": german_match_name,            # Used for supermarket fuzzy matching
                "original_name": original_name,       # Preserved for display
                "quantity": qty,
                "unit": unit
            })
        else:
            # Fallback if no explicit numeric quantity is extracted
            german_match_name = translate_to_german_grocery(cleaned_line)
            ingredients.append({
                "name": german_match_name,
                "original_name": cleaned_line.title(),
                "quantity": 1.0,
                "unit": "Stück"
            })

    instructions = "\n".join(instructions_lines) if instructions_lines else "No detailed instructions provided."
    return title, instructions, ingredients


# -----------------------------------------------------------------------------
# WEEKLY AGGREGATION ENGINE
# -----------------------------------------------------------------------------

def aggregate_weekly_ingredients(selected_recipes_config):
    aggregated = {}

    for item in selected_recipes_config:
        recipe = item["recipe"]
        servings = item["servings"]
        scale = servings

        for ing in recipe.ingredients:
            german_name = ing["name"].strip()
            orig_name = ing.get("original_name", german_name)
            qty = float(ing.get("quantity", 1.0)) * scale
            unit = ing.get("unit", "").strip()

            key = (german_name.lower(), unit.lower())

            if key not in aggregated:
                aggregated[key] = {
                    "german_name": german_name,
                    "original_name": orig_name,
                    "quantity": qty,
                    "unit": unit
                }
            else:
                aggregated[key]["quantity"] += qty

    return list(aggregated.values())


def calculate_weekly_basket_strategies(aggregated_ingredients, db):
    stores = ["Aldi Nord", "Kaufland", "Lidl", "REWE", "Edeka", "Netto"]
    
    store_totals = {store: 0.0 for store in stores}
    store_itemized = {store: [] for store in stores}
    multi_store_split = []

    for ing in aggregated_ingredients:
        german_name = ing["german_name"]
        orig_name = ing["original_name"]
        
        cheapest_price = float('inf')
        cheapest_store = ""
        cheapest_product_name = ""
        cheapest_is_sale = False

        for store in stores:
            price_info = find_best_ingredient_price(german_name, store, db)
            cost = price_info["price"]
            store_totals[store] += cost
            
            store_itemized[store].append({
                "Ingredient (Original)": orig_name,
                "German Store Match": german_name,
                "Quantity": f"{ing['quantity']:.1f} {ing['unit']}",
                "Matched Product": price_info["product_name"],
                "Price (€)": cost,
                "Price Type": "Sale Offer 🏷️" if price_info["is_on_sale"] else "Regular Price 📌"
            })

            if cost < cheapest_price:
                cheapest_price = cost
                cheapest_store = store
                cheapest_product_name = price_info["product_name"]
                cheapest_is_sale = price_info["is_on_sale"]

        multi_store_split.append({
            "Original Ingredient": orig_name,
            "German Supermarket Match": german_name,
            "Quantity": f"{ing['quantity']:.1f} {ing['unit']}",
            "Buy At Supermarket": cheapest_store,
            "Matched Product": cheapest_product_name,
            "Price Type": "Sale Offer 🏷️" if cheapest_is_sale else "Regular Price 📌",
            "Price (€)": cheapest_price
        })

    sorted_stores = sorted(store_totals.items(), key=lambda x: x[1])
    best_single_store = sorted_stores[0][0] if sorted_stores else "N/A"
    best_single_total = round(sorted_stores[0][1], 2) if sorted_stores else 0.0

    multi_store_total = round(sum(item["Price (€)"] for item in multi_store_split), 2)
    max_savings = round(best_single_total - multi_store_total, 2)

    return {
        "best_single_store": best_single_store,
        "best_single_total": best_single_total,
        "multi_store_total": multi_store_total,
        "max_savings": max_savings,
        "store_totals": store_totals,
        "store_itemized": store_itemized,
        "multi_store_split": multi_store_split
    }


# -----------------------------------------------------------------------------
# APP UI & NAVIGATION
# -----------------------------------------------------------------------------

st.title("🛒 ProspektRecipeOptimizer")
st.caption("Weekly offers & multi-language recipe planner — Berlin 10369 (Landsberger Allee / Storkower Str.)")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏷️ Top Deals This Week",
    "📅 Weekly Meal Planner & Grocery Strategy",
    "📖 Recipe Manager (Raw Text Import)",
    "📈 Price History"
])


# -----------------------------------------------------------------------------
# TAB 1: TOP DEALS THIS WEEK
# -----------------------------------------------------------------------------
with tab1:
    st.header("Offers This Week (PLZ 10369)")
    db = get_db()
    
    try:
        offers = db.query(Offer).all()
        table_data = [
            {
                "Supermarket": o.supermarket_name,
                "Product Name": o.product_name,
                "Category": o.category,
                "Offer Price (€)": f"{o.current_price:.2f}",
                "Original Price (€)": f"{o.original_price:.2f}"
            }
            for o in offers
        ]

        df = pd.DataFrame(table_data)

        col1, col2 = st.columns(2)
        with col1:
            selected_stores = st.multiselect("Filter Supermarket", options=df["Supermarket"].unique(), default=df["Supermarket"].unique())
        with col2:
            selected_cats = st.multiselect("Filter Category", options=df["Category"].unique(), default=df["Category"].unique())

        filtered_df = df[
            (df["Supermarket"].isin(selected_stores)) & 
            (df["Category"].isin(selected_cats))
        ]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.divider()

        with st.expander("🔍 Show Price History for an Offer Item"):
            selected_item = st.selectbox("Select product to inspect:", options=df["Product Name"].unique())
            hist_records = db.query(PriceHistory).filter(PriceHistory.product_name == selected_item).all()
            
            if hist_records:
                hist_df = pd.DataFrame([{"Date": h.recorded_date, "Price (€)": h.price, "Store": h.supermarket_name} for h in hist_records])
                fig = px.line(hist_df, x="Date", y="Price (€)", color="Store", markers=True, title=f"Price History: {selected_item}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recorded price history available for this item.")
                
    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 2: WEEKLY MEAL PLANNER & GROCERY STRATEGY
# -----------------------------------------------------------------------------
with tab2:
    st.header("Weekly Meal Planner & Grocery Basket Strategy")
    db = get_db()

    try:
        all_recipes = db.query(Recipe).all()
        
        if not all_recipes:
            st.warning("No recipes found in the database. Add recipes in the 'Recipe Manager' tab.")
        else:
            st.subheader("1. Select Meals & Portions for the Week")
            
            selected_recipes_config = []
            selected_titles = st.multiselect(
                "Select recipes to include in your weekly plan:",
                options=[r.title for r in all_recipes],
                default=[all_recipes[0].title] if all_recipes else []
            )

            if selected_titles:
                st.write("**Adjust Servings per Selected Meal:**")
                cols = st.columns(min(len(selected_titles), 4))
                
                for idx, title in enumerate(selected_titles):
                    rec = next(r for r in all_recipes if r.title == title)
                    col_idx = idx % 4
                    with cols[col_idx]:
                        servings = st.number_input(
                            f"Portions: {rec.title}",
                            min_value=1,
                            max_value=20,
                            value=1,
                            step=1,
                            key=f"servings_{rec.id}"
                        )
                        selected_recipes_config.append({"recipe": rec, "servings": servings})

                st.divider()
                st.subheader("2. Combined Weekly Ingredient List (Auto-Translated)")

                aggregated_ingredients = aggregate_weekly_ingredients(selected_recipes_config)
                agg_df = pd.DataFrame([
                    {
                        "Original Ingredient": item["original_name"],
                        "German Grocery Match": item["german_name"],
                        "Total Required Quantity": f"{item['quantity']:.1f} {item['unit']}"
                    }
                    for item in aggregated_ingredients
                ])
                st.dataframe(agg_df, use_container_width=True, hide_index=True)

                st.divider()
                st.subheader("3. Shopping Strategy Optimization (PLZ 10369)")

                strategy_data = calculate_weekly_basket_strategies(aggregated_ingredients, db)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric(
                        label="Best Single Supermarket (One-Stop)",
                        value=f"€{strategy_data['best_single_total']:.2f}",
                        delta=f"Store: {strategy_data['best_single_store']}"
                    )
                with m2:
                    st.metric(
                        label="Maximum Savings (Multi-Store Split)",
                        value=f"€{strategy_data['multi_store_total']:.2f}",
                        delta="Across multiple local stores"
                    )
                with m3:
                    st.metric(
                        label="Extra Euros Saved with Split",
                        value=f"€{strategy_data['max_savings']:.2f}",
                        delta_color="normal"
                    )

                st.markdown("---")

                st.write("### Strategy A: Best Single Supermarket Ranking")
                single_ranking_df = pd.DataFrame([
                    {
                        "Supermarket": store,
                        "Total Weekly Basket Cost (€)": f"{price:.2f}",
                        "Status": "🏆 Cheapest One-Stop" if store == strategy_data['best_single_store'] else "Standard"
                    }
                    for store, price in sorted(strategy_data["store_totals"].items(), key=lambda x: x[1])
                ])
                st.dataframe(single_ranking_df, use_container_width=True, hide_index=True)

                st.write("### Strategy B: Maximum Savings Itemized Shopping List")
                split_df = pd.DataFrame(strategy_data["multi_store_split"])
                split_df["Price (€)"] = split_df["Price (€)"].map(lambda v: f"{v:.2f}")
                st.dataframe(split_df, use_container_width=True, hide_index=True)

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 3: RECIPE MANAGER (RAW TEXT PARSER WITH MULTI-LANG TRANSLATION)
# -----------------------------------------------------------------------------
with tab3:
    st.header("Recipe Manager")
    st.caption("Paste raw recipe text from Recipe One, TikTok, or multi-language formats (DE, PT, EN, DA).")

    db = get_db()

    try:
        st.subheader("Paste Raw Recipe Text")
        
        # Sample template placeholder showing Portuguese/English/Danish multi-language input
        sample_placeholder = (
            "Bolo de Cenoura com Cobertura\n"
            "• 200 Gram Farinha de trigo\n"
            "• 3 Unidades Ovo\n"
            "• 200 Gram Açúcar\n"
            "• 100 Gram Manteiga\n\n"
            "Modo de preparo:\n"
            "1. Misture os ingredientes e asse por 40 minutos."
        )

        raw_recipe_text = st.text_area(
            "Paste full recipe here (Title on line 1, ingredients with bullet points/quantities):",
            height=250,
            placeholder=sample_placeholder
        )

        if st.button("Parse & Save Recipe"):
            if raw_recipe_text.strip():
                parsed_title, parsed_instructions, parsed_ingredients = parse_raw_recipe_text(raw_recipe_text)

                if parsed_ingredients:
                    new_recipe = Recipe(title=parsed_title, instructions=parsed_instructions)
                    new_recipe.ingredients = parsed_ingredients
                    db.add(new_recipe)
                    db.commit()

                    st.success(f"Successfully parsed and saved recipe: '{parsed_title}'!")
                    
                    st.write("**Parsed & Translated Ingredient Match Preview:**")
                    preview_df = pd.DataFrame([
                        {
                            "Original Name": ing["original_name"],
                            "Quantity": ing["quantity"],
                            "Unit": ing["unit"],
                            "German Supermarket Term": ing["name"]
                        }
                        for ing in parsed_ingredients
                    ])
                    st.dataframe(preview_df, use_container_width=True, hide_index=True)
                    st.rerun()
                else:
                    st.error("Could not extract ingredients. Please check the text format.")
            else:
                st.warning("Please paste recipe text into the box first.")

        st.divider()
        st.subheader("Saved Recipes")
        recipes_list = db.query(Recipe).all()
        for r in recipes_list:
            with st.expander(f"🍲 **{r.title}** ({len(r.ingredients)} ingredients)"):
                st.write("**Ingredients:**")
                for ing in r.ingredients:
                    orig = ing.get('original_name', ing['name'])
                    st.write(f"- {ing['quantity']} {ing['unit']} **{orig}** *(Mapped to: {ing['name']})*")
                st.write("**Instructions:**")
                st.write(r.instructions)

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 4: PRICE HISTORY
# -----------------------------------------------------------------------------
with tab4:
    st.header("Historical Price Trends")
    st.caption("Interactive price trend visualizer.")
    
    db = get_db()
    try:
        history_records = db.query(PriceHistory).all()
        if history_records:
            hist_df = pd.DataFrame([
                {
                    "Product": h.product_name,
                    "Supermarket": h.supermarket_name,
                    "Price": h.price,
                    "Date": h.recorded_date
                }
                for h in history_records
            ])

            selected_product = st.selectbox(
                "Select a product to inspect history:",
                options=hist_df["Product"].unique()
            )

            with st.expander("📊 Click to View Price History Chart", expanded=True):
                filtered_hist = hist_df[hist_df["Product"] == selected_product].sort_values(by="Date")
                fig = px.line(
                    filtered_hist,
                    x="Date",
                    y="Price",
                    color="Supermarket",
                    markers=True,
                    title=f"Price History: {selected_product}"
                )
                fig.update_layout(yaxis_title="Price (€)", xaxis_title="Date")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recorded price history available.")
    finally:
        db.close()

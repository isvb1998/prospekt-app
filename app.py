import re
import io
import json
import streamlit as st
import pandas as pd
import plotly.express as px
from pypdf import PdfReader

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

INGREDIENT_TRANSLATION_MAP = {
    # Portuguese
    "farinha de trigo": "Weizenmehl", "farinha": "Weizenmehl", "iogurte natural": "Naturjoghurt",
    "iogurte": "Joghurt", "passata de tomate": "Passierte Tomaten", "molho de tomate": "Passierte Tomaten",
    "tomate pelado": "Gehackte Tomaten", "mussarela": "Mozzarella", "queijo mussarela": "Mozzarella",
    "queijo": "Käse", "linguiça calabresa": "Mettwurst", "calabresa": "Mettwurst", "ovo": "Eier",
    "ovos": "Eier", "leite": "Milch", "manteiga": "Butter", "açúcar": "Zucker", "açucar": "Zucker",
    "sal": "Salz", "cebola": "Zwiebeln", "cebolas": "Zwiebeln", "alho": "Knoblauch", "batata": "Kartoffeln",
    "batatas": "Kartoffeln", "carne moída": "Hackfleisch", "carne moida": "Hackfleisch", "arroz": "Reis",
    "macarrão": "Spaghetti", "espaguete": "Spaghetti",
    # Danish
    "hvedemel": "Weizenmehl", "sukker": "Zucker", "æg": "Eier", "mælk": "Milch", "smør": "Butter",
    "kartofler": "Kartoffeln", "løg": "Zwiebeln", "hvidløg": "Knoblauch", "hakket oksekød": "Hackfleisch",
    "hakkekød": "Hackfleisch",
    # English
    "flour": "Weizenmehl", "wheat flour": "Weizenmehl", "eggs": "Eier", "egg": "Eier",
    "ground beef": "Hackfleisch", "minced meat": "Hackfleisch", "minced beef": "Hackfleisch",
    "milk": "Milch", "butter": "Butter", "sugar": "Zucker", "salt": "Salz", "onion": "Zwiebeln",
    "onions": "Zwiebeln", "garlic": "Knoblauch", "potatoes": "Kartoffeln", "potato": "Kartoffeln",
    "spaghetti": "Spaghetti", "pasta": "Spaghetti", "strained tomatoes": "Passierte Tomaten",
    "tomato paste": "Tomatenmark", "natural yogurt": "Naturjoghurt", "plain yogurt": "Naturjoghurt",
    "mozzarella": "Mozzarella", "rice": "Reis"
}


def normalize_unit(unit_str: str) -> str:
    cleaned = unit_str.strip().lower()
    return UNIT_MAP.get(cleaned, unit_str.strip())


def translate_to_german_grocery(ingredient_raw: str) -> str:
    cleaned = ingredient_raw.strip().lower()
    if cleaned in INGREDIENT_TRANSLATION_MAP:
        return INGREDIENT_TRANSLATION_MAP[cleaned]
    for key, german_term in INGREDIENT_TRANSLATION_MAP.items():
        if key in cleaned:
            return german_term
    return ingredient_raw.strip().title()


def parse_raw_recipe_text(raw_text: str) -> tuple[str, str, list[dict]]:
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]
    if not lines:
        return "Untitled Recipe", "", []

    title = lines[0].lstrip("#•-* ").strip()
    instructions_lines = []
    ingredients = []
    is_instruction_section = False

    for line in lines[1:]:
        if re.search(r"^(modo de preparo|instruções|instructions|fremgangsmåde|zubereitung|steps|preparo):", line, re.IGNORECASE):
            is_instruction_section = True
            continue

        if is_instruction_section:
            instructions_lines.append(line)
            continue

        cleaned_line = re.sub(r"^[•\-\*\d\.\)]+", "", line).strip()
        if not cleaned_line:
            continue

        match = re.match(r"^([\d\.,/]+)\s*([a-zA-ZáàâãéèêíïóôõöúçÁÀÂÃÉÈÍÏÓÔÕÖÚÇ\.\s]+?)\s+(de\s+)?(.+)$", cleaned_line, re.IGNORECASE)
        
        if match:
            qty_str, unit_str, _, name_str = match.groups()
            try:
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
                "name": german_match_name,
                "original_name": original_name,
                "quantity": qty,
                "unit": unit
            })
        else:
            german_match_name = translate_to_german_grocery(cleaned_line)
            ingredients.append({
                "name": german_match_name,
                "original_name": cleaned_line.title(),
                "quantity": 1.0,
                "unit": "Stück"
            })

    instructions = "\n".join(instructions_lines) if instructions_lines else "No detailed instructions provided."
    return title, instructions, ingredients


def parse_pdf_recipes(file_stream) -> list[tuple[str, str, list[dict]]]:
    reader = PdfReader(file_stream)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n---PAGE---\n"

    raw_recipes = [r.strip() for r in full_text.split("---PAGE---") if r.strip()]
    parsed_batch = []
    for raw in raw_recipes:
        t, inst, ing = parse_raw_recipe_text(raw)
        if ing:
            parsed_batch.append((t, inst, ing))
    return parsed_batch


# -----------------------------------------------------------------------------
# WEEKLY AGGREGATION & STRATEGY ENGINE
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


def calculate_cheapest_recipes(recipes, db, limit=5):
    evaluated_recipes = []

    for r in recipes:
        agg = aggregate_weekly_ingredients([{"recipe": r, "servings": 1}])
        strategy = calculate_weekly_basket_strategies(agg, db)
        
        total_onsale_savings = 0.0
        sale_ingredients_count = 0

        for item in strategy["multi_store_split"]:
            if "Sale Offer" in item["Price Type"]:
                sale_ingredients_count += 1
                total_onsale_savings += 0.50

        evaluated_recipes.append({
            "recipe": r,
            "cheapest_cost": strategy["multi_store_total"],
            "cheapest_store": strategy["best_single_store"],
            "savings_estimate": total_onsale_savings,
            "sale_count": sale_ingredients_count
        })

    evaluated_recipes.sort(key=lambda x: (x["cheapest_cost"], -x["sale_count"]))
    return evaluated_recipes[:limit]


# -----------------------------------------------------------------------------
# APP UI & NAVIGATION
# -----------------------------------------------------------------------------

st.title("🛒 ProspektRecipeOptimizer")
st.caption("Weekly offers & multi-language recipe planner — Berlin 10369 (Landsberger Allee / Storkower Str.)")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏷️ Top Deals This Week",
    "📅 Weekly Meal Planner",
    "📖 Recipe Manager & CRUD",
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
            selected_stores = st.multiselect("Filter Supermarket", options=df["Supermarket"].unique(), default=df["Supermarket"].unique(), key="tab1_store_filter")
        with col2:
            selected_cats = st.multiselect("Filter Category", options=df["Category"].unique(), default=df["Category"].unique(), key="tab1_cat_filter")

        filtered_df = df[
            (df["Supermarket"].isin(selected_stores)) & 
            (df["Category"].isin(selected_cats))
        ]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.divider()

        with st.expander("🔍 Show Price History for an Offer Item"):
            selected_item = st.selectbox("Select product to inspect:", options=df["Product Name"].unique(), key="tab1_product_select")
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
# TAB 2: WEEKLY MEAL PLANNER
# -----------------------------------------------------------------------------
with tab2:
    st.header("Weekly Meal Planner")
    db = get_db()

    try:
        all_recipes = db.query(Recipe).all()

        if not all_recipes:
            st.warning("No recipes found in database. Add or import recipes in 'Recipe Manager & CRUD'.")
        else:
            planning_mode = st.radio(
                "Select Planning Strategy Mode:",
                ["MODE 1: Auto-Generated Lowest-Cost Meal Plan", "MODE 2: Custom Selection & Smart Basket Comparison"],
                horizontal=True
            )

            st.divider()

            if planning_mode == "MODE 1: Auto-Generated Lowest-Cost Meal Plan":
                st.subheader("⚡ Top 5 Overall Lowest-Cost Recipes This Week")
                st.caption("Automatically calculated by ranking stored recipes against active weekly offers.")

                top_deals = calculate_cheapest_recipes(all_recipes, db, limit=5)

                auto_config = []
                for item in top_deals:
                    rec = item["recipe"]
                    st.write(f"- 🍲 **{rec.title}** — Est. Cost: **€{item['cheapest_cost']:.2f}** | On-Sale Ingredient Matches: **{item['sale_count']}**")
                    auto_config.append({"recipe": rec, "servings": 1})

                st.divider()
                st.subheader("Optimized Basket Strategy for Auto-Selected Menu")

                agg_ingredients = aggregate_weekly_ingredients(auto_config)
                strategy_data = calculate_weekly_basket_strategies(agg_ingredients, db)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Best Single Supermarket", f"€{strategy_data['best_single_total']:.2f}", delta=strategy_data['best_single_store'])
                with m2:
                    st.metric("Multi-Store Split Total", f"€{strategy_data['multi_store_total']:.2f}", delta="Maximum Savings")
                with m3:
                    st.metric("Total Saved with Split Strategy", f"€{strategy_data['max_savings']:.2f}")

                st.write("### Itemized Multi-Store Split List")
                split_df = pd.DataFrame(strategy_data["multi_store_split"])
                split_df["Price (€)"] = split_df["Price (€)"].map(lambda v: f"{v:.2f}")
                st.dataframe(split_df, use_container_width=True, hide_index=True)

            else:
                st.subheader("1. Pick Your Recipes & Portions")
                selected_titles = st.multiselect(
                    "Choose recipes for the week:",
                    options=[r.title for r in all_recipes],
                    default=[all_recipes[0].title] if all_recipes else []
                )

                selected_recipes_config = []
                if selected_titles:
                    cols = st.columns(min(len(selected_titles), 4))
                    for idx, title in enumerate(selected_titles):
                        rec = next(r for r in all_recipes if r.title == title)
                        with cols[idx % 4]:
                            servings = st.number_input(f"Portions: {rec.title}", min_value=1, max_value=20, value=1, key=f"custom_serv_{rec.id}")
                            selected_recipes_config.append({"recipe": rec, "servings": servings})

                    st.divider()
                    st.subheader("2. Basket Cost Strategy Breakdown")

                    agg_ingredients = aggregate_weekly_ingredients(selected_recipes_config)
                    strategy_data = calculate_weekly_basket_strategies(agg_ingredients, db)

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Single Supermarket Winner", f"€{strategy_data['best_single_total']:.2f}", delta=f"Cheapest Store: {strategy_data['best_single_store']}")
                    with m2:
                        st.metric("Multi-Store Split Strategy", f"€{strategy_data['multi_store_total']:.2f}", delta="Optimized")
                    with m3:
                        st.metric("Extra Savings via Split", f"€{strategy_data['max_savings']:.2f}")

                    st.write("### Single Store Total Bill Comparison")
                    single_df = pd.DataFrame([
                        {"Supermarket": store, "Total Bill (€)": f"{price:.2f}", "Winner": "🏆 Best Single Store" if store == strategy_data['best_single_store'] else ""}
                        for store, price in sorted(strategy_data["store_totals"].items(), key=lambda x: x[1])
                    ])
                    st.dataframe(single_df, use_container_width=True, hide_index=True)

                    st.write("### Itemized Multi-Store Shopping Split")
                    split_df = pd.DataFrame(strategy_data["multi_store_split"])
                    split_df["Price (€)"] = split_df["Price (€)"].map(lambda v: f"{v:.2f}")
                    st.dataframe(split_df, use_container_width=True, hide_index=True)

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 3: RECIPE MANAGER & CRUD
# -----------------------------------------------------------------------------
with tab3:
    st.header("Recipe Manager & Interactive CRUD")
    
    crud_subtab1, crud_subtab2, crud_subtab3 = st.tabs([
        "✏️ Manage & Edit Saved Recipes",
        "📄 Add / Import Recipes",
        "👁️ View Recipe Details"
    ])

    # -------------------------------------------------------------------------
    # SUB-TAB 1: MANAGE & EDIT SAVED RECIPES (BULK DATA EDITOR + SINGLE FORM)
    # -------------------------------------------------------------------------
    with crud_subtab1:
        st.subheader("Interactive Bulk Recipe Table")
        st.caption("Edit values directly inside table cells or select rows to delete. Click save to apply changes.")

        db = get_db()
        try:
            recipes_list = db.query(Recipe).all()

            if not recipes_list:
                st.info("No saved recipes found.")
            else:
                # Prepare dataframe for st.data_editor
                table_rows = []
                for r in recipes_list:
                    table_rows.append({
                        "ID": r.id,
                        "Title": r.title,
                        "Instructions": r.instructions,
                        "Ingredients Count": len(r.ingredients)
                    })
                
                df_recipes = pd.DataFrame(table_rows)

                edited_df = st.data_editor(
                    df_recipes,
                    num_rows="dynamic",
                    key="recipe_bulk_editor",
                    disabled=["ID", "Ingredients Count"],
                    use_container_width=True,
                    hide_index=True
                )

                if st.button("💾 Save Bulk Table Changes to Database"):
                    # 1. Handle Deletions: Compare IDs in original vs edited dataframe
                    current_ids = set(df_recipes["ID"].tolist())
                    edited_ids = set(edited_df["ID"].dropna().astype(int).tolist())
                    deleted_ids = current_ids - edited_ids

                    if deleted_ids:
                        for d_id in deleted_ids:
                            rec_to_del = db.query(Recipe).filter(Recipe.id == d_id).first()
                            if rec_to_del:
                                db.delete(rec_to_del)

                    # 2. Handle Cell Updates
                    for idx, row in edited_df.iterrows():
                        if pd.notna(row["ID"]):
                            r_id = int(row["ID"])
                            rec = db.query(Recipe).filter(Recipe.id == r_id).first()
                            if rec:
                                rec.title = str(row["Title"])
                                rec.instructions = str(row["Instructions"])

                    db.commit()
                    st.success("Successfully synchronized changes with SQLite database!")
                    st.rerun()

                st.divider()

                # -------------------------------------------------------------
                # SINGLE RECIPE FORM EDITOR & PERMANENT DELETER
                # -------------------------------------------------------------
                st.subheader("Single Recipe Form Editor")
                selected_recipe_title = st.selectbox(
                    "Select a specific recipe to edit or delete:",
                    options=[r.title for r in recipes_list],
                    key="single_recipe_selector"
                )

                target_recipe = next((r for r in recipes_list if r.title == selected_recipe_title), None)

                if target_recipe:
                    with st.form("edit_single_recipe_form"):
                        edit_title = st.text_input("Title", value=target_recipe.title)
                        edit_instructions = st.text_area("Instructions", value=target_recipe.instructions, height=150)
                        
                        # Format ingredients into line-by-line raw text representation
                        ing_lines = []
                        for ing in target_recipe.ingredients:
                            name = ing.get('original_name', ing['name'])
                            ing_lines.append(f"{name}, {ing['quantity']}, {ing['unit']}")
                        
                        edit_ingredients_raw = st.text_area(
                            "Ingredients (Format: Name, Quantity, Unit — one item per line)",
                            value="\n".join(ing_lines),
                            height=150
                        )

                        col_btn1, col_btn2 = st.columns(2)
                        with col_btn1:
                            submit_edits = st.form_submit_button("💾 Save Edits for Selected Recipe")
                        with col_btn2:
                            delete_single = st.form_submit_button("🚨 Delete Selected Recipe")

                        if submit_edits:
                            db_rec = db.query(Recipe).filter(Recipe.id == target_recipe.id).first()
                            if db_rec:
                                db_rec.title = edit_title
                                db_rec.instructions = edit_instructions
                                
                                # Re-parse edited ingredients line by line
                                updated_ingredients = []
                                for line in edit_ingredients_raw.strip().split("\n"):
                                    if line.strip():
                                        parts = [p.strip() for p in line.split(",")]
                                        if len(parts) >= 3:
                                            try:
                                                qty = float(parts[1])
                                            except ValueError:
                                                qty = 1.0
                                            
                                            raw_name = parts[0]
                                            mapped_name = translate_to_german_grocery(raw_name)
                                            updated_ingredients.append({
                                                "name": mapped_name,
                                                "original_name": raw_name,
                                                "quantity": qty,
                                                "unit": normalize_unit(parts[2])
                                            })
                                
                                db_rec.ingredients = updated_ingredients
                                db.commit()
                                st.success(f"Recipe '{edit_title}' updated successfully!")
                                st.rerun()

                        if delete_single:
                            db_rec = db.query(Recipe).filter(Recipe.id == target_recipe.id).first()
                            if db_rec:
                                db.delete(db_rec)
                                db.commit()
                                st.warning(f"Recipe '{target_recipe.title}' permanently deleted.")
                                st.rerun()

        finally:
            db.close()

    # -------------------------------------------------------------------------
    # SUB-TAB 2: ADD / IMPORT RECIPES
    # -------------------------------------------------------------------------
    with crud_subtab2:
        st.subheader("Add or Batch Import Recipes")
        db = get_db()

        try:
            import_mode = st.radio("Import Method:", ["Batch Upload PDF Recipes", "Paste Raw Recipe Text"], horizontal=True, key="add_recipe_import_mode")

            if import_mode == "Batch Upload PDF Recipes":
                uploaded_file = st.file_uploader("Upload a recipe collection PDF", type=["pdf"], key="crud_pdf_uploader")

                if uploaded_file is not None:
                    if st.button("Extract & Save Recipes from PDF", key="btn_pdf_import"):
                        parsed_recipes = parse_pdf_recipes(io.BytesIO(uploaded_file.read()))
                        
                        if parsed_recipes:
                            count = 0
                            for t, inst, ing in parsed_recipes:
                                new_recipe = Recipe(title=t, instructions=inst)
                                new_recipe.ingredients = ing
                                db.add(new_recipe)
                                count += 1
                            db.commit()
                            st.success(f"Successfully imported {count} recipes from PDF!")
                            st.rerun()
                        else:
                            st.error("Could not parse valid recipes from PDF. Ensure text layout has ingredients listed clearly.")

            else:
                sample_placeholder = (
                    "Bolo de Cenoura com Cobertura\n"
                    "• 200 Gram Farinha de trigo\n"
                    "• 3 Unidades Ovo\n"
                    "• 200 Gram Açúcar\n"
                    "• 100 Gram Manteiga\n\n"
                    "Modo de preparo:\n"
                    "1. Misture os ingredientes e asse por 40 minutos."
                )
                raw_text = st.text_area("Paste text here:", height=200, placeholder=sample_placeholder, key="crud_raw_text")

                if st.button("Parse & Save Text Recipe", key="btn_text_import"):
                    if raw_text.strip():
                        t, inst, ing = parse_raw_recipe_text(raw_text)
                        if ing:
                            new_recipe = Recipe(title=t, instructions=inst)
                            new_recipe.ingredients = ing
                            db.add(new_recipe)
                            db.commit()
                            st.success(f"Saved recipe: '{t}'!")
                            st.rerun()

        finally:
            db.close()

    # -------------------------------------------------------------------------
    # SUB-TAB 3: VIEW RECIPE DETAILS
    # -------------------------------------------------------------------------
    with crud_subtab3:
        st.subheader("Saved Recipes Collection")
        db = get_db()
        try:
            recipes_list = db.query(Recipe).all()
            if not recipes_list:
                st.info("No recipes saved yet.")
            else:
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

            selected_product = st.selectbox("Select product to inspect:", options=hist_df["Product"].unique(), key="tab4_product_select")

            with st.expander("📊 Click to View Price History Chart", expanded=True):
                filtered_hist = hist_df[hist_df["Product"] == selected_product].sort_values(by="Date")
                fig = px.line(filtered_hist, x="Date", y="Price", color="Supermarket", markers=True, title=f"Price History: {selected_product}")
                fig.update_layout(yaxis_title="Price (€)", xaxis_title="Date")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recorded price history available.")
    finally:
        db.close()

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


def aggregate_weekly_ingredients(selected_recipes_config):
    """
    Aggregates ingredients across selected recipes considering portion scaling.
    selected_recipes_config: list of dicts [{'recipe': RecipeObj, 'servings': int}]
    """
    aggregated = {}

    for item in selected_recipes_config:
        recipe = item["recipe"]
        servings = item["servings"]

        # Default base recipe scale multiplier (assumes base recipe serves 1 portion/base unit)
        scale = servings

        for ing in recipe.ingredients:
            name = ing["name"].strip()
            qty = float(ing.get("quantity", 1.0)) * scale
            unit = ing.get("unit", "").strip()

            key = (name.lower(), unit.lower())

            if key not in aggregated:
                aggregated[key] = {
                    "name": name,
                    "quantity": qty,
                    "unit": unit
                }
            else:
                aggregated[key]["quantity"] += qty

    return list(aggregated.values())


def calculate_weekly_basket_strategies(aggregated_ingredients, db):
    """
    Calculates Single-Store vs Multi-Store optimized costs for the aggregated weekly basket.
    """
    stores = ["Aldi Nord", "Kaufland", "Lidl", "REWE", "Edeka", "Netto"]
    
    store_totals = {store: 0.0 for store in stores}
    store_itemized = {store: [] for store in stores}
    multi_store_split = []

    for ing in aggregated_ingredients:
        ing_name = ing["name"]
        cheapest_price = float('inf')
        cheapest_store = ""
        cheapest_product_name = ""
        cheapest_is_sale = False

        for store in stores:
            price_info = find_best_ingredient_price(ing_name, store, db)
            cost = price_info["price"]
            store_totals[store] += cost
            
            store_itemized[store].append({
                "Ingredient": ing_name,
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
            "Ingredient": ing_name,
            "Quantity": f"{ing['quantity']:.1f} {ing['unit']}",
            "Buy At Supermarket": cheapest_store,
            "Matched Product": cheapest_product_name,
            "Price Type": "Sale Offer 🏷️" if cheapest_is_sale else "Regular Price 📌",
            "Price (€)": cheapest_price
        })

    # Sort single stores by total cost
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


# Header
st.title("🛒 ProspektRecipeOptimizer")
st.caption("Weekly offers & smart meal planner — Berlin 10369 (Landsberger Allee / Storkower Str.)")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏷️ Top Deals This Week",
    "📅 Weekly Meal Planner & Grocery Strategy",
    "📖 Recipe Manager",
    "📈 Price History"
])


# -----------------------------------------------------------------------------
# TAB 1: TOP DEALS THIS WEEK (CLEAN LAYOUT)
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

        # Filters
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
            st.warning("No recipes found in the database. Please add recipes in the 'Recipe Manager' tab.")
        else:
            st.subheader("1. Select Meals & Portions for the Week")
            
            selected_recipes_config = []
            
            # Recipe selection UI
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
                st.subheader("2. Combined Weekly Ingredient List")

                aggregated_ingredients = aggregate_weekly_ingredients(selected_recipes_config)
                agg_df = pd.DataFrame([
                    {
                        "Ingredient": item["name"],
                        "Total Required Quantity": f"{item['quantity']:.1f} {item['unit']}"
                    }
                    for item in aggregated_ingredients
                ])
                st.dataframe(agg_df, use_container_width=True, hide_index=True)

                st.divider()
                st.subheader("3. Shopping Strategy Optimization (PLZ 10369)")

                strategy_data = calculate_weekly_basket_strategies(aggregated_ingredients, db)

                # Metrics Overview
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

                # Strategy A: One-Stop Single Supermarket Ranking
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

                # Strategy B: Multi-Store Split Itemized Shopping List
                st.write("### Strategy B: Maximum Savings Itemized Shopping List")
                split_df = pd.DataFrame(strategy_data["multi_store_split"])
                split_df["Price (€)"] = split_df["Price (€)"].map(lambda v: f"{v:.2f}")
                st.dataframe(split_df, use_container_width=True, hide_index=True)

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 3: RECIPE MANAGER (SUPPORTS TIKTOK, RECIPE ONE & CUSTOM ENTRIES)
# -----------------------------------------------------------------------------
with tab3:
    st.header("Recipe Manager")
    st.caption("Import or create custom recipes (supports TikTok, Recipe One, or manual entry).")

    db = get_db()

    try:
        source_type = st.radio("Recipe Import Source:", ["Manual Entry", "Import Link (TikTok / Recipe One)"], horizontal=True)

        with st.form("add_recipe_form", clear_on_submit=True):
            if source_type == "Import Link (TikTok / Recipe One)":
                recipe_url = st.text_input("Recipe URL (TikTok, Recipe One, etc.)")
            
            title = st.text_input("Recipe Title")
            instructions = st.text_area("Cooking Instructions")
            ingredients_raw = st.text_area(
                "Ingredients (Format: Name, Quantity, Unit — one item per line)",
                help="Example:\nHackfleisch, 500, g\nZwiebeln, 2, Stück"
            )
            
            submitted = st.form_submit_button("Save Recipe")
            
            if submitted and title and instructions:
                parsed_ingredients = []
                for line in ingredients_raw.strip().split("\n"):
                    if line:
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 3:
                            parsed_ingredients.append({
                                "name": parts[0],
                                "quantity": float(parts[1]),
                                "unit": parts[2],
                                "optional": False
                            })
                
                # Append source link info to instructions if present
                full_instructions = instructions
                if source_type != "Manual Entry" and 'recipe_url' in locals() and recipe_url:
                    full_instructions += f"\n\nSource: {recipe_url}"

                new_recipe = Recipe(title=title, instructions=full_instructions)
                new_recipe.ingredients = parsed_ingredients
                db.add(new_recipe)
                db.commit()
                st.success(f"Recipe '{title}' saved successfully!")
                st.rerun()

        st.divider()
        st.subheader("Saved Recipes")
        recipes_list = db.query(Recipe).all()
        for r in recipes_list:
            with st.expander(f"🍲 **{r.title}** ({len(r.ingredients)} ingredients)"):
                st.write("**Ingredients:**")
                for ing in r.ingredients:
                    st.write(f"- {ing['quantity']} {ing['unit']} {ing['name']}")
                st.write("**Instructions:**")
                st.write(r.instructions)

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 4: PRICE HISTORY (CLICK-TO-VIEW)
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

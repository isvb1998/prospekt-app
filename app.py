import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, SessionLocal, Offer, Recipe, PriceHistory
from scraper import run_scraper
from engine import compare_recipe_store_costs

st.set_page_config(
    page_title="ProspektRecipeOptimizer - Berlin 10369",
    page_icon="🛒",
    layout="wide"
)

# Ensure database and weekly offer data exist
init_db()
run_scraper()


def get_db():
    return SessionLocal()


st.title("🛒 ProspektRecipeOptimizer")
st.caption("Weekly offers & basket optimizer — Berlin 10369 (Landsberger Allee / Storkower Str.)")

# Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏷️ Weekly Offers",
    "🧮 Recipe Basket Calculator",
    "📖 Recipe Manager",
    "📈 Price History"
])

# -----------------------------------------------------------------------------
# TAB 1: WEEKLY OFFERS (CLEAN DISPLAY)
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

        # Clean Filters
        col1, col2 = st.columns(2)
        with col1:
            selected_stores = st.multiselect("Filter Supermarket", options=df["Supermarket"].unique(), default=df["Supermarket"].unique())
        with col2:
            selected_cats = st.multiselect("Filter Category", options=df["Category"].unique(), default=df["Category"].unique())

        filtered_df = df[
            (df["Supermarket"].isin(selected_stores)) & 
            (df["Category"].isin(selected_cats))
        ]

        # Clean Table Output
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        st.divider()

        # On-Demand Price Trend Inspection
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
# TAB 2: RECIPE COST CALCULATOR & STORE COMPARISON
# -----------------------------------------------------------------------------
with tab2:
    st.header("Recipe Basket Price Comparison")
    db = get_db()
    
    try:
        recipes = db.query(Recipe).all()
        recipe_titles = [r.title for r in recipes]
        selected_title = st.selectbox("Choose a Recipe to Compare:", options=recipe_titles)
        
        selected_recipe = next(r for r in recipes if r.title == selected_title)
        analysis = compare_recipe_store_costs(selected_recipe, db)

        # Highlight Metrics
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric(
                label="Cheapest Single Supermarket Total",
                value=f"€{analysis['cheapest_single_total']:.2f}",
                delta=f"Store: {analysis['cheapest_single_store']}"
            )
        with col_b:
            st.metric(
                label="Multi-Store Optimized Total",
                value=f"€{analysis['multi_store_total']:.2f}",
                delta="Buying best deals across stores",
                delta_color="normal"
            )

        st.subheader("Total Basket Price by Supermarket")
        totals_df = pd.DataFrame([
            {"Supermarket": store, "Total Basket Price (€)": price}
            for store, price in sorted(analysis["store_totals"].items(), key=lambda x: x[1])
        ])
        st.dataframe(totals_df, use_container_width=True, hide_index=True)

        # Multi-Store Optimized Basket Breakdown
        with st.expander("🛒 View Multi-Store Optimized Basket Split"):
            multi_df = pd.DataFrame([
                {
                    "Ingredient": item["ingredient"],
                    "Best Store": item["best_store"],
                    "Matched Product": item["product"],
                    "Price (€)": f"{item['price']:.2f}"
                }
                for item in analysis["multi_store_breakdown"]
            ])
            st.dataframe(multi_df, use_container_width=True, hide_index=True)

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 3: RECIPE MANAGER
# -----------------------------------------------------------------------------
with tab3:
    st.header("Recipe Manager")
    db = get_db()

    try:
        with st.form("add_recipe_form", clear_on_submit=True):
            st.subheader("Add New Recipe")
            title = st.text_input("Recipe Title")
            instructions = st.text_area("Cooking Instructions")
            ingredients_raw = st.text_area(
                "Ingredients (Format: Name, Quantity, Unit — one per line)",
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
                
                new_recipe = Recipe(title=title, instructions=instructions)
                new_recipe.ingredients = parsed_ingredients
                db.add(new_recipe)
                db.commit()
                st.success(f"Recipe '{title}' saved!")
                st.rerun()

        st.divider()
        st.subheader("Saved Recipes")
        for r in db.query(Recipe).all():
            st.write(f"- **{r.title}** ({len(r.ingredients)} ingredients)")

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 4: PRICE TREND INSIGHTS (ON-DEMAND)
# -----------------------------------------------------------------------------
with tab4:
    st.header("Historical Price Trends")
    st.caption("Price trend charts load on demand when selected.")
    
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
                "Select a product to view trend history:",
                options=hist_df["Product"].unique()
            )

            # Interactive expander load
            with st.expander("📊 Click to View Price Trend Chart", expanded=True):
                filtered_hist = hist_df[hist_df["Product"] == selected_product].sort_values(by="Date")
                fig = px.line(
                    filtered_hist,
                    x="Date",
                    y="Price",
                    color="Supermarket",
                    markers=True,
                    title=f"Historical Price: {selected_product}"
                )
                fig.update_layout(yaxis_title="Price (€)", xaxis_title="Date")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No recorded price history available.")
    finally:
        db.close()

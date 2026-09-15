import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, SessionLocal, Offer, Recipe, PriceHistory
from scraper_mock import populate_mock_offers
from engine import calculate_deal_score, analyze_recipe_deals

# Page Config
st.set_page_config(
    page_title="ProspektRecipeOptimizer",
    page_icon="🛒",
    layout="wide"
)

# Initialize Database and Mock Data
init_db()
populate_mock_offers()


def get_db():
    return SessionLocal()


st.title("🛒 ProspektRecipeOptimizer")
st.caption("Smart weekly circular deal analyzer & budget recipe planner (German Supermarkets)")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🏷️ Top Deals This Week",
    "🍳 Best Recipes to Cook",
    "📖 Recipe Manager",
    "📈 Price Trend Insights"
])

# -----------------------------------------------------------------------------
# TAB 1: TOP DEALS THIS WEEK
# -----------------------------------------------------------------------------
with tab1:
    st.header("Weekly Supermarket Offers")
    db = get_db()
    
    try:
        offers = db.query(Offer).all()
        deal_data = []

        for o in offers:
            metrics = calculate_deal_score(o, db)
            deal_data.append({
                "Supermarket": o.supermarket_name,
                "Product": o.product_name,
                "Category": o.category,
                "Offer Price (€)": f"{o.current_price:.2f}",
                "Original (€)": f"{o.original_price:.2f}",
                "Discount %": o.discount_percent,
                "Deal Score": metrics["score"],
                "Staple?": "✅" if metrics["is_staple"] else "❌",
                "Highlights": ", ".join(metrics["reasons"])
            })

        df_deals = pd.DataFrame(deal_data)

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_store = st.multiselect("Supermarket", options=df_deals["Supermarket"].unique(), default=df_deals["Supermarket"].unique())
        with col2:
            selected_cat = st.multiselect("Category", options=df_deals["Category"].unique(), default=df_deals["Category"].unique())
        with col3:
            min_discount = st.slider("Minimum Discount %", 0, 70, 0)

        # Filter Application
        filtered_df = df_deals[
            (df_deals["Supermarket"].isin(selected_store)) &
            (df_deals["Category"].isin(selected_cat)) &
            (df_deals["Discount %"] >= min_discount)
        ].sort_values(by="Deal Score", ascending=False)

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 2: BEST RECIPES TO COOK
# -----------------------------------------------------------------------------
with tab2:
    st.header("Recommended Recipes Based on Weekly Deals")
    db = get_db()
    
    try:
        recipes = db.query(Recipe).all()
        analyzed_recipes = [analyze_recipe_deals(r, db) for r in recipes]
        
        # Sort recipes by Savings Score and Offer Coverage %
        analyzed_recipes.sort(key=lambda x: (x["savings_score"], x["coverage_percent"]), reverse=True)

        for rec in analyzed_recipes:
            with st.expander(f"🍲 **{rec['recipe_title']}** — Estimated Cost: **€{rec['cost_score']:.2f}** | Savings: **€{rec['savings_score']:.2f}** | Deal Coverage: **{rec['coverage_percent']}%**"):
                
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.subheader("Ingredients")
                    for ing in rec["ingredients"]:
                        opt = " *(Optional)*" if ing.get("optional") else ""
                        st.write(f"- {ing['quantity']} {ing['unit']} **{ing['name']}**{opt}")
                
                with col_right:
                    st.subheader("Matched Prospekt Deals")
                    if rec["matched_deals"]:
                        for d in rec["matched_deals"]:
                            st.success(f"**{d['ingredient']}** -> {d['offer_product']} ({d['supermarket']}) at **€{d['sale_price']:.2f}** *(Was €{d['original_price']:.2f})*")
                    else:
                        st.info("No active discounts matched for ingredients.")

                st.subheader("Instructions")
                st.write(rec["instructions"])
    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 3: RECIPE MANAGER
# -----------------------------------------------------------------------------
with tab3:
    st.header("Recipe Management")
    db = get_db()

    try:
        st.subheader("Add New Recipe")
        with st.form("add_recipe_form", clear_on_submit=True):
            title = st.text_input("Recipe Title")
            instructions = st.text_area("Cooking Instructions")
            ingredients_raw = st.text_area("Ingredients (Format: Name, Quantity, Unit, Optional[True/False] per line)", 
                                           help="Example:\nHackfleisch, 500, g, False\nZwiebeln, 2, Stück, False")
            
            submitted = st.form_submit_button("Save Recipe")
            
            if submitted and title and instructions:
                parsed_ingredients = []
                for line in ingredients_raw.strip().split("\n"):
                    if line:
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 3:
                            is_opt = parts[3].lower() == "true" if len(parts) > 3 else False
                            parsed_ingredients.append({
                                "name": parts[0],
                                "quantity": float(parts[1]),
                                "unit": parts[2],
                                "optional": is_opt
                            })
                
                new_recipe = Recipe(title=title, instructions=instructions)
                new_recipe.ingredients = parsed_ingredients
                db.add(new_recipe)
                db.commit()
                st.success(f"Recipe '{title}' saved successfully!")
                st.rerun()

        st.divider()
        st.subheader("Existing Recipes")
        all_recipes = db.query(Recipe).all()
        for r in all_recipes:
            st.write(f"- **{r.title}** ({len(r.ingredients)} ingredients)")

    finally:
        db.close()


# -----------------------------------------------------------------------------
# TAB 4: PRICE TREND INSIGHTS
# -----------------------------------------------------------------------------
with tab4:
    st.header("Historical Price Trends")
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

            product_list = hist_df["Product"].unique()
            selected_product = st.selectbox("Select Product to View Price History", options=product_list)

            filtered_hist = hist_df[hist_df["Product"] == selected_product].sort_values(by="Date")

            fig = px.line(
                filtered_hist, 
                x="Date", 
                y="Price", 
                color="Supermarket",
                markers=True,
                title=f"Price Trend: {selected_product}"
            )
            fig.update_layout(yaxis_title="Price (€)", xaxis_title="Date")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No price history recorded yet.")
    finally:
        db.close()

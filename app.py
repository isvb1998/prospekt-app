import re
from collections import Counter
import requests
import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from recipe_scrapers import scrape_html
    HAS_RECIPE_SCRAPERS = True
except ImportError:
    HAS_RECIPE_SCRAPERS = False

from database import init_db, SessionLocal, Offer, StandardBaselinePrice, Recipe, Ingredient, PriceHistory, UserLearnedMapping
from scraper import run_scraper
from engine import (
    find_best_ingredient_price,
    map_ingredient_to_german_sku,
    strip_ingredient_descriptors,
    save_user_learned_mapping
)
from seed_database import seed_database, seed_recipes
from receipt_parser import parse_and_log_receipt

st.set_page_config(
    page_title="Pro-Meal | Smart Circular Deals & Weekly Meal Optimization",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_db()

try:
    run_scraper()
except Exception as e:
    print(f"Scraper execution skipped or failed: {e}")

def get_db():
    return SessionLocal()

@st.cache_data(ttl=300)
def load_cached_recipes():
    db = get_db()
    try:
        recipes = db.query(Recipe).all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "category": getattr(r, "category", "Main Course"),
                "servings": getattr(r, "servings", 1),
                "instructions": r.instructions,
                "ingredients": r.ingredients
            }
            for r in recipes
        ]
    finally:
        db.close()

def check_and_seed_on_startup():
    db = get_db()
    try:
        recipe_count = db.query(Recipe).count()
        if recipe_count == 0:
            seed_database()
            db.commit()
            st.cache_data.clear()
    finally:
        db.close()

check_and_seed_on_startup()

# Initialize planning target state globally if not present
if "planning_week" not in st.session_state:
    st.session_state.planning_week = "Current Week 🟢"

st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .brand-header {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        border: 1px solid #334155;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
        margin-bottom: 2rem;
    }
    .brand-title {
        color: #f8fafc;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.025em;
    }
    .brand-tagline {
        color: #38bdf8;
        font-size: 0.95rem;
        font-weight: 500;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }
    div[data-testid="stMetric"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 1rem 1.25rem !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
</style>
""", unsafe_allow_html=True)

UNIT_MAP = {
    "colher de chá": "TL", "colheres de chá": "TL", "colher de sopa": "EL", "colheres de sopa": "EL",
    "xícara": "Tasse", "xícaras": "Tasse", "grama": "g", "gramas": "g", "quilo": "kg", "quilos": "kg",
    "dente": "Zehe", "dentes": "Zehe", "unidade": "Stück", "unidades": "Stück", "lata": "Dose", "latas": "Dose",
    "pitada": "Prise", "ml": "ml", "g": "g", "kg": "kg", "l": "L"
}

def normalize_unit(unit_str: str) -> str:
    cleaned = unit_str.strip().lower()
    return UNIT_MAP.get(cleaned, unit_str.strip())

def aggregate_weekly_ingredients(selected_recipes_config):
    aggregated = {}
    for item in selected_recipes_config:
        recipe = item["recipe"]
        scale = item["servings"]

        for ing in recipe.get("ingredients", []):
            german_name = ing.get("mapped_german_item") or ing.get("name", "").strip()
            orig_name = ing.get("original_name", ing.get("name", german_name))
            qty = float(ing.get("quantity", 1.0)) * scale
            unit = ing.get("unit", "").strip()
            category = ing.get("generic_category", "Vorrat")

            key = (german_name.lower(), unit.lower())
            if key not in aggregated:
                aggregated[key] = {
                    "german_name": german_name,
                    "original_name": orig_name,
                    "quantity": qty,
                    "unit": unit,
                    "category": category
                }
            else:
                aggregated[key]["quantity"] += qty
    return list(aggregated.values())

def calculate_weekly_basket_strategies(aggregated_ingredients, db, planning_week="Current Week"):
    stores = ["Aldi Nord", "Kaufland", "Lidl", "REWE", "Edeka", "Netto"]
    store_totals = {store: 0.0 for store in stores}
    store_itemized = {store: [] for store in stores}
    multi_store_split = []

    for ing in aggregated_ingredients:
        german_name = ing["german_name"]
        orig_name = ing["original_name"]
        category = ing["category"]
        quantity = ing["quantity"]
        unit = ing["unit"]
        
        cheapest_price = float('inf')
        cheapest_store = ""
        cheapest_product_name = ""
        cheapest_is_sale = False

        for store in stores:
            price_info = find_best_ingredient_price(
                german_sku=german_name,
                store_name=store,
                db=db,
                category=category,
                quantity=quantity,
                unit=unit,
                planning_week=planning_week
            )
            total_cost = price_info["price"]
            store_totals[store] += total_cost
            
            store_itemized[store].append({
                "Ingredient (Original)": orig_name,
                "German Store Match": german_name,
                "Quantity": f"{quantity:.1f} {unit}",
                "Matched Product": price_info["product_name"],
                "Pricing Tier": f"{price_info.get('pricing_tier', 'Standard')} {'🏷️' if price_info['is_on_sale'] else '📌'}",
                "Price (€)": total_cost
            })

            if total_cost < cheapest_price:
                cheapest_price = total_cost
                cheapest_store = store
                cheapest_product_name = price_info["product_name"]
                cheapest_is_sale = price_info["is_on_sale"]

        multi_store_split.append({
            "Original Ingredient": orig_name,
            "German Supermarket Match": german_name,
            "Quantity": f"{quantity:.1f} {unit}",
            "Buy At Supermarket": cheapest_store,
            "Matched Product": cheapest_product_name,
            "Price Type": "Sale Offer 🏷️" if cheapest_is_sale else "Baseline/Normal 📌",
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

def calculate_cheapest_recipes(recipes, db, planning_week="Current Week", limit=5):
    evaluated_recipes = []
    for r in recipes:
        agg = aggregate_weekly_ingredients([{"recipe": r, "servings": 1}])
        strategy = calculate_weekly_basket_strategies(agg, db, planning_week=planning_week)
        evaluated_recipes.append({
            "recipe": r,
            "cheapest_cost": strategy["multi_store_total"],
            "cheapest_store": strategy["best_single_store"],
            "sale_count": sum(1 for item in strategy["multi_store_split"] if "Sale Offer" in item["Price Type"])
        })
    evaluated_recipes.sort(key=lambda x: (x["cheapest_cost"], -x["sale_count"]))
    return evaluated_recipes[:limit]

st.markdown("""
<div class="brand-header">
    <h1 class="brand-title">🥗 Pro-Meal</h1>
    <p class="brand-tagline">Smart Circular Deals & Weekly Meal Optimization (Berlin 10369)</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏷️ Top Deals This Week",
    "📅 Weekly Meal Planner",
    "📖 Recipe Manager",
    "🧾 Receipt Parser",
    "📈 Price History"
])

with tab1:
    st.header("Weekly Store Circular Deals")
    db = get_db()
    try:
        offers = db.query(Offer).all()
        table_data = [
            {
                "Supermarket": o.supermarket_name,
                "Product Name": o.product_name,
                "Category": o.category,
                "Offer Price (€)": f"{o.offer_price:.2f}",
                "Original Price (€)": f"{(o.original_price or 0.0):.2f}"
            }
            for o in offers
        ]
        df = pd.DataFrame(table_data)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No active circular deals found in database.")
    finally:
        db.close()

# -----------------------------------------------------------------------------
# WEEKLY MEAL PLANNER TAB WITH INTEGRATED PLANNING TARGET TOGGLE
# -----------------------------------------------------------------------------
with tab2:
    st.header("Weekly Meal Planner & Basket Optimization")
    
    # Clean layout integration: Horizontal selector at the top of Tab 2
    st.markdown("### ⚙️ Planning Target Selection")
    st.session_state.planning_week = st.radio(
        "Planning Target:",
        ["Current Week 🟢", "Next Week ⏭️"],
        index=0 if st.session_state.planning_week == "Current Week 🟢" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    
    planning_target = "Current Week" if "Current" in st.session_state.planning_week else "Next Week"
    st.info(f"Active Pricing Mode: **{planning_target}**")
    st.divider()

    db = get_db()
    try:
        all_recipes = load_cached_recipes()
        if not all_recipes:
            st.warning("No recipes found in database.")
        else:
            planning_mode = st.radio(
                "Select Planning Strategy Mode:",
                ["MODE 1: Auto-Generated Lowest-Cost Meal Plan", "MODE 2: Custom Selection & Smart Basket Comparison"],
                horizontal=True
            )
            st.divider()

            if planning_mode == "MODE 1: Auto-Generated Lowest-Cost Meal Plan":
                st.subheader(f"⚡ Top 5 Lowest-Cost Recipes ({planning_target})")
                top_deals = calculate_cheapest_recipes(all_recipes, db, planning_week=planning_target, limit=5)
                auto_config = []
                for item in top_deals:
                    rec = item["recipe"]
                    st.write(f"- 🍲 **{rec['title']}** — Est. Cost: **€{item['cheapest_cost']:.2f}**")
                    auto_config.append({"recipe": rec, "servings": 1})

                st.divider()
                st.subheader("Optimized Basket Strategy")
                agg_ingredients = aggregate_weekly_ingredients(auto_config)
                strategy_data = calculate_weekly_basket_strategies(agg_ingredients, db, planning_week=planning_target)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Best Single Supermarket", f"€{strategy_data['best_single_total']:.2f}", delta=strategy_data['best_single_store'])
                with m2:
                    st.metric("Multi-Store Split Total", f"€{strategy_data['multi_store_total']:.2f}", delta="Optimized")
                with m3:
                    st.metric("Total Saved via Split", f"€{strategy_data['max_savings']:.2f}")

                split_df = pd.DataFrame(strategy_data["multi_store_split"])
                split_df["Price (€)"] = split_df["Price (€)"].map(lambda v: f"{v:.2f}")
                st.dataframe(split_df, use_container_width=True, hide_index=True)
            else:
                st.subheader("1. Pick Your Recipes & Portions")
                selected_titles = st.multiselect(
                    "Choose recipes for the week:",
                    options=[r["title"] for r in all_recipes],
                    default=[all_recipes[0]["title"]] if all_recipes else []
                )
                selected_recipes_config = []
                if selected_titles:
                    cols = st.columns(min(len(selected_titles), 4))
                    for idx, title in enumerate(selected_titles):
                        rec = next(r for r in all_recipes if r["title"] == title)
                        with cols[idx % 4]:
                            servings = st.number_input(f"Portions: {rec['title']}", min_value=1, max_value=20, value=1, key=f"custom_serv_{rec['id']}")
                            selected_recipes_config.append({"recipe": rec, "servings": servings})

                    st.divider()
                    st.subheader("2. Basket Cost Strategy Breakdown")
                    agg_ingredients = aggregate_weekly_ingredients(selected_recipes_config)
                    strategy_data = calculate_weekly_basket_strategies(agg_ingredients, db, planning_week=planning_target)

                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.metric("Single Supermarket Winner", f"€{strategy_data['best_single_total']:.2f}", delta=f"Cheapest: {strategy_data['best_single_store']}")
                    with m2:
                        st.metric("Multi-Store Split Strategy", f"€{strategy_data['multi_store_total']:.2f}", delta="Optimized")
                    with m3:
                        st.metric("Extra Savings via Split", f"€{strategy_data['max_savings']:.2f}")

                    split_df = pd.DataFrame(strategy_data["multi_store_split"])
                    split_df["Price (€)"] = split_df["Price (€)"].map(lambda v: f"{v:.2f}")
                    st.dataframe(split_df, use_container_width=True, hide_index=True)
    finally:
        db.close()

with tab3:
    st.header("Recipe Manager")
    db = get_db()
    try:
        recipes_list = load_cached_recipes()
        for r in recipes_list:
            with st.expander(f"🍲 **{r['title']}** ({len(r['ingredients'])} ingredients)"):
                for ing in r["ingredients"]:
                    st.write(f"- {ing['quantity']} {ing['unit']} **{ing.get('original_name', ing.get('name'))}** *(SKU: `{ing.get('mapped_german_item')}`)*")
    finally:
        db.close()

with tab4:
    st.header("🧾 Supermarket Receipt Upload & Price Logger")
    st.caption("Upload a receipt image or PDF to extract item prices via OCR and update your historical price database automatically.")
    
    uploaded_receipt = st.file_uploader("Upload Supermarket Receipt", type=["png", "jpg", "jpeg", "pdf"], key="receipt_uploader")
    
    if uploaded_receipt is not None:
        st.image(uploaded_receipt, caption="Uploaded Receipt Preview", width=300)
        if st.button("🔍 Parse Receipt & Update Prices", type="primary"):
            db = get_db()
            try:
                result = parse_and_log_receipt(uploaded_receipt, db)
                st.success(f"Successfully processed receipt from **{result['store']}**!")
                if result["items"]:
                    st.write("### Extracted & Logged Items:")
                    res_df = pd.DataFrame(result["items"])
                    st.dataframe(res_df, use_container_width=True, hide_index=True)
                else:
                    st.warning("No line item prices could be automatically matched. Try uploading a clearer receipt image.")
            except Exception as e:
                st.error(f"Error parsing receipt: {e}")
            finally:
                db.close()

with tab5:
    st.header("Historical Price Trends & Advance Baselines")
    db = get_db()
    try:
        baselines = db.query(StandardBaselinePrice).all()
        if baselines:
            base_df = pd.DataFrame([
                {"Supermarket": b.supermarket_name, "Product": b.product_name, "Standard Price (€)": b.price, "Category": b.category}
                for b in baselines
            ])
            st.subheader("Advance Prospekt Baseline Indexing (Normal Pricing)")
            st.dataframe(base_df, use_container_width=True, hide_index=True)

        history_records = db.query(PriceHistory).all()
        if history_records:
            hist_df = pd.DataFrame([
                {"Product": h.product_name, "Supermarket": h.supermarket_name, "Price": h.price, "Date": h.recorded_date}
                for h in history_records
            ])
            selected_product = st.selectbox("Select product to inspect history:", options=hist_df["Product"].unique())
            filtered_hist = hist_df[hist_df["Product"] == selected_product].sort_values(by="Date")
            fig = px.line(filtered_hist, x="Date", y="Price", color="Supermarket", markers=True, title=f"Price History: {selected_product}")
            st.plotly_chart(fig, use_container_width=True)
    finally:
        db.close()

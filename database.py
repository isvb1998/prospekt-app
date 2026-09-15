import json
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, Boolean, ForeignKey, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///pro_meal.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    supermarket_name = Column(String, index=True)
    product_name = Column(String, index=True)
    category = Column(String, index=True)
    current_price = Column(Float)
    original_price = Column(Float)
    is_on_sale = Column(Boolean, default=True)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    instructions = Column(Text, default="")
    category = Column(String, nullable=True, default="Main Course")
    servings = Column(Integer, default=1)
    ingredients = Column(JSON, default=list)

    # Optional relational mapping if using dedicated Ingredient objects
    ingredient_objects = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    name = Column(String, index=True)  # Original ingredient name
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="Stück")
    mapped_german_item = Column(String, index=True, nullable=True)  # Normalized German SKU match
    generic_category = Column(String, nullable=True, default="Vorrat")  # Molkerei, Fleisch, etc.

    recipe = relationship("Recipe", back_populates="ingredient_objects")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    supermarket_name = Column(String, index=True)
    price = Column(Float)
    recorded_date = Column(String)


def apply_migrations():
    """Safely adds missing columns to existing SQLite database tables without data loss."""
    inspector = inspect(engine)
    
    # Check if 'ingredients' table exists and lacks 'generic_category'
    if inspector.has_table("ingredients"):
        columns = [col["name"] for col in inspector.get_columns("ingredients")]
        with engine.begin() as conn:
            if "generic_category" not in columns:
                conn.execute(text("ALTER TABLE ingredients ADD COLUMN generic_category TEXT;"))
            if "mapped_german_item" not in columns:
                conn.execute(text("ALTER TABLE ingredients ADD COLUMN mapped_german_item TEXT;"))

    # Check if 'recipes' table lacks 'category' or 'servings'
    if inspector.has_table("recipes"):
        recipe_cols = [col["name"] for col in inspector.get_columns("recipes")]
        with engine.begin() as conn:
            if "category" not in recipe_cols:
                conn.execute(text("ALTER TABLE recipes ADD COLUMN category TEXT DEFAULT 'Main Course';"))
            if "servings" not in recipe_cols:
                conn.execute(text("ALTER TABLE recipes ADD COLUMN servings INTEGER DEFAULT 1;"))


def init_db():
    Base.metadata.create_all(bind=engine)
    apply_migrations()

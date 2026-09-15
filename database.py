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
    category = Column(String, nullable=True)
    offer_price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    valid_from = Column(String, nullable=True)
    valid_to = Column(String, nullable=True)


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    instructions = Column(Text, default="")
    category = Column(String, nullable=True, default="Main Course")
    servings = Column(Integer, default=1)
    ingredients = Column(JSON, default=list)

    ingredient_objects = relationship("Ingredient", back_populates="recipe", cascade="all, delete-orphan")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=True)
    name = Column(String, index=True)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="Stück")
    mapped_german_item = Column(String, index=True, nullable=True)
    generic_category = Column(String, nullable=True, default="Vorrat")

    recipe = relationship("Recipe", back_populates="ingredient_objects")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    supermarket_name = Column(String, index=True)
    price = Column(Float)
    recorded_date = Column(String)


class UserLearnedMapping(Base):
    __tablename__ = "user_learned_mappings"

    id = Column(Integer, primary_key=True, index=True)
    raw_ingredient = Column(String, unique=True, index=True)
    mapped_german_item = Column(String)


def apply_migrations():
    inspector = inspect(engine)

    if inspector.has_table("offers"):
        offer_cols = [col["name"] for col in inspector.get_columns("offers")]
        with engine.begin() as conn:
            if "offer_price" not in offer_cols and "current_price" in offer_cols:
                conn.execute(text("ALTER TABLE offers RENAME COLUMN current_price TO offer_price;"))
            elif "offer_price" not in offer_cols:
                conn.execute(text("ALTER TABLE offers ADD COLUMN offer_price FLOAT DEFAULT 0.0;"))
            if "valid_from" not in offer_cols:
                conn.execute(text("ALTER TABLE offers ADD COLUMN valid_from TEXT;"))
            if "valid_to" not in offer_cols:
                conn.execute(text("ALTER TABLE offers ADD COLUMN valid_to TEXT;"))

    if inspector.has_table("ingredients"):
        columns = [col["name"] for col in inspector.get_columns("ingredients")]
        with engine.begin() as conn:
            if "generic_category" not in columns:
                conn.execute(text("ALTER TABLE ingredients ADD COLUMN generic_category TEXT;"))
            if "mapped_german_item" not in columns:
                conn.execute(text("ALTER TABLE ingredients ADD COLUMN mapped_german_item TEXT;"))

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

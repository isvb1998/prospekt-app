import json
from datetime import date, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///prospekt_optimizer.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Supermarket(Base):
    __tablename__ = "supermarkets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    postal_code = Column(String, default="10369")
    
    offers = relationship("Offer", back_populates="supermarket")


class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    supermarket_name = Column(String, ForeignKey("supermarkets.name"), nullable=False)
    product_name = Column(String, nullable=False)
    generic_category = Column(String, nullable=False)  # Generic term: "Butter", "Milch", "Hackfleisch"
    category = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=False)
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=False)
    
    supermarket = relationship("Supermarket", back_populates="offers")


class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    supermarket_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    recorded_date = Column(Date, nullable=False)


class Recipe(Base):
    __tablename__ = "recipes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    instructions = Column(Text, nullable=False)
    ingredients_json = Column(Text, nullable=False)

    @property
    def ingredients(self):
        return json.loads(self.ingredients_json)

    @ingredients.setter
    def ingredients(self, value):
        self.ingredients_json = json.dumps(value)


def init_db():
    Base.metadata.create_all(bind=engine)
    seed_initial_data()


def seed_initial_data():
    db = SessionLocal()
    try:
        if db.query(Supermarket).count() > 0:
            return  # Already seeded

        # Stores for PLZ 10369 (Berlin - Landsberger Allee / Storkower Straße)
        stores = ["Aldi Nord", "Kaufland", "Lidl", "REWE", "Edeka", "Netto"]
        for s in stores:
            db.add(Supermarket(name=s, postal_code="10369"))
        db.commit()

        # Seed Sample Recipes
        initial_recipes = [
            {
                "title": "Klassisches Spaghetti Bolognese",
                "instructions": "1. Hackfleisch in Öl anbraten.\n2. Zwiebeln & Knoblauch dazugeben.\n3. Passierte Tomaten dazugeben und köcheln lassen.\n4. Spaghetti kochen und mit Sauce servieren.",
                "ingredients": [
                    {"name": "Hackfleisch", "quantity": 500, "unit": "g", "optional": False},
                    {"name": "Spaghetti", "quantity": 500, "unit": "g", "optional": False},
                    {"name": "Passierte Tomaten", "quantity": 400, "unit": "g", "optional": False},
                    {"name": "Zwiebeln", "quantity": 2, "unit": "Stück", "optional": False},
                    {"name": "Knoblauch", "quantity": 1, "unit": "Zehe", "optional": True}
                ]
            },
            {
                "title": "Kräuter-Quark mit Kartoffeln",
                "instructions": "1. Kartoffeln kochen.\n2. Quark mit etwas Milch glattrühren.\n3. Frische Kräuter hacken und unterrühren.\n4. Mit Butter servieren.",
                "ingredients": [
                    {"name": "Quark", "quantity": 500, "unit": "g", "optional": False},
                    {"name": "Kartoffeln", "quantity": 1000, "unit": "g", "optional": False},
                    {"name": "Milch", "quantity": 50, "unit": "ml", "optional": False},
                    {"name": "Butter", "quantity": 50, "unit": "g", "optional": True}
                ]
            },
            {
                "title": "Cremiger Milchreis mit Zimt",
                "instructions": "1. Milch aufkochen.\n2. Milchreis einrühren.\n3. Bei schwacher Hitze 25 Min. quellen lassen.\n4. Mit Butter & Zimt servieren.",
                "ingredients": [
                    {"name": "Milchreis", "quantity": 250, "unit": "g", "optional": False},
                    {"name": "Milch", "quantity": 1000, "unit": "ml", "optional": False},
                    {"name": "Butter", "quantity": 20, "unit": "g", "optional": True}
                ]
            }
        ]

        for r_data in initial_recipes:
            recipe = Recipe(title=r_data["title"], instructions=r_data["instructions"])
            recipe.ingredients = r_data["ingredients"]
            db.add(recipe)

        db.commit()
    finally:
        db.close()

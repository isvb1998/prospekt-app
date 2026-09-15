import json
from datetime import date, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "sqlite:///prospekt_optimizer.db"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Supermarket(Base):
    __tablename__ = "supermarkets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    
    offers = relationship("Offer", back_populates="supermarket")


class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    supermarket_name = Column(String, ForeignKey("supermarkets.name"), nullable=False)
    product_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=False)
    discount_percent = Column(Float, nullable=False)
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
    ingredients_json = Column(Text, nullable=False)  # JSON stored string: [{"name": "", "quantity": 1.0, "unit": "g", "optional": False}]

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
            return  # Data already seeded

        # Supermarkets
        stores = ["Aldi Süd", "Lidl", "Kaufland", "REWE"]
        for s in stores:
            db.add(Supermarket(name=s))
        db.commit()

        # Seed Recipes
        initial_recipes = [
            {
                "title": "Klassisches Spaghetti Bolognese",
                "instructions": "1. Hackfleisch in Öl anbraten.\n2. Zwiebeln & Knoblauch dazugeben.\n3. Passierte Tomaten dazugeben und köcheln lassen.\n4. Spaghetti kochen und mit Sauce servieren.",
                "ingredients": [
                    {"name": "Hackfleisch, gemischt", "quantity": 500, "unit": "g", "optional": False},
                    {"name": "Spaghetti", "quantity": 500, "unit": "g", "optional": False},
                    {"name": "Passierte Tomaten", "quantity": 400, "unit": "g", "optional": False},
                    {"name": "Zwiebeln", "quantity": 2, "unit": "Stück", "optional": False},
                    {"name": "Knoblauch", "quantity": 1, "unit": "Zehe", "optional": True},
                    {"name": "Olive Oil", "quantity": 2, "unit": "EL", "optional": True}
                ]
            },
            {
                "title": "Erfrischender Kräuter-Quark mit Kartoffeln",
                "instructions": "1. Kartoffeln kochen.\n2. Quark mit Milch glattrühren.\n3. Frische Kräuter hacken und unter den Quark heben.\n4. Mit Salz und Pfeffer abschmecken.",
                "ingredients": [
                    {"name": "Magerquark", "quantity": 500, "unit": "g", "optional": False},
                    {"name": "Kartoffeln", "quantity": 1000, "unit": "g", "optional": False},
                    {"name": "Milch", "quantity": 50, "unit": "ml", "optional": False},
                    {"name": "Butter", "quantity": 50, "unit": "g", "optional": True},
                    {"name": "Schnittlauch", "quantity": 1, "unit": "Bund", "optional": True}
                ]
            },
            {
                "title": "Cremiger Milchreis mit Zimt & Zucker",
                "instructions": "1. Milch aufkochen.\n2. Milchreis & Prise Salz einrühren.\n3. Bei schwacher Hitze 25 Min. quellen lassen.\n4. Mit Zimt und Zucker servieren.",
                "ingredients": [
                    {"name": "Milchreis", "quantity": 250, "unit": "g", "optional": False},
                    {"name": "Vollmilch", "quantity": 1000, "unit": "ml", "optional": False},
                    {"name": "Butter", "quantity": 20, "unit": "g", "optional": True},
                    {"name": "Zucker", "quantity": 2, "unit": "EL", "optional": True}
                ]
            }
        ]

        for r_data in initial_recipes:
            recipe = Recipe(
                title=r_data["title"],
                instructions=r_data["instructions"]
            )
            recipe.ingredients = r_data["ingredients"]
            db.add(recipe)

        db.commit()

        # Seed Price History (Last 90 Days)
        today = date.today()
        history_data = [
            ("Deutsche Markenbutter", "Aldi Süd", 2.59),
            ("Deutsche Markenbutter", "Lidl", 2.49),
            ("Hackfleisch", "Kaufland", 4.99),
            ("Hackfleisch", "REWE", 5.49),
            ("Vollmilch 3.5%", "Lidl", 1.15),
            ("Vollmilch 3.5%", "Aldi Süd", 1.09),
            ("Speisequark Magerstufe", "REWE", 1.49),
            ("Barilla Spaghetti", "Kaufland", 1.99),
            ("Tchibo Kaffee Feine Milde", "REWE", 6.99)
        ]

        for item, store, base_price in history_data:
            for days_ago in range(90, 0, -10):
                # Add slight random float variation to history
                variation = (days_ago % 3 - 1) * 0.10
                hist_date = today - timedelta(days=days_ago)
                db.add(PriceHistory(
                    product_name=item,
                    supermarket_name=store,
                    price=round(base_price + variation, 2),
                    recorded_date=hist_date
                ))

        db.commit()
    finally:
        db.close()

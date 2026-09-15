import json
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, JSON, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

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
    ingredients = Column(JSON, default=list)

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, index=True)
    supermarket_name = Column(String, index=True)
    price = Column(Float)
    recorded_date = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

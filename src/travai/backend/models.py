from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# 📌 Modèle des aliments génériques
class Food(Base):
    __tablename__ = "foods"

    food_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String)
    calories_per_100g = Column(Float, nullable=False)
    proteins_per_100g = Column(Float, nullable=False)
    carbs_per_100g = Column(Float, nullable=False)
    fats_per_100g = Column(Float, nullable=False)

# 📌 Modèle des repas
class Meal(Base):
    __tablename__ = "meals"

    meal_id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String, nullable=False)
    total_calories = Column(Float)
    total_proteins = Column(Float)
    total_carbs = Column(Float)
    total_fats = Column(Float)
    meal_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relation avec les aliments détectés
    detected_foods = relationship("DetectedFood", back_populates="meal")

# 📌 Modèle des aliments détectés dans un repas
class DetectedFood(Base):
    __tablename__ = "detected_foods"

    detected_food_id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.meal_id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.food_id"), nullable=False)
    confidence_score = Column(Float, nullable=False)
    estimated_weight = Column(Float, nullable=False)

    # Relations
    meal = relationship("Meal", back_populates="detected_foods")
    food = relationship("Food")
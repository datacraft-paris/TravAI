from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base



class Doctor(Base):
    __tablename__ = "doctors"

    doctor_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

class Patient(Base):
    __tablename__ = "patients"

    patient_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    doctor_id = Column(Integer, ForeignKey("doctors.doctor_id"), nullable=True)

class Meal(Base):
    __tablename__ = "meals"

    meal_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    date_start = Column(DateTime, nullable=False)
    image_path = Column(String, nullable=False)
    name = Column(String, nullable=False)

class Ingredient(Base):
    __tablename__ = "ingredients"

    ingredient_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    calories_per_100g = Column(Float, nullable=False)

class DetectedIngredient(Base):
    __tablename__ = "detected_ingredients"

    detected_ingredient_id = Column(Integer, primary_key=True, index=True)
    meal_id = Column(Integer, ForeignKey("meals.meal_id"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.ingredient_id"), nullable=False)
    ingredient_name = Column(String, nullable=False)
    quantity_grams = Column(Float, nullable=False)

class ModifiedIngredient(Base):
    __tablename__ = "modified_ingredients"

    modified_ingredient_id = Column(Integer, primary_key=True, index=True)
    detected_ingredient_id = Column(Integer, ForeignKey("detected_ingredients.detected_ingredient_id"), nullable=False)
    quantity_grams = Column(Float, nullable=False)

class Goal(Base):
    __tablename__ = "goals"

    goal_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)
    calories_in_grams_per_day = Column(Float, nullable=False)
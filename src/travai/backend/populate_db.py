from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from travai.backend.database import SessionLocal, engine, Base
from travai.backend.models import Patient, Doctor, Meal, Ingredient, DetectedIngredient, ModifiedIngredient, Goal


Base.metadata.create_all(bind=engine)

def populate_database():
    session = SessionLocal()

    try:
        # Add doctors
        doctor1 = Doctor(first_name="John", last_name="Doe", email="johndoe@example.com", password="hashed_password1")

        session.add_all([doctor1])
        session.commit()

        # add patient to doctors
        patient1 = Patient(first_name="Emma", last_name="Johnson", email="emma@example.com", password="hashed_password3", doctor_id=doctor1.doctor_id)
        patient2 = Patient(first_name="Liam", last_name="Brown", email="liam@example.com", password="hashed_password4", doctor_id=doctor1.doctor_id)

        session.add_all([patient1, patient2])
        session.commit()



        # Add meals to patients
        meal1 = Meal(patient_id=patient1.patient_id, date_start=datetime.now(), image_path="meal1.jpg", name="Breakfast")
        meal2 = Meal(patient_id=patient2.patient_id, date_start=datetime.now() - timedelta(days=1), image_path="meal2.jpg", name="Lunch")

        session.add_all([meal1, meal2])
        session.commit()

        # Add ingredients
        ingredient1 = Ingredient(name="Chicken Breast", calories_per_100g=165.0)
        ingredient2 = Ingredient(name="Rice", calories_per_100g=130.0)

        session.add_all([ingredient1, ingredient2])
        session.commit()

        # Add detected ingredients
        detected1 = DetectedIngredient(meal_id=meal1.meal_id, ingredient_id=ingredient1.ingredient_id, ingredient_name="Chicken Breast", quantity_grams=150.0)
        detected2 = DetectedIngredient(meal_id=meal2.meal_id, ingredient_id=ingredient2.ingredient_id, ingredient_name="Rice", quantity_grams=200.0)

        session.add_all([detected1, detected2])
        session.commit()

        # Add modified ingredients
        modified1 = ModifiedIngredient(detected_ingredient_id=detected1.detected_ingredient_id, quantity_grams=180.0)
        modified2 = ModifiedIngredient(detected_ingredient_id=detected2.detected_ingredient_id, quantity_grams=250.0)

        session.add_all([modified1, modified2])
        session.commit()

        # Add goals
        goal1 = Goal(patient_id=patient1.patient_id, date_start=datetime.now(), date_end=datetime.now() + timedelta(days=30), calories_in_grams_per_day=2000.0)
        goal2 = Goal(patient_id=patient2.patient_id, date_start=datetime.now(), date_end=datetime.now() + timedelta(days=15), calories_in_grams_per_day=1800.0)

        session.add_all([goal1, goal2])
        session.commit()

        print("Base de données peuplée avec succès !")

    except Exception as e:
        session.rollback()
        print(f"Erreur lors du peuplement de la base : {e}")

    finally:
        session.close()

# Exécuter le script
if __name__ == "__main__":
    populate_database()
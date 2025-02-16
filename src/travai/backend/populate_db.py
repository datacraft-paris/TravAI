from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from travai.backend.database import SessionLocal
from travai.backend.models import Patient, Doctor, Meal, Ingredient, DetectedIngredient, ModifiedIngredient, Goal


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



        print("Base de données peuplée avec succès !")

    except Exception as e:
        session.rollback()
        print(f"Erreur lors du peuplement de la base : {e}")

    finally:
        session.close()

# Exécuter le script
if __name__ == "__main__":
    populate_database()
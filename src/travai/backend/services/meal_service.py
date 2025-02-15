from sqlalchemy.orm import Session
from database import SessionLocal
from models import Meal, Patient
from datetime import datetime

def create_meal(patient_id: int, date_start: datetime, image_path: str, name: str):
    """
    Creates a new meal and assigns it to a patient.

    :param patient_id: ID of the patient who consumed the meal
    :param date_start: Date and time when the meal was consumed
    :param image_path: Path to the image of the meal
    :param name: Name of the meal
    :return: The created Meal object or None if an error occurs
    """
    session = SessionLocal()

    try:
        # Verify that the patient exists before creating the meal
        patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            print("Patient ID does not exist.")
            return None

        # Create a new Meal object
        new_meal = Meal(
            patient_id=patient_id,
            date_start=date_start,
            image_path=image_path,
            name=name
        )

        # Add the meal to the database
        session.add(new_meal)
        session.commit()
        session.refresh(new_meal)  # Refresh instance with DB values

        print(f"Meal created: {new_meal.name} for Patient ID {new_meal.patient_id}")
        return new_meal

    except Exception as e:
        session.rollback()
        print(f"Error while adding the meal: {e}")
        return None

    finally:
        session.close()


def get_meal_by_id(meal_id: int):
    """
    Retrieves a meal from the database using its ID.

    :param meal_id: The ID of the meal to retrieve
    :return: The Meal object if found, else None
    """
    session = SessionLocal()
    try:
        meal = session.query(Meal).filter(Meal.meal_id == meal_id).first()
        if meal:
            print(f"Meal found: {meal.name} (Meal ID: {meal.meal_id})")
        return meal
    except Exception as e:
        print(f"Error retrieving meal: {e}")
        return None
    finally:
        session.close()


def get_meals_by_patient(patient_id: int):
    """
    Retrieves all meals associated with a specific patient.

    :param patient_id: The ID of the patient whose meals are to be retrieved
    :return: A list of Meal objects or an empty list if none found
    """
    session = SessionLocal()
    try:
        meals = session.query(Meal).filter(Meal.patient_id == patient_id).all()
        print(f"{len(meals)} meals found for Patient ID {patient_id}")
        return meals
    except Exception as e:
        print(f"Error retrieving meals: {e}")
        return []
    finally:
        session.close()


def update_meal(meal_id: int, date_start: datetime = None, image_path: str = None, name: str = None):
    """
    Updates meal details in the database.

    :param meal_id: The ID of the meal to update
    :param date_start: (Optional) New date and time for the meal
    :param image_path: (Optional) New image path
    :param name: (Optional) New meal name
    :return: The updated Meal object or None if not found
    """
    session = SessionLocal()
    try:
        meal = session.query(Meal).filter(Meal.meal_id == meal_id).first()
        if not meal:
            print("Meal not found.")
            return None

        # Update fields if new values are provided
        if date_start:
            meal.date_start = date_start
        if image_path:
            meal.image_path = image_path
        if name:
            meal.name = name

        session.commit()
        session.refresh(meal)

        print(f"Meal updated: {meal.name} (Meal ID: {meal.meal_id})")
        return meal

    except Exception as e:
        session.rollback()
        print(f"Error updating meal: {e}")
        return None
    finally:
        session.close()


def delete_meal(meal_id: int):
    """
    Deletes a meal from the database.

    :param meal_id: The ID of the meal to delete
    :return: True if deleted successfully, False otherwise
    """
    session = SessionLocal()
    try:
        meal = session.query(Meal).filter(Meal.meal_id == meal_id).first()
        if not meal:
            print("Meal not found.")
            return False

        session.delete(meal)
        session.commit()

        print(f"Meal deleted: {meal.name} (Meal ID: {meal.meal_id})")
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting meal: {e}")
        return False
    finally:
        session.close()
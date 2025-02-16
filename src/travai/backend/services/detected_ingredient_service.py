from sqlalchemy.orm import Session
from travai.backend.database import SessionLocal
from travai.backend.models import DetectedIngredient, Meal, Ingredient, ModifiedIngredient

def create_detected_ingredient(meal_id: int, ingredient_id: int, ingredient_name: str, quantity_grams: float, calculated_calories:float):
    """
    Creates a new detected ingredient and assigns it to a meal.

    :param meal_id: ID of the meal where the ingredient was detected
    :param ingredient_id: ID of the detected ingredient
    :param ingredient_name: Name of the detected ingredient
    :param quantity_grams: Quantity of the ingredient in grams
    :return: The created DetectedIngredient object or None if an error occurs
    """
    session = SessionLocal()

    try:
        # Verify that the meal exists
        meal = session.query(Meal).filter(Meal.meal_id == meal_id).first()
        if not meal:
            print("Meal ID does not exist.")
            return None

        # Verify that the ingredient exists
        ingredient = session.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id).first()
        if not ingredient:
            print("Ingredient ID does not exist.")
            return None

        # Create a new DetectedIngredient object
        new_detected_ingredient = DetectedIngredient(
            meal_id=meal_id,
            ingredient_id=ingredient_id,
            ingredient_name=ingredient_name,
            quantity_grams=quantity_grams,
            calculated_calories=calculated_calories,
        )

        # Add the detected ingredient to the database
        session.add(new_detected_ingredient)
        session.commit()
        session.refresh(new_detected_ingredient)  # Refresh instance with DB values

        print(f"Detected ingredient created: {new_detected_ingredient.ingredient_name} ({new_detected_ingredient.quantity_grams}g) in Meal ID {new_detected_ingredient.meal_id}")
        return new_detected_ingredient

    except Exception as e:
        session.rollback()
        print(f"Error while adding the detected ingredient: {e}")
        return None

    finally:
        session.close()


def get_detected_ingredient_by_id(detected_ingredient_id: int):
    """
    Retrieves a detected ingredient from the database using its ID.

    :param detected_ingredient_id: The ID of the detected ingredient to retrieve
    :return: The DetectedIngredient object if found, else None
    """
    session = SessionLocal()
    try:
        detected_ingredient = session.query(DetectedIngredient).filter(DetectedIngredient.detected_ingredient_id == detected_ingredient_id).first()
        if detected_ingredient:
            print(f"Detected ingredient found: {detected_ingredient.ingredient_name} ({detected_ingredient.quantity_grams}g)")
        return detected_ingredient
    except Exception as e:
        print(f"Error retrieving detected ingredient: {e}")
        return None
    finally:
        session.close()


def get_detected_ingredients_by_meal(meal_id: int):
    """
    Retrieves all detected ingredients for a specific meal.

    :param meal_id: The ID of the meal whose detected ingredients are to be retrieved
    :return: A list of DetectedIngredient objects or an empty list if none found
    """
    session = SessionLocal()
    try:
        detected_ingredients = session.query(DetectedIngredient).filter(DetectedIngredient.meal_id == meal_id).all()
        print(f"{len(detected_ingredients)} detected ingredients found for Meal ID {meal_id}")
        return detected_ingredients
    except Exception as e:
        print(f"Error retrieving detected ingredients: {e}")
        return []
    finally:
        session.close()


def update_detected_ingredient(detected_ingredient_id: int, ingredient_name: str = None, quantity_grams: float = None, calculated_calories: float = None):
    """
    Updates details of a detected ingredient in the database.

    :param detected_ingredient_id: The ID of the detected ingredient to update
    :param ingredient_name: (Optional) New name of the detected ingredient
    :param quantity_grams: (Optional) New quantity in grams
    :return: The updated DetectedIngredient object or None if not found
    """
    session = SessionLocal()
    try:
        detected_ingredient = session.query(DetectedIngredient).filter(DetectedIngredient.detected_ingredient_id == detected_ingredient_id).first()
        if not detected_ingredient:
            print("Detected ingredient not found.")
            return None

        # Update fields if new values are provided
        if ingredient_name:
            detected_ingredient.ingredient_name = ingredient_name
        if quantity_grams is not None:
            detected_ingredient.quantity_grams = quantity_grams
        if calculated_calories is not None:
            detected_ingredient.calculated_calories = calculated_calories

        session.commit()
        session.refresh(detected_ingredient)

        print(f"Detected ingredient updated: {detected_ingredient.ingredient_name} ({detected_ingredient.quantity_grams}g)")
        return detected_ingredient

    except Exception as e:
        session.rollback()
        print(f"Error updating detected ingredient: {e}")
        return None
    finally:
        session.close()


def delete_detected_ingredient(detected_ingredient_id: int):
    """
    Deletes a detected ingredient from the database and removes all associated modified ingredients.

    :param detected_ingredient_id: The ID of the detected ingredient to delete
    :return: True if deleted successfully, False otherwise
    """
    session = SessionLocal()
    try:
        # Find the detected ingredient by ID
        detected_ingredient = session.query(DetectedIngredient).filter(DetectedIngredient.detected_ingredient_id == detected_ingredient_id).first()
        if not detected_ingredient:
            print("Detected ingredient not found.")
            return False

        # Now delete the detected ingredient
        session.delete(detected_ingredient)
        session.commit()

        print(f"Detected ingredient deleted: {detected_ingredient.ingredient_name} (All associated modified ingredients removed)")
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting detected ingredient: {e}")
        return False
    finally:
        session.close()
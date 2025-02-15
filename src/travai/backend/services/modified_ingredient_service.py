from sqlalchemy.orm import Session
from database import SessionLocal
from models import ModifiedIngredient, DetectedIngredient

def create_modified_ingredient(detected_ingredient_id: int, quantity_grams: float):
    """
    Creates a new modified ingredient and associates it with a detected ingredient.

    :param detected_ingredient_id: ID of the detected ingredient being modified
    :param quantity_grams: Updated quantity of the ingredient in grams
    :return: The created ModifiedIngredient object or None if an error occurs
    """
    session = SessionLocal()

    try:
        # Verify that the detected ingredient exists
        detected_ingredient = session.query(DetectedIngredient).filter(DetectedIngredient.detected_ingredient_id == detected_ingredient_id).first()
        if not detected_ingredient:
            print("Detected Ingredient ID does not exist.")
            return None

        # Create a new ModifiedIngredient object
        new_modified_ingredient = ModifiedIngredient(
            detected_ingredient_id=detected_ingredient_id,
            quantity_grams=quantity_grams
        )

        # Add the modified ingredient to the database
        session.add(new_modified_ingredient)
        session.commit()
        session.refresh(new_modified_ingredient)  # Refresh instance with DB values

        print(f"Modified ingredient created: {new_modified_ingredient.quantity_grams}g for Detected Ingredient ID {new_modified_ingredient.detected_ingredient_id}")
        return new_modified_ingredient

    except Exception as e:
        session.rollback()
        print(f"Error while adding the modified ingredient: {e}")
        return None

    finally:
        session.close()


def get_modified_ingredient_by_id(modified_ingredient_id: int):
    """
    Retrieves a modified ingredient from the database using its ID.

    :param modified_ingredient_id: The ID of the modified ingredient to retrieve
    :return: The ModifiedIngredient object if found, else None
    """
    session = SessionLocal()
    try:
        modified_ingredient = session.query(ModifiedIngredient).filter(ModifiedIngredient.modified_ingredient_id == modified_ingredient_id).first()
        if modified_ingredient:
            print(f"Modified ingredient found: {modified_ingredient.quantity_grams}g (Modified ID: {modified_ingredient.modified_ingredient_id})")
        return modified_ingredient
    except Exception as e:
        print(f"Error retrieving modified ingredient: {e}")
        return None
    finally:
        session.close()


def get_modified_ingredients_by_detected_ingredient(detected_ingredient_id: int):
    """
    Retrieves all modified ingredients linked to a specific detected ingredient.

    :param detected_ingredient_id: The ID of the detected ingredient
    :return: A list of ModifiedIngredient objects or an empty list if none found
    """
    session = SessionLocal()
    try:
        modified_ingredients = session.query(ModifiedIngredient).filter(ModifiedIngredient.detected_ingredient_id == detected_ingredient_id).all()
        print(f"{len(modified_ingredients)} modified ingredients found for Detected Ingredient ID {detected_ingredient_id}")
        return modified_ingredients
    except Exception as e:
        print(f"Error retrieving modified ingredients: {e}")
        return []
    finally:
        session.close()


def update_modified_ingredient(modified_ingredient_id: int, quantity_grams: float = None):
    """
    Updates details of a modified ingredient in the database.

    :param modified_ingredient_id: The ID of the modified ingredient to update
    :param quantity_grams: (Optional) New quantity in grams
    :return: The updated ModifiedIngredient object or None if not found
    """
    session = SessionLocal()
    try:
        modified_ingredient = session.query(ModifiedIngredient).filter(ModifiedIngredient.modified_ingredient_id == modified_ingredient_id).first()
        if not modified_ingredient:
            print("Modified ingredient not found.")
            return None

        # Update fields if new values are provided
        if quantity_grams is not None:
            modified_ingredient.quantity_grams = quantity_grams

        session.commit()
        session.refresh(modified_ingredient)

        print(f"Modified ingredient updated: {modified_ingredient.quantity_grams}g (Modified ID: {modified_ingredient.modified_ingredient_id})")
        return modified_ingredient

    except Exception as e:
        session.rollback()
        print(f"Error updating modified ingredient: {e}")
        return None
    finally:
        session.close()


def delete_modified_ingredient(modified_ingredient_id: int):
    """
    Deletes a modified ingredient from the database.

    :param modified_ingredient_id: The ID of the modified ingredient to delete
    :return: True if deleted successfully, False otherwise
    """
    session = SessionLocal()
    try:
        modified_ingredient = session.query(ModifiedIngredient).filter(ModifiedIngredient.modified_ingredient_id == modified_ingredient_id).first()
        if not modified_ingredient:
            print("Modified ingredient not found.")
            return False

        session.delete(modified_ingredient)
        session.commit()

        print(f"Modified ingredient deleted (ID: {modified_ingredient.modified_ingredient_id})")
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting modified ingredient: {e}")
        return False
    finally:
        session.close()
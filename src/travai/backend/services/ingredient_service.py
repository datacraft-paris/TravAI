from sqlalchemy.orm import Session
from database import SessionLocal
from models import Ingredient

def create_ingredient(name: str, calories_per_100g: float):
    """
    Creates a new ingredient in the database.

    :param name: Name of the ingredient
    :param calories_per_100g: Number of calories per 100 grams
    :return: The created Ingredient object or None if an error occurs
    """
    session = SessionLocal()

    try:
        # Check if an ingredient with the same name already exists
        existing_ingredient = session.query(Ingredient).filter(Ingredient.name == name).first()
        if existing_ingredient:
            print("An ingredient with this name already exists.")
            return None

        # Create a new Ingredient object
        new_ingredient = Ingredient(
            name=name,
            calories_per_100g=calories_per_100g
        )

        # Add the ingredient to the database
        session.add(new_ingredient)
        session.commit()
        session.refresh(new_ingredient)  # Refresh the instance with DB values

        print(f"Ingredient created: {new_ingredient.name} ({new_ingredient.calories_per_100g} kcal/100g)")
        return new_ingredient

    except Exception as e:
        session.rollback()
        print(f"Error while adding the ingredient: {e}")
        return None

    finally:
        session.close()


def get_ingredient_by_id(ingredient_id: int):
    """
    Retrieves an ingredient from the database using its ID.

    :param ingredient_id: The ID of the ingredient to retrieve
    :return: The Ingredient object if found, else None
    """
    session = SessionLocal()
    try:
        ingredient = session.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id).first()
        if ingredient:
            print(f"Ingredient found: {ingredient.name} ({ingredient.calories_per_100g} kcal/100g)")
        return ingredient
    except Exception as e:
        print(f"Error retrieving ingredient: {e}")
        return None
    finally:
        session.close()


def get_ingredient_by_name(name: str):
    """
    Retrieves an ingredient from the database using its name.

    :param name: The name of the ingredient to retrieve
    :return: The Ingredient object if found, else None
    """
    session = SessionLocal()
    try:
        ingredient = session.query(Ingredient).filter(Ingredient.name == name).first()
        if ingredient:
            print(f"Ingredient found: {ingredient.name} ({ingredient.calories_per_100g} kcal/100g)")
        return ingredient
    except Exception as e:
        print(f"Error retrieving ingredient: {e}")
        return None
    finally:
        session.close()


def get_all_ingredients():
    """
    Retrieves all ingredients from the database.

    :return: A list of Ingredient objects or an empty list if none found
    """
    session = SessionLocal()
    try:
        ingredients = session.query(Ingredient).all()
        print(f"{len(ingredients)} ingredients found.")
        return ingredients
    except Exception as e:
        print(f"Error retrieving ingredients: {e}")
        return []
    finally:
        session.close()


def update_ingredient(ingredient_id: int, name: str = None, calories_per_100g: float = None):
    """
    Updates ingredient details in the database.

    :param ingredient_id: The ID of the ingredient to update
    :param name: (Optional) New name of the ingredient
    :param calories_per_100g: (Optional) New calorie value per 100g
    :return: The updated Ingredient object or None if not found
    """
    session = SessionLocal()
    try:
        ingredient = session.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id).first()
        if not ingredient:
            print("Ingredient not found.")
            return None

        # Check if the new name is already taken by another ingredient
        if name and name != ingredient.name:
            existing_ingredient = session.query(Ingredient).filter(Ingredient.name == name).first()
            if existing_ingredient:
                print("Another ingredient with this name already exists.")
                return None
            ingredient.name = name

        # Update fields if new values are provided
        if calories_per_100g is not None:
            ingredient.calories_per_100g = calories_per_100g

        session.commit()
        session.refresh(ingredient)

        print(f"Ingredient updated: {ingredient.name} ({ingredient.calories_per_100g} kcal/100g)")
        return ingredient

    except Exception as e:
        session.rollback()
        print(f"Error updating ingredient: {e}")
        return None
    finally:
        session.close()


def delete_ingredient(ingredient_id: int):
    """
    Deletes an ingredient from the database.

    :param ingredient_id: The ID of the ingredient to delete
    :return: True if deleted successfully, False otherwise
    """
    session = SessionLocal()
    try:
        ingredient = session.query(Ingredient).filter(Ingredient.ingredient_id == ingredient_id).first()
        if not ingredient:
            print("Ingredient not found.")
            return False

        session.delete(ingredient)
        session.commit()

        print(f"Ingredient deleted: {ingredient.name}")
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting ingredient: {e}")
        return False
    finally:
        session.close()
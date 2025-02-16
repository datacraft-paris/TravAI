from travai.backend.services.modified_ingredient_service import get_modified_ingredients_by_meal_id
from travai.backend.services.detected_ingredient_service import get_detected_ingredients_by_meal

def get_sum_calories_per_meal_detected(meal_id: int):
    cnt = 0
    for modified_ingredient in get_detected_ingredients_by_meal(meal_id):
        cnt += modified_ingredient.calculated_calories
    return cnt

def get_sum_calories_per_meal_modified(meal_id: int):
    cnt = 0
    for modified_ingredient in get_modified_ingredients_by_meal_id(meal_id):
        cnt += modified_ingredient.calculated_calories
    return cnt

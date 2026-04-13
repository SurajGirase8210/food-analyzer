# Base nutrition templates (per serving)
CATEGORY_DATA = {
    "dessert": {"calories": 300, "protein": 4, "fat": 12, "carbs": 45},
    "fastfood": {"calories": 350, "protein": 15, "fat": 18, "carbs": 30},
    "fruit": {"calories": 90, "protein": 1, "fat": 0.3, "carbs": 22},
    "salad": {"calories": 150, "protein": 5, "fat": 8, "carbs": 15},
    "meat": {"calories": 250, "protein": 20, "fat": 15, "carbs": 5},
    "pasta": {"calories": 280, "protein": 10, "fat": 8, "carbs": 40},
    "rice": {"calories": 220, "protein": 4, "fat": 2, "carbs": 45},
    "seafood": {"calories": 200, "protein": 18, "fat": 10, "carbs": 5},
}


FOOD_CATEGORY = {
    "churros": "dessert",
    "donuts": "dessert",
    "ice_cream": "dessert",
    "cake": "dessert",

    "hamburger": "fastfood",
    "pizza": "fastfood",
    "hot_dog": "fastfood",
    "french_fries": "fastfood",

    "apple_pie": "dessert",
    "banana": "fruit",
    "apple": "fruit",

    "caesar_salad": "salad",
    "greek_salad": "salad",

    "steak": "meat",
    "chicken_wings": "meat",

    "spaghetti_bolognese": "pasta",
    "lasagna": "pasta",

    "fried_rice": "rice",

    "grilled_salmon": "seafood",
}


FOOD_CATEGORY = {
    "churros": "dessert",
    "donuts": "dessert",
    "ice_cream": "dessert",
    "cake": "dessert",

    "hamburger": "fastfood",
    "pizza": "fastfood",
    "hot_dog": "fastfood",
    "french_fries": "fastfood",

    "apple_pie": "dessert",
    "banana": "fruit",
    "apple": "fruit",

    "caesar_salad": "salad",
    "greek_salad": "salad",

    "steak": "meat",
    "chicken_wings": "meat",

    "spaghetti_bolognese": "pasta",
    "lasagna": "pasta",

    "fried_rice": "rice",

    "grilled_salmon": "seafood",
}

import random

def get_nutrition(food_name):
    food_name = food_name.lower()

    category = FOOD_CATEGORY.get(food_name)

    if category and category in CATEGORY_DATA:
        base = CATEGORY_DATA[category]

        # add slight variation (realistic)
        return {
            "calories": base["calories"] + random.randint(-30, 30),
            "protein": round(base["protein"] + random.uniform(-2, 2), 1),
            "fat": round(base["fat"] + random.uniform(-3, 3), 1),
            "carbs": round(base["carbs"] + random.uniform(-5, 5), 1),
        }

    # fallback
    return {
        "calories": random.randint(180, 320),
        "protein": round(random.uniform(3, 15), 1),
        "fat": round(random.uniform(5, 20), 1),
        "carbs": round(random.uniform(20, 50), 1),
    }
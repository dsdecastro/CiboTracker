import os
import requests
import urllib.parse
import json

from flask import redirect, render_template, request, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(query):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={query.replace(' ', '%20')}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    # Parse response
    try:
        foods = response.json()["foods"]
        foodList = []
        # Iterate through the food nutrients for the first five foods, 
        # and add the values for carbs, protein, fat, and calories to a unique dictionary
        for i in range(0,len(foods)):
            # Initialize dictionary for each food in the list
            foodDict = {
                "description": foods[i]["description"],
                "brand": "",
                "carbs": 0,
                "protein": 0,
                "fat": 0,
                "calories": 0
            }
            if "brandName" in foods[i].keys():
                foodDict["brand"] = foods[i]["brandName"]
            elif "brandOwner" in foods[i].keys():
                foodDict["brand"] = foods[i]["brandOwner"]
            # Add nutrient values to the dictionary
            nutrients = foods[i]["foodNutrients"]
            for nutrient in nutrients:
                name = nutrient["nutrientName"].lower()
                value = nutrient["value"]
                if "carbohydrate" in name:
                    foodDict["carbs"] = value
                elif "protein" in name:
                    foodDict["protein"] = value
                elif "fat" in name:
                    foodDict["fat"] = value
                elif "energy" in name:
                    if nutrient["unitName"].lower() == "kcal":
                        foodDict["calories"] = value
            foodList.append(foodDict)

        return foodList
    except (KeyError, TypeError, ValueError):
        return None

def str_to_dict(s):
    # Parse string of specific format into dictionary
    for i in range(0, len(s)):
        if s[i] == "'" and (s[i - 1] == "{" or s[i - 1] == " " or s[i + 1] == "," or s[i + 1] == ":"):
                s = s[:i] + '"' + s[i + 1:]
    
    return json.loads(s)

def sums(listFood):
    # Sum the calories and macronutrients of foods in a given list
    sums = {
        "calories": 0,
        "carbs": 0,
        "protein": 0,
        "fat": 0
    }

    for food in listFood:
        sums["calories"] += food.calories
        sums["carbs"] += food.carbs
        sums["protein"] += food.protein
        sums["fat"] += food.fat

    return sums

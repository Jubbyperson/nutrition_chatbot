"""
Core nutrition calculations and logic for NutriChat.
Implements base calculations for BMR, TDEE, and macronutrient recommendations.
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from utils import ACTIVITY_LEVELS, GOALS

@dataclass
class NutritionProfile:
    """Stores a user's calculated nutrition needs."""
    # User stats
    weight_lbs: float
    height_inches: float
    age: int
    sex: str
    activity_level: str
    
    # Calculated metrics
    bmr: float  # Basal Metabolic Rate
    tdee: float  # Total Daily Energy Expenditure
    target_calories: float
    protein_grams: float
    carbs_grams: float
    fat_grams: float
    water_oz: float

def calculate_bmr(weight_lbs: float, height_inches: float, age: int, sex: str) -> float:
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor Equation.
    
    Args:
        weight_lbs: Weight in pounds
        height_inches: Height in inches
        age: Age in years
        sex: 'male' or 'female'
    
    Returns:
        BMR in calories
    """
    # Convert weight to kg and height to cm
    weight_kg = weight_lbs * 0.453592
    height_cm = height_inches * 2.54
    
    # Mifflin-St Jeor Equation
    if sex.lower() == 'male':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return round(bmr)

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure based on activity level.
    
    Args:
        bmr: Basal Metabolic Rate in calories
        activity_level: Activity level from ACTIVITY_LEVELS
    
    Returns:
        TDEE in calories
    """
    activity_multipliers = {
        'sedentary': 1.2,        # Little or no exercise
        'light': 1.375,          # Light exercise 1-3 days/week
        'moderate': 1.55,        # Moderate exercise 3-5 days/week
        'active': 1.725,         # Hard exercise 6-7 days/week
        'very_active': 1.9       # Very hard exercise & physical job or training twice per day
    }
    
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    return round(bmr * multiplier)

def calculate_target_calories(tdee: float, goal: str) -> float:
    """
    Calculate target daily calories based on user's goal.
    
    Args:
        tdee: Total Daily Energy Expenditure in calories
        goal: Goal from GOALS
    
    Returns:
        Target calories per day
    """
    goal_adjustments = {
        'lose_weight': 0.85,     # 15% deficit
        'maintain': 1.0,         # Maintain current weight
        'gain_muscle': 1.1,      # 10% surplus
        'improve_endurance': 1.05 # 5% surplus
    }
    
    adjustment = goal_adjustments.get(goal.lower(), 1.0)
    return round(tdee * adjustment)

def calculate_macronutrients(target_calories: float, goal: str, weight_lbs: float) -> Tuple[float, float, float]:
    """
    Calculate recommended macronutrient distribution.
    
    Args:
        target_calories: Target daily calories
        goal: User's goal from GOALS
        weight_lbs: Weight in pounds
    
    Returns:
        Tuple of (protein_grams, carbs_grams, fat_grams)
    """
    # Protein calculation (1.6-2.2g per kg of bodyweight depending on goal)
    weight_kg = weight_lbs * 0.453592
    protein_multipliers = {
        'lose_weight': 2.2,      # Higher protein for muscle preservation
        'maintain': 1.8,         # Moderate protein
        'gain_muscle': 2.0,      # High protein for muscle growth
        'improve_endurance': 1.6  # Moderate protein
    }
    protein_multiplier = protein_multipliers.get(goal.lower(), 1.8)
    protein_grams = round(weight_kg * protein_multiplier)
    protein_calories = protein_grams * 4  # 4 calories per gram of protein
    
    # Fat calculation (20-35% of total calories)
    fat_percentages = {
        'lose_weight': 0.25,     # 25% of calories
        'maintain': 0.30,        # 30% of calories
        'gain_muscle': 0.25,     # 25% of calories
        'improve_endurance': 0.25 # 25% of calories
    }
    fat_percentage = fat_percentages.get(goal.lower(), 0.30)
    fat_calories = target_calories * fat_percentage
    fat_grams = round(fat_calories / 9)  # 9 calories per gram of fat
    
    # Remaining calories go to carbs
    carb_calories = target_calories - protein_calories - fat_calories
    carb_grams = round(carb_calories / 4)  # 4 calories per gram of carbs
    
    return protein_grams, carb_grams, fat_grams

def calculate_water_needs(weight_lbs: float, activity_level: str) -> float:
    """
    Calculate daily water needs in ounces.
    
    Args:
        weight_lbs: Weight in pounds
        activity_level: Activity level from ACTIVITY_LEVELS
    
    Returns:
        Recommended water intake in ounces
    """
    # Base calculation: 0.5-0.7 oz per pound of bodyweight
    base_multipliers = {
        'sedentary': 0.5,
        'light': 0.55,
        'moderate': 0.6,
        'active': 0.65,
        'very_active': 0.7
    }
    
    multiplier = base_multipliers.get(activity_level.lower(), 0.5)
    return round(weight_lbs * multiplier)

def calculate_nutrition_profile(
    weight_lbs: float,
    height_inches: float,
    age: int,
    sex: str,
    activity_level: str,
    goal: str
) -> NutritionProfile:
    """
    Calculate complete nutrition profile for a user.
    
    Args:
        weight_lbs: Weight in pounds
        height_inches: Height in inches
        age: Age in years
        sex: 'male' or 'female'
        activity_level: Activity level from ACTIVITY_LEVELS
        goal: Goal from GOALS
    
    Returns:
        NutritionProfile object with all calculated values
    """
    # Validate inputs
    if not all([weight_lbs > 0, height_inches > 0, age > 0]):
        raise ValueError("Weight, height, and age must be positive numbers")
    if sex.lower() not in ['male', 'female']:
        raise ValueError("Sex must be 'male' or 'female'")
    if activity_level.lower() not in ACTIVITY_LEVELS:
        raise ValueError(f"Activity level must be one of: {list(ACTIVITY_LEVELS.keys())}")
    if goal.lower() not in GOALS:
        raise ValueError(f"Goal must be one of: {list(GOALS.keys())}")
    
    # Calculate all metrics
    bmr = calculate_bmr(weight_lbs, height_inches, age, sex)
    tdee = calculate_tdee(bmr, activity_level)
    target_calories = calculate_target_calories(tdee, goal)
    protein_grams, carbs_grams, fat_grams = calculate_macronutrients(target_calories, goal, weight_lbs)
    water_oz = calculate_water_needs(weight_lbs, activity_level)
    
    return NutritionProfile(
        # User stats
        weight_lbs=weight_lbs,
        height_inches=height_inches,
        age=age,
        sex=sex,
        activity_level=activity_level,
        
        # Calculated metrics
        bmr=bmr,
        tdee=tdee,
        target_calories=target_calories,
        protein_grams=protein_grams,
        carbs_grams=carbs_grams,
        fat_grams=fat_grams,
        water_oz=water_oz
    )

def get_nutrition_advice(profile: NutritionProfile, goal: str) -> Dict[str, str]:
    """
    Generate basic nutrition advice based on the user's profile and goal.
    
    Args:
        profile: NutritionProfile object
        goal: User's goal from GOALS
    
    Returns:
        Dictionary of advice categories and recommendations
    """
    advice = {
        'calories': f"Your target daily calorie intake is {profile.target_calories} calories. ",
        'macronutrients': f"Aim for {profile.protein_grams}g protein, {profile.carbs_grams}g carbs, and {profile.fat_grams}g fat daily. ",
        'hydration': f"Drink at least {profile.water_oz}oz of water daily. ",
        'general': ""
    }
    
    # Add goal-specific advice
    if goal.lower() == 'lose_weight':
        advice['general'] = "Focus on high-protein, nutrient-dense foods. Consider meal timing around workouts."
    elif goal.lower() == 'gain_muscle':
        advice['general'] = "Prioritize protein intake and consider pre/post workout nutrition."
    elif goal.lower() == 'maintain':
        advice['general'] = "Maintain a balanced diet with regular meal timing."
    elif goal.lower() == 'improve_endurance':
        advice['general'] = "Focus on adequate carb intake for energy and proper hydration."
    
    return advice
# helpful user functions

from typing import Optional, Dict, Any
from datetime import datetime
import re

# Conversion constants
KG_TO_LBS = 2.20462
CM_TO_INCHES = 0.393701

# Activity level options
ACTIVITY_LEVELS = {
    'sedentary': 'Little or no exercise',
    'light': 'Light exercise 1-3 days/week',
    'moderate': 'Moderate exercise 3-5 days/week',
    'active': 'Hard exercise 6-7 days/week',
    'very_active': 'Very hard exercise & physical job or training twice per day'
}

# Goal options
GOALS = {
    'weight_loss': 'Lose weight',
    'maintenance': 'Maintain weight',
    'muscle_gain': 'Build muscle',
    'general_health': 'Improve general health'
}

# Unit conversion functions
def kg_to_lbs(kg: float) -> float:
    """Convert kilograms to pounds."""
    return kg * KG_TO_LBS

def lbs_to_kg(lbs: float) -> float:
    """Convert pounds to kilograms."""
    return lbs / KG_TO_LBS

def cm_to_inches(cm: float) -> float:
    """Convert centimeters to inches."""
    return cm * CM_TO_INCHES

def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches / CM_TO_INCHES

def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """Validate password strength."""
    if not password:
        return False
    # At least 8 characters, 1 uppercase, 1 lowercase, 1 number
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

def validate_age(age: Optional[int]) -> bool:
    """Validate age is reasonable."""
    if age is None:
        return True
    return 13 <= age <= 120

def validate_height(height: Optional[float]) -> bool:
    """Validate height in inches."""
    if height is None:
        return True
    # 20 inches to 100 inches (1.67ft to 8.33ft)
    return 20 <= height <= 100

def validate_weight(weight: Optional[float]) -> bool:
    """Validate weight in pounds."""
    if weight is None:
        return True
    # 50lbs to 661lbs (22.7kg to 300kg)
    return 50 <= weight <= 661

def validate_sex(sex: Optional[str]) -> bool:
    """Validate sex/gender."""
    if sex is None:
        return True
    return sex.lower() in ['male', 'female', 'other']

def validate_activity_level(activity_level: Optional[str]) -> bool:
    """Validate activity level."""
    if activity_level is None:
        return True
    return activity_level.lower() in ACTIVITY_LEVELS

def validate_goal(goal: Optional[str]) -> bool:
    """Validate fitness goal."""
    if goal is None:
        return True
    return goal.lower() in GOALS

def validate_nutrition_values(calories: Optional[float] = None,
                            protein: Optional[float] = None,
                            carbs: Optional[float] = None,
                            fat: Optional[float] = None) -> bool:
    """Validate nutrition values are reasonable."""
    if calories is not None and not (0 <= calories <= 10000):
        return False
    if protein is not None and not (0 <= protein <= 500):
        return False
    if carbs is not None and not (0 <= carbs <= 1000):
        return False
    if fat is not None and not (0 <= fat <= 500):
        return False
    return True

def validate_date(date_str: Optional[str]) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    if date_str is None:
        return True
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def validate_user_data(email: str, password: str, age: Optional[int] = None,
                      height: Optional[float] = None, weight: Optional[float] = None,
                      sex: Optional[str] = None, activity_level: Optional[str] = None,
                      goal: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate all user data fields.
    Returns a dictionary of validation results and error messages.
    Note: height is in inches, weight is in pounds
    """
    errors = {}
    
    if not validate_email(email):
        errors['email'] = "Invalid email format"
    
    if not validate_password(password):
        errors['password'] = "Password must be at least 8 characters with 1 uppercase, 1 lowercase, and 1 number"
    
    if not validate_age(age):
        errors['age'] = "Age must be between 13 and 120"
    
    if not validate_height(height):
        errors['height'] = "Height must be between 20 and 100 inches (1.67ft to 8.33ft)"
    
    if not validate_weight(weight):
        errors['weight'] = "Weight must be between 50 and 661 pounds"
    
    if not validate_sex(sex):
        errors['sex'] = "Sex must be 'male', 'female', or 'other'"
    
    if not validate_activity_level(activity_level):
        errors['activity_level'] = f"Activity level must be one of: {', '.join(ACTIVITY_LEVELS.keys())}"
    
    if not validate_goal(goal):
        errors['goal'] = f"Goal must be one of: {', '.join(GOALS.keys())}"
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }

def validate_log_data(user_id: int, weight: Optional[float] = None,
                     calories: Optional[float] = None, protein: Optional[float] = None,
                     carbs: Optional[float] = None, fat: Optional[float] = None,
                     date: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate all log data fields.
    Returns a dictionary of validation results and error messages.
    Note: weight is in pounds
    """
    errors = {}
    
    if not isinstance(user_id, int) or user_id <= 0:
        errors['user_id'] = "Invalid user ID"
    
    if not validate_weight(weight):
        errors['weight'] = "Weight must be between 50 and 661 pounds"
    
    if not validate_nutrition_values(calories, protein, carbs, fat):
        errors['nutrition'] = "Nutrition values must be reasonable (calories: 0-10000, protein: 0-500, carbs: 0-1000, fat: 0-500)"
    
    if not validate_date(date):
        errors['date'] = "Date must be in YYYY-MM-DD format"
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }
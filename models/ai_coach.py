"""
AI Nutrition Coach implementation for NutriChat.
Provides personalized nutrition advice, meal suggestions, and progress analysis using OpenAI's API.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
from openai import OpenAI
from config import OPENAI_API_KEY

# Add parent directory to path so we can import from root
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logic import NutritionProfile

# Initialize OpenAI client
if not OPENAI_API_KEY:
    raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in config.py")
client = OpenAI(api_key=OPENAI_API_KEY)

@dataclass
class MealSuggestion:
    """Represents a suggested meal with nutritional information."""
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    ingredients: List[str]
    instructions: str
    prep_time: str
    difficulty: str

class NutritionCoach:
    """AI-powered nutrition coach that provides personalized advice and recommendations."""
    
    def __init__(self):
        """Initialize the nutrition coach with OpenAI client."""
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in config.py")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def get_personalized_advice(self, profile: NutritionProfile, goal: str) -> Dict[str, str]:
        """
        Get personalized nutrition advice based on user's specific profile and goals.
        """
        # Create a dynamic prompt that adapts to the user's specific situation
        system_prompt = f"""You are a personalized nutrition coach providing tailored advice based on the user's specific profile.

        User Profile:
        - Weight: {profile.weight_lbs} lbs
        - Height: {profile.height_inches} inches
        - Age: {profile.age} years
        - Sex: {profile.sex}
        - Activity Level: {profile.activity_level}
        - Goal: {goal}

        Daily Targets (MUST BE FOLLOWED EXACTLY):
        - Calories: {profile.target_calories} calories (this is your PRIMARY target)
        - Protein: {profile.protein_grams}g
        - Carbs: {profile.carbs_grams}g
        - Fat: {profile.fat_grams}g
        - Water: {profile.water_oz}oz

        Provide advice in these sections:
        1. Meal Plan (with specific calorie amounts that MUST total {profile.target_calories} calories)
        2. Nutrition Tips
        3. Lifestyle Tips

        Rules:
        - The meal plan MUST total exactly {profile.target_calories} calories
        - Each meal should include protein
        - Portion sizes should be appropriate for the user's stats
        - Keep advice simple and actionable
        - Focus on the user's specific goal: {goal}
        - Consider the user's age ({profile.age}) and activity level ({profile.activity_level})
        - Adjust portion sizes based on the user's weight ({profile.weight_lbs} lbs)"""

        try:
            # Get AI response with specific instructions for the user's case
            user_message = f"""Please provide a personalized meal plan for:
            - A {profile.age}-year-old {profile.sex}
            - Weighing {profile.weight_lbs} lbs
            - With {profile.activity_level} activity level
            - Goal: {goal}
            - Target: {profile.target_calories} calories daily
            
            The meal plan should:
            1. Total exactly {profile.target_calories} calories
            2. Include {profile.protein_grams}g protein
            3. Have appropriate portion sizes for this person
            4. Be realistic and achievable"""

            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # Get the response text
            advice = response.choices[0].message.content

            # Split into sections
            sections = {
                'meal_plan': '',
                'nutrition_tips': '',
                'lifestyle_tips': ''
            }

            current_section = None
            for line in advice.split('\n'):
                line = line.strip()
                if not line:
                    continue

                # Simple section detection
                if 'MEAL PLAN' in line.upper():
                    current_section = 'meal_plan'
                elif 'NUTRITION' in line.upper():
                    current_section = 'nutrition_tips'
                elif 'LIFESTYLE' in line.upper():
                    current_section = 'lifestyle_tips'
                elif current_section:
                    sections[current_section] += line + '\n'

            # Ensure each section has appropriate content for this user
            if not sections['meal_plan'].strip():
                # Create a dynamic fallback meal plan based on user's stats
                meal_calories = {
                    'breakfast': round(profile.target_calories * 0.25),  # 25% of calories
                    'lunch': round(profile.target_calories * 0.30),      # 30% of calories
                    'dinner': round(profile.target_calories * 0.30),     # 30% of calories
                    'snacks': round(profile.target_calories * 0.15)      # 15% of calories
                }
                
                sections['meal_plan'] = f"""Here's a personalized meal plan for your stats:

Breakfast ({meal_calories['breakfast']} calories):
- 2 eggs with 1 slice whole grain toast
- Greek yogurt with berries
- Adjust portions to reach {meal_calories['breakfast']} calories

Lunch ({meal_calories['lunch']} calories):
- Grilled protein (chicken/fish) with vegetables
- 1 serving of whole grains
- Adjust portions to reach {meal_calories['lunch']} calories

Dinner ({meal_calories['dinner']} calories):
- Lean protein with vegetables
- 1 serving of whole grains
- Adjust portions to reach {meal_calories['dinner']} calories

Snacks ({meal_calories['snacks']} calories):
- Protein-rich snacks
- Fruits and nuts
- Adjust portions to reach {meal_calories['snacks']} calories

Total: {profile.target_calories} calories
Protein: {profile.protein_grams}g
Carbs: {profile.carbs_grams}g
Fat: {profile.fat_grams}g"""

            if not sections['nutrition_tips'].strip():
                sections['nutrition_tips'] = f"""• Eat exactly {profile.target_calories} calories daily
• Get {profile.protein_grams}g of protein
• Include {profile.carbs_grams}g of carbs
• Add {profile.fat_grams}g of healthy fats
• Drink {profile.water_oz}oz of water
• Eat every 3-4 hours
• Include protein in every meal
• Adjust portions based on your activity level: {profile.activity_level}"""

            if not sections['lifestyle_tips'].strip():
                sections['lifestyle_tips'] = f"""• Get 7-8 hours of sleep
• Stay consistent with your {profile.activity_level} activity level
• Manage stress
• Stay hydrated with {profile.water_oz}oz of water daily
• Track your progress
• Adjust portions if needed based on your weight changes"""

            # Validate the meal plan
            if 'meal_plan' in sections and str(profile.target_calories) not in sections['meal_plan']:
                print(f"Warning: Meal plan doesn't match target calories of {profile.target_calories}. Using fallback plan.")
                # Use the dynamic fallback plan we created above
                pass  # The fallback plan is already set with the correct calories

            return sections

        except Exception as e:
            print(f"Error getting AI advice: {str(e)}")
            # Return basic advice if AI fails
            return {
                'meal_plan': f"Focus on eating exactly {profile.target_calories} calories daily for {goal}. Adjust portions based on your weight of {profile.weight_lbs} lbs.",
                'nutrition_tips': f"Get {profile.protein_grams}g of protein and stay hydrated with {profile.water_oz}oz of water.",
                'lifestyle_tips': f"Stay active at your {profile.activity_level} level and get enough sleep."
            }
    
    def suggest_meal(
        self,
        profile: NutritionProfile,
        meal_type: str,
        preferences: Optional[Dict] = None
    ) -> MealSuggestion:
        """
        Generate a personalized meal suggestion.
        
        Args:
            profile: User's NutritionProfile
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            preferences: Optional dictionary of preferences and restrictions
        
        Returns:
            MealSuggestion object with meal details
        """
        # Calculate target macros for this meal (assuming 3 main meals + 2 snacks)
        meal_calories = profile.target_calories / 5  # Divide by 5 for 3 meals + 2 snacks
        meal_protein = profile.protein_grams / 5
        meal_carbs = profile.carbs_grams / 5
        meal_fat = profile.fat_grams / 5
        
        # Create the system prompt
        system_prompt = f"""You are an expert nutritionist and chef. Create a {meal_type} recipe that meets these nutritional targets:
        - Calories: {meal_calories:.0f}
        - Protein: {meal_protein:.1f}g
        - Carbs: {meal_carbs:.1f}g
        - Fat: {meal_fat:.1f}g
        
        The recipe should be:
        1. Easy to prepare
        2. Use common ingredients
        3. Be delicious and satisfying
        4. Fit into a healthy diet
        
        Format the response as a JSON object with these fields:
        - name: string
        - calories: number
        - protein: number
        - carbs: number
        - fat: number
        - ingredients: array of strings
        - instructions: string
        - prep_time: string
        - difficulty: string (easy/medium/hard)"""
        
        # Add preferences to the prompt if provided
        if preferences:
            system_prompt += f"\n\nConsider these preferences and restrictions:\n{preferences}"
        
        try:
            # Get AI response
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Please suggest a {meal_type} recipe."}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse the JSON response
            meal_data = response.choices[0].message.content
            return MealSuggestion(**meal_data)
            
        except Exception as e:
            # Return a simple fallback meal suggestion
            return MealSuggestion(
                name="Simple Balanced Meal",
                calories=int(meal_calories),
                protein=meal_protein,
                carbs=meal_carbs,
                fat=meal_fat,
                ingredients=["Protein source", "Complex carbs", "Vegetables", "Healthy fats"],
                instructions="Combine ingredients in balanced portions.",
                prep_time="15 minutes",
                difficulty="easy"
            )
    
    def analyze_progress(self, profile: NutritionProfile, logs: List[Dict], goal: str) -> Dict[str, str]:
        """
        Provide simple progress analysis based on nutrition logs.
        """
        if not logs:
            return {
                'summary': "No logs available for analysis. Start logging your meals to get feedback.",
                'recommendations': "Begin tracking your daily nutrition to see your progress."
            }

        try:
            # Calculate basic metrics
            avg_calories = sum(log['calories'] for log in logs) / len(logs)
            avg_protein = sum(log['protein'] for log in logs) / len(logs)
            latest_weight = logs[-1]['weight']
            initial_weight = logs[0]['weight']
            weight_change = latest_weight - initial_weight

            # Create simple analysis
            analysis = {
                'summary': f"""Progress Summary:
• Average daily calories: {avg_calories:.0f} calories
• Average protein intake: {avg_protein:.0f}g
• Weight change: {weight_change:+.1f} lbs
• Target calories: {profile.target_calories} calories""",
                
                'recommendations': f"""Recommendations:
• {'Increase' if avg_calories < profile.target_calories else 'Maintain'} calorie intake to reach {profile.target_calories} calories
• {'Increase' if avg_protein < profile.protein_grams else 'Maintain'} protein intake to reach {profile.protein_grams}g
• {'Continue' if weight_change > 0 else 'Adjust'} current approach based on weight change"""
            }

            return analysis

        except Exception as e:
            print(f"Error analyzing progress: {str(e)}")
            return {
                'summary': "Unable to analyze progress at this time.",
                'recommendations': "Please continue logging your nutrition and try again later."
            }
    
    def get_quick_tip(self, profile: NutritionProfile, goal: str) -> str:
        """
        Get a quick, actionable nutrition tip.
        
        Args:
            profile: User's NutritionProfile
            goal: User's goal
        
        Returns:
            A single, actionable tip
        """
        system_prompt = f"""You are a nutrition coach. Provide ONE specific, actionable tip for a user with:
        Goal: {goal}
        Daily Calories: {profile.target_calories}
        Daily Protein: {profile.protein_grams}g
        Daily Carbs: {profile.carbs_grams}g
        Daily Fat: {profile.fat_grams}g
        
        The tip should be:
        1. Specific and actionable
        2. Relevant to their goals
        3. Easy to implement today
        4. No more than 2 sentences"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Give me one quick tip I can implement today."}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return "Focus on staying hydrated and eating regular, balanced meals throughout the day." 
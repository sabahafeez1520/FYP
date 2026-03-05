from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date, timedelta
from typing import Optional
import json

from app.models.all_models import DietPlan, DailyMealPlan, Meal, MealItem, FoodItem, UserProfile
from app.core.config import settings


MEAL_TYPES_BY_FREQUENCY = {
    3: ["breakfast", "lunch", "dinner"],
    4: ["breakfast", "lunch", "evening_snack", "dinner"],
    5: ["breakfast", "morning_snack", "lunch", "evening_snack", "dinner"],
    6: ["breakfast", "morning_snack", "lunch", "evening_snack", "dinner", "late_snack"],
}

MEAL_TIMES = {
    "breakfast":      "08:00",
    "morning_snack":  "10:30",
    "lunch":          "13:00",
    "evening_snack":  "16:30",
    "dinner":         "19:30",
    "late_snack":     "21:00",
}

# Calorie distribution per meal type (%)
CALORIE_SPLIT = {
    3: {"breakfast": 0.30, "lunch": 0.40, "dinner": 0.30},
    4: {"breakfast": 0.28, "lunch": 0.35, "evening_snack": 0.12, "dinner": 0.25},
    5: {"breakfast": 0.25, "morning_snack": 0.10, "lunch": 0.30, "evening_snack": 0.10, "dinner": 0.25},
    6: {"breakfast": 0.22, "morning_snack": 0.08, "lunch": 0.28, "evening_snack": 0.10, "dinner": 0.25, "late_snack": 0.07},
}


class DietPlanService:

    @staticmethod
    def get_active_plan(db: Session, user_id: int) -> Optional[DietPlan]:
        return db.query(DietPlan).filter(
            DietPlan.user_id == user_id,
            DietPlan.is_active == True
        ).order_by(DietPlan.created_at.desc()).first()

    @staticmethod
    def get_plan_or_404(db: Session, plan_id: int, user_id: int) -> DietPlan:
        plan = db.query(DietPlan).filter(
            DietPlan.plan_id == plan_id,
            DietPlan.user_id == user_id
        ).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Diet plan not found")
        return plan

    @staticmethod
    def generate_plan(db: Session, user_id: int, days: int = 7) -> DietPlan:
        """Generate a diet plan based on user profile."""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            raise HTTPException(status_code=400, detail="Complete your profile before generating a plan")
        if not profile.recommended_calories:
            raise HTTPException(status_code=400, detail="Profile nutrition data incomplete. Update your profile with height, weight, and goals.")

        # Deactivate old plan
        db.query(DietPlan).filter(
            DietPlan.user_id == user_id,
            DietPlan.is_active == True
        ).update({"is_active": False})

        # Determine meals per day
        freq = min(6, max(3, profile.meal_frequency or 3))
        meal_types = MEAL_TYPES_BY_FREQUENCY.get(freq, MEAL_TYPES_BY_FREQUENCY[3])

        # Create plan
        plan = DietPlan(
            user_id=user_id,
            plan_name=f"SmartBites Plan - {date.today().strftime('%B %Y')}",
            description=f"Personalized {days}-day plan for {profile.primary_goal.replace('_', ' ').title()}",
            daily_calories=profile.recommended_calories,
            protein_target_g=profile.recommended_protein,
            carbs_target_g=profile.recommended_carbs,
            fats_target_g=profile.recommended_fats,
            fiber_target_g=25,
            meals_per_day=freq,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=days - 1),
            generated_by="ai",
        )
        db.add(plan)
        db.flush()

        # Get suitable foods for this user
        foods = DietPlanService._get_suitable_foods(db, profile)
        if not foods:
            raise HTTPException(status_code=400, detail="No suitable foods found for your dietary preferences")

        # Generate daily plans
        calorie_split = CALORIE_SPLIT.get(freq, CALORIE_SPLIT[3])

        for day in range(1, days + 1):
            daily = DailyMealPlan(
                plan_id=plan.plan_id,
                day_number=day,
                meal_date=date.today() + timedelta(days=day - 1),
            )
            db.add(daily)
            db.flush()

            day_calories = 0
            day_protein  = 0
            day_carbs    = 0
            day_fats     = 0

            for meal_type in meal_types:
                target_cal = int(profile.recommended_calories * calorie_split.get(meal_type, 0.20))

                meal = Meal(
                    daily_plan_id=daily.daily_plan_id,
                    meal_type=meal_type,
                    meal_name=meal_type.replace("_", " ").title(),
                    scheduled_time=MEAL_TIMES.get(meal_type),
                )
                db.add(meal)
                db.flush()

                # Add food items to this meal
                items, m_cal, m_prot, m_carbs, m_fats = DietPlanService._fill_meal(
                    db, meal.meal_id, foods, target_cal, profile
                )

                meal.total_calories = round(m_cal)
                meal.total_protein  = round(m_prot, 1)
                meal.total_carbs    = round(m_carbs, 1)
                meal.total_fats     = round(m_fats, 1)

                day_calories += m_cal
                day_protein  += m_prot
                day_carbs    += m_carbs
                day_fats     += m_fats

            daily.total_calories = round(day_calories)
            daily.total_protein  = round(day_protein, 1)
            daily.total_carbs    = round(day_carbs, 1)
            daily.total_fats     = round(day_fats, 1)

        db.commit()
        db.refresh(plan)
        return plan

    @staticmethod
    def _get_suitable_foods(db: Session, profile: UserProfile):
        query = db.query(FoodItem).filter(FoodItem.is_active == True)

        pref = profile.dietary_preference
        if pref == "vegetarian":
            query = query.filter(FoodItem.is_vegetarian == True)
        elif pref == "vegan":
            query = query.filter(FoodItem.is_vegan == True)

        # Filter allergens
        allergies = profile.allergies or []
        all_foods = query.all()

        if allergies:
            filtered = []
            for food in all_foods:
                allergens = food.common_allergens or []
                if not any(a.lower() in [x.lower() for x in allergens] for a in allergies):
                    filtered.append(food)
            return filtered

        return all_foods

    @staticmethod
    def _fill_meal(db: Session, meal_id: int, foods, target_cal: int, profile):
        """Add 2-4 food items to reach target calories."""
        from app.models.all_models import MealItem
        import random

        # Categorize foods
        proteins = [f for f in foods if f.protein_g and float(f.protein_g) > 10]
        carbs    = [f for f in foods if f.carbohydrates_g and float(f.carbohydrates_g) > 10]
        veggies  = [f for f in foods if f.calories and float(f.calories) < 60]
        all_f    = foods

        selected = []
        if proteins:
            selected.append(random.choice(proteins))
        if carbs:
            selected.append(random.choice([f for f in carbs if f not in selected] or carbs))
        if veggies:
            veg = [f for f in veggies if f not in selected]
            if veg:
                selected.append(random.choice(veg))
        if not selected:
            selected = random.sample(all_f, min(2, len(all_f)))

        total_cal = total_prot = total_carbs = total_fats = 0
        remaining_cal = target_cal

        for i, food in enumerate(selected):
            food_cal_per_100 = float(food.calories)
            if food_cal_per_100 == 0:
                continue

            # Last item fills remaining calories
            if i == len(selected) - 1:
                qty = max(30, min(300, (remaining_cal / food_cal_per_100) * 100))
            else:
                qty = max(30, min(200, (remaining_cal / len(selected) / food_cal_per_100) * 100))

            qty = round(qty, 1)
            factor = qty / 100

            item_cal   = float(food.calories) * factor
            item_prot  = float(food.protein_g or 0) * factor
            item_carbs = float(food.carbohydrates_g or 0) * factor
            item_fats  = float(food.fats_g or 0) * factor

            item = MealItem(
                meal_id=meal_id,
                food_id=food.food_id,
                quantity_g=qty,
                calories=round(item_cal, 1),
                protein_g=round(item_prot, 1),
                carbs_g=round(item_carbs, 1),
                fats_g=round(item_fats, 1),
            )
            db.add(item)

            total_cal   += item_cal
            total_prot  += item_prot
            total_carbs += item_carbs
            total_fats  += item_fats
            remaining_cal -= item_cal

        return [], total_cal, total_prot, total_carbs, total_fats

    @staticmethod
    def deactivate_plan(db: Session, plan_id: int, user_id: int):
        plan = DietPlanService.get_plan_or_404(db, plan_id, user_id)
        plan.is_active = False
        db.commit()

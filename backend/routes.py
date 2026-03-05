from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import date, timedelta
import os, uuid, shutil

from app.db.session import get_db
from app.core.security import get_current_user, require_admin
from app.core.config import settings
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest,
    ProfileCreateRequest, ProfileUpdateRequest, ProfileOut,
    MessageResponse, ChangePasswordRequest
)
from app.services.auth_service import AuthService
from app.services.profile_service import ProfileService
from app.services.diet_service import DietPlanService
from app.services.chat_service import ChatService
from app.models.all_models import (
    User, UserProfile, FoodItem, FoodCategory, DietPlan, DailyMealPlan, Meal, MealItem,
    MealLog, WaterLog, WeightTracking, Notification, NutritionTip,
    Nutritionist, NutritionistQuery, UserFeedback, ProgressMilestone, ChatSession
)
from app.utils.nutrition import full_nutrition_profile
from pydantic import BaseModel, EmailStr
from datetime import datetime

router = APIRouter()


# ═══════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════

@router.post("/auth/register", tags=["Auth"])
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = AuthService.register(db, data)
    return {"message": "Registration successful", "user_id": user.user_id, "username": user.username}


@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else None
    ua = request.headers.get("User-Agent")
    return AuthService.login(db, data, ip=ip, user_agent=ua)


@router.post("/auth/refresh", tags=["Auth"])
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    return AuthService.refresh_token(db, data.refresh_token)


@router.post("/auth/logout", tags=["Auth"])
def logout(request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    AuthService.logout(db, token)
    return {"message": "Logged out successfully"}


@router.post("/auth/change-password", tags=["Auth"])
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    from app.core.security import verify_password, hash_password
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated successfully"}


# ═══════════════════════════════════════════════════════════════
# USER / PROFILE
# ═══════════════════════════════════════════════════════════════

@router.get("/users/me", tags=["User"])
def get_me(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role,
        "profile_picture": current_user.profile_picture,
        "is_verified": current_user.is_verified,
        "last_login": current_user.last_login,
        "created_at": current_user.created_at,
    }


@router.post("/profile", tags=["Profile"])
def create_profile(data: ProfileCreateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = ProfileService.create_or_update(db, current_user.user_id, data)
    return {"message": "Profile saved", "onboarding_complete": profile.onboarding_complete}


@router.get("/profile", tags=["Profile"])
def get_profile(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return ProfileService.get_or_404(db, current_user.user_id)


@router.patch("/profile", tags=["Profile"])
def update_profile(data: ProfileUpdateRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return ProfileService.update_partial(db, current_user.user_id, data)


@router.post("/profile/picture", tags=["Profile"])
async def upload_profile_picture(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES_LIST:
        raise HTTPException(status_code=400, detail="Invalid file type. Use JPEG, PNG, or WebP.")

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB.")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    filename = f"{current_user.user_id}_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, "profiles", filename)

    with open(filepath, "wb") as f:
        f.write(contents)

    current_user.profile_picture = f"/uploads/profiles/{filename}"
    db.commit()
    return {"message": "Profile picture updated", "url": current_user.profile_picture}


# ═══════════════════════════════════════════════════════════════
# FOOD DATABASE
# ═══════════════════════════════════════════════════════════════

@router.get("/foods", tags=["Food"])
def search_foods(
    q: Optional[str] = Query(None, description="Search term"),
    category_id: Optional[int] = None,
    vegetarian: Optional[bool] = None,
    vegan: Optional[bool] = None,
    gluten_free: Optional[bool] = None,
    page: int = 1,
    per_page: int = 20,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    query = db.query(FoodItem).filter(FoodItem.is_active == True)
    if q:
        query = query.filter(FoodItem.food_name.ilike(f"%{q}%"))
    if category_id:
        query = query.filter(FoodItem.category_id == category_id)
    if vegetarian is not None:
        query = query.filter(FoodItem.is_vegetarian == vegetarian)
    if vegan is not None:
        query = query.filter(FoodItem.is_vegan == vegan)
    if gluten_free is not None:
        query = query.filter(FoodItem.is_gluten_free == gluten_free)

    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"items": items, "total": total, "page": page, "per_page": per_page}


@router.get("/foods/{food_id}", tags=["Food"])
def get_food(food_id: int, db: Session = Depends(get_db), _=Depends(get_current_user)):
    food = db.query(FoodItem).filter(FoodItem.food_id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food


@router.get("/food-categories", tags=["Food"])
def get_categories(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(FoodCategory).all()


# ═══════════════════════════════════════════════════════════════
# DIET PLANS
# ═══════════════════════════════════════════════════════════════

@router.post("/diet-plans/generate", tags=["Diet Plan"])
def generate_diet_plan(days: int = 7, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    plan = DietPlanService.generate_plan(db, current_user.user_id, days=days)
    return {"message": "Diet plan generated", "plan_id": plan.plan_id, "plan_name": plan.plan_name}


@router.get("/diet-plans", tags=["Diet Plan"])
def list_diet_plans(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    plans = db.query(DietPlan).filter(DietPlan.user_id == current_user.user_id)\
              .order_by(DietPlan.created_at.desc()).limit(10).all()
    return plans


@router.get("/diet-plans/active", tags=["Diet Plan"])
def get_active_plan(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    plan = DietPlanService.get_active_plan(db, current_user.user_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active diet plan found")
    return plan


@router.get("/diet-plans/{plan_id}", tags=["Diet Plan"])
def get_plan(plan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return DietPlanService.get_plan_or_404(db, plan_id, current_user.user_id)


@router.get("/diet-plans/{plan_id}/day/{day_number}", tags=["Diet Plan"])
def get_day_plan(plan_id: int, day_number: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    plan = DietPlanService.get_plan_or_404(db, plan_id, current_user.user_id)
    daily = db.query(DailyMealPlan).filter(
        DailyMealPlan.plan_id == plan_id,
        DailyMealPlan.day_number == day_number
    ).first()
    if not daily:
        raise HTTPException(status_code=404, detail="Day not found")

    meals = db.query(Meal).filter(Meal.daily_plan_id == daily.daily_plan_id).all()
    result = []
    for meal in meals:
        items = db.query(MealItem).filter(MealItem.meal_id == meal.meal_id).all()
        meal_data = {
            "meal_id": meal.meal_id,
            "meal_type": meal.meal_type,
            "meal_name": meal.meal_name,
            "scheduled_time": str(meal.scheduled_time) if meal.scheduled_time else None,
            "total_calories": meal.total_calories,
            "total_protein": float(meal.total_protein or 0),
            "total_carbs": float(meal.total_carbs or 0),
            "total_fats": float(meal.total_fats or 0),
            "items": []
        }
        for item in items:
            food = db.query(FoodItem).filter(FoodItem.food_id == item.food_id).first()
            meal_data["items"].append({
                "meal_item_id": item.meal_item_id,
                "food_id": item.food_id,
                "food_name": food.food_name if food else "Unknown",
                "quantity_g": float(item.quantity_g),
                "calories": float(item.calories or 0),
                "protein_g": float(item.protein_g or 0),
                "carbs_g": float(item.carbs_g or 0),
                "fats_g": float(item.fats_g or 0),
            })
        result.append(meal_data)

    return {
        "daily_plan_id": daily.daily_plan_id,
        "day_number": daily.day_number,
        "meal_date": str(daily.meal_date) if daily.meal_date else None,
        "total_calories": daily.total_calories,
        "meals": result
    }


@router.delete("/diet-plans/{plan_id}", tags=["Diet Plan"])
def deactivate_plan(plan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    DietPlanService.deactivate_plan(db, plan_id, current_user.user_id)
    return {"message": "Diet plan deactivated"}


# ═══════════════════════════════════════════════════════════════
# MEAL LOGGING
# ═══════════════════════════════════════════════════════════════

class MealLogRequest(BaseModel):
    food_id: int
    meal_type: str
    quantity_g: float
    logged_date: Optional[date] = None
    logged_time: Optional[str] = None
    satisfaction_rating: Optional[int] = None
    mood_before: Optional[str] = None
    mood_after: Optional[str] = None
    notes: Optional[str] = None


@router.post("/meal-logs", tags=["Meal Logging"])
def log_meal(data: MealLogRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    food = db.query(FoodItem).filter(FoodItem.food_id == data.food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    factor = data.quantity_g / 100
    log_date = data.logged_date or date.today()

    log = MealLog(
        user_id=current_user.user_id,
        food_id=data.food_id,
        meal_type=data.meal_type,
        quantity_g=data.quantity_g,
        actual_calories=round(float(food.calories) * factor, 2),
        actual_protein_g=round(float(food.protein_g or 0) * factor, 2),
        actual_carbs_g=round(float(food.carbohydrates_g or 0) * factor, 2),
        actual_fats_g=round(float(food.fats_g or 0) * factor, 2),
        logged_date=log_date,
        logged_time=data.logged_time,
        satisfaction_rating=data.satisfaction_rating,
        mood_before=data.mood_before,
        mood_after=data.mood_after,
        notes=data.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Meal logged", "log_id": log.log_id, "calories": float(log.actual_calories)}


@router.get("/meal-logs/today", tags=["Meal Logging"])
def get_today_logs(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logs = db.query(MealLog).filter(
        MealLog.user_id == current_user.user_id,
        MealLog.logged_date == date.today()
    ).order_by(MealLog.logged_time).all()

    result = []
    for log in logs:
        food = db.query(FoodItem).filter(FoodItem.food_id == log.food_id).first()
        result.append({
            "log_id": log.log_id,
            "food_name": food.food_name if food else "Unknown",
            "meal_type": log.meal_type,
            "quantity_g": float(log.quantity_g),
            "calories": float(log.actual_calories or 0),
            "protein_g": float(log.actual_protein_g or 0),
            "carbs_g": float(log.actual_carbs_g or 0),
            "fats_g": float(log.actual_fats_g or 0),
            "logged_time": str(log.logged_time) if log.logged_time else None,
        })
    return result


@router.get("/meal-logs/summary", tags=["Meal Logging"])
def get_nutrition_summary(
    start_date: date = None,
    end_date: date = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not start_date:
        start_date = date.today() - timedelta(days=6)
    if not end_date:
        end_date = date.today()

    logs = db.query(MealLog).filter(
        MealLog.user_id == current_user.user_id,
        MealLog.logged_date >= start_date,
        MealLog.logged_date <= end_date,
    ).all()

    from collections import defaultdict
    daily = defaultdict(lambda: {"calories": 0, "protein": 0, "carbs": 0, "fats": 0, "entries": 0})
    for log in logs:
        d = str(log.logged_date)
        daily[d]["calories"] += float(log.actual_calories or 0)
        daily[d]["protein"]  += float(log.actual_protein_g or 0)
        daily[d]["carbs"]    += float(log.actual_carbs_g or 0)
        daily[d]["fats"]     += float(log.actual_fats_g or 0)
        daily[d]["entries"]  += 1

    return {"start_date": str(start_date), "end_date": str(end_date), "daily": dict(daily)}


@router.delete("/meal-logs/{log_id}", tags=["Meal Logging"])
def delete_log(log_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = db.query(MealLog).filter(MealLog.log_id == log_id, MealLog.user_id == current_user.user_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(log)
    db.commit()
    return {"message": "Log deleted"}


# ═══════════════════════════════════════════════════════════════
# WATER LOGGING
# ═══════════════════════════════════════════════════════════════

class WaterLogRequest(BaseModel):
    amount_ml: int
    logged_date: Optional[date] = None

@router.post("/water-logs", tags=["Water"])
def log_water(data: WaterLogRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    log = WaterLog(
        user_id=current_user.user_id,
        amount_ml=data.amount_ml,
        logged_date=data.logged_date or date.today(),
    )
    db.add(log)
    db.commit()
    return {"message": "Water logged", "amount_ml": data.amount_ml}


@router.get("/water-logs/today", tags=["Water"])
def get_today_water(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    logs = db.query(WaterLog).filter(
        WaterLog.user_id == current_user.user_id,
        WaterLog.logged_date == date.today()
    ).all()
    total_ml = sum(l.amount_ml for l in logs)
    return {"total_ml": total_ml, "total_liters": round(total_ml / 1000, 2), "entries": len(logs)}


# ═══════════════════════════════════════════════════════════════
# WEIGHT TRACKING
# ═══════════════════════════════════════════════════════════════

class WeightLogRequest(BaseModel):
    weight_kg: float
    recorded_date: Optional[date] = None
    notes: Optional[str] = None

@router.post("/weight", tags=["Weight"])
def log_weight(data: WeightLogRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rec_date = data.recorded_date or date.today()
    existing = db.query(WeightTracking).filter(
        WeightTracking.user_id == current_user.user_id,
        WeightTracking.recorded_date == rec_date
    ).first()

    if existing:
        existing.weight_kg = data.weight_kg
        existing.notes = data.notes
        db.commit()
        return {"message": "Weight updated", "weight_kg": data.weight_kg}

    log = WeightTracking(
        user_id=current_user.user_id,
        weight_kg=data.weight_kg,
        recorded_date=rec_date,
        notes=data.notes,
    )
    db.add(log)

    # Update profile weight
    if current_user.profile:
        current_user.profile.weight_kg = data.weight_kg

    db.commit()
    return {"message": "Weight logged", "weight_kg": data.weight_kg}


@router.get("/weight/history", tags=["Weight"])
def get_weight_history(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    since = date.today() - timedelta(days=days)
    logs = db.query(WeightTracking).filter(
        WeightTracking.user_id == current_user.user_id,
        WeightTracking.recorded_date >= since
    ).order_by(WeightTracking.recorded_date.asc()).all()
    return logs


# ═══════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════

@router.get("/dashboard", tags=["Dashboard"])
def get_dashboard(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.user_id).first()
    today = date.today()

    # Today's nutrition
    today_logs = db.query(MealLog).filter(
        MealLog.user_id == current_user.user_id,
        MealLog.logged_date == today
    ).all()
    today_cal   = round(sum(float(l.actual_calories or 0) for l in today_logs))
    today_prot  = round(sum(float(l.actual_protein_g or 0) for l in today_logs), 1)
    today_carbs = round(sum(float(l.actual_carbs_g or 0) for l in today_logs), 1)
    today_fats  = round(sum(float(l.actual_fats_g or 0) for l in today_logs), 1)

    # Today's water
    water_logs = db.query(WaterLog).filter(
        WaterLog.user_id == current_user.user_id,
        WaterLog.logged_date == today
    ).all()
    today_water_ml = sum(l.amount_ml for l in water_logs)

    # Active plan
    active_plan = DietPlanService.get_active_plan(db, current_user.user_id)

    # Latest weight
    latest_weight = db.query(WeightTracking).filter(
        WeightTracking.user_id == current_user.user_id
    ).order_by(WeightTracking.recorded_date.desc()).first()

    # Unread notifications
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.user_id,
        Notification.is_read == False
    ).count()

    return {
        "user": {
            "username": current_user.username,
            "full_name": profile.full_name if profile else current_user.username,
            "profile_picture": current_user.profile_picture,
        },
        "today_nutrition": {
            "calories_consumed": today_cal,
            "calories_target": profile.recommended_calories if profile else 2000,
            "protein_g": today_prot,
            "carbs_g": today_carbs,
            "fats_g": today_fats,
            "meals_logged": len(today_logs),
        },
        "water": {
            "consumed_ml": today_water_ml,
            "target_liters": float(profile.water_intake_liters or 2.0) if profile else 2.0,
        },
        "weight": {
            "current_kg": float(latest_weight.weight_kg) if latest_weight else None,
            "target_kg": float(profile.target_weight_kg) if profile and profile.target_weight_kg else None,
            "last_recorded": str(latest_weight.recorded_date) if latest_weight else None,
        },
        "active_plan": {
            "plan_id": active_plan.plan_id if active_plan else None,
            "plan_name": active_plan.plan_name if active_plan else None,
            "daily_calories": active_plan.daily_calories if active_plan else None,
        } if active_plan else None,
        "unread_notifications": unread_count,
        "goal": profile.primary_goal if profile else None,
    }


# ═══════════════════════════════════════════════════════════════
# CHATBOT
# ═══════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@router.post("/chat", tags=["Chat"])
def chat(data: ChatRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return ChatService.chat(db, current_user.user_id, data.message, data.session_id)


@router.get("/chat/sessions", tags=["Chat"])
def get_chat_sessions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return ChatService.get_sessions(db, current_user.user_id)


@router.get("/chat/sessions/{session_id}/history", tags=["Chat"])
def get_chat_history(session_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return ChatService.get_history(db, session_id, current_user.user_id)


@router.delete("/chat/sessions/{session_id}", tags=["Chat"])
def delete_session(session_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == current_user.user_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.is_active = False
    db.commit()
    return {"message": "Chat session deleted"}


# ═══════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════

@router.get("/notifications", tags=["Notifications"])
def get_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Notification).filter(Notification.user_id == current_user.user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    return query.order_by(Notification.created_at.desc()).limit(50).all()


@router.patch("/notifications/{notification_id}/read", tags=["Notifications"])
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    notif = db.query(Notification).filter(
        Notification.notification_id == notification_id,
        Notification.user_id == current_user.user_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.patch("/notifications/read-all", tags=["Notifications"])
def mark_all_read(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    db.query(Notification).filter(
        Notification.user_id == current_user.user_id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}


# ═══════════════════════════════════════════════════════════════
# NUTRITIONIST QUERIES
# ═══════════════════════════════════════════════════════════════

class QueryRequest(BaseModel):
    subject: str
    message: str
    priority: str = "normal"

@router.get("/nutritionists", tags=["Nutritionist"])
def list_nutritionists(db: Session = Depends(get_db), _=Depends(get_current_user)):
    return db.query(Nutritionist).filter(Nutritionist.is_available == True).all()


@router.post("/nutritionist-queries", tags=["Nutritionist"])
def submit_query(data: QueryRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    query = NutritionistQuery(
        user_id=current_user.user_id,
        subject=data.subject,
        message=data.message,
        priority=data.priority,
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return {"message": "Query submitted", "query_id": query.query_id}


@router.get("/nutritionist-queries", tags=["Nutritionist"])
def get_my_queries(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(NutritionistQuery).filter(
        NutritionistQuery.user_id == current_user.user_id
    ).order_by(NutritionistQuery.created_at.desc()).all()


# ═══════════════════════════════════════════════════════════════
# PROGRESS & MILESTONES
# ═══════════════════════════════════════════════════════════════

@router.get("/progress/milestones", tags=["Progress"])
def get_milestones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(ProgressMilestone).filter(
        ProgressMilestone.user_id == current_user.user_id
    ).order_by(ProgressMilestone.created_at.desc()).all()


@router.get("/progress/summary", tags=["Progress"])
def get_progress_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.user_id).first()

    # Weight trend
    weight_logs = db.query(WeightTracking).filter(
        WeightTracking.user_id == current_user.user_id
    ).order_by(WeightTracking.recorded_date.asc()).all()

    start_weight = float(weight_logs[0].weight_kg) if weight_logs else None
    current_weight = float(weight_logs[-1].weight_kg) if weight_logs else None
    weight_change = round(current_weight - start_weight, 1) if (start_weight and current_weight) else None

    # Logging streak
    today = date.today()
    streak = 0
    check_date = today
    while True:
        has_log = db.query(MealLog).filter(
            MealLog.user_id == current_user.user_id,
            MealLog.logged_date == check_date
        ).first()
        if has_log:
            streak += 1
            check_date = check_date - timedelta(days=1)
        else:
            break

    return {
        "start_weight_kg": start_weight,
        "current_weight_kg": current_weight,
        "target_weight_kg": float(profile.target_weight_kg) if profile and profile.target_weight_kg else None,
        "weight_change_kg": weight_change,
        "logging_streak_days": streak,
        "total_days_logged": db.query(MealLog.logged_date).filter(
            MealLog.user_id == current_user.user_id
        ).distinct().count(),
        "goal": profile.primary_goal if profile else None,
        "bmi": float(profile.weight_kg) / ((float(profile.height_cm) / 100) ** 2) if (profile and profile.weight_kg and profile.height_cm) else None,
    }


# ═══════════════════════════════════════════════════════════════
# FEEDBACK
# ═══════════════════════════════════════════════════════════════

class FeedbackRequest(BaseModel):
    feedback_type: str
    rating: Optional[int] = None
    comments: Optional[str] = None

@router.post("/feedback", tags=["Feedback"])
def submit_feedback(data: FeedbackRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    fb = UserFeedback(
        user_id=current_user.user_id,
        feedback_type=data.feedback_type,
        rating=data.rating,
        comments=data.comments,
    )
    db.add(fb)
    db.commit()
    return {"message": "Feedback submitted, thank you!"}


# ═══════════════════════════════════════════════════════════════
# NUTRITION TIPS
# ═══════════════════════════════════════════════════════════════

@router.get("/nutrition-tips", tags=["Tips"])
def get_tips(limit: int = 3, db: Session = Depends(get_db), _=Depends(get_current_user)):
    tips = db.query(NutritionTip).filter(NutritionTip.is_active == True).limit(limit).all()
    return tips

from sqlalchemy import (
    Column, Integer, String, Boolean, Text, Date, Time,
    DateTime, Enum, JSON, DECIMAL, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import enum


# ── Users ──────────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    user_id         = Column(Integer, primary_key=True, autoincrement=True)
    username        = Column(String(50), unique=True, nullable=False)
    email           = Column(String(100), unique=True, nullable=False)
    password_hash   = Column(String(255), nullable=False)
    profile_picture = Column(String(500), nullable=True)
    role            = Column(Enum("user", "admin", "nutritionist"), default="user")
    is_active       = Column(Boolean, default=True)
    is_verified     = Column(Boolean, default=False)
    verify_token    = Column(String(255), nullable=True)
    reset_token     = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    last_login      = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    profile         = relationship("UserProfile", back_populates="user", uselist=False)
    sessions        = relationship("UserSession", back_populates="user")
    weight_logs     = relationship("WeightTracking", back_populates="user")
    diet_plans      = relationship("DietPlan", back_populates="user")
    meal_logs       = relationship("MealLog", back_populates="user")
    water_logs      = relationship("WaterLog", back_populates="user")
    chat_sessions   = relationship("ChatSession", back_populates="user")
    notifications   = relationship("Notification", back_populates="user")
    notification_prefs = relationship("NotificationPreference", back_populates="user", uselist=False)
    milestones      = relationship("ProgressMilestone", back_populates="user")
    feedback        = relationship("UserFeedback", back_populates="user")
    pdf_reports     = relationship("PdfReport", back_populates="user")
    queries         = relationship("NutritionistQuery", back_populates="user")


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id    = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    session_token = Column(String(512), unique=True, nullable=False)
    refresh_token = Column(String(512), unique=True, nullable=True)
    ip_address    = Column(String(45))
    user_agent    = Column(Text)
    device_type   = Column(String(50))
    is_active     = Column(Boolean, default=True)
    login_time    = Column(DateTime, server_default=func.now())
    last_activity = Column(DateTime, server_default=func.now(), onupdate=func.now())
    logout_time   = Column(DateTime, nullable=True)
    expires_at    = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="sessions")


# ── User Profile ──────────────────────────────────────────────────────────────

class UserProfile(Base):
    __tablename__ = "user_profiles"

    profile_id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name       = Column(String(100), nullable=False)
    date_of_birth   = Column(Date, nullable=True)
    gender          = Column(Enum("male", "female", "other", "prefer_not_to_say"), nullable=True)
    height_cm       = Column(DECIMAL(5, 2), nullable=True)
    weight_kg       = Column(DECIMAL(5, 2), nullable=True)

    # Health
    diagnosed_diseases  = Column(JSON, nullable=True)
    medications         = Column(JSON, nullable=True)
    allergies           = Column(JSON, nullable=True)
    recent_surgeries    = Column(Text, nullable=True)
    special_conditions  = Column(JSON, nullable=True)

    # Lifestyle
    activity_level  = Column(Enum("sedentary", "lightly_active", "moderately_active", "very_active"), default="sedentary")
    work_type       = Column(Enum("desk_job", "field_work", "active_job", "other"), default="desk_job")
    sleep_duration  = Column(DECIMAL(3, 1), nullable=True)
    sleep_quality   = Column(Enum("good", "poor", "irregular"), nullable=True)
    stress_level    = Column(Enum("low", "moderate", "high"), nullable=True)

    # Diet
    dietary_preference  = Column(Enum("vegetarian", "non_vegetarian", "vegan", "pescatarian"), default="non_vegetarian")
    meal_frequency      = Column(Integer, default=3)
    snacking_habits     = Column(Boolean, default=False)
    snack_types         = Column(Text, nullable=True)
    meal_timings        = Column(JSON, nullable=True)
    water_intake_liters = Column(DECIMAL(4, 2), nullable=True)
    beverages_consumed  = Column(JSON, nullable=True)
    favorite_foods      = Column(Text, nullable=True)
    disliked_foods      = Column(Text, nullable=True)

    # Goals
    primary_goal        = Column(Enum("weight_loss", "weight_gain", "maintenance", "muscle_gain", "improve_health"), default="maintenance")
    target_weight_kg    = Column(DECIMAL(5, 2), nullable=True)
    goal_timeline_days  = Column(Integer, nullable=True)
    past_diet_plans     = Column(Boolean, default=False)
    past_diet_experience = Column(Text, nullable=True)

    # Preferences
    food_cravings       = Column(JSON, nullable=True)
    cooking_habits      = Column(Enum("home_cooked", "outside_food", "mixed"), default="mixed")
    cultural_restrictions = Column(Text, nullable=True)

    # Calculated
    calculated_tdee         = Column(Integer, nullable=True)
    recommended_calories    = Column(Integer, nullable=True)
    recommended_protein     = Column(DECIMAL(5, 2), nullable=True)
    recommended_carbs       = Column(DECIMAL(5, 2), nullable=True)
    recommended_fats        = Column(DECIMAL(5, 2), nullable=True)

    onboarding_complete = Column(Boolean, default=False)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="profile")


# ── Food ──────────────────────────────────────────────────────────────────────

class FoodCategory(Base):
    __tablename__ = "food_categories"

    category_id   = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), unique=True, nullable=False)
    description   = Column(Text, nullable=True)
    icon          = Column(String(100), nullable=True)

    food_items = relationship("FoodItem", back_populates="category")


class FoodItem(Base):
    __tablename__ = "food_items"

    food_id           = Column(Integer, primary_key=True, autoincrement=True)
    food_name         = Column(String(150), nullable=False)
    food_name_local   = Column(String(150), nullable=True)
    category_id       = Column(Integer, ForeignKey("food_categories.category_id"), nullable=True)
    calories          = Column(DECIMAL(7, 2), nullable=False)
    protein_g         = Column(DECIMAL(6, 2), default=0)
    carbohydrates_g   = Column(DECIMAL(6, 2), default=0)
    fats_g            = Column(DECIMAL(6, 2), default=0)
    fiber_g           = Column(DECIMAL(6, 2), default=0)
    sugar_g           = Column(DECIMAL(6, 2), default=0)
    sodium_mg         = Column(DECIMAL(7, 2), default=0)
    default_serving_g = Column(DECIMAL(6, 2), default=100)
    serving_description = Column(String(100), default="100g")
    is_vegetarian     = Column(Boolean, default=True)
    is_vegan          = Column(Boolean, default=False)
    is_gluten_free    = Column(Boolean, default=False)
    is_dairy_free     = Column(Boolean, default=True)
    common_allergens  = Column(JSON, nullable=True)
    is_active         = Column(Boolean, default=True)
    source            = Column(String(100), default="manual")
    created_at        = Column(DateTime, server_default=func.now())
    updated_at        = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category     = relationship("FoodCategory", back_populates="food_items")
    alternatives = relationship("FoodAlternative", foreign_keys="FoodAlternative.food_id", back_populates="food")
    meal_items   = relationship("MealItem", back_populates="food")
    meal_logs    = relationship("MealLog", back_populates="food")


class FoodAlternative(Base):
    __tablename__ = "food_alternatives"

    alternative_id      = Column(Integer, primary_key=True, autoincrement=True)
    food_id             = Column(Integer, ForeignKey("food_items.food_id"), nullable=False)
    alternative_food_id = Column(Integer, ForeignKey("food_items.food_id"), nullable=False)
    reason              = Column(Text, nullable=True)
    suitability_score   = Column(Integer, nullable=True)
    created_at          = Column(DateTime, server_default=func.now())

    food        = relationship("FoodItem", foreign_keys=[food_id], back_populates="alternatives")
    alternative = relationship("FoodItem", foreign_keys=[alternative_food_id])


# ── Diet Plans ────────────────────────────────────────────────────────────────

class DietPlan(Base):
    __tablename__ = "diet_plans"

    plan_id             = Column(Integer, primary_key=True, autoincrement=True)
    user_id             = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    plan_name           = Column(String(100), default="My Diet Plan")
    description         = Column(Text, nullable=True)
    daily_calories      = Column(Integer, nullable=False)
    protein_target_g    = Column(DECIMAL(6, 2), nullable=True)
    carbs_target_g      = Column(DECIMAL(6, 2), nullable=True)
    fats_target_g       = Column(DECIMAL(6, 2), nullable=True)
    fiber_target_g      = Column(DECIMAL(5, 2), nullable=True)
    water_target_liters = Column(DECIMAL(4, 2), default=2.0)
    meals_per_day       = Column(Integer, default=3)
    start_date          = Column(Date, nullable=False)
    end_date            = Column(Date, nullable=True)
    is_active           = Column(Boolean, default=True)
    generated_by        = Column(Enum("ai", "nutritionist", "user"), default="ai")
    version             = Column(Integer, default=1)
    created_at          = Column(DateTime, server_default=func.now())
    updated_at          = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user        = relationship("User", back_populates="diet_plans")
    daily_plans = relationship("DailyMealPlan", back_populates="plan", cascade="all, delete-orphan")
    adjustments = relationship("DietAdjustment", back_populates="plan")


class DailyMealPlan(Base):
    __tablename__ = "daily_meal_plans"

    daily_plan_id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id       = Column(Integer, ForeignKey("diet_plans.plan_id", ondelete="CASCADE"), nullable=False)
    day_number    = Column(Integer, nullable=False)
    meal_date     = Column(Date, nullable=True)
    total_calories = Column(Integer, default=0)
    total_protein  = Column(DECIMAL(6, 2), default=0)
    total_carbs    = Column(DECIMAL(6, 2), default=0)
    total_fats     = Column(DECIMAL(6, 2), default=0)
    notes          = Column(Text, nullable=True)

    plan  = relationship("DietPlan", back_populates="daily_plans")
    meals = relationship("Meal", back_populates="daily_plan", cascade="all, delete-orphan")


class Meal(Base):
    __tablename__ = "meals"

    meal_id        = Column(Integer, primary_key=True, autoincrement=True)
    daily_plan_id  = Column(Integer, ForeignKey("daily_meal_plans.daily_plan_id", ondelete="CASCADE"), nullable=False)
    meal_type      = Column(Enum("breakfast", "morning_snack", "lunch", "evening_snack", "dinner", "late_snack"), nullable=False)
    meal_name      = Column(String(100), nullable=True)
    scheduled_time = Column(Time, nullable=True)
    total_calories = Column(Integer, default=0)
    total_protein  = Column(DECIMAL(6, 2), default=0)
    total_carbs    = Column(DECIMAL(6, 2), default=0)
    total_fats     = Column(DECIMAL(6, 2), default=0)
    instructions   = Column(Text, nullable=True)

    daily_plan = relationship("DailyMealPlan", back_populates="meals")
    items      = relationship("MealItem", back_populates="meal", cascade="all, delete-orphan")
    missed     = relationship("MissedMeal", back_populates="meal")


class MealItem(Base):
    __tablename__ = "meal_items"

    meal_item_id      = Column(Integer, primary_key=True, autoincrement=True)
    meal_id           = Column(Integer, ForeignKey("meals.meal_id", ondelete="CASCADE"), nullable=False)
    food_id           = Column(Integer, ForeignKey("food_items.food_id"), nullable=False)
    quantity_g        = Column(DECIMAL(7, 2), nullable=False)
    calories          = Column(DECIMAL(7, 2), default=0)
    protein_g         = Column(DECIMAL(6, 2), default=0)
    carbs_g           = Column(DECIMAL(6, 2), default=0)
    fats_g            = Column(DECIMAL(6, 2), default=0)
    preparation_notes = Column(Text, nullable=True)

    meal = relationship("Meal", back_populates="items")
    food = relationship("FoodItem", back_populates="meal_items")


class DietAdjustment(Base):
    __tablename__ = "diet_adjustments"

    adjustment_id     = Column(Integer, primary_key=True, autoincrement=True)
    plan_id           = Column(Integer, ForeignKey("diet_plans.plan_id", ondelete="CASCADE"), nullable=False)
    adjustment_reason = Column(Enum("weight_change", "missed_meals", "user_feedback", "goal_update", "allergy_update", "plateau"), nullable=False)
    old_calories      = Column(Integer, nullable=True)
    new_calories      = Column(Integer, nullable=True)
    old_macros        = Column(JSON, nullable=True)
    new_macros        = Column(JSON, nullable=True)
    adjustment_details = Column(Text, nullable=True)
    adjusted_by       = Column(Enum("system", "admin", "nutritionist"), default="system")
    created_at        = Column(DateTime, server_default=func.now())

    plan = relationship("DietPlan", back_populates="adjustments")


# ── Tracking ──────────────────────────────────────────────────────────────────

class WeightTracking(Base):
    __tablename__ = "weight_tracking"

    weight_id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    weight_kg      = Column(DECIMAL(5, 2), nullable=False)
    body_fat_pct   = Column(DECIMAL(4, 2), nullable=True)
    muscle_mass_kg = Column(DECIMAL(5, 2), nullable=True)
    recorded_date  = Column(Date, nullable=False)
    notes          = Column(Text, nullable=True)
    created_at     = Column(DateTime, server_default=func.now())

    __table_args__ = (UniqueConstraint("user_id", "recorded_date"),)
    user = relationship("User", back_populates="weight_logs")


class MealLog(Base):
    __tablename__ = "meal_logs"

    log_id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id             = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    food_id             = Column(Integer, ForeignKey("food_items.food_id"), nullable=False)
    meal_type           = Column(Enum("breakfast", "morning_snack", "lunch", "evening_snack", "dinner", "late_snack", "other"), nullable=False)
    quantity_g          = Column(DECIMAL(7, 2), nullable=False)
    actual_calories     = Column(DECIMAL(7, 2), default=0)
    actual_protein_g    = Column(DECIMAL(6, 2), default=0)
    actual_carbs_g      = Column(DECIMAL(6, 2), default=0)
    actual_fats_g       = Column(DECIMAL(6, 2), default=0)
    logged_date         = Column(Date, nullable=False)
    logged_time         = Column(Time, nullable=True)
    is_planned          = Column(Boolean, default=False)
    plan_id             = Column(Integer, ForeignKey("diet_plans.plan_id"), nullable=True)
    satisfaction_rating = Column(Integer, nullable=True)
    mood_before         = Column(String(50), nullable=True)
    mood_after          = Column(String(50), nullable=True)
    notes               = Column(Text, nullable=True)
    created_at          = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="meal_logs")
    food = relationship("FoodItem", back_populates="meal_logs")


class WaterLog(Base):
    __tablename__ = "water_logs"

    water_log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    amount_ml    = Column(Integer, nullable=False)
    logged_date  = Column(Date, nullable=False)
    logged_time  = Column(Time, nullable=True)
    created_at   = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="water_logs")


class MissedMeal(Base):
    __tablename__ = "missed_meals"

    missed_id       = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    meal_id         = Column(Integer, ForeignKey("meals.meal_id"), nullable=False)
    missed_date     = Column(Date, nullable=False)
    reason          = Column(String(255), nullable=True)
    was_compensated = Column(Boolean, default=False)
    created_at      = Column(DateTime, server_default=func.now())

    meal = relationship("Meal", back_populates="missed")


# ── Progress ──────────────────────────────────────────────────────────────────

class ProgressMilestone(Base):
    __tablename__ = "progress_milestones"

    milestone_id   = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    milestone_type = Column(Enum("weight", "habit", "streak", "calorie", "hydration", "achievement"), nullable=False)
    milestone_name = Column(String(150), nullable=False)
    description    = Column(Text, nullable=True)
    target_value   = Column(DECIMAL(10, 2), nullable=True)
    achieved_value = Column(DECIMAL(10, 2), nullable=True)
    achieved_date  = Column(Date, nullable=True)
    is_achieved    = Column(Boolean, default=False)
    badge_icon     = Column(String(100), nullable=True)
    created_at     = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="milestones")


# ── Chat ──────────────────────────────────────────────────────────────────────

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id      = Column(String(100), primary_key=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title           = Column(String(200), default="New Chat")
    started_at      = Column(DateTime, server_default=func.now())
    last_message_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_active       = Column(Boolean, default=True)

    user     = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatHistory", back_populates="session", cascade="all, delete-orphan")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    chat_id          = Column(Integer, primary_key=True, autoincrement=True)
    session_id       = Column(String(100), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    user_id          = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    role             = Column(Enum("user", "assistant"), nullable=False)
    message          = Column(Text, nullable=False)
    intent           = Column(String(100), nullable=True)
    sentiment        = Column(String(30), nullable=True)
    confidence_score = Column(DECIMAL(4, 3), nullable=True)
    tokens_used      = Column(Integer, nullable=True)
    created_at       = Column(DateTime, server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")


# ── Notifications ─────────────────────────────────────────────────────────────

class Notification(Base):
    __tablename__ = "notifications"

    notification_id   = Column(Integer, primary_key=True, autoincrement=True)
    user_id           = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    notification_type = Column(Enum("meal_reminder", "weight_update", "diet_update", "progress_update", "tip", "achievement", "system"), nullable=False)
    title             = Column(String(200), nullable=False)
    message           = Column(Text, nullable=False)
    icon              = Column(String(100), nullable=True)
    scheduled_time    = Column(DateTime, nullable=True)
    sent_time         = Column(DateTime, nullable=True)
    is_sent           = Column(Boolean, default=False)
    is_read           = Column(Boolean, default=False)
    action_url        = Column(String(500), nullable=True)
    created_at        = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="notifications")


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    pref_id            = Column(Integer, primary_key=True, autoincrement=True)
    user_id            = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    meal_reminders     = Column(Boolean, default=True)
    weight_reminders   = Column(Boolean, default=True)
    diet_updates       = Column(Boolean, default=True)
    progress_updates   = Column(Boolean, default=True)
    nutrition_tips     = Column(Boolean, default=True)
    achievement_alerts = Column(Boolean, default=True)
    reminder_time      = Column(Time, default="08:00:00")
    timezone           = Column(String(50), default="UTC")
    created_at         = Column(DateTime, server_default=func.now())
    updated_at         = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="notification_prefs")


# ── Nutrition Tips ────────────────────────────────────────────────────────────

class NutritionTip(Base):
    __tablename__ = "nutrition_tips"

    tip_id      = Column(Integer, primary_key=True, autoincrement=True)
    tip_title   = Column(String(200), nullable=False)
    tip_content = Column(Text, nullable=False)
    category    = Column(Enum("nutrition", "hydration", "lifestyle", "meal_timing", "weight_management", "mental_health"), nullable=False)
    tags        = Column(JSON, nullable=True)
    target_goals      = Column(JSON, nullable=True)
    target_conditions = Column(JSON, nullable=True)
    frequency   = Column(Enum("daily", "weekly", "on_request", "milestone_based"), default="weekly")
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())


class UserNutritionTip(Base):
    __tablename__ = "user_nutrition_tips"

    user_tip_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    tip_id      = Column(Integer, ForeignKey("nutrition_tips.tip_id"), nullable=False)
    shown_date  = Column(Date, nullable=False)
    is_read     = Column(Boolean, default=False)
    is_helpful  = Column(Boolean, nullable=True)
    feedback    = Column(Text, nullable=True)
    created_at  = Column(DateTime, server_default=func.now())


# ── Nutritionists ─────────────────────────────────────────────────────────────

class Nutritionist(Base):
    __tablename__ = "nutritionists"

    nutritionist_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), unique=True, nullable=True)
    full_name       = Column(String(100), nullable=False)
    email           = Column(String(100), unique=True, nullable=False)
    phone           = Column(String(20), nullable=True)
    specialization  = Column(String(150), nullable=True)
    bio             = Column(Text, nullable=True)
    profile_picture = Column(String(500), nullable=True)
    qualifications  = Column(JSON, nullable=True)
    languages       = Column(JSON, nullable=True)
    is_available    = Column(Boolean, default=True)
    rating          = Column(DECIMAL(3, 2), nullable=True)
    total_reviews   = Column(Integer, default=0)
    created_at      = Column(DateTime, server_default=func.now())

    queries = relationship("NutritionistQuery", back_populates="nutritionist")


class NutritionistQuery(Base):
    __tablename__ = "nutritionist_queries"

    query_id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    nutritionist_id = Column(Integer, ForeignKey("nutritionists.nutritionist_id"), nullable=True)
    subject         = Column(String(200), nullable=False)
    message         = Column(Text, nullable=False)
    attachments     = Column(JSON, nullable=True)
    priority        = Column(Enum("low", "normal", "high", "urgent"), default="normal")
    status          = Column(Enum("pending", "assigned", "in_progress", "responded", "closed"), default="pending")
    response        = Column(Text, nullable=True)
    responded_at    = Column(DateTime, nullable=True)
    closed_at       = Column(DateTime, nullable=True)
    created_at      = Column(DateTime, server_default=func.now())
    updated_at      = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user         = relationship("User", back_populates="queries")
    nutritionist = relationship("Nutritionist", back_populates="queries")


# ── Reports & Feedback ────────────────────────────────────────────────────────

class PdfReport(Base):
    __tablename__ = "pdf_reports"

    report_id      = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    report_type    = Column(Enum("diet_plan", "progress_report", "health_summary", "weekly_summary"), nullable=False)
    report_title   = Column(String(200), nullable=False)
    file_path      = Column(String(500), nullable=True)
    generated_date = Column(Date, nullable=False)
    report_data    = Column(JSON, nullable=True)
    download_count = Column(Integer, default=0)
    created_at     = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="pdf_reports")


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    feedback_id   = Column(Integer, primary_key=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    feedback_type = Column(Enum("meal_satisfaction", "plan_adherence", "general", "feature_request", "bug_report"), nullable=False)
    rating        = Column(Integer, nullable=True)
    comments      = Column(Text, nullable=True)
    context       = Column(JSON, nullable=True)
    created_at    = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="feedback")

-- ============================================================
-- SmartBites Diet Planner - Production Schema
-- Version: 1.0
-- Engine: MySQL 8.0+
-- ============================================================

CREATE DATABASE IF NOT EXISTS smartbites_diet_planner
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smartbites_diet_planner;

-- ============================================================
-- 1. USERS & AUTH
-- ============================================================

CREATE TABLE users (
    user_id        INT PRIMARY KEY AUTO_INCREMENT,
    username       VARCHAR(50) UNIQUE NOT NULL,
    email          VARCHAR(100) UNIQUE NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(500) DEFAULT NULL,
    role           ENUM('user', 'admin', 'nutritionist') DEFAULT 'user',
    is_active      BOOLEAN DEFAULT TRUE,
    is_verified    BOOLEAN DEFAULT FALSE,          -- email verification
    verify_token   VARCHAR(255) DEFAULT NULL,
    reset_token    VARCHAR(255) DEFAULT NULL,
    reset_token_expires TIMESTAMP NULL DEFAULT NULL,
    last_login     TIMESTAMP NULL DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    session_id     INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    session_token  VARCHAR(512) UNIQUE NOT NULL,
    refresh_token  VARCHAR(512) UNIQUE DEFAULT NULL,
    ip_address     VARCHAR(45),
    user_agent     TEXT,
    device_type    VARCHAR(50),
    is_active      BOOLEAN DEFAULT TRUE,
    login_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    logout_time    TIMESTAMP NULL DEFAULT NULL,
    expires_at     TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_token (session_token(255)),
    INDEX idx_user_active (user_id, is_active)
);

-- ============================================================
-- 2. USER PROFILES
-- ============================================================

CREATE TABLE user_profiles (
    profile_id     INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT UNIQUE NOT NULL,

    -- Basic Info
    full_name      VARCHAR(100) NOT NULL,
    date_of_birth  DATE DEFAULT NULL,
    age            INT GENERATED ALWAYS AS (TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE())) VIRTUAL,
    gender         ENUM('male', 'female', 'other', 'prefer_not_to_say'),
    height_cm      DECIMAL(5,2) DEFAULT NULL,
    weight_kg      DECIMAL(5,2) DEFAULT NULL,
    bmi            DECIMAL(4,2) GENERATED ALWAYS AS (
                     ROUND(weight_kg / ((height_cm/100) * (height_cm/100)), 2)
                   ) VIRTUAL,

    -- Health & Medical
    diagnosed_diseases  JSON DEFAULT NULL,   -- ["diabetes","hypertension"]
    medications         JSON DEFAULT NULL,
    allergies           JSON DEFAULT NULL,   -- ["gluten","nuts","dairy"]
    recent_surgeries    TEXT DEFAULT NULL,
    special_conditions  JSON DEFAULT NULL,   -- ["pregnancy","lactation"]

    -- Lifestyle
    activity_level  ENUM('sedentary','lightly_active','moderately_active','very_active') DEFAULT 'sedentary',
    work_type       ENUM('desk_job','field_work','active_job','other') DEFAULT 'desk_job',
    sleep_duration  DECIMAL(3,1) DEFAULT NULL,
    sleep_quality   ENUM('good','poor','irregular') DEFAULT 'good',
    stress_level    ENUM('low','moderate','high') DEFAULT 'moderate',

    -- Dietary Habits
    dietary_preference  ENUM('vegetarian','non_vegetarian','vegan','pescatarian') DEFAULT 'non_vegetarian',
    meal_frequency      INT DEFAULT 3,
    snacking_habits     BOOLEAN DEFAULT FALSE,
    snack_types         TEXT DEFAULT NULL,
    meal_timings        JSON DEFAULT NULL,   -- {"breakfast":"08:00","lunch":"13:00","dinner":"20:00"}
    water_intake_liters DECIMAL(4,2) DEFAULT NULL,
    beverages_consumed  JSON DEFAULT NULL,   -- ["tea","coffee"]
    favorite_foods      TEXT DEFAULT NULL,
    disliked_foods      TEXT DEFAULT NULL,

    -- Goals
    primary_goal    ENUM('weight_loss','weight_gain','maintenance','muscle_gain','improve_health') DEFAULT 'maintenance',
    target_weight_kg DECIMAL(5,2) DEFAULT NULL,
    goal_timeline_days INT DEFAULT NULL,
    past_diet_plans  BOOLEAN DEFAULT FALSE,
    past_diet_experience TEXT DEFAULT NULL,

    -- Food Preferences
    food_cravings       JSON DEFAULT NULL,   -- ["sugar","salty","fried"]
    cooking_habits      ENUM('home_cooked','outside_food','mixed') DEFAULT 'mixed',
    cultural_restrictions TEXT DEFAULT NULL,

    -- Calculated TDEE & Macros (auto-populated by backend)
    calculated_tdee     INT DEFAULT NULL,
    recommended_calories INT DEFAULT NULL,
    recommended_protein  DECIMAL(5,2) DEFAULT NULL,
    recommended_carbs    DECIMAL(5,2) DEFAULT NULL,
    recommended_fats     DECIMAL(5,2) DEFAULT NULL,

    onboarding_complete BOOLEAN DEFAULT FALSE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_goal (primary_goal),
    INDEX idx_dietary (dietary_preference)
);

-- ============================================================
-- 3. FOOD DATABASE
-- ============================================================

CREATE TABLE food_categories (
    category_id   INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    description   TEXT DEFAULT NULL,
    icon          VARCHAR(100) DEFAULT NULL
);

CREATE TABLE food_items (
    food_id        INT PRIMARY KEY AUTO_INCREMENT,
    food_name      VARCHAR(150) NOT NULL,
    food_name_local VARCHAR(150) DEFAULT NULL,  -- local language name
    category_id    INT DEFAULT NULL,
    -- Nutrition per 100g
    calories       DECIMAL(7,2) NOT NULL,
    protein_g      DECIMAL(6,2) DEFAULT 0,
    carbohydrates_g DECIMAL(6,2) DEFAULT 0,
    fats_g         DECIMAL(6,2) DEFAULT 0,
    fiber_g        DECIMAL(6,2) DEFAULT 0,
    sugar_g        DECIMAL(6,2) DEFAULT 0,
    sodium_mg      DECIMAL(7,2) DEFAULT 0,
    -- Serving info
    default_serving_g DECIMAL(6,2) DEFAULT 100,
    serving_description VARCHAR(100) DEFAULT '100g',
    -- Dietary flags
    is_vegetarian  BOOLEAN DEFAULT TRUE,
    is_vegan       BOOLEAN DEFAULT FALSE,
    is_gluten_free BOOLEAN DEFAULT FALSE,
    is_dairy_free  BOOLEAN DEFAULT TRUE,
    common_allergens JSON DEFAULT NULL,
    -- Meta
    is_active      BOOLEAN DEFAULT TRUE,
    source         VARCHAR(100) DEFAULT 'manual',
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES food_categories(category_id),
    INDEX idx_name (food_name),
    INDEX idx_category (category_id),
    INDEX idx_flags (is_vegetarian, is_vegan, is_gluten_free)
);

CREATE TABLE food_alternatives (
    alternative_id       INT PRIMARY KEY AUTO_INCREMENT,
    food_id              INT NOT NULL,
    alternative_food_id  INT NOT NULL,
    reason               TEXT DEFAULT NULL,
    suitability_score    TINYINT CHECK (suitability_score BETWEEN 1 AND 10),
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES food_items(food_id),
    FOREIGN KEY (alternative_food_id) REFERENCES food_items(food_id),
    UNIQUE KEY unique_alt (food_id, alternative_food_id)
);

-- ============================================================
-- 4. DIET PLANS
-- ============================================================

CREATE TABLE diet_plans (
    plan_id          INT PRIMARY KEY AUTO_INCREMENT,
    user_id          INT NOT NULL,
    plan_name        VARCHAR(100) DEFAULT 'My Diet Plan',
    description      TEXT DEFAULT NULL,
    daily_calories   INT NOT NULL,
    protein_target_g  DECIMAL(6,2) DEFAULT NULL,
    carbs_target_g    DECIMAL(6,2) DEFAULT NULL,
    fats_target_g     DECIMAL(6,2) DEFAULT NULL,
    fiber_target_g    DECIMAL(5,2) DEFAULT NULL,
    water_target_liters DECIMAL(4,2) DEFAULT 2.0,
    meals_per_day    INT DEFAULT 3,
    start_date       DATE NOT NULL,
    end_date         DATE DEFAULT NULL,
    is_active        BOOLEAN DEFAULT TRUE,
    generated_by     ENUM('ai','nutritionist','user') DEFAULT 'ai',
    version          INT DEFAULT 1,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_active (user_id, is_active),
    INDEX idx_dates (start_date, end_date)
);

CREATE TABLE daily_meal_plans (
    daily_plan_id  INT PRIMARY KEY AUTO_INCREMENT,
    plan_id        INT NOT NULL,
    day_number     INT NOT NULL,           -- Day 1, 2, 3... of the plan
    meal_date      DATE DEFAULT NULL,
    total_calories INT DEFAULT 0,
    total_protein  DECIMAL(6,2) DEFAULT 0,
    total_carbs    DECIMAL(6,2) DEFAULT 0,
    total_fats     DECIMAL(6,2) DEFAULT 0,
    notes          TEXT DEFAULT NULL,
    FOREIGN KEY (plan_id) REFERENCES diet_plans(plan_id) ON DELETE CASCADE,
    UNIQUE KEY unique_plan_day (plan_id, day_number),
    INDEX idx_date (meal_date)
);

CREATE TABLE meals (
    meal_id        INT PRIMARY KEY AUTO_INCREMENT,
    daily_plan_id  INT NOT NULL,
    meal_type      ENUM('breakfast','morning_snack','lunch','evening_snack','dinner','late_snack') NOT NULL,
    meal_name      VARCHAR(100) DEFAULT NULL,
    scheduled_time TIME DEFAULT NULL,
    total_calories INT DEFAULT 0,
    total_protein  DECIMAL(6,2) DEFAULT 0,
    total_carbs    DECIMAL(6,2) DEFAULT 0,
    total_fats     DECIMAL(6,2) DEFAULT 0,
    instructions   TEXT DEFAULT NULL,
    FOREIGN KEY (daily_plan_id) REFERENCES daily_meal_plans(daily_plan_id) ON DELETE CASCADE,
    INDEX idx_type (meal_type)
);

CREATE TABLE meal_items (
    meal_item_id   INT PRIMARY KEY AUTO_INCREMENT,
    meal_id        INT NOT NULL,
    food_id        INT NOT NULL,
    quantity_g     DECIMAL(7,2) NOT NULL,
    calories       DECIMAL(7,2) DEFAULT 0,
    protein_g      DECIMAL(6,2) DEFAULT 0,
    carbs_g        DECIMAL(6,2) DEFAULT 0,
    fats_g         DECIMAL(6,2) DEFAULT 0,
    preparation_notes TEXT DEFAULT NULL,
    FOREIGN KEY (meal_id) REFERENCES meals(meal_id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(food_id)
);

CREATE TABLE diet_adjustments (
    adjustment_id     INT PRIMARY KEY AUTO_INCREMENT,
    plan_id           INT NOT NULL,
    adjustment_reason ENUM('weight_change','missed_meals','user_feedback','goal_update','allergy_update','plateau') NOT NULL,
    old_calories      INT,
    new_calories      INT,
    old_macros        JSON DEFAULT NULL,
    new_macros        JSON DEFAULT NULL,
    adjustment_details TEXT DEFAULT NULL,
    adjusted_by       ENUM('system','admin','nutritionist') DEFAULT 'system',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES diet_plans(plan_id) ON DELETE CASCADE
);

-- ============================================================
-- 5. MEAL LOGGING & TRACKING
-- ============================================================

CREATE TABLE weight_tracking (
    weight_id      INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    weight_kg      DECIMAL(5,2) NOT NULL,
    body_fat_pct   DECIMAL(4,2) DEFAULT NULL,
    muscle_mass_kg DECIMAL(5,2) DEFAULT NULL,
    recorded_date  DATE NOT NULL,
    notes          TEXT DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, recorded_date),
    INDEX idx_user_date (user_id, recorded_date)
);

CREATE TABLE meal_logs (
    log_id              INT PRIMARY KEY AUTO_INCREMENT,
    user_id             INT NOT NULL,
    food_id             INT NOT NULL,
    meal_type           ENUM('breakfast','morning_snack','lunch','evening_snack','dinner','late_snack','other') NOT NULL,
    quantity_g          DECIMAL(7,2) NOT NULL,
    actual_calories     DECIMAL(7,2) DEFAULT 0,
    actual_protein_g    DECIMAL(6,2) DEFAULT 0,
    actual_carbs_g      DECIMAL(6,2) DEFAULT 0,
    actual_fats_g       DECIMAL(6,2) DEFAULT 0,
    logged_date         DATE NOT NULL,
    logged_time         TIME DEFAULT NULL,
    is_planned          BOOLEAN DEFAULT FALSE,   -- was this part of their plan?
    plan_id             INT DEFAULT NULL,
    satisfaction_rating TINYINT DEFAULT NULL CHECK (satisfaction_rating BETWEEN 1 AND 5),
    mood_before         VARCHAR(50) DEFAULT NULL,
    mood_after          VARCHAR(50) DEFAULT NULL,
    notes               TEXT DEFAULT NULL,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(food_id),
    FOREIGN KEY (plan_id) REFERENCES diet_plans(plan_id),
    INDEX idx_user_date (user_id, logged_date),
    INDEX idx_date_type (logged_date, meal_type)
);

CREATE TABLE water_logs (
    water_log_id   INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    amount_ml      INT NOT NULL,
    logged_date    DATE NOT NULL,
    logged_time    TIME DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_date (user_id, logged_date)
);

CREATE TABLE missed_meals (
    missed_id      INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    meal_id        INT NOT NULL,
    missed_date    DATE NOT NULL,
    reason         VARCHAR(255) DEFAULT NULL,
    was_compensated BOOLEAN DEFAULT FALSE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (meal_id) REFERENCES meals(meal_id)
);

-- ============================================================
-- 6. PROGRESS & MILESTONES
-- ============================================================

CREATE TABLE progress_milestones (
    milestone_id   INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    milestone_type ENUM('weight','habit','streak','calorie','hydration','achievement') NOT NULL,
    milestone_name VARCHAR(150) NOT NULL,
    description    TEXT DEFAULT NULL,
    target_value   DECIMAL(10,2) DEFAULT NULL,
    achieved_value DECIMAL(10,2) DEFAULT NULL,
    achieved_date  DATE DEFAULT NULL,
    is_achieved    BOOLEAN DEFAULT FALSE,
    badge_icon     VARCHAR(100) DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_achieved (user_id, is_achieved)
);

-- ============================================================
-- 7. CHATBOT
-- ============================================================

CREATE TABLE chat_sessions (
    session_id     VARCHAR(100) PRIMARY KEY,
    user_id        INT NOT NULL,
    title          VARCHAR(200) DEFAULT 'New Chat',
    started_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active      BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
);

CREATE TABLE chat_history (
    chat_id        INT PRIMARY KEY AUTO_INCREMENT,
    session_id     VARCHAR(100) NOT NULL,
    user_id        INT NOT NULL,
    role           ENUM('user','assistant') NOT NULL,
    message        TEXT NOT NULL,
    intent         VARCHAR(100) DEFAULT NULL,
    sentiment      VARCHAR(30) DEFAULT NULL,
    confidence_score DECIMAL(4,3) DEFAULT NULL,
    tokens_used    INT DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_user_time (user_id, created_at)
);

CREATE TABLE chat_context (
    context_id     INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    session_id     VARCHAR(100) NOT NULL,
    context_key    VARCHAR(100) NOT NULL,
    context_value  TEXT,
    expires_at     TIMESTAMP NULL DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_session_key (session_id, context_key),
    INDEX idx_session_key (session_id, context_key)
);

-- ============================================================
-- 8. NOTIFICATIONS
-- ============================================================

CREATE TABLE notifications (
    notification_id  INT PRIMARY KEY AUTO_INCREMENT,
    user_id          INT NOT NULL,
    notification_type ENUM('meal_reminder','weight_update','diet_update','progress_update','tip','achievement','system') NOT NULL,
    title            VARCHAR(200) NOT NULL,
    message          TEXT NOT NULL,
    icon             VARCHAR(100) DEFAULT NULL,
    scheduled_time   TIMESTAMP DEFAULT NULL,
    sent_time        TIMESTAMP NULL DEFAULT NULL,
    is_sent          BOOLEAN DEFAULT FALSE,
    is_read          BOOLEAN DEFAULT FALSE,
    action_url       VARCHAR(500) DEFAULT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_read (user_id, is_read),
    INDEX idx_scheduled (scheduled_time, is_sent)
);

CREATE TABLE notification_preferences (
    pref_id           INT PRIMARY KEY AUTO_INCREMENT,
    user_id           INT UNIQUE NOT NULL,
    meal_reminders    BOOLEAN DEFAULT TRUE,
    weight_reminders  BOOLEAN DEFAULT TRUE,
    diet_updates      BOOLEAN DEFAULT TRUE,
    progress_updates  BOOLEAN DEFAULT TRUE,
    nutrition_tips    BOOLEAN DEFAULT TRUE,
    achievement_alerts BOOLEAN DEFAULT TRUE,
    reminder_time     TIME DEFAULT '08:00:00',
    timezone          VARCHAR(50) DEFAULT 'UTC',
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ============================================================
-- 9. NUTRITION TIPS
-- ============================================================

CREATE TABLE nutrition_tips (
    tip_id         INT PRIMARY KEY AUTO_INCREMENT,
    tip_title      VARCHAR(200) NOT NULL,
    tip_content    TEXT NOT NULL,
    category       ENUM('nutrition','hydration','lifestyle','meal_timing','weight_management','mental_health') NOT NULL,
    tags           JSON DEFAULT NULL,
    target_goals   JSON DEFAULT NULL,  -- ["weight_loss","muscle_gain"]
    target_conditions JSON DEFAULT NULL, -- ["diabetes","hypertension"]
    frequency      ENUM('daily','weekly','on_request','milestone_based') DEFAULT 'weekly',
    is_active      BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE user_nutrition_tips (
    user_tip_id    INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    tip_id         INT NOT NULL,
    shown_date     DATE NOT NULL,
    is_read        BOOLEAN DEFAULT FALSE,
    is_helpful     BOOLEAN DEFAULT NULL,
    feedback       TEXT DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (tip_id) REFERENCES nutrition_tips(tip_id),
    UNIQUE KEY unique_user_tip_date (user_id, tip_id, shown_date)
);

-- ============================================================
-- 10. NUTRITIONIST MODULE
-- ============================================================

CREATE TABLE nutritionists (
    nutritionist_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id         INT UNIQUE DEFAULT NULL,   -- linked to users table
    full_name       VARCHAR(100) NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    phone           VARCHAR(20) DEFAULT NULL,
    specialization  VARCHAR(150) DEFAULT NULL,
    bio             TEXT DEFAULT NULL,
    profile_picture VARCHAR(500) DEFAULT NULL,
    qualifications  JSON DEFAULT NULL,
    languages       JSON DEFAULT NULL,
    is_available    BOOLEAN DEFAULT TRUE,
    rating          DECIMAL(3,2) DEFAULT NULL,
    total_reviews   INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE TABLE nutritionist_queries (
    query_id         INT PRIMARY KEY AUTO_INCREMENT,
    user_id          INT NOT NULL,
    nutritionist_id  INT DEFAULT NULL,
    subject          VARCHAR(200) NOT NULL,
    message          TEXT NOT NULL,
    attachments      JSON DEFAULT NULL,
    priority         ENUM('low','normal','high','urgent') DEFAULT 'normal',
    status           ENUM('pending','assigned','in_progress','responded','closed') DEFAULT 'pending',
    response         TEXT DEFAULT NULL,
    responded_at     TIMESTAMP NULL DEFAULT NULL,
    closed_at        TIMESTAMP NULL DEFAULT NULL,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (nutritionist_id) REFERENCES nutritionists(nutritionist_id),
    INDEX idx_status (status),
    INDEX idx_user (user_id)
);

-- ============================================================
-- 11. REPORTS & FEEDBACK
-- ============================================================

CREATE TABLE pdf_reports (
    report_id      INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    report_type    ENUM('diet_plan','progress_report','health_summary','weekly_summary') NOT NULL,
    report_title   VARCHAR(200) NOT NULL,
    file_path      VARCHAR(500) DEFAULT NULL,
    generated_date DATE NOT NULL,
    report_data    JSON DEFAULT NULL,
    download_count INT DEFAULT 0,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_type (user_id, report_type)
);

CREATE TABLE user_feedback (
    feedback_id    INT PRIMARY KEY AUTO_INCREMENT,
    user_id        INT NOT NULL,
    feedback_type  ENUM('meal_satisfaction','plan_adherence','general','feature_request','bug_report') NOT NULL,
    rating         TINYINT DEFAULT NULL CHECK (rating BETWEEN 1 AND 5),
    comments       TEXT DEFAULT NULL,
    context        JSON DEFAULT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_type (user_id, feedback_type)
);

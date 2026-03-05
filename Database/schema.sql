-- Create database
CREATE DATABASE IF NOT EXISTS smartbites_diet_planner;
USE smartbites_diet_planner;

-- Users table with profile picture
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(500), -- Path to stored profile image
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role ENUM('user', 'admin') DEFAULT 'user'
);

-- User profiles table (extended to cover all requirements)
CREATE TABLE user_profiles (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,
    -- Basic Information
    full_name VARCHAR(100) NOT NULL,
    age INT,
    gender ENUM('male', 'female', 'other', 'prefer_not_to_say'),
    height DECIMAL(5,2), -- in cm
    weight DECIMAL(5,2), -- in kg
    
    -- Health & Medical Information
    diagnosed_diseases JSON, -- Array of diseases: Diabetes, Hypertension, Thyroid, Heart disease, etc.
    medications JSON, -- Array of medications/supplements
    allergies JSON, -- Array of allergies: Gluten, Lactose, Nuts, Seafood, etc.
    recent_surgeries TEXT,
    special_conditions JSON, -- Pregnancy, Lactation, Menopause, etc.
    
    -- Lifestyle & Activity
    activity_level ENUM('sedentary', 'lightly_active', 'moderately_active', 'very_active'),
    work_type ENUM('desk_job', 'field_work', 'active_job', 'other'),
    sleep_duration DECIMAL(3,1), -- hours per night
    sleep_quality ENUM('good', 'poor', 'irregular'),
    stress_level ENUM('low', 'moderate', 'high'),
    
    -- Dietary Habits
    dietary_preference ENUM('vegetarian', 'non_vegetarian', 'vegan', 'pescatarian'),
    meal_frequency INT, -- Number of meals per day
    snacking_habits BOOLEAN DEFAULT FALSE,
    snack_types TEXT,
    meal_timings JSON, -- Typical timings for Breakfast, Lunch, Dinner
    water_intake DECIMAL(5,2), -- in liters per day
    beverages_consumed JSON, -- Tea, Coffee, Soft drinks, Alcohol, etc.
    favorite_foods TEXT,
    disliked_foods TEXT,
    
    -- Health Goals
    primary_goal ENUM('weight_loss', 'weight_gain', 'maintenance', 'muscle_gain', 'improve_health'),
    target_weight DECIMAL(5,2),
    target_milestone TEXT,
    goal_timeline INT, -- days to achieve goal
    past_diet_plans BOOLEAN DEFAULT FALSE,
    past_diet_experience TEXT,
    
    -- Additional Information
    food_cravings JSON, -- Sugar, Salty, Fried, etc.
    cooking_habits ENUM('home_cooked', 'outside_food', 'mixed'),
    cultural_restrictions TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Weight tracking table
CREATE TABLE weight_tracking (
    weight_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    weight DECIMAL(5,2) NOT NULL,
    recorded_date DATE NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, recorded_date)
);

-- Food database table
CREATE TABLE food_items (
    food_id INT PRIMARY KEY AUTO_INCREMENT,
    food_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    calories DECIMAL(7,2) NOT NULL,
    protein DECIMAL(5,2),
    carbohydrates DECIMAL(5,2),
    fats DECIMAL(5,2),
    fiber DECIMAL(5,2),
    serving_size VARCHAR(50),
    serving_unit VARCHAR(20),
    is_vegetarian BOOLEAN DEFAULT TRUE,
    is_vegan BOOLEAN DEFAULT TRUE,
    is_gluten_free BOOLEAN DEFAULT FALSE,
    is_dairy_free BOOLEAN DEFAULT TRUE,
    common_allergens JSON, -- Nuts, seafood, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Diet plans table
CREATE TABLE diet_plans (
    plan_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    plan_name VARCHAR(100),
    daily_calories INT,
    protein_target DECIMAL(5,2),
    carbs_target DECIMAL(5,2),
    fats_target DECIMAL(5,2),
    start_date DATE,
    end_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Daily meal plans table
CREATE TABLE daily_meal_plans (
    daily_plan_id INT PRIMARY KEY AUTO_INCREMENT,
    plan_id INT,
    meal_date DATE,
    total_calories INT,
    notes TEXT,
    FOREIGN KEY (plan_id) REFERENCES diet_plans(plan_id) ON DELETE CASCADE
);

-- Meals table (breakfast, lunch, dinner, snacks)
CREATE TABLE meals (
    meal_id INT PRIMARY KEY AUTO_INCREMENT,
    daily_plan_id INT,
    meal_type ENUM('breakfast', 'lunch', 'dinner', 'snack1', 'snack2', 'snack3') NOT NULL,
    meal_time TIME,
    total_calories INT,
    FOREIGN KEY (daily_plan_id) REFERENCES daily_meal_plans(daily_plan_id) ON DELETE CASCADE
);

-- Meal items (junction table between meals and food_items)
CREATE TABLE meal_items (
    meal_item_id INT PRIMARY KEY AUTO_INCREMENT,
    meal_id INT,
    food_id INT,
    quantity DECIMAL(5,2),
    unit VARCHAR(20),
    calories DECIMAL(7,2),
    notes TEXT,
    FOREIGN KEY (meal_id) REFERENCES meals(meal_id) ON DELETE CASCADE,
    FOREIGN KEY (food_id) REFERENCES food_items(food_id)
);

-- Meal logging table
CREATE TABLE meal_logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    meal_item_id INT,
    logged_date DATE NOT NULL,
    logged_time TIME,
    quantity_consumed DECIMAL(5,2),
    actual_calories DECIMAL(7,2),
    is_confirmed BOOLEAN DEFAULT FALSE,
    mood_before VARCHAR(50),
    mood_after VARCHAR(50),
    satisfaction_rating INT CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (meal_item_id) REFERENCES meal_items(meal_item_id)
);

-- Missed meals tracking
CREATE TABLE missed_meals (
    missed_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    meal_id INT,
    missed_date DATE NOT NULL,
    missed_time TIME,
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (meal_id) REFERENCES meals(meal_id)
);

-- Alternative food suggestions
CREATE TABLE food_alternatives (
    alternative_id INT PRIMARY KEY AUTO_INCREMENT,
    food_id INT,
    alternative_food_id INT,
    reason TEXT,
    suitability_score INT, -- 1-10 based on nutritional similarity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (food_id) REFERENCES food_items(food_id),
    FOREIGN KEY (alternative_food_id) REFERENCES food_items(food_id)
);

-- Chat history table
CREATE TABLE chat_history (
    chat_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    session_id VARCHAR(100),
    message TEXT NOT NULL,
    response TEXT,
    intent VARCHAR(50),
    sentiment VARCHAR(20),
    confidence_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session (session_id),
    INDEX idx_user_created (user_id, created_at)
);

-- Chat context tracking
CREATE TABLE chat_context (
    context_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    session_id VARCHAR(100),
    context_key VARCHAR(100),
    context_value TEXT,
    expires_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_session_key (session_id, context_key)
);

-- Nutrition tips table
CREATE TABLE nutrition_tips (
    tip_id INT PRIMARY KEY AUTO_INCREMENT,
    tip_title VARCHAR(200),
    tip_content TEXT,
    category ENUM('nutrition', 'hydration', 'lifestyle', 'meal_timing', 'weight_management'),
    tags JSON,
    frequency ENUM('daily', 'weekly', 'on_request', 'milestone_based'),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- User-specific nutrition tips
CREATE TABLE user_nutrition_tips (
    user_tip_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    tip_id INT,
    shown_date DATE,
    is_read BOOLEAN DEFAULT FALSE,
    is_helpful BOOLEAN DEFAULT NULL,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (tip_id) REFERENCES nutrition_tips(tip_id)
);

-- Notifications table
CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    notification_type ENUM('meal_reminder', 'weight_update', 'diet_update', 'progress_update', 'general_tip', 'achievement'),
    title VARCHAR(200),
    message TEXT,
    scheduled_time TIMESTAMP,
    sent_time TIMESTAMP NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    is_read BOOLEAN DEFAULT FALSE,
    action_required BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_scheduled (scheduled_time, is_sent),
    INDEX idx_user_read (user_id, is_read)
);

-- Notification preferences
CREATE TABLE notification_preferences (
    pref_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE,
    meal_reminders BOOLEAN DEFAULT TRUE,
    weight_reminders BOOLEAN DEFAULT TRUE,
    diet_updates BOOLEAN DEFAULT TRUE,
    progress_updates BOOLEAN DEFAULT TRUE,
    nutrition_tips BOOLEAN DEFAULT TRUE,
    reminder_time TIME DEFAULT '09:00:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Nutritionist contacts table
CREATE TABLE nutritionists (
    nutritionist_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    specialization VARCHAR(100),
    bio TEXT,
    profile_picture VARCHAR(500),
    is_available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Nutritionist queries
CREATE TABLE nutritionist_queries (
    query_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    nutritionist_id INT,
    subject VARCHAR(200),
    message TEXT,
    priority ENUM('low', 'normal', 'high', 'urgent') DEFAULT 'normal',
    status ENUM('pending', 'assigned', 'in_progress', 'responded', 'closed') DEFAULT 'pending',
    response TEXT,
    responded_at TIMESTAMP NULL,
    closed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (nutritionist_id) REFERENCES nutritionists(nutritionist_id),
    INDEX idx_status (status)
);

-- PDF reports table
CREATE TABLE pdf_reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    report_type ENUM('diet_plan', 'progress_report', 'health_summary'),
    report_title VARCHAR(200),
    file_path VARCHAR(500),
    generated_date DATE,
    report_data JSON, -- Store report metadata
    download_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Diet plan adjustments table
CREATE TABLE diet_adjustments (
    adjustment_id INT PRIMARY KEY AUTO_INCREMENT,
    plan_id INT,
    adjustment_reason ENUM('weight_change', 'missed_meals', 'user_feedback', 'goal_update', 'allergy_update'),
    old_calories INT,
    new_calories INT,
    old_macros JSON,
    new_macros JSON,
    adjustment_details TEXT,
    adjusted_by ENUM('system', 'admin', 'nutritionist'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES diet_plans(plan_id) ON DELETE CASCADE
);

-- User feedback table
CREATE TABLE user_feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    feedback_type ENUM('meal_satisfaction', 'plan_adherence', 'general', 'feature_request', 'bug_report'),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    context JSON, -- Store contextual information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Progress tracking milestones
CREATE TABLE progress_milestones (
    milestone_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    milestone_type ENUM('weight', 'habit', 'streak', 'achievement'),
    milestone_name VARCHAR(100),
    target_value DECIMAL(10,2),
    achieved_value DECIMAL(10,2),
    achieved_date DATE,
    is_achieved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- User sessions table
CREATE TABLE user_sessions (
    session_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    session_token VARCHAR(255) UNIQUE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    device_type VARCHAR(50),
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    logout_time TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_token (session_token)
);

-- Insert sample data for food items
INSERT INTO food_items (food_name, category, calories, protein, carbohydrates, fats, fiber, serving_size, serving_unit, is_vegetarian, is_vegan, is_gluten_free, is_dairy_free, common_allergens) VALUES
('Grilled Chicken Breast', 'Protein', 165, 31, 0, 3.6, 0, '100', 'g', false, false, true, true, '[]'),
('Brown Rice', 'Grains', 112, 2.6, 23.5, 0.9, 1.8, '100', 'g', true, true, true, true, '[]'),
('Broccoli', 'Vegetables', 34, 2.8, 6.6, 0.4, 2.6, '100', 'g', true, true, true, true, '[]'),
('Salmon', 'Protein', 208, 20, 0, 13, 0, '100', 'g', false, false, true, true, '["seafood"]'),
('Greek Yogurt', 'Dairy', 59, 10, 3.6, 0.4, 0, '100', 'g', true, false, true, false, '["dairy"]'),
('Almonds', 'Nuts', 579, 21, 22, 50, 12.5, '100', 'g', true, true, true, true, '["nuts"]'),
('Tofu', 'Protein', 76, 8, 1.9, 4.8, 0.3, '100', 'g', true, true, true, true, '["soy"]'),
('Quinoa', 'Grains', 120, 4.4, 21.3, 1.9, 2.8, '100', 'g', true, true, true, true, '[]');

-- Insert sample nutrition tips
INSERT INTO nutrition_tips (tip_title, tip_content, category, tags, frequency) VALUES
('Stay Hydrated', 'Drink at least 8 glasses of water daily to maintain proper hydration and support metabolism.', 'hydration', '["water", "hydration", "daily"]', 'daily'),
('Protein Distribution', 'Distribute protein intake evenly across meals for better muscle synthesis and satiety.', 'nutrition', '["protein", "meals", "muscle"]', 'weekly'),
('Mindful Eating', 'Eat slowly without distractions to better recognize hunger and fullness cues.', 'lifestyle', '["eating habits", "mindfulness"]', 'on_request'),
('Colorful Plate', 'Include different colored vegetables in your meals to get various nutrients and antioxidants.', 'nutrition', '["vegetables", "nutrients"]', 'weekly'),
('Meal Prep Benefits', 'Prepare meals in advance to avoid unhealthy food choices when busy or tired.', 'meal_timing', '["preparation", "planning"]', 'weekly');

-- Insert sample nutritionists
INSERT INTO nutritionists (full_name, email, phone, specialization, bio, is_available) VALUES
('Dr. Sarah Johnson', 'sarah.johnson@smartbites.com', '+1234567890', 'Clinical Nutrition', 'PhD in Nutrition Science with 10+ years experience in weight management', true),
('Dr. Michael Chen', 'michael.chen@smartbites.com', '+1234567891', 'Sports Nutrition', 'Specialized in muscle gain and athletic performance nutrition', true);

-- Create indexes for better performance
CREATE INDEX idx_user_profiles_goals ON user_profiles(user_id, primary_goal);
CREATE INDEX idx_weight_tracking_user_date ON weight_tracking(user_id, recorded_date);
CREATE INDEX idx_diet_plans_user_active ON diet_plans(user_id, is_active);
CREATE INDEX idx_meal_logs_user_date ON meal_logs(user_id, logged_date);
CREATE INDEX idx_notifications_user_sent ON notifications(user_id, is_sent, scheduled_time);
CREATE INDEX idx_chat_history_user ON chat_history(user_id, created_at);
CREATE INDEX idx_nutritionist_queries_user_status ON nutritionist_queries(user_id, status);
CREATE INDEX idx_progress_milestones_user ON progress_milestones(user_id, is_achieved);
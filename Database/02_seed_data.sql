-- ============================================================
-- SmartBites Diet Planner - Seed Data
-- Run AFTER 01_schema.sql
-- ============================================================

USE smartbites_diet_planner;

-- ============================================================
-- Food Categories
-- ============================================================
INSERT INTO food_categories (category_name, description, icon) VALUES
('Grains & Cereals',   'Rice, wheat, oats, bread, pasta',     '🌾'),
('Proteins',           'Meat, poultry, fish, legumes, eggs',  '🥩'),
('Dairy',              'Milk, cheese, yogurt, butter',         '🥛'),
('Vegetables',         'All vegetables and leafy greens',      '🥦'),
('Fruits',             'Fresh and dried fruits',               '🍎'),
('Nuts & Seeds',       'Almonds, walnuts, chia, flaxseed',    '🥜'),
('Oils & Fats',        'Cooking oils, ghee, butter',          '🫙'),
('Beverages',          'Tea, coffee, juices, smoothies',       '🍵'),
('Snacks',             'Biscuits, crackers, energy bars',      '🍪'),
('Condiments',         'Sauces, spices, dressings',           '🧂');

-- ============================================================
-- Food Items (per 100g)
-- ============================================================
INSERT INTO food_items (food_name, category_id, calories, protein_g, carbohydrates_g, fats_g, fiber_g, sugar_g, sodium_mg, default_serving_g, serving_description, is_vegetarian, is_vegan, is_gluten_free, is_dairy_free, common_allergens) VALUES
-- Grains
('Brown Rice',           1, 112,  2.6,  23.5, 0.9,  1.8,  0.4,   5,  180, '1 cup cooked',   TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('White Rice',           1, 130,  2.7,  28.2, 0.3,  0.4,  0.1,   1,  180, '1 cup cooked',   TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Oats',                 1, 389,  17,   66.3, 7,    10.6, 0,     2,   80, '1 cup dry',      TRUE,  TRUE,  FALSE, TRUE,  '["gluten"]'),
('Whole Wheat Bread',    1, 247,  13,   41.3, 4.2,  6.8,  5.6,  472,  60, '2 slices',       TRUE,  TRUE,  FALSE, TRUE,  '["gluten","wheat"]'),
('Quinoa',               1, 120,  4.4,  21.3, 1.9,  2.8,  0.9,   7,  185, '1 cup cooked',   TRUE,  TRUE,  TRUE,  TRUE,  '[]'),

-- Proteins
('Grilled Chicken Breast', 2, 165, 31,   0,    3.6,  0,    0,    74,  150, '1 medium piece', FALSE, FALSE, TRUE,  TRUE,  '[]'),
('Eggs (Whole)',          2, 155,  13,   1.1,  11,   0,    1.1,  124,  60, '1 large egg',    TRUE,  FALSE, TRUE,  TRUE,  '["eggs"]'),
('Egg Whites',            2,  52,  11,   0.7,  0.2,  0,    0.5,  166,  60, '2 egg whites',   TRUE,  FALSE, TRUE,  TRUE,  '["eggs"]'),
('Salmon (Grilled)',      2, 208,  20,   0,    13,   0,    0,    59,  150, '1 fillet',       FALSE, FALSE, TRUE,  TRUE,  '["fish"]'),
('Tuna (Canned)',         2, 132,  29,   0,    1.0,  0,    0,    396, 100, '1/2 can',        FALSE, FALSE, TRUE,  TRUE,  '["fish"]'),
('Tofu (Firm)',           2,  76,  8,    1.9,  4.8,  0.3,  0.7,  7,  100, '100g block',     TRUE,  TRUE,  TRUE,  TRUE,  '["soy"]'),
('Red Lentils',           2, 116,  9,    20,   0.4,  7.9,  1.8,  2,  200, '1 cup cooked',   TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Chickpeas',             2, 164,  8.9,  27.4, 2.6,  7.6,  4.8,  24, 200, '1 cup cooked',   TRUE,  TRUE,  TRUE,  TRUE,  '[]'),

-- Dairy
('Greek Yogurt (Low Fat)', 3, 59,  10,   3.6,  0.4,  0,    3.2,  36, 150, '3/4 cup',        TRUE,  FALSE, TRUE,  FALSE, '["dairy"]'),
('Milk (Whole)',           3,  61,  3.2,  4.8,  3.3,  0,    5.1,  43, 240, '1 cup',          TRUE,  FALSE, TRUE,  FALSE, '["dairy"]'),
('Paneer',                3, 265,  18.3, 1.2,  20.8, 0,    0,    60, 100, '100g',           TRUE,  FALSE, TRUE,  FALSE, '["dairy"]'),
('Cheddar Cheese',        3, 403,  25,   1.3,  33,   0,    0.5,  621, 30, '1 slice (30g)',  TRUE,  FALSE, TRUE,  FALSE, '["dairy"]'),

-- Vegetables
('Broccoli',              4,  34,  2.8,  6.6,  0.4,  2.6,  1.7,  33, 100, '1 cup',          TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Spinach (Raw)',          4,  23,  2.9,  3.6,  0.4,  2.2,  0.4,  79,  30, '1 cup',          TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Sweet Potato',           4,  86,  1.6,  20.1, 0.1,  3,    4.2,  55, 130, '1 medium',       TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Carrot',                 4,  41,  0.9,  9.6,  0.2,  2.8,  4.7,  69, 100, '1 medium',       TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Cucumber',               4,  15,  0.7,  3.6,  0.1,  0.5,  1.7,  2,  100, '1/2 cup sliced', TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Tomato',                 4,  18,  0.9,  3.9,  0.2,  1.2,  2.6,  5,  120, '1 medium',       TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Onion',                  4,  40,  1.1,  9.3,  0.1,  1.7,  4.2,  4,   50, '1/2 medium',     TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Bell Pepper',            4,  31,  1,    6,    0.3,  2.1,  4.2,  4,   80, '1/2 medium',     TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Cauliflower',            4,  25,  1.9,  5,    0.3,  2,    1.9,  30, 100, '1 cup',          TRUE,  TRUE,  TRUE,  TRUE,  '[]'),

-- Fruits
('Banana',                 5,  89,  1.1,  22.8, 0.3,  2.6,  12.2, 1, 120, '1 medium',       TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Apple',                  5,  52,  0.3,  13.8, 0.2,  2.4,  10.4, 1, 150, '1 medium',       TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Orange',                 5,  47,  0.9,  11.8, 0.1,  2.4,  9.4,  0, 130, '1 medium',       TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Mango',                  5,  60,  0.8,  15,   0.4,  1.6,  13.7, 1, 165, '1 cup diced',    TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Blueberries',            5,  57,  0.7,  14.5, 0.3,  2.4,  10,   1, 150, '1 cup',          TRUE,  TRUE,  TRUE,  TRUE,  '[]'),

-- Nuts & Seeds
('Almonds',               6, 579,  21.2, 21.7, 49.9, 12.5, 3.9,  1,   30, '1 oz (30g)',     TRUE,  TRUE,  TRUE,  TRUE,  '["nuts"]'),
('Walnuts',               6, 654,  15.2, 13.7, 65.2, 6.7,  2.6,  2,   30, '1 oz (30g)',     TRUE,  TRUE,  TRUE,  TRUE,  '["nuts"]'),
('Chia Seeds',            6, 486,  16.5, 42.1, 30.7, 34.4, 0,    16,  15, '1 tbsp',         TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Flaxseeds',             6, 534,  18.3, 28.9, 42.2, 27.3, 1.6,  30,  15, '1 tbsp',         TRUE,  TRUE,  TRUE,  TRUE,  '[]'),

-- Oils
('Olive Oil',             7, 884,  0,    0,    100,  0,    0,    0,   10, '1 tbsp',          TRUE,  TRUE,  TRUE,  TRUE,  '[]'),
('Coconut Oil',           7, 862,  0,    0,    100,  0,    0,    0,   10, '1 tbsp',          TRUE,  TRUE,  TRUE,  TRUE,  '[]');

-- ============================================================
-- Food Alternatives
-- ============================================================
INSERT INTO food_alternatives (food_id, alternative_food_id, reason, suitability_score) VALUES
-- Brown Rice alternatives
(1, 2,  'White rice - similar macros, less fiber',                    7),
(1, 5,  'Quinoa - higher protein, gluten-free',                       9),
-- Chicken alternatives
(6, 11, 'Tofu - vegan protein source',                                8),
(6, 12, 'Red lentils - plant-based protein',                          7),
(6, 7,  'Eggs - complete protein',                                    8),
-- Salmon alternatives
(9, 10, 'Tuna - similar protein, lower fat',                          8),
(9, 6,  'Chicken - lower fat protein option',                         7),
-- Greek Yogurt alternatives
(14, 15, 'Whole milk - similar dairy nutrients',                      6),
(14, 11, 'Tofu - dairy-free protein option',                          7);

-- ============================================================
-- Nutrition Tips
-- ============================================================
INSERT INTO nutrition_tips (tip_title, tip_content, category, tags, target_goals, frequency) VALUES
('Start Your Day with Water',
 'Drink a glass of water as soon as you wake up. This kickstarts your metabolism and helps with hydration after 7-8 hours of sleep.',
 'hydration', '["water","morning","metabolism"]', '["weight_loss","improve_health"]', 'daily'),

('The Protein Rule',
 'Aim for at least 20-30g of protein at each main meal. This supports muscle maintenance and keeps you full longer, reducing unnecessary snacking.',
 'nutrition', '["protein","meals","satiety"]', '["muscle_gain","weight_loss"]', 'weekly'),

('Eat the Rainbow',
 'Try to include at least 3 different colored vegetables daily. Each color represents different phytonutrients and antioxidants essential for health.',
 'nutrition', '["vegetables","antioxidants","colorful"]', '["improve_health","maintenance"]', 'weekly'),

('Mindful Eating Practice',
 'Put down your fork between bites and chew thoroughly. It takes 20 minutes for your brain to register fullness — eating slowly helps prevent overeating.',
 'lifestyle', '["mindfulness","eating_habits","satiety"]', '["weight_loss","improve_health"]', 'on_request'),

('Pre-Meal Hydration',
 'Drinking 500ml of water 30 minutes before meals can reduce calorie intake and improve digestion. Try this before lunch and dinner.',
 'hydration', '["water","pre-meal","digestion"]', '["weight_loss","maintenance"]', 'daily'),

('Post-Workout Nutrition',
 'Consume a combination of protein and carbohydrates within 45 minutes after exercise. This helps with muscle recovery and glycogen replenishment.',
 'nutrition', '["post-workout","protein","carbs","recovery"]', '["muscle_gain"]', 'on_request'),

('Fiber for Gut Health',
 'Aim for 25-30g of dietary fiber daily from whole grains, vegetables, and fruits. Good fiber intake supports gut health and blood sugar stability.',
 'nutrition', '["fiber","gut_health","blood_sugar"]', '["improve_health","weight_loss"]', 'weekly'),

('Sleep and Weight Management',
 'Poor sleep increases hunger hormones (ghrelin) and decreases satiety hormones (leptin). Aim for 7-9 hours of quality sleep to support your diet goals.',
 'lifestyle', '["sleep","hormones","weight"]', '["weight_loss","improve_health"]', 'weekly'),

('Healthy Snack Strategy',
 'Keep healthy snacks like fruits, nuts, or yogurt accessible. Planning your snacks prevents impulsive eating of processed, high-calorie foods.',
 'meal_timing', '["snacking","planning","healthy_choices"]', '["weight_loss","maintenance"]', 'weekly'),

('Sodium Awareness',
 'High sodium intake can cause water retention and increase blood pressure. Aim to keep daily sodium under 2,300mg and choose low-sodium options when available.',
 'nutrition', '["sodium","blood_pressure","water_retention"]', '["improve_health"]', 'weekly');

-- ============================================================
-- Nutritionists
-- ============================================================
INSERT INTO nutritionists (full_name, email, phone, specialization, bio, qualifications, languages, is_available) VALUES
('Dr. Sarah Johnson',
 'sarah.johnson@smartbites.com',
 '+1-555-0101',
 'Clinical Nutrition & Weight Management',
 'PhD in Nutritional Sciences with 12+ years of experience. Specialized in evidence-based weight management and chronic disease nutrition therapy.',
 '["PhD Nutritional Sciences","RD Registered Dietitian","CSSD Certified"]',
 '["English","Spanish"]',
 TRUE),

('Dr. Michael Chen',
 'michael.chen@smartbites.com',
 '+1-555-0102',
 'Sports Nutrition & Performance',
 'MS in Exercise Physiology and Nutrition. Worked with Olympic athletes. Specializes in performance nutrition and muscle gain programs.',
 '["MS Exercise Physiology","CSCS Certified Strength Coach","CISSN Sports Nutrition"]',
 '["English","Mandarin"]',
 TRUE),

('Dr. Priya Patel',
 'priya.patel@smartbites.com',
 '+1-555-0103',
 'Diabetes & Cardiac Nutrition',
 'Specializes in medical nutrition therapy for diabetes, cardiovascular disease, and metabolic disorders. 8+ years of clinical experience.',
 '["MD Internal Medicine","Certified Diabetes Educator","RD Registered Dietitian"]',
 '["English","Hindi","Gujarati"]',
 TRUE);

-- ============================================================
-- Sample Admin User (password: Admin@123 - bcrypt hashed)
-- ============================================================
INSERT INTO users (username, email, password_hash, role, is_active, is_verified) VALUES
('admin', 'admin@smartbites.com',
 '$2b$12$placeholder_hash_change_in_production',
 'admin', TRUE, TRUE);

-- ============================================================
-- Default Notification Preferences trigger
-- (Auto-create when user registers - handled in backend,
--  but also added here for reference)
-- ============================================================

-- ============================================================
-- Useful Views
-- ============================================================

-- Daily nutrition summary per user
CREATE OR REPLACE VIEW vw_daily_nutrition_summary AS
SELECT
    ml.user_id,
    ml.logged_date,
    SUM(ml.actual_calories)  AS total_calories,
    SUM(ml.actual_protein_g) AS total_protein_g,
    SUM(ml.actual_carbs_g)   AS total_carbs_g,
    SUM(ml.actual_fats_g)    AS total_fats_g,
    COUNT(ml.log_id)         AS total_food_entries
FROM meal_logs ml
GROUP BY ml.user_id, ml.logged_date;

-- User progress overview
CREATE OR REPLACE VIEW vw_user_progress AS
SELECT
    u.user_id,
    u.username,
    up.full_name,
    up.weight_kg AS current_weight,
    up.target_weight_kg,
    up.primary_goal,
    up.bmi,
    (SELECT wt.weight_kg FROM weight_tracking wt
     WHERE wt.user_id = u.user_id
     ORDER BY wt.recorded_date DESC LIMIT 1) AS latest_logged_weight,
    (SELECT COUNT(*) FROM meal_logs ml
     WHERE ml.user_id = u.user_id
     AND ml.logged_date = CURDATE()) AS meals_logged_today
FROM users u
JOIN user_profiles up ON u.user_id = up.user_id
WHERE u.is_active = TRUE;

-- Active diet plan summary
CREATE OR REPLACE VIEW vw_active_diet_plans AS
SELECT
    dp.plan_id,
    dp.user_id,
    dp.plan_name,
    dp.daily_calories,
    dp.protein_target_g,
    dp.carbs_target_g,
    dp.fats_target_g,
    dp.start_date,
    dp.end_date,
    DATEDIFF(IFNULL(dp.end_date, DATE_ADD(dp.start_date, INTERVAL 90 DAY)), CURDATE()) AS days_remaining
FROM diet_plans dp
WHERE dp.is_active = TRUE;

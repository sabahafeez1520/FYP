# SmartBites Backend — FastAPI

## Project Structure

```
backend/
├── main.py                          # App entry point
├── requirements.txt
├── .env.example                     # Copy to .env and fill in values
├── app/
│   ├── api/v1/endpoints/
│   │   └── routes.py                # All API routes
│   ├── core/
│   │   ├── config.py                # Settings (reads .env)
│   │   └── security.py             # JWT, password hashing
│   ├── db/
│   │   └── session.py              # SQLAlchemy engine + get_db()
│   ├── models/
│   │   └── all_models.py           # All SQLAlchemy ORM models
│   ├── schemas/
│   │   └── auth.py                 # Pydantic request/response schemas
│   ├── services/
│   │   ├── auth_service.py         # Register, login, token management
│   │   ├── profile_service.py      # User profile CRUD + TDEE calc
│   │   ├── diet_service.py         # Diet plan generation
│   │   └── chat_service.py         # AI chatbot (Anthropic)
│   └── utils/
│       └── nutrition.py            # BMR, TDEE, macro calculations
```

## Setup

### 1. Create virtual environment
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your database credentials, secret key, and Anthropic API key
```

### 4. Set up database
```bash
# Run the SQL files in order:
mysql -u root -p < ../database/01_schema.sql
mysql -u root -p < ../database/02_seed_data.sql
```

### 5. Run the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc
- Health:      http://localhost:8000/health

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/register | Register new user |
| POST | /api/v1/auth/login | Login, get JWT tokens |
| POST | /api/v1/auth/refresh | Refresh access token |
| POST | /api/v1/auth/logout | Logout |
| GET  | /api/v1/users/me | Get current user |
| POST | /api/v1/profile | Create/update profile |
| GET  | /api/v1/profile | Get profile |
| PATCH| /api/v1/profile | Update profile fields |
| GET  | /api/v1/dashboard | Full dashboard data |
| GET  | /api/v1/foods | Search food database |
| POST | /api/v1/diet-plans/generate | Generate AI diet plan |
| GET  | /api/v1/diet-plans/active | Get active diet plan |
| GET  | /api/v1/diet-plans/{id}/day/{n} | Get specific day meals |
| POST | /api/v1/meal-logs | Log a meal |
| GET  | /api/v1/meal-logs/today | Today's meal logs |
| GET  | /api/v1/meal-logs/summary | Nutrition summary by date range |
| POST | /api/v1/water-logs | Log water intake |
| POST | /api/v1/weight | Log weight |
| GET  | /api/v1/weight/history | Weight history |
| POST | /api/v1/chat | Chat with AI assistant |
| GET  | /api/v1/chat/sessions | Chat sessions list |
| GET  | /api/v1/notifications | Get notifications |
| GET  | /api/v1/nutritionists | List nutritionists |
| POST | /api/v1/nutritionist-queries | Submit query |
| GET  | /api/v1/progress/summary | Progress overview |
| POST | /api/v1/feedback | Submit feedback |

## Authentication
All endpoints (except register/login) require:
```
Authorization: Bearer <access_token>
```

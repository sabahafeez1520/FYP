from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import date
import uuid
import anthropic

from app.models.all_models import ChatSession, ChatHistory, UserProfile, DietPlan, MealLog
from app.core.config import settings


SYSTEM_PROMPT = """You are SmartBites AI, a friendly and knowledgeable nutrition and diet assistant.

Your role:
- Help users understand their diet plan, track meals, and stay motivated
- Answer questions about nutrition, calories, macros, food alternatives
- Provide personalized advice based on the user's profile
- Offer healthy recipe suggestions and food swaps
- Keep users motivated and positive about their health journey

Rules:
- Always be encouraging and supportive
- Provide evidence-based nutrition advice
- If asked about medical conditions, recommend consulting a doctor
- Keep responses concise and actionable (2-4 sentences unless detail is requested)
- Use simple, friendly language

User Profile Context:
{profile_context}
"""


class ChatService:

    @staticmethod
    def get_or_create_session(db: Session, user_id: int, session_id: str = None) -> ChatSession:
        if session_id:
            session = db.query(ChatSession).filter(
                ChatSession.session_id == session_id,
                ChatSession.user_id == user_id,
            ).first()
            if session:
                return session

        # Create new session
        new_session = ChatSession(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            title="New Chat",
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        return new_session

    @staticmethod
    def get_sessions(db: Session, user_id: int) -> list:
        return db.query(ChatSession).filter(
            ChatSession.user_id == user_id,
            ChatSession.is_active == True,
        ).order_by(ChatSession.last_message_at.desc()).limit(20).all()

    @staticmethod
    def get_history(db: Session, session_id: str, user_id: int, limit: int = 50) -> list:
        return db.query(ChatHistory).filter(
            ChatHistory.session_id == session_id,
            ChatHistory.user_id == user_id,
        ).order_by(ChatHistory.created_at.asc()).limit(limit).all()

    @staticmethod
    def _build_profile_context(db: Session, user_id: int) -> str:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            return "No profile available."

        plan = db.query(DietPlan).filter(
            DietPlan.user_id == user_id,
            DietPlan.is_active == True
        ).first()

        today_logs = db.query(MealLog).filter(
            MealLog.user_id == user_id,
            MealLog.logged_date == date.today()
        ).all()
        today_calories = sum(float(l.actual_calories or 0) for l in today_logs)

        ctx_parts = [
            f"Name: {profile.full_name}",
            f"Goal: {(profile.primary_goal or 'N/A').replace('_', ' ')}",
            f"Diet: {profile.dietary_preference or 'N/A'}",
            f"Allergies: {', '.join(profile.allergies or []) or 'None'}",
        ]

        if profile.recommended_calories:
            ctx_parts.append(f"Daily calorie target: {profile.recommended_calories} kcal")
            ctx_parts.append(f"Calories consumed today: {round(today_calories)} kcal")

        if plan:
            ctx_parts.append(f"Active plan: {plan.plan_name}")

        return " | ".join(ctx_parts)

    @staticmethod
    def chat(db: Session, user_id: int, message: str, session_id: str = None) -> dict:
        if not settings.ANTHROPIC_API_KEY:
            # Fallback response if no API key configured
            return ChatService._fallback_response(db, user_id, message, session_id)

        session = ChatService.get_or_create_session(db, user_id, session_id)

        # Save user message
        user_msg = ChatHistory(
            session_id=session.session_id,
            user_id=user_id,
            role="user",
            message=message,
        )
        db.add(user_msg)
        db.flush()

        # Build conversation history for API
        history = ChatService.get_history(db, session.session_id, user_id, limit=20)
        messages = [
            {"role": h.role, "content": h.message}
            for h in history
            if h.chat_id != user_msg.chat_id
        ]
        messages.append({"role": "user", "content": message})

        # Build profile context
        profile_context = ChatService._build_profile_context(db, user_id)
        system = SYSTEM_PROMPT.format(profile_context=profile_context)

        try:
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=system,
                messages=messages,
            )
            reply = response.content[0].text
            tokens = response.usage.input_tokens + response.usage.output_tokens

        except Exception as e:
            reply = "I'm having trouble connecting right now. Please try again in a moment."
            tokens = 0

        # Save assistant response
        assistant_msg = ChatHistory(
            session_id=session.session_id,
            user_id=user_id,
            role="assistant",
            message=reply,
            tokens_used=tokens,
        )
        db.add(assistant_msg)

        # Update session title if first message
        if len(history) == 0:
            title = message[:60] + ("..." if len(message) > 60 else "")
            session.title = title

        db.commit()

        return {
            "session_id":  session.session_id,
            "message":     reply,
            "tokens_used": tokens,
        }

    @staticmethod
    def _fallback_response(db: Session, user_id: int, message: str, session_id: str = None) -> dict:
        """Simple rule-based fallback when Anthropic API is not configured."""
        session = ChatService.get_or_create_session(db, user_id, session_id)

        msg_lower = message.lower()
        if any(w in msg_lower for w in ["calorie", "calories", "kcal"]):
            reply = "Calories are units of energy in food. Your daily target is set based on your profile goals. Check your dashboard for today's calorie summary!"
        elif any(w in msg_lower for w in ["protein", "macro"]):
            reply = "Protein is essential for muscle repair and satiety. Aim to include a protein source (eggs, chicken, legumes, tofu) in every main meal."
        elif any(w in msg_lower for w in ["water", "hydrat"]):
            reply = "Staying hydrated is key! Aim for 8+ glasses of water daily. Try keeping a water bottle nearby as a reminder."
        elif any(w in msg_lower for w in ["snack", "hungry"]):
            reply = "Healthy snack options include: a handful of nuts, Greek yogurt, fruits, or vegetable sticks with hummus. Keep snacks under 150-200 calories."
        elif any(w in msg_lower for w in ["weight", "loss", "gain"]):
            reply = "Sustainable weight change happens at 0.5-1 kg per week. Focus on consistency with your meal plan and stay active. You've got this!"
        else:
            reply = "I'm here to help with your nutrition journey! Ask me about calories, macros, meal ideas, food alternatives, or your diet plan."

        # Save to DB
        for role, msg in [("user", message), ("assistant", reply)]:
            db.add(ChatHistory(
                session_id=session.session_id,
                user_id=user_id,
                role=role,
                message=msg,
            ))

        if not session.title or session.title == "New Chat":
            session.title = message[:60]

        db.commit()

        return {"session_id": session.session_id, "message": reply, "tokens_used": 0}

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import uuid

from app.models.all_models import User, UserSession, UserProfile, NotificationPreference
from app.schemas.auth import RegisterRequest, LoginRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.config import settings


class AuthService:

    @staticmethod
    def register(db: Session, data: RegisterRequest) -> User:
        # Check duplicates
        if db.query(User).filter(User.email == data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        if db.query(User).filter(User.username == data.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        # Create user
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            verify_token=str(uuid.uuid4()),
            is_verified=True,    # set False when email is configured
        )
        db.add(user)
        db.flush()  # get user_id

        # Create empty profile
        profile = UserProfile(
            user_id=user.user_id,
            full_name=data.full_name,
        )
        db.add(profile)

        # Create default notification preferences
        prefs = NotificationPreference(user_id=user.user_id)
        db.add(prefs)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def login(db: Session, data: LoginRequest, ip: str = None, user_agent: str = None) -> dict:
        user = db.query(User).filter(User.email == data.email).first()

        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(status_code=400, detail="Account is deactivated")

        # Create tokens
        token_data = {"sub": str(user.user_id), "role": user.role}
        access_token  = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        # Store session
        session = UserSession(
            user_id=user.user_id,
            session_token=access_token,
            refresh_token=refresh_token,
            ip_address=ip,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        db.add(session)

        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()

        # Check onboarding
        onboarding_complete = user.profile.onboarding_complete if user.profile else False

        return {
            "access_token":       access_token,
            "refresh_token":      refresh_token,
            "token_type":         "bearer",
            "expires_in":         settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id":            user.user_id,
            "username":           user.username,
            "role":               user.role,
            "onboarding_complete": onboarding_complete,
        }

    @staticmethod
    def refresh_token(db: Session, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user_id = int(payload["sub"])
        session = db.query(UserSession).filter(
            UserSession.refresh_token == refresh_token,
            UserSession.is_active == True
        ).first()

        if not session:
            raise HTTPException(status_code=401, detail="Session expired or invalid")

        user = db.query(User).filter(User.user_id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found")

        # Issue new tokens
        token_data = {"sub": str(user.user_id), "role": user.role}
        new_access  = create_access_token(token_data)
        new_refresh = create_refresh_token(token_data)

        session.session_token = new_access
        session.refresh_token = new_refresh
        session.expires_at = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        db.commit()

        return {
            "access_token":  new_access,
            "refresh_token": new_refresh,
            "token_type":    "bearer",
            "expires_in":    settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }

    @staticmethod
    def logout(db: Session, token: str):
        session = db.query(UserSession).filter(UserSession.session_token == token).first()
        if session:
            session.is_active = False
            session.logout_time = datetime.utcnow()
            db.commit()

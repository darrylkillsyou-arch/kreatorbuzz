"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.users import User
from app.models.creators import CreatorProfile
from app.schemas.users import UserCreate, UserLogin, UserResponse, Token
from app.dependencies import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user (brand or creator)."""
    existing_user = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    hashed_pw = get_password_hash(user_in.password)
    user = User(
        email=user_in.email.lower(),
        password_hash=hashed_pw,
        full_name=user_in.full_name,
        role=user_in.role,
        avatar_url=user_in.avatar_url or "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80",
        bio=user_in.bio,
        location=user_in.location or "Global",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # If role is creator, auto-initialize an empty creator profile
    if user.role == "creator":
        creator_profile = CreatorProfile(
            user_id=user.id,
            display_name=user.full_name,
            tagline="AI Visual Artist & Director",
            specialization="Cinematic Video & Luxury",
            skills=["Prompt Engineering", "Visual Direction", "Post-Production"],
            ai_tools=["Midjourney v6", "Runway Gen-3", "ComfyUI"],
            starting_rate=500.0,
            delivery_days=7,
            commercial_rights=True,
            availability_status="available",
            rating=5.0,
            sla_score=99.0,
            on_time_percentage=100.0,
            location=user.location,
        )
        db.add(creator_profile)
        db.commit()

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))


@router.post("/login", response_model=Token)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user with email and password."""
    user = db.query(User).filter(User.email == login_data.email.lower()).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=token, token_type="bearer", user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the current authenticated user."""
    return current_user

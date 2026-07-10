"""
Auth API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr
import uuid

from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.models.farmer_profile import FarmerProfile
from sqlalchemy import select

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str = ""
    password: str
    preferred_language: str = "en"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check duplicate
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=req.name,
        email=req.email,
        phone=req.phone or None,
        hashed_password=hash_password(req.password),
        preferred_language=req.preferred_language,
    )
    db.add(user)
    await db.flush()

    # Auto-create empty profile
    profile = FarmerProfile(user_id=user.id)
    db.add(profile)
    await db.commit()

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user_id=str(user.id), name=user.name, email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, user_id=str(user.id), name=user.name, email=user.email)

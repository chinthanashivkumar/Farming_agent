"""
Farmer Profile Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.farmer_profile import FarmerProfile
from app.models.user import User

router = APIRouter()


class ProfileUpdate(BaseModel):
    state: Optional[str] = None
    district: Optional[str] = None
    village: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    pincode: Optional[str] = None
    farm_size_acres: Optional[float] = None
    soil_type: Optional[str] = None
    irrigation_type: Optional[str] = None
    water_source: Optional[str] = None
    primary_crops: Optional[List[str]] = None
    soil_ph: Optional[float] = None
    soil_nitrogen: Optional[float] = None
    soil_phosphorus: Optional[float] = None
    soil_potassium: Optional[float] = None
    soil_organic_carbon: Optional[float] = None
    bio: Optional[str] = None


@router.get("/")
async def get_profile(db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == uuid.UUID(current_user["user_id"]))
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {
        "user_id": str(profile.user_id),
        "state": profile.state,
        "district": profile.district,
        "village": profile.village,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "farm_size_acres": profile.farm_size_acres,
        "soil_type": profile.soil_type,
        "irrigation_type": profile.irrigation_type,
        "primary_crops": profile.primary_crops or [],
        "soil_ph": profile.soil_ph,
        "soil_nitrogen": profile.soil_nitrogen,
        "soil_phosphorus": profile.soil_phosphorus,
        "soil_potassium": profile.soil_potassium,
        "soil_organic_carbon": profile.soil_organic_carbon,
    }


@router.put("/")
async def update_profile(
    update: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(FarmerProfile).where(FarmerProfile.user_id == uuid.UUID(current_user["user_id"]))
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for field, value in update.dict(exclude_none=True).items():
        setattr(profile, field, value)

    await db.commit()
    return {"message": "Profile updated successfully"}

"""
SQLAlchemy Models — Farmer Profile
"""
from sqlalchemy import Column, String, Float, Text, ForeignKey, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)

    # Location
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    village = Column(String(100), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    pincode = Column(String(10), nullable=True)

    # Farm Details
    farm_size_acres = Column(Float, nullable=True)
    soil_type = Column(String(50), nullable=True)
    irrigation_type = Column(String(50), nullable=True)   # drip / flood / rainfed
    water_source = Column(String(50), nullable=True)

    # Crops
    primary_crops = Column(JSON, default=list)            # ["rice", "wheat"]
    favorite_crops = Column(JSON, default=list)

    # Soil nutrients (last reading)
    soil_ph = Column(Float, nullable=True)
    soil_nitrogen = Column(Float, nullable=True)
    soil_phosphorus = Column(Float, nullable=True)
    soil_potassium = Column(Float, nullable=True)
    soil_organic_carbon = Column(Float, nullable=True)

    bio = Column(Text, nullable=True)

    user = relationship("User", back_populates="profile")

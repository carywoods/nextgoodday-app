from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

def generate_uuid():
    """Generate a unique UUID for user identification"""
    return str(uuid.uuid4())

class User(Base):
    """User profile model"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    age_range = Column(String, nullable=False)  # e.g., "18-24", "25-34", etc.
    gender = Column(String, nullable=True)
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    location_name = Column(String, nullable=True)  # City, region format
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")

class Activity(Base):
    """Pre-defined activities that users can select"""
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # e.g., "outdoor", "creative", "social"
    weather_preferences = Column(JSON, nullable=True)  # JSON for ideal weather conditions
    
    # Demographics targeting (optional, for recommendations)
    min_age = Column(Integer, nullable=True)
    max_age = Column(Integer, nullable=True)
    gender_preference = Column(String, nullable=True)  # null means all genders
    
    # Relationships
    user_activities = relationship("UserActivity", back_populates="activity")

class UserActivity(Base):
    """Junction table between users and their selected activities with preferences"""
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    
    # User-specific preferences for this activity
    preferred_time_start = Column(Integer, nullable=True)  # Hour of day (0-23)
    preferred_time_end = Column(Integer, nullable=True)  # Hour of day (0-23)
    preferred_days = Column(String, nullable=True)  # Comma-separated days of week (e.g., "0,1,5,6" for Sun,Mon,Fri,Sat)
    min_temperature = Column(Float, nullable=True)
    max_temperature = Column(Float, nullable=True)
    avoid_rain = Column(Boolean, default=True)
    avoid_snow = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    activity = relationship("Activity", back_populates="user_activities")
    recommendations = relationship("Recommendation", back_populates="user_activity", cascade="all, delete-orphan")

class Recommendation(Base):
    """Recommended days for user activities"""
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True)
    user_activity_id = Column(Integer, ForeignKey("user_activities.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    score = Column(Float, nullable=False)  # 1-10 score
    explanation = Column(Text, nullable=False)  # Text explanation of the score
    weather_summary = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)  # In Fahrenheit
    precipitation_probability = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_activity = relationship("UserActivity", back_populates="recommendations")

class Message(Base):
    """Stored email messages for invitations (not sent in MVP)"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    recipient_email = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="messages")

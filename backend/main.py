from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field

import os
import logging
from datetime import datetime, timedelta
import json

# Import local modules with correct relative imports
from backend.models import Base, User, Activity, UserActivity, Recommendation, Message
from backend.utils import fetch_weather_data, get_location_name, generate_ics_file, generate_invite_email, filter_activities_by_demographics
from backend.scoring import get_top_recommendations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="The Next Good Day API", 
              description="Find the best days for your activities based on weather and availability",
              version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Load initial activities data
def load_initial_activities():
    db = SessionLocal()
    # Check if activities already exist
    if db.query(Activity).count() == 0:
        logger.info("Loading initial activities...")
        
        activities = [
            {
                "name": "Hiking",
                "description": "Explore nature trails and enjoy the outdoors",
                "category": "outdoor",
                "weather_preferences": {
                    "min_temperature": 50,
                    "max_temperature": 85,
                    "avoid_rain": True,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Photography",
                "description": "Capture beautiful moments and scenes",
                "category": "creative",
                "weather_preferences": {
                    "min_temperature": 45,
                    "max_temperature": 90,
                    "avoid_rain": False,
                    "avoid_snow": False
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Cycling",
                "description": "Go for a bike ride",
                "category": "outdoor",
                "weather_preferences": {
                    "min_temperature": 55,
                    "max_temperature": 85,
                    "avoid_rain": True,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Picnic",
                "description": "Enjoy a meal outdoors",
                "category": "social",
                "weather_preferences": {
                    "min_temperature": 65,
                    "max_temperature": 85,
                    "avoid_rain": True,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Painting",
                "description": "Express yourself through art",
                "category": "creative",
                "weather_preferences": {
                    "min_temperature": 50,
                    "max_temperature": 90,
                    "avoid_rain": False,
                    "avoid_snow": False
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Reading",
                "description": "Enjoy a good book",
                "category": "creative",
                "weather_preferences": {
                    "min_temperature": 50,
                    "max_temperature": 90,
                    "avoid_rain": False,
                    "avoid_snow": False
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Running",
                "description": "Go for a jog or run",
                "category": "outdoor",
                "weather_preferences": {
                    "min_temperature": 45,
                    "max_temperature": 80,
                    "avoid_rain": True,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Beach Day",
                "description": "Relax by the water",
                "category": "outdoor",
                "weather_preferences": {
                    "min_temperature": 75,
                    "max_temperature": 95,
                    "avoid_rain": True,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Coffee Shop Work",
                "description": "Productive time at a local coffee shop",
                "category": "creative",
                "weather_preferences": {
                    "min_temperature": 40,
                    "max_temperature": 100,
                    "avoid_rain": False,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Gardening",
                "description": "Tend to plants and garden",
                "category": "outdoor",
                "weather_preferences": {
                    "min_temperature": 55,
                    "max_temperature": 85,
                    "avoid_rain": True,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            },
            {
                "name": "Yoga",
                "description": "Practice yoga outdoors",
                "category": "outdoor",
                "weather_preferences": {
                    "min_temperature": 60,
                    "max_temperature": 85,
                    "avoid_rain": True,
                    "avoid_snow": True
                },
                "min_age": None,
                "max_age": None,
                "gender_preference": None
            }
        ]
        
        # Add activities to database
        for activity_data in activities:
            activity = Activity(
                name=activity_data["name"],
                description=activity_data["description"],
                category=activity_data["category"],
                weather_preferences=activity_data["weather_preferences"],
                min_age=activity_data["min_age"],
                max_age=activity_data["max_age"],
                gender_preference=activity_data["gender_preference"]
            )
            db.add(activity)
        
        db.commit()
        logger.info(f"Added {len(activities)} initial activities")
    
    db.close()

# Load initial activities on startup
@app.on_event("startup")
def startup_event():
    load_initial_activities()

# Pydantic models for API requests and responses
class UserCreate(BaseModel):
    email: EmailStr
    age_range: str
    gender: Optional[str] = None
    location_lat: float
    location_lon: float

class UserResponse(BaseModel):
    id: str
    email: str
    age_range: str
    gender: Optional[str]
    location_name: Optional[str]
    
    class Config:
        orm_mode = True

class ActivityResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    category: str
    
    class Config:
        orm_mode = True

class UserActivityCreate(BaseModel):
    activity_id: int
    preferred_time_start: Optional[int] = None
    preferred_time_end: Optional[int] = None
    preferred_days: Optional[str] = None
    min_temperature: Optional[float] = None
    max_temperature: Optional[float] = None
    avoid_rain: Optional[bool] = True
    avoid_snow: Optional[bool] = True

class RecommendationResponse(BaseModel):
    id: int
    date: datetime
    score: float
    explanation: str
    weather_summary: str
    temperature: float
    preferred_time_start: Optional[int]
    preferred_time_end: Optional[int]
    
    class Config:
        orm_mode = True

class InviteEmailRequest(BaseModel):
    recommendation_id: int
    recipient_email: EmailStr

class InviteEmailResponse(BaseModel):
    id: int
    subject: str
    body: str
    
    class Config:
        orm_mode = True

# API Endpoints
@app.post("/api/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user profile"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return existing_user
    
    # Get location name
    location_name = await get_location_name(user_data.location_lat, user_data.location_lon)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        age_range=user_data.age_range,
        gender=user_data.gender,
        location_lat=user_data.location_lat,
        location_lon=user_data.location_lon,
        location_name=location_name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get user profile by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/api/activities", response_model=List[ActivityResponse])
def get_activities(
    age_range: Optional[str] = None,
    gender: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all activities or filter by demographics"""
    activities = db.query(Activity).all()
    
    # Filter activities if demographic info provided
    if age_range:
        activities_data = [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "category": a.category,
                "min_age": a.min_age,
                "max_age": a.max_age,
                "gender_preference": a.gender_preference
            }
            for a in activities
        ]
        
        filtered_activities_data = filter_activities_by_demographics(
            activities_data, age_range, gender
        )
        
        # Get IDs of filtered activities
        filtered_ids = [a["id"] for a in filtered_activities_data]
        
        # Return filtered activities
        return [a for a in activities if a.id in filtered_ids]
    
    return activities

@app.post("/api/users/{user_id}/activities", response_model=dict)
async def add_user_activity(
    user_id: str,
    activity_data: UserActivityCreate,
    db: Session = Depends(get_db)
):
    """Add an activity to a user's profile and get recommendations"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if activity exists
    activity = db.query(Activity).filter(Activity.id == activity_data.activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Create user activity
    user_activity = UserActivity(
        user_id=user_id,
        activity_id=activity_data.activity_id,
        preferred_time_start=activity_data.preferred_time_start,
        preferred_time_end=activity_data.preferred_time_end,
        preferred_days=activity_data.preferred_days,
        min_temperature=activity_data.min_temperature,
        max_temperature=activity_data.max_temperature,
        avoid_rain=activity_data.avoid_rain,
        avoid_snow=activity_data.avoid_snow
    )
    
    db.add(user_activity)
    db.commit()
    db.refresh(user_activity)
    
    # Fetch weather data for user's location
    weather_data = await fetch_weather_data(user.location_lat, user.location_lon)
    
    if not weather_data:
        return {
            "user_activity_id": user_activity.id,
            "recommendations": []
        }
    
    # Get user preferences from the user activity
    user_preferences = {
        "min_temperature": user_activity.min_temperature,
        "max_temperature": user_activity.max_temperature,
        "avoid_rain": user_activity.avoid_rain,
        "avoid_snow": user_activity.avoid_snow
    }
    
    # Get top recommendations
    recommendations = get_top_recommendations(
        weather_data=weather_data,
        user_age_range=user.age_range,
        activity_category=activity.category,
        user_preferences=user_preferences,
        top_n=3
    )
    
    # Store recommendations in database
    db_recommendations = []
    for rec in recommendations:
        new_rec = Recommendation(
            user_activity_id=user_activity.id,
            date=rec["date"],
            score=rec["score"],
            explanation=rec["explanation"],
            weather_summary=rec["weather_summary"],
            temperature=rec["temperature"],
            precipitation_probability=rec.get("precipitation_probability", 0),
            wind_speed=rec.get("wind_speed", 0)
        )
        db.add(new_rec)
        db_recommendations.append(new_rec)
    
    db.commit()
    for rec in db_recommendations:
        db.refresh(rec)
    
    # Format response
    response_recommendations = [
        {
            "id": rec.id,
            "date": rec.date,
            "score": rec.score,
            "explanation": rec.explanation,
            "weather_summary": rec.weather_summary,
            "temperature": rec.temperature,
            "preferred_time_start": recommendations[i].get("preferred_time_start"),
            "preferred_time_end": recommendations[i].get("preferred_time_end")
        }
        for i, rec in enumerate(db_recommendations)
    ]
    
    return {
        "user_activity_id": user_activity.id,
        "recommendations": response_recommendations
    }

@app.get("/api/users/{user_id}/recommendations", response_model=List[RecommendationResponse])
async def get_user_recommendations(
    user_id: str,
    activity_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all recommendations for a user, optionally filtered by activity"""
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Query to get all user activities
    query = db.query(UserActivity).filter(UserActivity.user_id == user_id)
    
    # Filter by activity if specified
    if activity_id:
        query = query.filter(UserActivity.activity_id == activity_id)
    
    user_activities = query.all()
    
    # Get recommendations for all user activities
    recommendations = []
    for ua in user_activities:
        ua_recommendations = db.query(Recommendation).filter(
            Recommendation.user_activity_id == ua.id
        ).all()
        
        for rec in ua_recommendations:
            # Get the activity for this recommendation
            activity = db.query(Activity).filter(Activity.id == ua.activity_id).first()
            
            # Add to response
            recommendations.append({
                "id": rec.id,
                "date": rec.date,
                "score": rec.score,
                "explanation": rec.explanation,
                "weather_summary": rec.weather_summary,
                "temperature": rec.temperature,
                "preferred_time_start": ua.preferred_time_start,
                "preferred_time_end": ua.preferred_time_end,
                "activity_name": activity.name if activity else "Unknown Activity"
            })
    
    # Sort by score (highest first)
    recommendations.sort(key=lambda x: x["score"], reverse=True)
    
    return recommendations

@app.post("/api/recommendations/{recommendation_id}/invite", response_model=InviteEmailResponse)
async def create_invite_email(
    recommendation_id: int,
    invite_data: InviteEmailRequest,
    db: Session = Depends(get_db)
):
    """Create an invitation email for a recommendation (stored, not sent)"""
    # Get the recommendation
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Get the user activity
    user_activity = db.query(UserActivity).filter(
        UserActivity.id == recommendation.user_activity_id
    ).first()
    
    if not user_activity:
        raise HTTPException(status_code=404, detail="User activity not found")
    
    # Get the user and activity
    user = db.query(User).filter(User.id == user_activity.user_id).first()
    activity = db.query(Activity).filter(Activity.id == user_activity.activity_id).first()
    
    if not user or not activity:
        raise HTTPException(status_code=404, detail="User or activity not found")
    
    # Format recommendation data for email generation
    rec_data = {
        "date": recommendation.date,
        "score": recommendation.score,
        "weather_summary": recommendation.weather_summary,
        "preferred_time_start": user_activity.preferred_time_start or 12,
        "preferred_time_end": user_activity.preferred_time_end or 18
    }
    
    # Generate email content
    email_data = generate_invite_email(
        user_name="You",  # For MVP, we don't collect names
        recipient_email=invite_data.recipient_email,
        activity_name=activity.name,
        recommendation=rec_data,
        location=user.location_name or "your area"
    )
    
    # Store the email message
    message = Message(
        user_id=user.id,
        recipient_email=invite_data.recipient_email,
        subject=email_data["subject"],
        body=email_data["body"],
        recommendation_id=recommendation_id
    )
    
    db.add(message)
    db.commit()
    db.refresh(message)
    
    return message

@app.get("/api/recommendations/{recommendation_id}/calendar", response_model=dict)
async def get_calendar_file(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    """Generate an ICS file for a recommendation"""
    # Get the recommendation
    recommendation = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Get the user activity
    user_activity = db.query(UserActivity).filter(
        UserActivity.id == recommendation.user_activity_id
    ).first()
    
    if not user_activity:
        raise HTTPException(status_code=404, detail="User activity not found")
    
    # Get the activity and user
    activity = db.query(Activity).filter(Activity.id == user_activity.activity_id).first()
    user = db.query(User).filter(User.id == user_activity.user_id).first()
    
    if not activity or not user:
        raise HTTPException(status_code=404, detail="Activity or user not found")
    
    # Default time window if not specified
    time_start = user_activity.preferred_time_start or 12  # Default to noon
    time_end = user_activity.preferred_time_end or 18      # Default to 6pm
    
    # Generate ICS content
    ics_content = generate_ics_file(
        activity_name=activity.name,
        date=recommendation.date,
        time_start=time_start,
        time_end=time_end,
        location=user.location_name or "Your Location",
        description=f"Weather: {recommendation.weather_summary}\n{recommendation.explanation}"
    )
    
    # Return ICS content and filename
    return {
        "ics_content": ics_content,
        "filename": f"{activity.name.lower().replace(' ', '_')}_{recommendation.date.strftime('%Y-%m-%d')}.ics"
    }

# Serve frontend static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

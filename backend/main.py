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

# Import local modules
from models import Base, User, Activity, UserActivity, Recommendation, Message
from utils import fetch_weather_data, get_location_name, generate_ics_file, generate_invite_email, filter_activities_by_demographics
from scoring import get_top_recommendations

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

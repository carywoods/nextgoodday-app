import httpx
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
from ics import Calendar, Event

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_weather_data(lat: float, lon: float, days: int = 5) -> List[Dict]:
    """
    Fetch weather forecast from Open-Meteo API
    
    Args:
        lat: Latitude
        lon: Longitude
        days: Number of days to forecast (default: 5)
    
    Returns:
        List of daily weather data
    """
    # Open-Meteo API endpoint
    url = "https://api.open-meteo.com/v1/forecast"
    
    # Query parameters
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,precipitation_probability_max,windspeed_10m_max",
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "forecast_days": days,
        "timezone": "auto"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Process the API response
            daily_data = []
            for i in range(len(data["daily"]["time"])):
                daily_data.append({
                    "date": data["daily"]["time"][i],
                    "temperature": data["daily"]["temperature_2m_max"][i],
                    "precipitation_probability": data["daily"]["precipitation_probability_max"][i] / 100,  # Convert percentage to 0-1
                    "wind_speed": data["daily"]["windspeed_10m_max"][i]
                })
            
            return daily_data
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        # Return empty data in case of error
        return []

async def get_location_name(lat: float, lon: float) -> str:
    """
    Get location name from coordinates using Open-Meteo Geocoding API
    
    Args:
        lat: Latitude
        lon: Longitude
    
    Returns:
        Location name (City, Country)
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "count": 1,
        "format": "json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                result = data["results"][0]
                city = result.get("name", "Unknown Location")
                country = result.get("country", "")
                return f"{city}, {country}" if country else city
            
            return "Unknown Location"
    except Exception as e:
        logger.error(f"Error getting location name: {e}")
        return "Unknown Location"

def generate_ics_file(
    activity_name: str,
    date: datetime,
    time_start: int,
    time_end: int,
    location: str,
    description: str
) -> str:
    """
    Generate an ICS file content for calendar events
    
    Args:
        activity_name: Name of the activity
        date: Date of the activity
        time_start: Start hour (0-23)
        time_end: End hour (0-23)
        location: Location description
        description: Event description
    
    Returns:
        ICS file content as string
    """
    calendar = Calendar()
    event = Event()
    
    # Set event details
    event.name = f"{activity_name}"
    
    # Set start and end times
    start_datetime = date.replace(hour=time_start, minute=0, second=0)
    end_datetime = date.replace(hour=time_end, minute=0, second=0)
    event.begin = start_datetime
    event.end = end_datetime
    
    event.location = location
    event.description = description
    
    # Add event to calendar
    calendar.events.add(event)
    
    return str(calendar)

def generate_invite_email(
    user_name: str,
    recipient_email: str,
    activity_name: str,
    recommendation: Dict,
    location: str
) -> Dict:
    """
    Generate an invitation email (for storage, not sending in MVP)
    
    Args:
        user_name: Name of the user
        recipient_email: Email of the recipient
        activity_name: Name of the activity
        recommendation: Recommendation data
        location: Location name
    
    Returns:
        Email data dict with subject and body
    """
    # Format the date
    activity_date = recommendation["date"]
    day_name = activity_date.strftime("%A")
    date_str = activity_date.strftime("%B %d")
    
    # Format time range
    time_start = recommendation["preferred_time_start"]
    time_end = recommendation["preferred_time_end"]
    time_start_str = f"{time_start}:00"
    time_end_str = f"{time_end}:00"
    if time_start >= 12:
        time_start_str = f"{time_start - 12 if time_start > 12 else 12}:00 PM"
    else:
        time_start_str = f"{time_start}:00 AM"
    
    if time_end >= 12:
        time_end_str = f"{time_end - 12 if time_end > 12 else 12}:00 PM"
    else:
        time_end_str = f"{time_end}:00 AM"
    
    # Create email subject and body
    subject = f"Join me for {activity_name} on {day_name}?"
    
    body = f"""
Hi there!

I'm planning to enjoy some time {activity_name.lower()} on {day_name}, {date_str} and I'd love for you to join me!

Time: {time_start_str} to {time_end_str}
Location: {location}
Weather forecast: {recommendation["weather_summary"]}

The forecast looks {get_score_description(recommendation["score"])} for this activity!

Let me know if you can make it!

Best,
{user_name}

--
Powered by The Next Good Day
https://nextgoodday.app
"""
    
    return {
        "subject": subject,
        "body": body.strip()
    }

def get_score_description(score: float) -> str:
    """Get a descriptive text based on the score"""
    if score >= 8.5:
        return "perfect"
    elif score >= 7.0:
        return "excellent"
    elif score >= 5.5:
        return "very good"
    elif score >= 4.0:
        return "good"
    else:
        return "decent"

def filter_activities_by_demographics(activities: List[Dict], age_range: str, gender: Optional[str] = None) -> List[Dict]:
    """
    Filter activities based on user demographics
    
    Args:
        activities: List of activity dicts
        age_range: User's age range (e.g., "18-24")
        gender: User's gender (optional)
    
    Returns:
        Filtered list of activities
    """
    # Extract min and max age from age range
    age_parts = age_range.replace("+", "-100").split("-")
    try:
        min_user_age = int(age_parts[0])
        max_user_age = int(age_parts[1]) if len(age_parts) > 1 else 100
    except (ValueError, IndexError):
        # Default in case of parsing error
        min_user_age = 18
        max_user_age = 65
    
    filtered = []
    for activity in activities:
        # Check age criteria if specified
        if activity.get("min_age") is not None and min_user_age < activity["min_age"]:
            continue
        if activity.get("max_age") is not None and max_user_age > activity["max_age"]:
            continue
        
        # Check gender criteria if specified
        if gender and activity.get("gender_preference") and activity["gender_preference"] != gender:
            continue
        
        filtered.append(activity)
    
    return filtered

import datetime
from typing import Dict, List, Tuple, Optional
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default preferences by age group
AGE_GROUP_PREFERENCES = {
    "18-24": {
        "weekday_hours": (17, 22),  # 5PM to 10PM
        "weekend_hours": (10, 22),  # 10AM to 10PM
    },
    "25-34": {
        "weekday_hours": (18, 21),  # 6PM to 9PM
        "weekend_hours": (9, 21),   # 9AM to 9PM
    },
    "35-44": {
        "weekday_hours": (17, 20),  # 5PM to 8PM
        "weekend_hours": (8, 20),   # 8AM to 8PM
    },
    "45-54": {
        "weekday_hours": (17, 20),  # 5PM to 8PM
        "weekend_hours": (8, 19),   # 8AM to 7PM
    },
    "55+": {
        "weekday_hours": (10, 18),  # 10AM to 6PM - more flexible schedule
        "weekend_hours": (9, 18),   # 9AM to 6PM
    }
}

# Default activity preferences
ACTIVITY_DEFAULTS = {
    "outdoor": {
        "min_temperature": 60,  # °F
        "max_temperature": 85,  # °F
        "avoid_rain": True,
        "avoid_snow": True,
    },
    "creative": {
        "min_temperature": 50,  # °F - indoor activities can be comfortable at lower temps
        "max_temperature": 90,  # °F
        "avoid_rain": False,    # Doesn't matter for indoor activities
        "avoid_snow": False,    # Doesn't matter for indoor activities
    },
    "social": {
        "min_temperature": 55,  # °F
        "max_temperature": 90,  # °F
        "avoid_rain": True,     # Assuming some activities might be outdoors
        "avoid_snow": True,
    }
}

def is_weekend(date: datetime.datetime) -> bool:
    """Check if the given date is a weekend (Saturday or Sunday)"""
    return date.weekday() >= 5  # 5=Saturday, 6=Sunday

def get_default_time_window(age_range: str, date: datetime.datetime) -> Tuple[int, int]:
    """Get default time window based on age range and whether it's a weekend"""
    if age_range not in AGE_GROUP_PREFERENCES:
        # Default to mid-range if age not specified
        age_range = "25-34"
    
    if is_weekend(date):
        return AGE_GROUP_PREFERENCES[age_range]["weekend_hours"]
    else:
        return AGE_GROUP_PREFERENCES[age_range]["weekday_hours"]

def calculate_weather_score(
    temperature: float,
    precipitation_probability: float,
    wind_speed: float,
    min_temp: float = 60,
    max_temp: float = 85,
    avoid_rain: bool = True
) -> Tuple[float, str]:
    """
    Calculate a weather score from 1-10 based on temperature and precipitation
    
    Returns:
        Tuple of (score, explanation)
    """
    score = 5.0  # Start with a neutral score
    explanation_parts = []
    
    # Temperature scoring (ideal is between min_temp and max_temp)
    if min_temp <= temperature <= max_temp:
        temp_score = 3.0  # Bonus for ideal temperature
        explanation_parts.append(f"Ideal temperature of {temperature:.1f}°F")
    elif temperature < min_temp:
        # Linear penalty for cold temperatures
        temp_diff = min_temp - temperature
        temp_score = max(0, 3.0 - (temp_diff / 10))
        explanation_parts.append(f"A bit cool at {temperature:.1f}°F")
    else:  # temperature > max_temp
        # Linear penalty for hot temperatures
        temp_diff = temperature - max_temp
        temp_score = max(0, 3.0 - (temp_diff / 10))
        explanation_parts.append(f"A bit warm at {temperature:.1f}°F")
    
    score += temp_score
    
    # Precipitation scoring
    if avoid_rain and precipitation_probability > 0.5:
        rain_penalty = 4.0 * (precipitation_probability - 0.5)
        score -= rain_penalty
        explanation_parts.append(f"High chance of rain ({precipitation_probability*100:.0f}%)")
    elif avoid_rain and precipitation_probability > 0.2:
        rain_penalty = 2.0 * (precipitation_probability - 0.2)
        score -= rain_penalty
        explanation_parts.append(f"Some chance of rain ({precipitation_probability*100:.0f}%)")
    elif precipitation_probability < 0.1:
        score += 1.0
        explanation_parts.append("Clear skies expected")
    
    # Wind scoring - penalty for high winds
    if wind_speed > 15:
        wind_penalty = min(2.0, (wind_speed - 15) / 10)
        score -= wind_penalty
        explanation_parts.append(f"Windy conditions ({wind_speed:.1f} mph)")
    
    # Ensure score is between 1 and 10
    score = max(1.0, min(10.0, score))
    
    # Create final explanation
    if score >= 8.0:
        quality = "Perfect"
    elif score >= 6.0:
        quality = "Great"
    elif score >= 4.0:
        quality = "Good"
    else:
        quality = "Fair"
    
    explanation = f"{quality} conditions: " + "; ".join(explanation_parts)
    
    return (score, explanation)

def get_weather_summary(
    temperature: float,
    precipitation_probability: float
) -> str:
    """Generate a simple weather summary"""
    if precipitation_probability > 0.7:
        condition = "Rainy"
    elif precipitation_probability > 0.4:
        condition = "Chance of rain"
    elif precipitation_probability > 0.2:
        condition = "Partly cloudy"
    else:
        condition = "Clear"
    
    return f"{condition}, {temperature:.1f}°F"

def score_days(
    weather_data: List[Dict],
    user_age_range: str,
    activity_category: str,
    user_preferences: Optional[Dict] = None
) -> List[Dict]:
    """
    Score each day based on weather and user preferences
    
    Args:
        weather_data: List of daily weather forecasts
        user_age_range: User's age range for default availability
        activity_category: Category of activity ("outdoor", "creative", "social")
        user_preferences: Optional dict of user-specific preferences
    
    Returns:
        List of scored day recommendations, sorted by score (descending)
    """
    # Get default preferences for the activity category
    activity_prefs = ACTIVITY_DEFAULTS.get(activity_category, ACTIVITY_DEFAULTS["outdoor"])
    
    # Override defaults with user preferences if provided
    if user_preferences:
        for key, value in user_preferences.items():
            if key in activity_prefs and value is not None:
                activity_prefs[key] = value
    
    # Score each day
    scored_days = []
    for day_data in weather_data:
        day_date = datetime.datetime.fromisoformat(day_data["date"])
        
        # Get default time window based on age and weekday/weekend
        time_start, time_end = get_default_time_window(user_age_range, day_date)
        
        # Calculate weather score
        score, explanation = calculate_weather_score(
            temperature=day_data["temperature"],
            precipitation_probability=day_data["precipitation_probability"],
            wind_speed=day_data.get("wind_speed", 0),
            min_temp=activity_prefs["min_temperature"],
            max_temp=activity_prefs["max_temperature"],
            avoid_rain=activity_prefs["avoid_rain"]
        )
        
        # Availability bonus for weekends
        if is_weekend(day_date):
            score += 0.5
            availability_note = "Weekend availability"
        else:
            availability_note = "Evening availability"
        
        weather_summary = get_weather_summary(
            day_data["temperature"],
            day_data["precipitation_probability"]
        )
        
        # Full explanation
        full_explanation = f"{explanation}. {availability_note}."
        
        scored_days.append({
            "date": day_date,
            "score": score,
            "explanation": full_explanation,
            "weather_summary": weather_summary,
            "temperature": day_data["temperature"],
            "precipitation_probability": day_data["precipitation_probability"],
            "preferred_time_start": time_start,
            "preferred_time_end": time_end
        })
    
    # Sort by score (descending)
    scored_days.sort(key=lambda x: x["score"], reverse=True)
    
    return scored_days

def get_top_recommendations(
    weather_data: List[Dict],
    user_age_range: str,
    activity_category: str,
    user_preferences: Optional[Dict] = None,
    top_n: int = 3
) -> List[Dict]:
    """
    Get the top N recommended days
    
    Args:
        weather_data: List of daily weather forecasts
        user_age_range: User's age range
        activity_category: Category of activity
        user_preferences: Optional dict of user-specific preferences
        top_n: Number of top days to return
    
    Returns:
        List of top N recommended days
    """
    scored_days = score_days(
        weather_data=weather_data,
        user_age_range=user_age_range,
        activity_category=activity_category,
        user_preferences=user_preferences
    )
    
    # Return top N days
    return scored_days[:top_n]

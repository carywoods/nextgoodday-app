# nextgoodday-app
# The Next Good Day - MVP

A web-based SaaS app that helps users identify the best upcoming days to pursue activities based on weather, availability, and other contextual signals.

## Overview

The Next Good Day is a mobile-first application that:
- Helps users find optimal days for their activities
- Combines weather data with user preferences
- Generates personalized recommendations
- Allows basic sharing functionality

## Features

- **User Setup**: Minimal friction onboarding with browser geolocation
- **Activity Selection**: Choose from a pre-filtered list of activities
- **Smart Recommendations**: Algorithm scores days based on weather and default availability
- **Calendar Integration**: Download ICS files for calendar import
- **Invites**: Generate (but don't send) email invitations to friends

## Tech Stack

- **Frontend**: React with Tailwind CSS for mobile-first design
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **APIs**: 
  - Open-Meteo for weather data
  - Browser geolocation for location detection
  - ICS file generation for calendar integration

## Project Structure

```
/nextgoodday/
├── backend/
│   ├── main.py (FastAPI app)
│   ├── models.py (SQLAlchemy)
│   ├── scoring.py (Scoring algorithm)
│   ├── utils.py (Helper functions)
├── frontend/
│   ├── index.html
│   ├── app.js (Main React app)
│   ├── styles.css
│   ├── components/
│   │   ├── Onboarding.js
│   │   ├── ActivitySelector.js
│   │   ├── Recommendations.js
│   │   ├── InviteForm.js
│   │   ├── Navbar.js
│   │   └── Loading.js
│   └── services/
│       └── api.js (API client)
├── static/
│   └── favicon.ico
├── db.sqlite3
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js and npm (for development)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/nextgoodday.git
   cd nextgoodday
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies:
   ```
   pip install fastapi uvicorn sqlalchemy httpx python-dotenv
   ```

4. Create a .env file from the template:
   ```
   cp .env.example .env
   ```
   
5. Initialize the database:
   ```
   python -m backend.main
   ```
   
6. Run the development server:
   ```
   uvicorn backend.main:app --reload
   ```
   
7. Access the application at http://localhost:8000

## Deployment

### Traditional Web Hosting (InMotion/Hostinger)

To deploy this application on traditional web hosting services like InMotion or Hostinger:

1. Ensure your hosting plan supports Python applications (typically available in most shared hosting plans)
2. Access your hosting control panel (cPanel, Plesk, etc.)
3. Set up a Python application:
   - Create a Python application through the hosting control panel
   - Select Python 3.9+ as the version
   - Set the application root to your project directory
   
4. Upload files via FTP:
   - Upload all project files to your hosting space
   - Make sure to maintain the folder structure

5. Configure environment:
   - Create a .env file with your settings
   - Set environment variables through the hosting control panel if supported

6. Install dependencies:
   - Use SSH access (if available) to run pip install commands
   - Alternatively, use the hosting panel's package installer if available

7. Set up the database:
   - Create a SQLite database file (or use PostgreSQL if available)
   - Run the initialization script to create tables

8. Configure web server:
   - Set up WSGI configuration (most hosts use Apache with mod_wsgi)
   - Create a WSGI configuration file:

```python
# wsgi.py
from backend.main import app

# For standard WSGI servers
application = app
```

9. Set the entry point in your hosting control panel to the wsgi.py file

10. Restart the application through the control panel

### Alternatives for Easier Deployment

If you encounter difficulties with traditional hosting, consider these alternatives:

- **Heroku**: Easy deployment with Git integration
- **Render**: Simple deployment for FastAPI applications
- **Railway**: Push-to-deploy functionality
- **DigitalOcean App Platform**: Managed hosting with easy setup

## Next Steps

Future enhancements planned for after MVP:

- Google Calendar integration
- Email delivery implementation
- User authentication
- Custom activity creation
- More detailed weather preferences
- Mobile app packaging

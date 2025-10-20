import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'flight_tracking')
    
    # Flask Configuration
    DEBUG = os.getenv('DEBUG', False)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Mapbox Configuration (for frontend)
    MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN', '')
    MAPBOX_STYLE = os.getenv('MAPBOX_STYLE', 'mapbox/streets-v11')
    
    # API Configuration
    MAX_TRACKING_POINTS = 10000
    RECENT_PATH_LIMIT = 10
    
    # Visualization Configuration
    MAP_ZOOM_START = 5
    DEFAULT_MAP_TILES = 'OpenStreetMap'
    
    @classmethod
    def validate_mapbox_config(cls):
        """Validate Mapbox configuration for frontend"""
        if not cls.MAPBOX_ACCESS_TOKEN:
            print("WARNING: MAPBOX_ACCESS_TOKEN not set. Mapbox features will be disabled.")
            return False
        return True
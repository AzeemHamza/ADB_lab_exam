from datetime import datetime

def parse_iso_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO timestamp string to datetime object"""
    return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers"""
    # Simplified calculation - in production use geopy or similar
    from math import radians, sin, cos, sqrt, atan2
    R = 6371  # Earth radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c
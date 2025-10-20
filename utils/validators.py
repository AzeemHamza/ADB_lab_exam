def validate_tracking_data(data: dict) -> str:
    """Validate tracking update data"""
    required_fields = ['flight_id', 'receiver_id', 'position', 'timestamp']
    
    for field in required_fields:
        if field not in data:
            return f'Missing required field: {field}'
    
    position_fields = ['latitude', 'longitude', 'altitude', 'heading', 'speed']
    for field in position_fields:
        if field not in data['position']:
            return f'Missing required position field: {field}'
    
    # Validate coordinate ranges
    lat = data['position']['latitude']
    lon = data['position']['longitude']
    if not (-90 <= lat <= 90):
        return 'Latitude must be between -90 and 90'
    if not (-180 <= lon <= 180):
        return 'Longitude must be between -180 and 180'
    
    return None

def validate_flight_id(flight_id: str) -> bool:
    """Validate flight ID format"""
    if not flight_id or len(flight_id) < 3:
        return False
    return True
from datetime import datetime
from typing import Dict, List, Optional

class Position:
    def __init__(self, latitude: float, longitude: float, altitude: float, 
                 heading: float, speed: float, vertical_rate: float = 0):
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.heading = heading
        self.speed = speed
        self.vertical_rate = vertical_rate
    
    def to_dict(self) -> Dict:
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'heading': self.heading,
            'speed': self.speed,
            'vertical_rate': self.vertical_rate
        }

class Airport:
    def __init__(self, code: str, name: str, city: str, country: str):
        self.code = code
        self.name = name
        self.city = city
        self.country = country
    
    def to_dict(self) -> Dict:
        return {
            'code': self.code,
            'name': self.name,
            'city': self.city,
            'country': self.country
        }

class Aircraft:
    def __init__(self, registration: str, type: str, model: str):
        self.registration = registration
        self.type = type
        self.model = model
    
    def to_dict(self) -> Dict:
        return {
            'registration': self.registration,
            'type': self.type,
            'model': self.model
        }

class Flight:
    def __init__(self, flight_id: str, airline: str, flight_number: str,
                 origin: Airport, destination: Airport, aircraft: Aircraft,
                 status: str = "scheduled"):
        self.flight_id = flight_id
        self.airline = airline
        self.flight_number = flight_number
        self.origin = origin
        self.destination = destination
        self.aircraft = aircraft
        self.status = status
        self.scheduled_departure = None
        self.scheduled_arrival = None
        self.current_position = None
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
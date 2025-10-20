from datetime import datetime
from models.database import db
from pymongo import ASCENDING, DESCENDING
#flight_service.py acts as the middle layer between the routes (controllers) and the database.
#It performs the actual operations like fetching flights, marking them complete, or retrieving their history — all by interacting with MongoDB.
class FlightService:
    def complete_flight(self, flight_id: str) -> dict:
        """Move completed flight to logs collection"""
        flight = db.flights.find_one({'flight_id': flight_id})
        if not flight:
            raise ValueError('Flight not found')
        
        # Get complete tracking path
        tracking_path = list(db.tracking_updates.find( #Fetches all tracking updates (positions, timestamps) related to that flight.
            {'flight_id': flight_id},
            {'position': 1, 'timestamp': 1}
        ).sort('timestamp', ASCENDING))
        
        # Create flight log
        flight_log = {  #Creates a new dictionary that contains all important details of this flight.
            'flight_id': flight_id,
            'airline': flight.get('airline'),
            'flight_number': flight.get('flight_number'),
            'origin': flight.get('origin'),
            'destination': flight.get('destination'),
            'aircraft': flight.get('aircraft'),
            'scheduled_departure': flight.get('scheduled_departure'),
            'scheduled_arrival': flight.get('scheduled_arrival'),
            'actual_departure': flight.get('actual_departure'),
            'actual_arrival': datetime.utcnow(),
            'tracking_path': [
                {  #Basically, this is the entire flight path from takeoff to landing.
                    'latitude': point['position']['latitude'],
                    'longitude': point['position']['longitude'],
                    'altitude': point['position']['altitude'],
                    'heading': point['position'].get('heading'),
                    'speed': point['position'].get('speed'),
                    'timestamp': point['timestamp']
                }
                for point in tracking_path
            ],
            'created_at': flight.get('created_at'),
            'completed_at': datetime.utcnow()
        }
        
        # Save to logs (active_flights -> flight_logs)
        db.flight_logs.insert_one(flight_log)
        
        # Remove from active collections (delete from flight_logs)
        db.flights.delete_one({'flight_id': flight_id})
        db.tracking_updates.delete_many({'flight_id': flight_id}) 
        #This means the flight has now been moved to “history” — it’s done flying.
        return {
            'status': 'success',
            'message': f'Flight {flight_id} completed and moved to logs'
        }
    
    def get_flights(self, status_filter: str = None) -> list:
        """Get all flights with optional status filter"""
        query = {}
        if status_filter:
            query['status'] = status_filter #If a filter like "active" or "delayed" is provided, it only fetches flights with that status.
        
        flights = list(db.flights.find(query)) #Retrieves all flights matching the query and converts them to a list.
        return flights
    
    def get_flight_history(self, flight_id: str) -> dict:
        """Get complete flight history from logs"""
        flight_log = db.flight_logs.find_one({'flight_id': flight_id})
        if not flight_log:
            raise ValueError('Flight history not found')
        
        return flight_log
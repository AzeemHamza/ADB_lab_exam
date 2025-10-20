from datetime import datetime
from models.database import db
from utils.helpers import parse_iso_timestamp
#It’s the "live tracking brain" of your system — constantly recording and updating where each flight is.
class TrackingService:
    def process_tracking_update(self, data: dict) -> dict:
        """Process and store tracking update"""
        timestamp = parse_iso_timestamp(data['timestamp'])
        
        # Store tracking update
        tracking_data = {
            'flight_id': data['flight_id'],
            'position': data['position'],
            'timestamp': timestamp,
            'receiver': {
                'id': data['receiver_id'],
                'signal_strength': data.get('signal_strength', 1.0)
            },
            'created_at': datetime.utcnow()
        }
        
        db.tracking_updates.insert_one(tracking_data)
        
        # Update current flight position
        flight_update = { #Update flight’s current position
            'current_position': data['position'],
            'updated_at': datetime.utcnow(),
            'status': 'active'
        }
        
        db.flights.update_one( #Update (or create as upsert=true  will create a flight if it doesnt exist) flight record
            {'flight_id': data['flight_id']},
            {'$set': flight_update},
            upsert=True
        )
        
        return {'success': True}
    
    def get_flight_position(self, flight_id: str, timestamp_str: str = None, 
                           include_path: bool = False) -> dict:
        """Get flight position (current or historical)"""
        from pymongo import DESCENDING
        
        # Find flight details
        flight = db.flights.find_one({'flight_id': flight_id})
        if not flight:
            raise ValueError('Flight not found')
        
        position_data = None
        
        if timestamp_str:
            # Get historical position
            target_time = parse_iso_timestamp(timestamp_str) #converts to a string understandable by python
            position_data = db.tracking_updates.find_one(
                {
                    'flight_id': flight_id,
                    'timestamp': {'$lte': target_time}
                },
                sort=[('timestamp', DESCENDING)]
            )
        else:
            # Get latest position
            position_data = db.tracking_updates.find_one(
                {'flight_id': flight_id},
                sort=[('timestamp', DESCENDING)]
            )
        
        if not position_data and not timestamp_str:
            position_data = {'position': flight.get('current_position')}
        
        response = {
            'flight_id': flight_id,
            'airline': flight.get('airline'),
            'flight_number': flight.get('flight_number'),
            'status': flight.get('status', 'unknown'),
            'position': position_data['position'] if position_data else None,
            'origin': flight.get('origin'),
            'destination': flight.get('destination')
        }
        
        if include_path and position_data: #“Show me the last 10 times we received position data for this flight.”
            recent_path = list(db.tracking_updates.find(
                {'flight_id': flight_id},
                {'position': 1, 'timestamp': 1}
            ).sort('timestamp', DESCENDING).limit(10))
            
            response['recent_path'] = [
                {
                    'latitude': pos['position']['latitude'],
                    'longitude': pos['position']['longitude'],
                    'altitude': pos['position']['altitude'],
                    'timestamp': pos['timestamp']
                }
                for pos in reversed(recent_path)
            ]
        
        return response
from flask import Blueprint, request, jsonify, render_template
from models.database import db
from services.flight_service import FlightService
from services.visualization_service import VisualizationService
from config import Config  # Add this import
from bson.json_util import dumps

#Defining different API endpoints (routes) that handle all 
# the flight-related requests — like getting all flights,
#  marking a flight as completed, showing a flight’s history, or visualizing its 
# path on a map.
flight_bp = Blueprint('flights', __name__)
#Makes objects from the service classes so you can call their functions later.
flight_service = FlightService()
visualization_service = VisualizationService()

#Defines a GET API endpoint /api/flights to get flight data.
@flight_bp.route('/api/flights', methods=['GET'])
def get_all_flights():
    """Get all active flights"""
    try:
        status_filter = request.args.get('status') #reads from the query
        flights = flight_service.get_flights(status_filter) #gets the flight through the query
        return dumps({"flights": flights}), 200, {'Content-Type': 'application/json'} # converts to json 
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#API endpoint to mark a flight as completed, e.g. /api/flights/PK303/complete.
@flight_bp.route('/api/flights/<flight_id>/complete', methods=['POST'])
def complete_flight(flight_id):
    """Mark flight as completed and move to logs"""
    try:
        result = flight_service.complete_flight(flight_id)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# get flight history
@flight_bp.route('/api/flights/<flight_id>/history', methods=['GET'])
def get_flight_history(flight_id):
    """Get complete flight path from logs"""
    try:
        history = flight_service.get_flight_history(flight_id)
        return jsonify(history)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Add new endpoint for Mapbox visualization
@flight_bp.route('/api/flights/<flight_id>/visualize', methods=['GET'])
def visualize_flight(flight_id):
    """Generate Mapbox visualization for flight path"""
    try:
        map_type = request.args.get('map_type', 'mapbox')
        
        if map_type == 'mapbox':
            result = visualization_service.create_mapbox_map(flight_id, 'static/maps')
        else:
            result = visualization_service.plot_flight_path(flight_id, 'static/maps')
        
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@flight_bp.route('/flight/map', methods=['GET'])
def flight_map():
    """Serve real-time flight tracking map"""
    return render_template('flight_map.html', 
                         mapbox_token=Config.MAPBOX_ACCESS_TOKEN,  # Now Config is defined
                         mapbox_enabled=visualization_service.mapbox_enabled)

@flight_bp.route('/flight/<flight_id>/map', methods=['GET'])
def individual_flight_map(flight_id):
    """Serve individual flight tracking page"""
    flight = db.flights.find_one({'flight_id': flight_id})
    if not flight:
        return jsonify({'error': 'Flight not found'}), 404
    
    return render_template('individual_flight.html',
                         flight=flight,
                         mapbox_token=Config.MAPBOX_ACCESS_TOKEN,  # Now Config is defined
                         mapbox_enabled=visualization_service.mapbox_enabled)

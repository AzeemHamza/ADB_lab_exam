from flask import Blueprint, request, jsonify
from models.database import db
from services.tracking_service import TrackingService
from utils.validators import validate_tracking_data

tracking_bp = Blueprint('tracking', __name__)
tracking_service = TrackingService()

@tracking_bp.route('/api/tracking/update', methods=['POST'])
def tracking_update():
    """Ingest flight tracking data from receivers"""
    try:
        data = request.get_json()
        
        # Validate input data
        validation_error = validate_tracking_data(data)
        if validation_error:
            return jsonify({'error': validation_error}), 400
        
        # Process tracking data
        result = tracking_service.process_tracking_update(data)
        
        return jsonify({
            'status': 'success',
            'message': 'Tracking data received',
            'flight_id': data['flight_id'],
            'timestamp': data['timestamp']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tracking_bp.route('/api/flights/<flight_id>/position', methods=['GET'])
def get_flight_position(flight_id):
    """Get flight position at specific time or latest"""
    try:
        timestamp_str = request.args.get('timestamp')
        include_path = request.args.get('include_path', 'false').lower() == 'true'
        
        position_data = tracking_service.get_flight_position(
            flight_id, timestamp_str, include_path
        )
        
        return jsonify(position_data)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
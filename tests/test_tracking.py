import pytest
from app import create_app
from models.database import db

class TestTrackingAPI:
    def setup_method(self):
        self.app = create_app()
        self.client = self.app.test_client()
        
    def test_tracking_update(self):
        data = {
            "flight_id": "TEST123",
            "receiver_id": "REC-001",
            "position": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "altitude": 35000,
                "heading": 85.5,
                "speed": 450,
                "vertical_rate": 0
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        response = self.client.post('/api/tracking/update', json=data)
        assert response.status_code == 200
        assert response.json['status'] == 'success'
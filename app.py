from flask import Flask, jsonify, render_template
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json

app = Flask(__name__)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["flight_tracking"]

# Helper to make ObjectId JSON serializable
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder


# ---- ROUTE: GET ALL FLIGHTS ----
@app.route("/api/flights", methods=["GET"])
def get_all_flights():
    """Returns all flights stored in the database"""
    flights = list(db.flights.find())
    
    if not flights:
        return jsonify({"error": "No flights found"}), 404

    for flight in flights:
        flight["_id"] = str(flight["_id"])

    return jsonify({"flights": flights}), 200


# ---- ROUTE: GET FLIGHT HISTORY ----
@app.route("/api/flights/<flight_id>/history", methods=["GET"])
def get_flight_history(flight_id):
    """Returns all tracking updates for a specific flight"""
    records = list(db.tracking_updates.find({"flight_id": flight_id}))
    
    if not records:
        return jsonify({"error": "Flight history not found"}), 404
    
    for record in records:
        record["_id"] = str(record["_id"])
        record["created_at"] = record["created_at"].isoformat()

    return jsonify({"history": records}), 200


# ---- ROUTE: SHOW FLIGHT MAP PAGE ----
@app.route("/flight_map")
def show_flight_map():
    """Displays the frontend map for tracking flights"""
    return render_template("flight_map.html")


if __name__ == "__main__":
    app.run(debug=True)

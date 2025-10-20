from flask import Flask, jsonify
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json   # ✅ This line was missing!
from flask import render_template

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

# ---- ROUTE TO GET FLIGHT HISTORY ----
@app.route("/api/flights/<flight_id>/history", methods=["GET"])
def get_flight_history(flight_id):
    records = list(db.tracking_updates.find({"flight_id": flight_id}))
    
    if not records:
        return jsonify({"error": "Flight history not found"}), 404
    
    for record in records:
        record["_id"] = str(record["_id"])
        record["created_at"] = record["created_at"].isoformat()

    return jsonify({"history": records}), 200


if __name__ == "__main__":
    app.run(debug=True)
    
@app.route("/map")
def show_map():
    return render_template("map.html")

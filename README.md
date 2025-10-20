Name : M.Hamza Azeem
Reg.No : FA23-BCS-112
Section :C
Lab exam paper : E


# 🛫 Flight Tracking System (ADB Lab Exam)

## 📋 Overview
This project is a **Flask-based flight tracking system** similar to FlightAware.  
It receives, stores, and retrieves flight and tracking data in **MongoDB**, providing APIs to query active flights, their details, and movement history.

The system demonstrates core concepts of:
- REST API design using **Flask**
- **MongoDB integration** using `PyMongo`
- **JSON-based communication**
- **Data modeling and insertion** for flights and tracking updates

---

## ⚙️ Tech Stack
| Component | Technology |
|------------|-------------|
| Backend | Python (Flask) |
| Database | MongoDB |
| Driver | PyMongo |
| API Format | REST + JSON |
| Environment | Virtualenv / VS Code |
| Testing | Browser or cURL / Postman |

---

## 📂 Project Structure
```
ADB_lab_exam/
│
├── app.py                     # Flask entry point
├── config.py                  # Database and environment configuration
├── routes/
│   ├── __init__.py
│   └── tracking_routes.py     # API routes for flights and tracking
│
├── models/
│   ├── __init__.py
│   ├── flight_model.py        # Flight data schema
│   └── tracking_model.py      # Tracking update schema
│
├── utils/
│   ├── __init__.py
│   └── json_encoder.py        # Custom JSON encoder for ObjectId
│
├── insert_flight_and_points.py # Script to insert sample data
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🧩 Installation & Setup

### 1️⃣ Prerequisites
- **Python 3.8+**
- **MongoDB** (running locally)
- **VS Code / Terminal access**

---

### 2️⃣ Setup Virtual Environment
```powershell
# inside project folder
python -m venv .venv
.venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies
```powershell
pip install -r requirements.txt
```

If you don’t have `requirements.txt`, install manually:
```powershell
pip install flask pymongo
```

---

### 4️⃣ Start MongoDB
Make sure MongoDB is running:
```powershell
Get-Service *mongo*
```
If it’s stopped:
```powershell
Start-Service MongoDB
```

---

### 5️⃣ Set Environment Variables
```powershell
$env:DATABASE_NAME = "flight_tracking"
$env:MONGODB_URI = "mongodb://127.0.0.1:27017/"
$env:FLASK_APP = "app.py"
$env:FLASK_ENV = "development"
```

---

### 6️⃣ Insert Sample Data
Run the data insertion script to populate sample flight and tracking information:
```powershell
python insert_flight_and_points.py
```

---

### 7️⃣ Run the Flask Server
```powershell
python app.py
```
or
```powershell
flask run
```

Server starts at:
> 🔗 http://127.0.0.1:5000

---

## 🧠 API Endpoints

| Endpoint | Method | Description |
|-----------|--------|-------------|
| `/api/flights` | GET | Retrieve list of all flights |
| `/api/flights/<flight_id>` | GET | Get details of a specific flight |
| `/api/flights/<flight_id>/history` | GET | Retrieve tracking updates for a flight |
| `/api/tracking` | POST | Add a new tracking update (for testing insertion) |

---

### 📡 Example API Usage

**Get all flights:**
```
GET http://127.0.0.1:5000/api/flights
```

**Get single flight info:**
```
GET http://127.0.0.1:5000/api/flights/PK201
```

**Get flight tracking history:**
```
GET http://127.0.0.1:5000/api/flights/PK201/history
```

**Insert new tracking update (example POST):**
```json
POST /api/tracking
{
  "flight_id": "PK201",
  "receiver_id": "RCV001",
  "position": {
    "latitude": 24.8618,
    "longitude": 67.0102,
    "altitude": 29900,
    "heading": 95,
    "speed": 445
  },
  "timestamp": "2025-10-20T10:15:00Z"
}
```

---

## 🧾 Sample Response

**GET /api/flights**
```json
{
  "flights": [
    {
      "flight_id": "PK201",
      "callsign": "PK201",
      "origin": "KHI",
      "destination": "LHE",
      "status": "enroute",
      "aircraft_type": "A320"
    }
  ]
}
```

---

## 🧰 Troubleshooting

**1️⃣ MongoDB not connecting?**
- Check that MongoDB service is running:
  ```powershell
  Get-Service *mongo*
  ```

**2️⃣ Empty `{ "flights": [] }`?**
- Make sure `$env:DATABASE_NAME = "flight_tracking"` before running the app.
- Reinsert sample data if necessary.

**3️⃣ Port already in use?**
- Stop other Flask servers or use:
  ```powershell
  flask run -p 5050
  ```

---

## 🧑‍💻 Author
**Muhammad Hamza Azeem**  
ADB Lab Exam Project – Flight Tracking System

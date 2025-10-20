from pymongo import MongoClient, ASCENDING, DESCENDING
from config import Config

class Database:
    def __init__(self):
        self.client = MongoClient(Config.MONGODB_URI) # creates a mongo client connected to mongo db (self.client is a client obj from pymongo)
        self.db = self.client[Config.DATABASE_NAME] #made to access collections
        
        # Collections (these lines create refrences to mongo db colections)
        self.flights = self.db.flights                  #active flight documents
        self.tracking_updates = self.db.tracking_updates#frequent position updates
        self.flight_logs = self.db.flight_logs          #archived/completed flight logs
        self.receivers = self.db.receivers              #metadata about data receivers
        
        self._create_indexes()
        #indexes are used for efficient searching 
    def _create_indexes(self):
        # Index for tracking updates (most important for performance)
        self.tracking_updates.create_index([
            ('flight_id', ASCENDING),
            ('timestamp', ASCENDING)
        ])
        
        self.tracking_updates.create_index([('timestamp', DESCENDING)])
        
        # Index for flights collection
        self.flights.create_index([('flight_id', ASCENDING)])
        self.flights.create_index([('status', ASCENDING)])
        
        # Index for flight logs
        self.flight_logs.create_index([('flight_id', ASCENDING)])
        self.flight_logs.create_index([('completed_at', DESCENDING)])
        
        # Index for receivers
        self.receivers.create_index([('receiver_id', ASCENDING)])
        
        print("Database indexes created successfully")

# Global database instance
db = Database()
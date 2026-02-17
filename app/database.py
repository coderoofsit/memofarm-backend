from pymongo import MongoClient
from flask import current_app


class Database:
    """MongoDB Database Connection"""

    client = None
    db = None

    @staticmethod
    def initialize(app):
        """Initialize database connection"""
        try:
            print(f"[DEBUG] Connecting to MongoDB URI: {app.config['MONGODB_URI']}")
            Database.client = MongoClient(app.config["MONGODB_URI"])
            Database.db = Database.client[app.config["DB_NAME"]]

            # Create indexes
            Database.create_indexes()

            print(f"✅ Connected to MongoDB: {app.config['DB_NAME']}")
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            raise

    @staticmethod
    def create_indexes():
        """Create database indexes for better performance"""
        # Users collection indexes
        Database.db.users.create_index("firebase_uid", unique=True)
        Database.db.users.create_index("email")

        # Medicines collection indexes
        Database.db.medicines.create_index([("user_id", 1), ("aic_code", 1)])
        Database.db.medicines.create_index([("user_id", 1), ("expiry_date", 1)])
        Database.db.medicines.create_index("barcode")

        # Italian medicines collection indexes
        Database.db.italian_medicines.create_index("codice_aic", unique=True)
        Database.db.italian_medicines.create_index("denominazione")
        Database.db.italian_medicines.create_index("ragione_sociale")
        Database.db.italian_medicines.create_index("pa_associati")
        Database.db.italian_medicines.create_index("codice_atc")

        print("✅ Database indexes created")

    @staticmethod
    def get_db():
        """Get database instance"""
        return Database.db

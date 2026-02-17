from datetime import datetime
from bson import ObjectId
from app.database import Database


class User:
    """User Model"""

    collection = "users"

    @staticmethod
    def create(data):
        """Create new user"""
        db = Database.get_db()
        user_data = {
            "firebase_uid": data.get("firebase_uid"),
            "email": data.get("email"),
            "name": data.get("name"),
            "provider": data.get("provider"),  # google or apple
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = db[User.collection].insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return user_data

    @staticmethod
    def find_by_firebase_uid(firebase_uid):
        """Find user by Firebase UID"""
        db = Database.get_db()
        return db[User.collection].find_one({"firebase_uid": firebase_uid})

    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        db = Database.get_db()
        return db[User.collection].find_one({"email": email})

    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        db = Database.get_db()
        return db[User.collection].find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def update(user_id, data):
        """Update user"""
        db = Database.get_db()
        data["updated_at"] = datetime.utcnow()
        result = db[User.collection].update_one(
            {"_id": ObjectId(user_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(user_id):
        """Delete user"""
        db = Database.get_db()
        result = db[User.collection].delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @staticmethod
    def get_all(limit=50, skip=0, query=None):
        """Get all users with pagination"""
        db = Database.get_db()
        search_query = query if query else {}
        return list(
            db[User.collection]
            .find(search_query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

    @staticmethod
    def count(query=None):
        """Count users with optional query filter"""
        db = Database.get_db()
        search_query = query if query else {}
        return db[User.collection].count_documents(search_query)

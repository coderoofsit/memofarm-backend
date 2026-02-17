from datetime import datetime
from bson import ObjectId
from app.database import Database


class Medicine:
    """Medicine Model"""

    collection = "medicines"

    @staticmethod
    def create(user_id, data):
        """Create new medicine"""
        db = Database.get_db()
        medicine_data = {
            "user_id": ObjectId(user_id),
            "aic_code": data.get("aic_code"),  # Italian AIC code
            "barcode": data.get("barcode"),  # Full barcode from scanner
            "name": data.get("name"),
            "description": data.get("description"),
            "manufacturer": data.get("manufacturer"),
            "batch_number": data.get("batch_number"),
            "serial_number": data.get("serial_number"),
            "expiry_date": data.get("expiry_date"),
            "quantity": data.get("quantity", 1),
            "category": data.get("category", "General"),
            "notes": data.get("notes", ""),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = db[Medicine.collection].insert_one(medicine_data)
        medicine_data["_id"] = result.inserted_id
        return medicine_data

    @staticmethod
    def find_by_user(user_id, filters=None):
        """Get all medicines for a user with optional filters"""
        db = Database.get_db()
        query = {"user_id": ObjectId(user_id)}

        if filters:
            if filters.get("category"):
                query["category"] = filters["category"]
            if filters.get("expired"):
                query["expiry_date"] = {"$lt": datetime.utcnow()}

        return list(db[Medicine.collection].find(query).sort("expiry_date", 1))

    @staticmethod
    def find_by_id(medicine_id, user_id):
        """Find medicine by ID and user ID"""
        db = Database.get_db()
        return db[Medicine.collection].find_one(
            {"_id": ObjectId(medicine_id), "user_id": ObjectId(user_id)}
        )

    @staticmethod
    def find_by_barcode(barcode, user_id=None):
        """Find medicine by barcode"""
        db = Database.get_db()
        query = {"barcode": barcode}
        if user_id:
            query["user_id"] = ObjectId(user_id)
        return db[Medicine.collection].find_one(query)

    @staticmethod
    def find_by_aic(aic_code, user_id=None):
        """Find medicine by AIC code"""
        db = Database.get_db()
        query = {"aic_code": aic_code}
        if user_id:
            query["user_id"] = ObjectId(user_id)
        return db[Medicine.collection].find_one(query)

    @staticmethod
    def update(medicine_id, user_id, data):
        """Update medicine"""
        db = Database.get_db()
        data["updated_at"] = datetime.utcnow()
        result = db[Medicine.collection].update_one(
            {"_id": ObjectId(medicine_id), "user_id": ObjectId(user_id)},
            {"$set": data},
        )
        return result.modified_count > 0

    @staticmethod
    def delete(medicine_id, user_id):
        """Delete medicine"""
        db = Database.get_db()
        result = db[Medicine.collection].delete_one(
            {"_id": ObjectId(medicine_id), "user_id": ObjectId(user_id)}
        )
        return result.deleted_count > 0

    @staticmethod
    def delete_all_by_user(user_id):
        """Delete all medicines for a user"""
        db = Database.get_db()
        result = db[Medicine.collection].delete_many({"user_id": ObjectId(user_id)})
        return result.deleted_count

    @staticmethod
    def get_expiring_soon(user_id, days=30):
        """Get medicines expiring within specified days"""
        db = Database.get_db()
        expiry_date = datetime.utcnow()
        expiry_date = expiry_date.replace(
            day=expiry_date.day + days
        )  # Simplified for example
        return list(
            db[Medicine.collection]
            .find(
                {
                    "user_id": ObjectId(user_id),
                    "expiry_date": {
                        "$gte": datetime.utcnow(),
                        "$lte": expiry_date,
                    },
                }
            )
            .sort("expiry_date", 1)
        )

    @staticmethod
    def find_by_id_admin(medicine_id):
        """Find medicine by ID without user restriction (admin only)"""
        db = Database.get_db()
        return db[Medicine.collection].find_one({"_id": ObjectId(medicine_id)})

    @staticmethod
    def update_admin(medicine_id, data):
        """Update medicine without user restriction (admin only)"""
        db = Database.get_db()
        data["updated_at"] = datetime.utcnow()
        result = db[Medicine.collection].update_one(
            {"_id": ObjectId(medicine_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete_admin(medicine_id):
        """Delete medicine without user restriction (admin only)"""
        db = Database.get_db()
        result = db[Medicine.collection].delete_one({"_id": ObjectId(medicine_id)})
        return result.deleted_count > 0

    @staticmethod
    def get_all(limit=50, skip=0, query=None):
        """Get all medicines with pagination (admin only)"""
        db = Database.get_db()
        search_query = query if query else {}
        return list(
            db[Medicine.collection]
            .find(search_query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )

    @staticmethod
    def count(query=None):
        """Count medicines with optional query filter"""
        db = Database.get_db()
        search_query = query if query else {}
        return db[Medicine.collection].count_documents(search_query)

    @staticmethod
    def count_by_user(user_id):
        """Count medicines for a specific user"""
        db = Database.get_db()
        return db[Medicine.collection].count_documents({"user_id": ObjectId(user_id)})

from datetime import datetime
from bson import ObjectId
from app.database import Database


class ItalianMedicine:
    """Italian Medicine Database Model (from AIFA confezioni.csv)"""

    collection = "italian_medicines"

    @staticmethod
    def create(data):
        """Create new Italian medicine entry"""
        db = Database.get_db()
        medicine_data = {
            "codice_aic": data.get("codice_aic"),  # AIC code (unique)
            "cod_farmaco": data.get("cod_farmaco"),  # Drug code
            "cod_confezione": data.get("cod_confezione"),  # Package code
            "denominazione": data.get("denominazione"),  # Medicine name
            "descrizione": data.get("descrizione"),  # Description
            "codice_ditta": data.get("codice_ditta"),  # Company code
            "ragione_sociale": data.get("ragione_sociale"),  # Manufacturer
            "stato_amministrativo": data.get("stato_amministrativo"),  # Status
            "tipo_procedura": data.get("tipo_procedura"),  # Procedure type
            "forma": data.get("forma"),  # Form (tablet, capsule, etc.)
            "codice_atc": data.get("codice_atc"),  # ATC code
            "pa_associati": data.get("pa_associati"),  # Active ingredients
            "link": data.get("link", ""),  # Link
            "created_at": datetime.utcnow(),
        }
        result = db[ItalianMedicine.collection].insert_one(medicine_data)
        medicine_data["_id"] = result.inserted_id
        return medicine_data

    @staticmethod
    def bulk_create(medicines_list):
        """Bulk insert Italian medicines"""
        db = Database.get_db()
        if medicines_list:
            result = db[ItalianMedicine.collection].insert_many(medicines_list)
            return len(result.inserted_ids)
        return 0

    @staticmethod
    def find_by_aic(codice_aic):
        """Find Italian medicine by AIC code"""
        db = Database.get_db()
        return db[ItalianMedicine.collection].find_one({"codice_aic": codice_aic})

    @staticmethod
    def search_by_name(name, limit=20):
        """Search Italian medicines by name"""
        db = Database.get_db()
        regex_pattern = {"$regex": name, "$options": "i"}
        return list(
            db[ItalianMedicine.collection]
            .find({"denominazione": regex_pattern})
            .limit(limit)
        )

    @staticmethod
    def search_by_manufacturer(manufacturer, limit=20):
        """Search Italian medicines by manufacturer"""
        db = Database.get_db()
        regex_pattern = {"$regex": manufacturer, "$options": "i"}
        return list(
            db[ItalianMedicine.collection]
            .find({"ragione_sociale": regex_pattern})
            .limit(limit)
        )

    @staticmethod
    def search_by_active_ingredient(ingredient, limit=20):
        """Search Italian medicines by active ingredient"""
        db = Database.get_db()
        regex_pattern = {"$regex": ingredient, "$options": "i"}
        return list(
            db[ItalianMedicine.collection]
            .find({"pa_associati": regex_pattern})
            .limit(limit)
        )

    @staticmethod
    def get_all(limit=100, skip=0):
        """Get all Italian medicines with pagination"""
        db = Database.get_db()
        return list(
            db[ItalianMedicine.collection].find().skip(skip).limit(limit)
        )

    @staticmethod
    def count():
        """Count total Italian medicines"""
        db = Database.get_db()
        return db[ItalianMedicine.collection].count_documents({})

    @staticmethod
    def delete_all():
        """Delete all Italian medicines (for re-import)"""
        db = Database.get_db()
        result = db[ItalianMedicine.collection].delete_many({})
        return result.deleted_count

    @staticmethod
    def find_by_id(medicine_id):
        """Find Italian medicine by ID"""
        db = Database.get_db()
        return db[ItalianMedicine.collection].find_one({"_id": ObjectId(medicine_id)})

    @staticmethod
    def update(medicine_id, data):
        """Update Italian medicine"""
        db = Database.get_db()
        result = db[ItalianMedicine.collection].update_one(
            {"_id": ObjectId(medicine_id)}, {"$set": data}
        )
        return result.modified_count > 0

    @staticmethod
    def delete(medicine_id):
        """Delete Italian medicine"""
        db = Database.get_db()
        result = db[ItalianMedicine.collection].delete_one({"_id": ObjectId(medicine_id)})
        return result.deleted_count > 0

    @staticmethod
    def search_advanced(query=None, limit=50, skip=0):
        """Advanced search with multiple filters"""
        db = Database.get_db()
        search_query = query if query else {}
        return list(
            db[ItalianMedicine.collection]
            .find(search_query)
            .skip(skip)
            .limit(limit)
        )

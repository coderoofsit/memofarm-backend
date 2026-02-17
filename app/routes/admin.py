from flask import Blueprint, request
from datetime import datetime
from app.models.user import User
from app.models.medicine import Medicine
from app.models.italian_medicine import ItalianMedicine
from app.utils.auth import create_response, serialize_doc
from bson import ObjectId

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Simple admin authentication - In production, use environment variable
import os
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "memofarm_admin_2026_secure_key")


def admin_required(f):
    """Decorator to protect admin routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-Admin-Key")
        
        if not api_key or api_key != ADMIN_API_KEY:
            return create_response(message="Unauthorized: Invalid admin credentials", status=401)
        
        return f(*args, **kwargs)
    
    return decorated


# ==================== USER MANAGEMENT ====================

@admin_bp.route("/users", methods=["GET"])
@admin_required
def get_all_users():
    """
    Get all users with pagination and filtering
    GET /api/admin/users?limit=50&skip=0&status=active&search=email
    """
    try:
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        status = request.args.get("status")  # active, paused, all
        search = request.args.get("search", "").strip()
        
        # Build query
        query = {}
        if status == "active":
            query["status"] = {"$ne": "paused"}
        elif status == "paused":
            query["status"] = "paused"
        
        if search:
            # Search by email or name
            query["$or"] = [
                {"email": {"$regex": search, "$options": "i"}},
                {"name": {"$regex": search, "$options": "i"}}
            ]
        
        users = User.get_all(limit=limit, skip=skip, query=query)
        total_count = User.count(query=query)
        
        # Get medicine count for each user
        for user in users:
            user_id = str(user.get("_id"))
            user["medicine_count"] = Medicine.count_by_user(user_id)
        
        return create_response(
            data={
                "users": serialize_doc(users),
                "total": total_count,
                "limit": limit,
                "skip": skip
            },
            status=200
        )
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/users/<user_id>", methods=["GET"])
@admin_required
def get_user_details(user_id):
    """
    Get detailed user information including their medicines
    GET /api/admin/users/<user_id>
    """
    try:
        user = User.find_by_id(user_id)
        if not user:
            return create_response(message="User not found", status=404)
        
        # Get user's medicines
        medicines = Medicine.find_by_user(user_id)
        
        user_data = serialize_doc(user)
        user_data["medicines"] = serialize_doc(medicines)
        user_data["medicine_count"] = len(medicines)
        
        return create_response(data=user_data, status=200)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/users/<user_id>/pause", methods=["PUT"])
@admin_required
def pause_user(user_id):
    """
    Pause/Suspend a user account
    PUT /api/admin/users/<user_id>/pause
    Body: {"paused": true, "reason": "Violation of terms"}
    """
    try:
        data = request.get_json() or {}
        paused = data.get("paused", True)
        reason = data.get("reason", "")
        
        update_data = {
            "status": "paused" if paused else "active",
            "paused_at": datetime.utcnow() if paused else None,
            "pause_reason": reason if paused else None,
            "updated_at": datetime.utcnow()
        }
        
        success = User.update(user_id, update_data)
        
        if success:
            user = User.find_by_id(user_id)
            return create_response(
                data=serialize_doc(user),
                message=f"User {'paused' if paused else 'activated'} successfully",
                status=200
            )
        else:
            return create_response(message="User not found", status=404)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/users/<user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    """
    Delete a user and all their medicines
    DELETE /api/admin/users/<user_id>
    """
    try:
        # Delete all user's medicines first
        Medicine.delete_all_by_user(user_id)
        
        # Delete user
        success = User.delete(user_id)
        
        if success:
            return create_response(
                message="User and all associated data deleted successfully",
                status=200
            )
        else:
            return create_response(message="User not found", status=404)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


# ==================== MEDICINE MANAGEMENT ====================

@admin_bp.route("/medicines", methods=["GET"])
@admin_required
def get_all_medicines():
    """
    Get all medicines across all users
    GET /api/admin/medicines?limit=50&skip=0&category=Antibiotics&expired=true&user_id=xxx
    """
    try:
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        category = request.args.get("category")
        expired = request.args.get("expired")
        user_id = request.args.get("user_id")
        search = request.args.get("search", "").strip()
        
        # Build query
        query = {}
        if category:
            query["category"] = category
        if expired == "true":
            query["expiry_date"] = {"$lt": datetime.utcnow()}
        elif expired == "false":
            query["expiry_date"] = {"$gte": datetime.utcnow()}
        if user_id:
            query["user_id"] = ObjectId(user_id)
        if search:
            query["name"] = {"$regex": search, "$options": "i"}
        
        medicines = Medicine.get_all(limit=limit, skip=skip, query=query)
        total_count = Medicine.count(query=query)
        
        # Populate user info for each medicine
        for medicine in medicines:
            user_id = medicine.get("user_id")
            if user_id:
                user = User.find_by_id(str(user_id))
                medicine["user_email"] = user.get("email") if user else None
        
        return create_response(
            data={
                "medicines": serialize_doc(medicines),
                "total": total_count,
                "limit": limit,
                "skip": skip
            },
            status=200
        )
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/medicines/<medicine_id>", methods=["GET"])
@admin_required
def get_medicine_details(medicine_id):
    """
    Get medicine details without user restriction
    GET /api/admin/medicines/<medicine_id>
    """
    try:
        medicine = Medicine.find_by_id_admin(medicine_id)
        
        if not medicine:
            return create_response(message="Medicine not found", status=404)
        
        # Get user info
        user_id = medicine.get("user_id")
        if user_id:
            user = User.find_by_id(str(user_id))
            medicine["user"] = serialize_doc(user) if user else None
        
        return create_response(data=serialize_doc(medicine), status=200)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/medicines", methods=["POST"])
@admin_required
def create_medicine_admin():
    """
    Create a medicine for a specific user
    POST /api/admin/medicines
    Body: {user_id, name, category, quantity, expiry_date, ...}
    """
    try:
        data = request.get_json()
        
        if not data.get("user_id"):
            return create_response(message="user_id is required", status=400)
        if not data.get("name"):
            return create_response(message="Medicine name is required", status=400)
        
        user_id = data.pop("user_id")
        
        # Verify user exists
        user = User.find_by_id(user_id)
        if not user:
            return create_response(message="User not found", status=404)
        
        # Parse expiry date if provided
        if "expiry_date" in data and isinstance(data["expiry_date"], str):
            try:
                data["expiry_date"] = datetime.fromisoformat(
                    data["expiry_date"].replace("Z", "+00:00")
                )
            except:
                return create_response(message="Invalid expiry date format", status=400)
        
        medicine = Medicine.create(user_id, data)
        
        return create_response(
            data=serialize_doc(medicine),
            message="Medicine created successfully",
            status=201
        )
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/medicines/<medicine_id>", methods=["PUT"])
@admin_required
def update_medicine_admin(medicine_id):
    """
    Update any medicine without user restriction
    PUT /api/admin/medicines/<medicine_id>
    Body: {name, quantity, category, ...}
    """
    try:
        data = request.get_json()
        
        # Parse expiry date if provided
        if "expiry_date" in data and isinstance(data["expiry_date"], str):
            try:
                data["expiry_date"] = datetime.fromisoformat(
                    data["expiry_date"].replace("Z", "+00:00")
                )
            except:
                return create_response(message="Invalid expiry date format", status=400)
        
        success = Medicine.update_admin(medicine_id, data)
        
        if success:
            medicine = Medicine.find_by_id_admin(medicine_id)
            return create_response(
                data=serialize_doc(medicine),
                message="Medicine updated successfully",
                status=200
            )
        else:
            return create_response(message="Medicine not found", status=404)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/medicines/<medicine_id>", methods=["DELETE"])
@admin_required
def delete_medicine_admin(medicine_id):
    """
    Delete any medicine without user restriction
    DELETE /api/admin/medicines/<medicine_id>
    """
    try:
        success = Medicine.delete_admin(medicine_id)
        
        if success:
            return create_response(
                message="Medicine deleted successfully",
                status=200
            )
        else:
            return create_response(message="Medicine not found", status=404)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


# ==================== STATISTICS ====================

@admin_bp.route("/stats", methods=["GET"])
@admin_required
def get_admin_stats():
    """
    Get overall system statistics
    GET /api/admin/stats
    """
    try:
        total_users = User.count()
        active_users = User.count(query={"status": {"$ne": "paused"}})
        paused_users = User.count(query={"status": "paused"})
        
        total_medicines = Medicine.count()
        expired_medicines = Medicine.count(query={"expiry_date": {"$lt": datetime.utcnow()}})
        
        # Get medicines by category
        from app.database import Database
        db = Database.get_db()
        
        category_stats = list(db.medicines.aggregate([
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]))
        
        return create_response(
            data={
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "paused": paused_users
                },
                "medicines": {
                    "total": total_medicines,
                    "expired": expired_medicines,
                    "by_category": category_stats
                },
                "italian_medicines": {
                    "total": ItalianMedicine.count()
                }
            },
            status=200
        )
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


# ==================== ITALIAN MEDICINES DATABASE MANAGEMENT ====================

@admin_bp.route("/italian-medicines", methods=["GET"])
@admin_required
def get_italian_medicines():
    """
    Get Italian medicines database with advanced filtering
    GET /api/admin/italian-medicines?limit=50&skip=0&search=aspirina&manufacturer=bayer&aic=027912010
    """
    try:
        limit = int(request.args.get("limit", 50))
        skip = int(request.args.get("skip", 0))
        search = request.args.get("search", "").strip()
        manufacturer = request.args.get("manufacturer", "").strip()
        aic_code = request.args.get("aic", "").strip()
        
        # Build query
        query = {}
        if search:
            query["denominazione"] = {"$regex": search, "$options": "i"}
        if manufacturer:
            query["ragione_sociale"] = {"$regex": manufacturer, "$options": "i"}
        if aic_code:
            query["codice_aic"] = aic_code
        
        medicines = ItalianMedicine.search_advanced(query=query, limit=limit, skip=skip)
        total_count = ItalianMedicine.count() if not query else len(medicines)
        
        return create_response(
            data={
                "medicines": serialize_doc(medicines),
                "total": total_count,
                "limit": limit,
                "skip": skip
            },
            status=200
        )
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/italian-medicines/<medicine_id>", methods=["GET"])
@admin_required
def get_italian_medicine(medicine_id):
    """
    Get single Italian medicine details
    GET /api/admin/italian-medicines/<medicine_id>
    """
    try:
        medicine = ItalianMedicine.find_by_id(medicine_id)
        
        if not medicine:
            return create_response(message="Italian medicine not found", status=404)
        
        return create_response(data=serialize_doc(medicine), status=200)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/italian-medicines", methods=["POST"])
@admin_required
def create_italian_medicine():
    """
    Create new Italian medicine in database
    POST /api/admin/italian-medicines
    Body: {codice_aic, denominazione, ragione_sociale, forma, pa_associati, ...}
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get("codice_aic"):
            return create_response(message="codice_aic is required", status=400)
        if not data.get("denominazione"):
            return create_response(message="denominazione (medicine name) is required", status=400)
        
        # Check if AIC code already exists
        existing = ItalianMedicine.find_by_aic(data["codice_aic"])
        if existing:
            return create_response(
                message=f"Medicine with AIC code {data['codice_aic']} already exists",
                status=400
            )
        
        medicine = ItalianMedicine.create(data)
        
        return create_response(
            data=serialize_doc(medicine),
            message="Italian medicine created successfully",
            status=201
        )
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/italian-medicines/<medicine_id>", methods=["PUT"])
@admin_required
def update_italian_medicine(medicine_id):
    """
    Update Italian medicine in database
    PUT /api/admin/italian-medicines/<medicine_id>
    Body: {denominazione, ragione_sociale, forma, ...}
    """
    try:
        data = request.get_json()
        
        # Remove fields that shouldn't be updated
        data.pop("_id", None)
        data.pop("created_at", None)
        
        success = ItalianMedicine.update(medicine_id, data)
        
        if success:
            medicine = ItalianMedicine.find_by_id(medicine_id)
            return create_response(
                data=serialize_doc(medicine),
                message="Italian medicine updated successfully",
                status=200
            )
        else:
            return create_response(message="Italian medicine not found", status=404)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/italian-medicines/<medicine_id>", methods=["DELETE"])
@admin_required
def delete_italian_medicine(medicine_id):
    """
    Delete Italian medicine from database
    DELETE /api/admin/italian-medicines/<medicine_id>
    """
    try:
        success = ItalianMedicine.delete(medicine_id)
        
        if success:
            return create_response(
                message="Italian medicine deleted successfully",
                status=200
            )
        else:
            return create_response(message="Italian medicine not found", status=404)
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@admin_bp.route("/italian-medicines/bulk-delete", methods=["POST"])
@admin_required
def bulk_delete_italian_medicines():
    """
    Bulk delete Italian medicines
    POST /api/admin/italian-medicines/bulk-delete
    Body: {ids: ["id1", "id2", ...]}
    """
    try:
        data = request.get_json()
        ids = data.get("ids", [])
        
        if not ids:
            return create_response(message="No IDs provided", status=400)
        
        from app.database import Database
        db = Database.get_db()
        
        object_ids = [ObjectId(id) for id in ids]
        result = db[ItalianMedicine.collection].delete_many({"_id": {"$in": object_ids}})
        
        return create_response(
            data={"deleted_count": result.deleted_count},
            message=f"Successfully deleted {result.deleted_count} medicines",
            status=200
        )
    
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)

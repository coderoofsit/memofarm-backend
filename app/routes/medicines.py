from flask import Blueprint, request
from datetime import datetime
from app.models.medicine import Medicine
from app.utils.auth import token_required, create_response, serialize_doc

medicines_bp = Blueprint("medicines", __name__, url_prefix="/medicines")


@medicines_bp.route("", methods=["GET"])
@token_required
def get_medicines():
    """Get all medicines for the authenticated user"""
    try:
        user = request.current_user
        user_id = str(user["_id"])

        # Get query parameters for filtering
        category = request.args.get("category")
        expired = request.args.get("expired") == "true"

        filters = {}
        if category:
            filters["category"] = category
        if expired:
            filters["expired"] = True

        medicines = Medicine.find_by_user(user_id, filters)
        return create_response(data=serialize_doc(medicines), status=200)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@medicines_bp.route("", methods=["POST"])
@token_required
def create_medicine():
    """Create new medicine"""
    try:
        user = request.current_user
        user_id = str(user["_id"])
        data = request.get_json()

        # Parse expiry date if provided as string
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
            message="Medicine added successfully",
            status=201,
        )

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@medicines_bp.route("/<medicine_id>", methods=["GET"])
@token_required
def get_medicine(medicine_id):
    """Get medicine by ID"""
    try:
        user = request.current_user
        user_id = str(user["_id"])

        medicine = Medicine.find_by_id(medicine_id, user_id)
        if not medicine:
            return create_response(message="Medicine not found", status=404)

        return create_response(data=serialize_doc(medicine), status=200)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@medicines_bp.route("/<medicine_id>", methods=["PUT"])
@token_required
def update_medicine(medicine_id):
    """Update medicine"""
    try:
        user = request.current_user
        user_id = str(user["_id"])
        data = request.get_json()

        # Parse expiry date if provided as string
        if "expiry_date" in data and isinstance(data["expiry_date"], str):
            try:
                data["expiry_date"] = datetime.fromisoformat(
                    data["expiry_date"].replace("Z", "+00:00")
                )
            except:
                return create_response(message="Invalid expiry date format", status=400)

        success = Medicine.update(medicine_id, user_id, data)
        if success:
            updated_medicine = Medicine.find_by_id(medicine_id, user_id)
            return create_response(
                data=serialize_doc(updated_medicine),
                message="Medicine updated successfully",
                status=200,
            )
        else:
            return create_response(message="Medicine not found", status=404)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@medicines_bp.route("/<medicine_id>", methods=["DELETE"])
@token_required
def delete_medicine(medicine_id):
    """Delete medicine"""
    try:
        user = request.current_user
        user_id = str(user["_id"])

        success = Medicine.delete(medicine_id, user_id)
        if success:
            return create_response(message="Medicine deleted successfully", status=200)
        else:
            return create_response(message="Medicine not found", status=404)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@medicines_bp.route("/barcode/<barcode>", methods=["GET"])
@token_required
def get_medicine_by_barcode(barcode):
    """Get medicine by barcode"""
    try:
        user = request.current_user
        user_id = str(user["_id"])

        medicine = Medicine.find_by_barcode(barcode, user_id)
        if not medicine:
            return create_response(message="Medicine not found", status=404)

        return create_response(data=serialize_doc(medicine), status=200)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@medicines_bp.route("/aic/<aic_code>", methods=["GET"])
@token_required
def get_medicine_by_aic(aic_code):
    """Get medicine by AIC code"""
    try:
        user = request.current_user
        user_id = str(user["_id"])

        medicine = Medicine.find_by_aic(aic_code, user_id)
        if not medicine:
            return create_response(message="Medicine not found", status=404)

        return create_response(data=serialize_doc(medicine), status=200)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@medicines_bp.route("/expiring", methods=["GET"])
@token_required
def get_expiring_medicines():
    """Get medicines expiring soon"""
    try:
        user = request.current_user
        user_id = str(user["_id"])

        days = request.args.get("days", 30, type=int)
        medicines = Medicine.get_expiring_soon(user_id, days)

        return create_response(data=serialize_doc(medicines), status=200)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)

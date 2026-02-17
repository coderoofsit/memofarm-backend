from flask import Blueprint, request
from app.models.user import User
from app.models.medicine import Medicine
from app.utils.auth import token_required, create_response, serialize_doc

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    """Get user profile"""
    try:
        user = request.current_user
        return create_response(data=serialize_doc(user), status=200)
    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@users_bp.route("/profile", methods=["PUT"])
@token_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user = request.current_user
        user_id = str(user["_id"])

        # Only allow updating specific fields
        allowed_fields = ["name"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if not update_data:
            return create_response(message="No valid fields to update", status=400)

        success = User.update(user_id, update_data)

        if success:
            updated_user = User.find_by_id(user_id)
            return create_response(
                data=serialize_doc(updated_user),
                message="Profile updated successfully",
                status=200,
            )
        else:
            return create_response(message="Failed to update profile", status=500)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)


@users_bp.route("/account", methods=["DELETE"])
@token_required
def delete_account():
    """Delete user account and all associated data"""
    try:
        user = request.current_user
        user_id = str(user["_id"])

        # Delete all user's medicines first
        Medicine.delete_all_by_user(user_id)

        # Delete user account
        success = User.delete(user_id)

        if success:
            return create_response(message="Account deleted successfully", status=200)
        else:
            return create_response(message="Failed to delete account", status=500)

    except Exception as e:
        return create_response(message=f"Error: {str(e)}", status=500)

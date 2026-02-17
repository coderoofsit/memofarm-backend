from flask import Blueprint, request
from app.models.user import User
from app.utils.auth import create_response, serialize_doc, token_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/google", methods=["POST"])
def google_login():
    """
    Google OAuth login - Sync user after Firebase authentication
    Expects: { "firebase_uid": "...", "email": "...", "name": "..." }
    """
    try:
        data = request.get_json()
        firebase_uid = data.get("firebase_uid")
        email = data.get("email")

        if not firebase_uid:
            return create_response(message="Firebase UID is required", status=400)

        # Check if user exists
        user = User.find_by_firebase_uid(firebase_uid)

        if not user:
            # Create new user
            user_data = {
                "firebase_uid": firebase_uid,
                "email": email,
                "name": data.get("name", email.split("@")[0] if email else "User"),
                "provider": "google",
            }
            user = User.create(user_data)
            print(f"✅ Created new user: {email}")
        else:
            # Update existing user info
            update_data = {
                "name": data.get("name", user.get("name")),
            }
            User.update(str(user["_id"]), update_data)
            user = User.find_by_firebase_uid(firebase_uid)
            print(f"✅ Updated existing user: {email}")

        return create_response(
            data={"user": serialize_doc(user)}, 
            message="Login successful", 
            status=200
        )

    except Exception as e:
        print(f"❌ Google login error: {str(e)}")
        return create_response(message=f"Login failed: {str(e)}", status=500)


@auth_bp.route("/apple", methods=["POST"])
def apple_login():
    """
    Apple Sign In login - Sync user after Firebase authentication
    Expects: { "firebase_uid": "...", "email": "...", "name": "..." }
    """
    try:
        data = request.get_json()
        firebase_uid = data.get("firebase_uid")
        email = data.get("email")

        if not firebase_uid:
            return create_response(message="Firebase UID is required", status=400)

        # Check if user exists
        user = User.find_by_firebase_uid(firebase_uid)

        if not user:
            # Create new user
            user_data = {
                "firebase_uid": firebase_uid,
                "email": email or "",
                "name": data.get("name", "Apple User"),
                "provider": "apple",
            }
            user = User.create(user_data)
            print(f"✅ Created new Apple user: {email or firebase_uid}")
        else:
            # Update existing user info
            update_data = {}
            if data.get("name"):
                update_data["name"] = data.get("name")
            
            if update_data:
                User.update(str(user["_id"]), update_data)
                user = User.find_by_firebase_uid(firebase_uid)
            print(f"✅ Updated existing Apple user: {email or firebase_uid}")

        return create_response(
            data={"user": serialize_doc(user)}, 
            message="Login successful", 
            status=200
        )

    except Exception as e:
        print(f"❌ Apple login error: {str(e)}")
        return create_response(message=f"Login failed: {str(e)}", status=500)


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():
    """Get current authenticated user"""
    try:
        user = request.current_user
        
        if not user:
            return create_response(message="User not found", status=404)
            
        return create_response(data={"user": serialize_doc(user)}, status=200)
    except Exception as e:
        print(f"❌ Get user error: {str(e)}")
        return create_response(message=f"Error: {str(e)}", status=500)

import jwt
import os
from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User

# Try to import Firebase Admin SDK
try:
    import firebase_admin
    from firebase_admin import auth, credentials
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("⚠️ Firebase Admin SDK not installed. Using development mode.")

# Initialize Firebase Admin SDK if credentials file exists
FIREBASE_INITIALIZED = False
if FIREBASE_AVAILABLE:
    credential_paths = [
        "serviceAccountKey.json",
        "backend/serviceAccountKey.json",
        os.path.join(os.path.dirname(__file__), "..", "..", "serviceAccountKey.json"),
    ]
    
    for cred_path in credential_paths:
        if os.path.exists(cred_path):
            try:
                if not firebase_admin._apps:
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    FIREBASE_INITIALIZED = True
                    print(f"✅ Firebase Admin SDK initialized with credentials from {cred_path}")
                break
            except Exception as e:
                print(f"❌ Failed to initialize Firebase Admin SDK: {e}")
    
    if not FIREBASE_INITIALIZED:
        print("⚠️ Firebase service account key not found. Using development mode.")
        print("   To enable full Firebase verification, add serviceAccountKey.json")


def verify_firebase_token(id_token):
    """Verify Firebase ID token"""
    try:
        # Try using Firebase Admin SDK if available and initialized
        if FIREBASE_AVAILABLE and FIREBASE_INITIALIZED:
            decoded_token = auth.verify_id_token(id_token)
            print(f"✅ Token verified via Firebase Admin SDK for user: {decoded_token.get('uid')}")
            return decoded_token
        
        # Fallback: Decode JWT without verification (DEVELOPMENT ONLY)
        # This extracts user info but doesn't verify the signature
        print("⚠️ Using development mode: decoding token without verification")
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        print(f"ℹ️ Token decoded for user: {decoded_token.get('user_id') or decoded_token.get('uid')}")
        return decoded_token
        
    except Exception as e:
        print(f"❌ Token verification error: {e}")
        return None


def token_required(f):
    """Decorator to protect routes with authentication"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401

        try:
            # Verify Firebase token
            payload = verify_firebase_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401

            # Extract user ID (Firebase tokens use "uid")
            user_id = payload.get("uid") or payload.get("user_id")
            if not user_id:
                print(f"❌ No user ID in token payload: {payload.keys()}")
                return jsonify({"error": "Invalid token: missing user ID"}), 401

            # Get user from database
            user = User.find_by_firebase_uid(user_id)
            if not user:
                print(f"⚠️ User not found in database for uid: {user_id}")
                return jsonify({"error": "User not found"}), 404

            # Add user to request context
            request.current_user = user
            print(f"✅ Authenticated request for user: {user.get('email')}")

        except Exception as e:
            print(f"❌ Token verification failed: {str(e)}")
            return jsonify({"error": f"Token verification failed: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated


def create_response(data=None, message=None, status=200):
    """Create standardized JSON response"""
    response = {}

    if message:
        response["message"] = message

    if data is not None:
        response["data"] = data

    return jsonify(response), status


def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None

    if isinstance(doc, list):
        return [serialize_doc(d) for d in doc]

    if "_id" in doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]

    if "user_id" in doc:
        doc["user_id"] = str(doc["user_id"])

    # Convert datetime objects to ISO format
    for key, value in doc.items():
        if hasattr(value, "isoformat"):
            doc[key] = value.isoformat()

    return doc

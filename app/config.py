import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb+srv://coderoofitsolutions:9yg700rXeFfcS6op@eventdating.phubh6n.mongodb.net/memofarm")
    DB_NAME = os.getenv("DB_NAME", "memofarm")

    # Google OAuth
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

    # Apple Sign In
    APPLE_CLIENT_ID = os.getenv("APPLE_CLIENT_ID")
    APPLE_TEAM_ID = os.getenv("APPLE_TEAM_ID")
    APPLE_KEY_ID = os.getenv("APPLE_KEY_ID")

    # Firebase
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

    # API
    API_PREFIX = os.getenv("API_PREFIX", "/api")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    FLASK_ENV = "production"


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}

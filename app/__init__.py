from flask import Flask
from flask_cors import CORS
from app.config import config
from app.database import Database


def create_app(config_name="development"):
    """Create and configure Flask application"""

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Enable CORS
    CORS(app, origins=app.config["CORS_ORIGINS"])

    # Initialize database
    Database.initialize(app)

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.users import users_bp
    from app.routes.medicines import medicines_bp
    from app.routes.italian_medicines import italian_medicines_bp
    from app.routes.admin import admin_bp

    api_prefix = app.config["API_PREFIX"]
    app.register_blueprint(auth_bp, url_prefix=f"{api_prefix}/auth")
    app.register_blueprint(users_bp, url_prefix=f"{api_prefix}/users")
    app.register_blueprint(medicines_bp, url_prefix=f"{api_prefix}/medicines")
    app.register_blueprint(italian_medicines_bp, url_prefix=f"{api_prefix}/italian-medicines")
    app.register_blueprint(admin_bp, url_prefix=f"{api_prefix}/admin")

    # Health check endpoint
    @app.route("/health", methods=["GET"])
    def health_check():
        return {"status": "ok", "message": "Memofarm API is running"}, 200

    # Root endpoint
    @app.route("/", methods=["GET"])
    def root():
        return {
            "message": "Memofarm API",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "auth": f"{api_prefix}/auth",
                "users": f"{api_prefix}/users",
                "medicines": f"{api_prefix}/medicines",
                "italian_medicines": f"{api_prefix}/italian-medicines",
                "admin": f"{api_prefix}/admin",
            },
        }, 200

    return app

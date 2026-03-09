import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SUPABASE_URL"] = os.environ.get("SUPABASE_URL", "")
    app.config["SUPABASE_ANON_KEY"] = os.environ.get("SUPABASE_ANON_KEY", "")
    app.config["SUPABASE_SERVICE_ROLE_KEY"] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    app.config["SUPABASE_JWT_SECRET"] = os.environ.get("SUPABASE_JWT_SECRET", "")

    CORS(app, origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ])

    from authentication import bp as auth_bp
    from routes import bp as routes_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(routes_bp, url_prefix="/api")

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG", "0") == "1")

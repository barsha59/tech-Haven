# app.py - TechHaven (Updated)
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os

# Initialize Flask
app = Flask(__name__)
CORS(app)

# ---------------- DATABASE CONFIG ----------------
database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Remove SSL parameter (Aiven handles SSL automatically)
    if "?ssl-mode=REQUIRED" in database_url:
        database_url = database_url.replace("?ssl-mode=REQUIRED", "")

    # Use mysqlclient driver for MySQL
    if database_url.startswith("mysql://"):
        database_url = database_url.replace("mysql://", "mysql+mysqldb://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print("✅ Using Aiven MySQL database")
else:
    # Local SQLite fallback
    sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "local.db")
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)  # Ensure folder exists
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
    print(f"⚠️ Using SQLite (local): {sqlite_path}")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---------------- INIT DB ----------------
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database error: {str(e)[:100]}")

# ---------------- REGISTER ROUTES ----------------
app.register_blueprint(routes_bp)

# ---------------- HEALTH CHECK ----------------
@app.route("/")
def home():
    return {"message": "TechHaven API Running"}

@app.route("/health")
def health_check():
    return {"status": "ready", "service": "TechHaven"}

# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting TechHaven on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)

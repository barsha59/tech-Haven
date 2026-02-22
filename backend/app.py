# app.py - TechHaven (Cleaned)
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os

# ---------------- INITIALIZE FLASK ----------------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ---------------- DATABASE CONFIG ----------------
# Point directly to your SQLite database
sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instance", "database.db")
if not os.path.exists(sqlite_path):
    raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
print(f"✅ Using SQLite database: {sqlite_path}")

# ---------------- INIT DB ----------------
db.init_app(app)

with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables ensured")
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
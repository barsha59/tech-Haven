# app.py - TechHaven (Clean MySQL Version)
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os

app = Flask(__name__)
CORS(app)

# ---- CLEAN DATABASE CONFIG ----
database_url = os.environ.get('DATABASE_URL')

if database_url and ('mysql://' in database_url or 'postgresql://' in database_url):
    # Use whatever database URL is provided
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print(f"✅ Using external database")
else:
    # Fallback to SQLite for local development
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, "instance")
    os.makedirs(instance_path, exist_ok=True)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(instance_path, "database.db")
    )
    print("⚠️ Using SQLite database (local development)")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---- INIT DB ----
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()
    print("✅ Database tables created")

# ---- REGISTER ROUTES ----
app.register_blueprint(routes_bp)

@app.route("/")
def home():
    return {"message": "TechHaven Electronics API Running"}

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ready", "service": "TechHaven"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
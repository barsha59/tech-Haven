# app.py - TechHaven (Aiven MySQL Ready)
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os

app = Flask(__name__)
CORS(app)

# ---- DATABASE CONFIGURATION FOR AIVEN MYSQL ----
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Aiven MySQL: mysql:// → mysql+pymysql:// (REQUIRED)
    if database_url.startswith('mysql://'):
        database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print("✅ Using Aiven MySQL database (pymysql driver)")
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
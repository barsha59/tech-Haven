# app.py - TechHaven (Fixed Aiven MySQL Version)
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
    # Remove SSL parameter entirely (Aiven handles it automatically)
    if '?ssl-mode=REQUIRED' in database_url:
        database_url = database_url.replace('?ssl-mode=REQUIRED', '')
    
    # Use mysqlclient driver (better for Aiven)
    if database_url.startswith('mysql://'):
        database_url = database_url.replace('mysql://', 'mysql+mysqldb://', 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print("✅ Using Aiven MySQL database (mysqlclient)")
else:
    # Fallback to SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///local.db"
    print("⚠️ Using SQLite (local)")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---- INIT DB ----
db.init_app(app)

# Create tables with error handling
with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables created")
    except Exception as e:
        print(f"⚠️ Database error (continuing anyway): {str(e)[:100]}")
        # Continue even if database fails

# ---- REGISTER ROUTES ----
app.register_blueprint(routes_bp)

@app.route("/")
def home():
    return {"message": "TechHaven Electronics API Running - Aiven MySQL"}

@app.route("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ready", "service": "TechHaven"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Starting TechHaven on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
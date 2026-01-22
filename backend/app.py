from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os
import models  # 👈 IMPORTANT: ensures models are registered
import threading
import time

app = Flask(__name__)
CORS(app)

# ---- DATABASE SETUP WITH SSL ----
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Ensure SSL parameters are included
    if 'sslmode' not in database_url:
        if '?' in database_url:
            database_url += '&sslmode=require'
        else:
            database_url += '?sslmode=require'
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    
    # CRITICAL: Engine options for Render + Supabase
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_timeout": 30,
        "max_overflow": 10,
        "connect_args": {
            "connect_timeout": 30,
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "sslmode": "require",
            "sslrootcert": "/etc/ssl/certs/ca-certificates.crt",  # Render has this
        }
    }
    
    print(f"✅ Using PostgreSQL with SSL")
else:
    # Fallback for local development only
    basedir = os.path.abspath(os.path.dirname(__file__))
    instance_path = os.path.join(basedir, "instance")
    os.makedirs(instance_path, exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + os.path.join(instance_path, "database.db")
    )
    print("⚠️ Using SQLite (local development)")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ---- INIT DB ----
db.init_app(app)

# ---- DEFER DATABASE CREATION ----
def init_database():
    """Initialize database with error handling"""
    with app.app_context():
        try:
            print("🔄 Attempting database connection...")
            
            # Simple test query first
            from sqlalchemy import text
            connection = db.engine.connect()
            result = connection.execute(text("SELECT version()"))
            db_version = result.fetchone()[0]
            print(f"✅ Database connected: {db_version[:50]}...")
            connection.close()
            
            # Create tables
            db.create_all()
            print("✅ Database tables created")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {str(e)[:100]}")
            print("⚠️ Application will run in limited mode")

# Remove the immediate db.create_all() call - we'll do it delayed
# ---- REGISTER ROUTES ----
app.register_blueprint(routes_bp)

@app.route("/")
def home():
    return {"message": "Demo Shopping Website 1 API Running"}

@app.route("/health")
def health():
    """Simple health check"""
    return {"status": "ok", "database": "checking..."}

# ---- DELAYED DATABASE INITIALIZATION ----
def delayed_init():
    time.sleep(3)  # Wait for app to fully start
    init_database()

# Start database init in background
init_thread = threading.Thread(target=delayed_init, daemon=True)

# app.py - ADD/UPDATE THIS SECTION AT THE BOTTOM
if __name__ == "__main__":
    # Start database initialization
    init_thread.start()
    
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT environment variable
    app.run(host="0.0.0.0", port=port)
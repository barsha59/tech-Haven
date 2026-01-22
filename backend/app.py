# app.py - TechHaven Electronics Store (Working Version)
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os

app = Flask(__name__)
CORS(app)

# ---- DATABASE CONFIGURATION FOR SUPABASE ----
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Ensure SSL for Supabase
    if 'sslmode=require' not in database_url:
        if '?' in database_url:
            database_url += '&sslmode=require'
        else:
            database_url += '?sslmode=require'
    
    # Use psycopg2 driver (you already have this in requirements.txt)
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://', 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print("✅ Using Supabase PostgreSQL with SSL (psycopg2)")
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tech-haven-secret-key')

# ---- INIT DB ----
db.init_app(app)

# Create tables only - NO PRODUCT POPULATION
with app.app_context():
    db.create_all()
    print("✅ Database tables created for TechHaven")

# ---- REGISTER ROUTES ----
app.register_blueprint(routes_bp)

@app.route("/")
def home():
    return {"message": "TechHaven Electronics API Running - Supabase Edition"}

@app.route("/health")
def health_check():
    """Health check endpoint for monitoring"""
    from models import Product
    try:
        product_count = Product.query.count()
        return {
            "status": "healthy",
            "service": "TechHaven API",
            "product_count": product_count,
            "database": "Supabase PostgreSQL" if os.environ.get('DATABASE_URL') else "SQLite"
        }
    except:
        return {"status": "database_error"}, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
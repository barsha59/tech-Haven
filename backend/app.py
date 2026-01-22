# app.py - ONLY REPLACE LINES 11-22
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os
import models  # 👈 IMPORTANT: ensures models are registered

app = Flask(__name__)
CORS(app)

# ---- DATABASE SETUP ----
import os

# Get database URL from environment (from Supabase via Render)
database_url = os.environ.get('DATABASE_URL')

if database_url:
    # Use PostgreSQL from Supabase
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print("✅ Using PostgreSQL (Supabase)")
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

# 🔥 CREATE TABLES HERE (THIS WAS MISSING)
with app.app_context():
    db.create_all()
    print("✅ Database & tables created")

# ---- REGISTER ROUTES ----
app.register_blueprint(routes_bp)

@app.route("/")
def home():
    return {"message": "Demo Shopping Website 1 API Running"}

# app.py - ADD/UPDATE THIS SECTION AT THE BOTTOM
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render sets PORT environment variable
    app.run(host="0.0.0.0", port=port)
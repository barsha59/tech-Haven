# app.py
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os
import models  # 👈 IMPORTANT: ensures models are registered

app = Flask(__name__)
CORS(app)

# ---- DATABASE PATH SETUP ----
basedir = os.path.abspath(os.path.dirname(__file__))
instance_path = os.path.join(basedir, "instance")

# ensure instance folder exists
os.makedirs(instance_path, exist_ok=True)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(instance_path, "database.db")
)
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

if __name__ == "__main__":
    app.run(debug=True)

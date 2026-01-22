# app.py - TechHaven Electronics Store (Supabase Version)
from flask import Flask
from flask_cors import CORS
from extensions import db
from routes import routes_bp
import os
import models  # 👈 IMPORTANT: ensures models are registered

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
    
    # Use pg8000 driver (required for Render + Supabase)
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    print("✅ Using Supabase PostgreSQL with SSL")
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

# 🔥 CREATE TABLES & POPULATE WITH ELECTRONICS PRODUCTS
with app.app_context():
    db.create_all()
    print("✅ Database & tables created for TechHaven")
    
    # Check and populate electronics products
    from models import Product
    product_count = Product.query.count()
    print(f"📊 Current product count: {product_count}")
    
    if product_count == 0:
        print("📦 Adding sample electronics products to TechHaven...")
        
        # ELECTRONICS PRODUCTS FOR TECHHAVEN
        sample_products = [
            Product(
                name="Gaming Laptop Pro",
                price=1299.99,
                rating=4.5,
                review_count=128,
                category="Laptops",
                stock=15,
                image_url="https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400",
                description="High-performance gaming laptop with RTX 4070, 32GB RAM, 1TB SSD"
            ),
            Product(
                name="Wireless Mouse",
                price=29.99,
                rating=4.2,
                review_count=89,
                category="Accessories",
                stock=50,
                image_url="https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
                description="Ergonomic wireless mouse with 2-year battery life"
            ),
            Product(
                name="Mechanical Keyboard",
                price=89.99,
                rating=4.7,
                review_count=203,
                category="Accessories",
                stock=25,
                image_url="https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400",
                description="RGB mechanical keyboard with blue switches"
            ),
            Product(
                name="Noise Cancelling Headphones",
                price=199.99,
                rating=4.8,
                review_count=312,
                category="Audio",
                stock=30,
                image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                description="Premium wireless headphones with Active Noise Cancellation"
            ),
            Product(
                name="27-inch 4K Monitor",
                price=399.99,
                rating=4.4,
                review_count=67,
                category="Monitors",
                stock=12,
                image_url="https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=400",
                description="Ultra HD monitor with HDR support and 144Hz refresh rate"
            ),
            Product(
                name="Smartphone Pro",
                price=899.99,
                rating=4.6,
                review_count=421,
                category="Phones",
                stock=20,
                image_url="https://images.unsplash.com/photo-1592899677977-9c10ca588bbd?w=400",
                description="Latest smartphone with triple camera and 5G support"
            ),
            Product(
                name="Fitness Smartwatch",
                price=249.99,
                rating=4.3,
                review_count=156,
                category="Wearables",
                stock=35,
                image_url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400",
                description="Health tracking smartwatch with ECG and blood oxygen monitor"
            ),
            Product(
                name="Gaming Console",
                price=499.99,
                rating=4.9,
                review_count=289,
                category="Gaming",
                stock=8,
                image_url="https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400",
                description="Next-gen gaming console with 1TB storage and VR ready"
            )
        ]
        
        for product in sample_products:
            db.session.add(product)
        
        db.session.commit()
        print(f"✅ Added {len(sample_products)} electronics products to TechHaven")
    else:
        print(f"✅ TechHaven already has {product_count} products in database")

# ---- REGISTER ROUTES ----
app.register_blueprint(routes_bp)

@app.route("/")
def home():
    return {"message": "TechHaven Electronics API Running - Supabase Edition"}

@app.route("/health")
def health_check():
    """Health check endpoint for monitoring"""
    from models import Product
    product_count = Product.query.count()
    return {
        "status": "healthy",
        "service": "TechHaven API",
        "product_count": product_count,
        "database": "Supabase PostgreSQL" if os.environ.get('DATABASE_URL') else "SQLite"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
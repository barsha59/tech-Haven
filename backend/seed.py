# backend/seed.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import Product

# Sample products data
sample_products = [
    {
        "name": "Blue Cotton Shirt",
        "price": 25.99,
        "rating": 4.5,
        "review_count": 120,
        "category": "Clothing",
        "stock": 50,
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=300",
        "description": "Comfortable blue cotton shirt, perfect for casual wear."
    },
    {
        "name": "Wireless Headphones",
        "price": 89.99,
        "rating": 4.7,
        "review_count": 89,
        "category": "Electronics",
        "stock": 30,
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
        "description": "Noise-cancelling wireless headphones with 30-hour battery."
    },
    {
        "name": "Running Shoes",
        "price": 65.50,
        "rating": 4.3,
        "review_count": 210,
        "category": "Footwear",
        "stock": 40,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300",
        "description": "Lightweight running shoes with excellent grip."
    },
    {
        "name": "Smart Watch",
        "price": 199.99,
        "rating": 4.8,
        "review_count": 156,
        "category": "Electronics",
        "stock": 25,
        "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300",
        "description": "Track your fitness and receive notifications."
    },
    {
        "name": "Backpack",
        "price": 45.99,
        "rating": 4.2,
        "review_count": 78,
        "category": "Accessories",
        "stock": 60,
        "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w-300",
        "description": "Durable backpack with laptop compartment."
    },
    {
        "name": "Coffee Maker",
        "price": 75.00,
        "rating": 4.6,
        "review_count": 95,
        "category": "Home",
        "stock": 20,
        "image_url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=300",
        "description": "Automatic coffee maker with programmable timer."
    },
    {
        "name": "Yoga Mat",
        "price": 29.99,
        "rating": 4.4,
        "review_count": 142,
        "category": "Fitness",
        "stock": 100,
        "image_url": "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0?w=300",
        "description": "Non-slip yoga mat with carrying strap."
    },
    {
        "name": "Desk Lamp",
        "price": 34.99,
        "rating": 4.1,
        "review_count": 67,
        "category": "Home",
        "stock": 45,
        "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=300",
        "description": "LED desk lamp with adjustable brightness."
    },
]

def seed_database():
    with app.app_context():
        # Clear existing products
        db.session.query(Product).delete()
        
        # Add sample products
        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)
        
        db.session.commit()
        print(f"✅ Added {len(sample_products)} sample products to database")

if __name__ == "__main__":
    seed_database()
# add_real_products.py
import requests
import json

# ---------------- BACKEND URL ----------------
BACKEND_URL = "http://localhost:5000"  # Update if your app runs on a different port

# ---------------- PRODUCTS ----------------
REAL_PRODUCTS = [
    # --- Smartphones ---
    {"name": "iPhone 15 Pro Max 256GB", "price": 129999, "category": "Smartphones", "stock": 25, "rating": 4.8, "review_count": 342,
     "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w-400", "description": "256GB, Titanium, A17 Pro chip"},
    {"name": "iPhone 15 Pro Max 512GB", "price": 149999, "category": "Smartphones", "stock": 20, "rating": 4.9, "review_count": 298,
     "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w-400", "description": "512GB, Titanium, A17 Pro chip"},
    {"name": "iPhone 15", "price": 109999, "category": "Smartphones", "stock": 30, "rating": 4.7, "review_count": 401,
     "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w-400", "description": "128GB, Aluminum, A17 chip"},
    {"name": "Samsung Galaxy S24 Ultra 512GB", "price": 114999, "category": "Smartphones", "stock": 18, "rating": 4.7, "review_count": 287,
     "image_url": "https://images.unsplash.com/photo-1610945264815-d3e49530c1a0?w-400", "description": "12GB RAM, 512GB, S-Pen included"},
    {"name": "Samsung Galaxy S24", "price": 94999, "category": "Smartphones", "stock": 22, "rating": 4.6, "review_count": 199,
     "image_url": "https://images.unsplash.com/photo-1610945264815-d3e49530c1a0?w-400", "description": "8GB RAM, 256GB, S-Pen included"},

    # --- Laptops ---
    {"name": "MacBook Air M3 256GB", "price": 104999, "category": "Laptops", "stock": 12, "rating": 4.9, "review_count": 156,
     "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w-400", "description": "13-inch, 8GB RAM, 256GB SSD"},
    {"name": "MacBook Air M3 512GB", "price": 124999, "category": "Laptops", "stock": 10, "rating": 4.9, "review_count": 98,
     "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w-400", "description": "13-inch, 16GB RAM, 512GB SSD"},
]

# ---------------- ADD PRODUCTS ----------------
def add_products():
    try:
        # Check if backend is running
        print("🔗 Checking backend connection...")
        resp = requests.get(f"{BACKEND_URL}/health")
        if resp.status_code != 200:
            print(f"❌ Cannot connect to backend at {BACKEND_URL}")
            return
        print("✅ Backend is ready!")

        # Use bulk-add for efficiency
        print(f"📦 Adding {len(REAL_PRODUCTS)} products...")
        res = requests.post(f"{BACKEND_URL}/api/products/bulk-add", json=REAL_PRODUCTS)

        if res.status_code == 200:
            data = res.json()
            print(f"✅ Success! {data.get('total_added', 0)} products added.")
        else:
            print(f"❌ Failed to add products, status: {res.status_code}")
            print(res.text)

    except Exception as e:
        print(f"❌ Exception occurred: {e}")

# ---------------- MAIN ----------------
if __name__ == "__main__":
    add_products()

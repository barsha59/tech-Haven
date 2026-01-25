# add_real_products.py
import requests
import json

# Your backend URL (update this)
BACKEND_URL = "http://localhost:5000"  # Change to your actual URL

# Real electronics products with proper images
REAL_PRODUCTS = {
    "products": [
        {
            "name": "iPhone 15 Pro Max",
            "price": 129999,
            "category": "Smartphones",
            "stock": 25,
            "rating": 4.8,
            "review_count": 342,
            "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w-400",
            "description": "256GB, Titanium, A17 Pro chip"
        },
        {
            "name": "Samsung Galaxy S24 Ultra",
            "price": 114999,
            "category": "Smartphones",
            "stock": 18,
            "rating": 4.7,
            "review_count": 287,
            "image_url": "https://images.unsplash.com/photo-1610945264815-d3e49530c1a0?w-400",
            "description": "12GB RAM, 512GB, S-Pen included"
        },
        {
            "name": "MacBook Air M3",
            "price": 104999,
            "category": "Laptops",
            "stock": 12,
            "rating": 4.9,
            "review_count": 156,
            "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w-400",
            "description": "13-inch, 8GB RAM, 256GB SSD"
        },
        {
            "name": "Dell XPS 15",
            "price": 149999,
            "category": "Laptops",
            "stock": 8,
            "rating": 4.6,
            "review_count": 89,
            "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w-400",
            "description": "Intel i9, 32GB RAM, 1TB SSD, RTX 4060"
        },
        {
            "name": "Sony WH-1000XM5",
            "price": 24999,
            "category": "Audio",
            "stock": 30,
            "rating": 4.8,
            "review_count": 512,
            "image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w-400",
            "description": "Noise Cancelling Wireless Headphones"
        },
        {
            "name": "Apple AirPods Pro (2nd Gen)",
            "price": 18999,
            "category": "Audio",
            "stock": 45,
            "rating": 4.7,
            "review_count": 623,
            "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w-400",
            "description": "Active Noise Cancellation, MagSafe Charging"
        },
        {
            "name": "Samsung Odyssey G9",
            "price": 89999,
            "category": "Monitors",
            "stock": 6,
            "rating": 4.5,
            "review_count": 78,
            "image_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w-400",
            "description": "49-inch Curved Gaming Monitor, 240Hz"
        },
        {
            "name": "LG UltraGear 27GP850",
            "price": 34999,
            "category": "Monitors",
            "stock": 15,
            "rating": 4.4,
            "review_count": 134,
            "image_url": "https://images.unsplash.com/photo-1546538915-a9e2c8d0a0b1?w-400",
            "description": "27-inch QHD Nano IPS, 180Hz"
        },
        {
            "name": "Logitech MX Master 3S",
            "price": 8999,
            "category": "Accessories",
            "stock": 50,
            "rating": 4.6,
            "review_count": 456,
            "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?w-400",
            "description": "Wireless Mouse, Darkfield Tracking"
        },
        {
            "name": "Keychron K8 Pro",
            "price": 12999,
            "category": "Accessories",
            "stock": 20,
            "rating": 4.7,
            "review_count": 289,
            "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w-400",
            "description": "Mechanical Keyboard, Hot-swappable"
        },
        {
            "name": "iPad Air (5th Gen)",
            "price": 54999,
            "category": "Tablets",
            "stock": 22,
            "rating": 4.6,
            "review_count": 198,
            "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w-400",
            "description": "M1 Chip, 64GB, Wi-Fi"
        },
        {
            "name": "Samsung Galaxy Tab S9",
            "price": 67999,
            "category": "Tablets",
            "stock": 14,
            "rating": 4.5,
            "review_count": 112,
            "image_url": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w-400",
            "description": "12GB RAM, 256GB, S-Pen included"
        },
        {
            "name": "DJI Mini 3 Pro",
            "price": 84999,
            "category": "Drones",
            "stock": 9,
            "rating": 4.8,
            "review_count": 203,
            "image_url": "https://images.unsplash.com/photo-1473968512647-3e447244af8f?w-400",
            "description": "4K Camera Drone, 34-min Flight Time"
        },
        {
            "name": "GoPro Hero 12",
            "price": 42999,
            "category": "Cameras",
            "stock": 18,
            "rating": 4.5,
            "review_count": 167,
            "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w-400",
            "description": "Action Camera, 5.3K Video, HyperSmooth"
        },
        {
            "name": "Sony Alpha 7 IV",
            "price": 189999,
            "category": "Cameras",
            "stock": 5,
            "rating": 4.9,
            "review_count": 89,
            "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w-400",
            "description": "Full-frame Mirrorless Camera"
        },
        {
            "name": "PlayStation 5",
            "price": 44999,
            "category": "Gaming",
            "stock": 15,
            "rating": 4.8,
            "review_count": 423,
            "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w-400",
            "description": "825GB SSD, DualSense Wireless Controller"
        },
        {
            "name": "Xbox Series X",
            "price": 41999,
            "category": "Gaming",
            "stock": 12,
            "rating": 4.7,
            "review_count": 387,
            "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w-400",
            "description": "1TB SSD, 4K Gaming, Game Pass included"
        },
        {
            "name": "Nintendo Switch OLED",
            "price": 32999,
            "category": "Gaming",
            "stock": 25,
            "rating": 4.6,
            "review_count": 512,
            "image_url": "https://images.unsplash.com/photo-1587844791456-72e29d88e673?w-400",
            "description": "7-inch OLED Screen, 64GB"
        },
        {
            "name": "Amazon Echo Dot (5th Gen)",
            "price": 4499,
            "category": "Smart Home",
            "stock": 40,
            "rating": 4.3,
            "review_count": 678,
            "image_url": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w-400",
            "description": "Smart Speaker with Alexa"
        },
        {
            "name": "Google Nest Hub (2nd Gen)",
            "price": 6999,
            "category": "Smart Home",
            "stock": 28,
            "rating": 4.4,
            "review_count": 342,
            "image_url": "https://images.unsplash.com/photo-1558089687-f282ffcbc0d4?w-400",
            "description": "7-inch Smart Display with Google Assistant"
        },
        {
            "name": "Fitbit Charge 6",
            "price": 12999,
            "category": "Wearables",
            "stock": 35,
            "rating": 4.2,
            "review_count": 456,
            "image_url": "https://images.unsplash.com/photo-1576243345690-4e4b79b63288?w-400",
            "description": "Fitness Tracker with GPS, Heart Rate"
        },
        {
            "name": "Apple Watch Series 9",
            "price": 41999,
            "category": "Wearables",
            "stock": 20,
            "rating": 4.7,
            "review_count": 289,
            "image_url": "https://images.unsplash.com/photo-1434493650001-5d43a6fea0a6?w-400",
            "description": "GPS + Cellular, 45mm, Midnight"
        },
        {
            "name": "SanDisk Extreme Portable SSD 1TB",
            "price": 8999,
            "category": "Storage",
            "stock": 60,
            "rating": 4.6,
            "review_count": 412,
            "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w-400",
            "description": "1050MB/s read, IP65 water & dust resistant"
        },
        {
            "name": "WD Black SN850X 2TB NVMe",
            "price": 14999,
            "category": "Storage",
            "stock": 30,
            "rating": 4.8,
            "review_count": 234,
            "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w-400",
            "description": "PCIe Gen4 SSD, 7300MB/s read"
        }
    ]
}

def add_products():
    """Add products to database via API"""
    try:
        # First check if we can connect
        print("Checking connection to backend...")
        response = requests.get(f"{BACKEND_URL}/api/debug-info")
        
        if response.status_code != 200:
            print(f"❌ Cannot connect to backend at {BACKEND_URL}")
            print(f"Status: {response.status_code}")
            return
        
        # Get current product count
        product_count = response.json().get('total_products', 0)
        print(f"📊 Current products in database: {product_count}")
        
        # Ask user confirmation
        if product_count > 10:
            confirm = input(f"⚠️ You already have {product_count} products. Add more? (y/n): ")
            if confirm.lower() != 'y':
                return
        
        # Add products
        print(f"🚀 Adding {len(REAL_PRODUCTS['products'])} products...")
        
        # Use bulk-add endpoint if available, otherwise use individual
        bulk_url = f"{BACKEND_URL}/api/products/bulk-add"
        
        # Try bulk add first
        response = requests.post(bulk_url, json=REAL_PRODUCTS)
        
        if response.status_code == 404:
            print("Bulk endpoint not found, adding one by one...")
            # Fallback: add products one by one
            added = 0
            for product in REAL_PRODUCTS['products']:
                try:
                    # You need to implement a single product endpoint first
                    # Or use your existing add_sample_products route
                    pass
                except:
                    continue
        else:
            result = response.json()
            print(f"✅ {result.get('message', 'Products added successfully')}")
            print(f"📈 Total products now: {result.get('total_products', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    add_products()
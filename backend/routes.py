# routes.py - TechHaven Electronics Store
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import Product, Order, Review, User, Wishlist 
import stripe
import os

print("✅ TechHaven routes.py loaded")

routes_bp = Blueprint("routes", __name__)

# Stripe test secret key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_51Sl1TM2YdULA0kvGpfx1oZOXm23IjU8gHAuGgHnT5g6mTCwWroS2FarkOOEItnjOVvDjbakucO2nFxVepPbGeldS00tkYhBAbR")

# ----------------------
# GET all products
# ----------------------
@routes_bp.route('/api/products', methods=['GET'])
def get_products():
    sort_by = request.args.get('sort')
    
    if sort_by == "price":
        products = Product.query.order_by(Product.price.asc()).all()
    elif sort_by == "rating":
        products = Product.query.order_by(Product.rating.desc()).all()
    else:
        products = Product.query.all()
    
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "rating": p.rating,
            "reviews": p.review_count,
            "category": p.category,
            "stock": p.stock,
            "image": p.image_url
        }
        for p in products
    ])

@routes_bp.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify({
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "rating": product.rating,
        "reviews": product.review_count,
        "category": product.category,
        "stock": product.stock,
        "image_url": product.image_url
    })


# ----------------------
# CREATE ORDER
# ----------------------
@routes_bp.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json
    customer_name = data.get("customer_name")
    address = data.get("address")
    phone = data.get("phone")
    cart_items = data.get("cart")  # Expecting: [{"product_id":1,"quantity":2}, ...]

    if not customer_name or not address or not phone:
        return jsonify({"error": "Customer info is required"}), 400

    if not cart_items or not isinstance(cart_items, list):
        return jsonify({"error": "Cart is empty or invalid"}), 400

    orders_created = []

    for item in cart_items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)

        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": f"Product ID {product_id} not found"}), 404

        if product.stock < quantity:
            return jsonify({"error": f"{product.name} out of stock"}), 400

        # Create one Order record per cart item
        order = Order(
            product_id=product.id,
            customer_name=customer_name,
            address=address,
            phone=phone,
            status="Pending"
        )
        db.session.add(order)
        orders_created.append(order)

        # Reduce product stock
        product.stock -= quantity

    db.session.commit()

    return jsonify({
        "message": "Orders placed successfully",
        "order_ids": [o.id for o in orders_created]
    })


# ----------------------
# ADD REVIEW
# ----------------------
@routes_bp.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    print("DEBUG - Received review data:", data)  # <-- log it
    product_id = data.get("product_id")
    rating = data.get("rating")
    comment = data.get("comment", "")

    if product_id is None or rating is None:
        return jsonify({"error": "Product ID and rating are required"}), 400

    review = Review(product_id=product_id, rating=rating, comment=comment)
    db.session.add(review)

    product = Product.query.get(product_id)
    if product:
        all_reviews = Review.query.filter_by(product_id=product_id).all()
        product.review_count = len(all_reviews)
        product.rating = sum(r.rating for r in all_reviews) / len(all_reviews)

    db.session.commit()
    return jsonify({"message": "Review added successfully"})

# ----------------------
# STRIPE PAYMENT
# ----------------------
@routes_bp.route('/api/pay', methods=['POST'])
def create_payment():
    data = request.json
    amount = data.get("amount")  # in cents

    if not amount:
        return jsonify({"error": "Amount is required"}), 400

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount),
            currency="usd",
            payment_method_types=["card"],
        )
        return jsonify({"client_secret": intent.client_secret})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------
# CONFIRM ORDER PAYMENT
# ----------------------
@routes_bp.route('/api/orders/<int:order_id>/pay', methods=['POST'])
def confirm_payment(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    order.status = "Paid"
    db.session.commit()
    return jsonify({"message": f"Order {order_id} marked as Paid"})

# ----------------------
# USER AUTHENTICATION
# ----------------------
@routes_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')
    
    if not email or not name or not password:
        return jsonify({"error": "All fields are required"}), 400
    
    # Check if user exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
    # Create new user
    user = User(email=email, name=name)
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "User registered successfully",
        "user": {"id": user.id, "email": user.email, "name": user.name}
    })

@routes_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    return jsonify({
        "message": "Login successful",
        "user": {"id": user.id, "email": user.email, "name": user.name}
    })

# ----------------------
# PRODUCT SEARCH (FOR CHATBOT)
# ----------------------
@routes_bp.route('/api/products/search', methods=['GET'])
def search_products():
    query = request.args.get('q', '').lower()
    category = request.args.get('category', '')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    # Start with all products
    products_query = Product.query
    
    # Apply filters
    if query:
        products_query = products_query.filter(
            Product.name.ilike(f'%{query}%') | 
            Product.description.ilike(f'%{query}%')
        )
    
    if category:
        products_query = products_query.filter_by(category=category)
    
    if min_price:
        try:
            products_query = products_query.filter(Product.price >= float(min_price))
        except:
            pass
    
    if max_price:
        try:
            products_query = products_query.filter(Product.price <= float(max_price))
        except:
            pass
    
    products = products_query.all()
    
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "rating": p.rating,
            "reviews": p.review_count,
            "category": p.category,
            "stock": p.stock,
            "image": p.image_url,
            "description": p.description
        }
        for p in products
    ])

# ----------------------
# GET PRODUCT DETAILS WITH REVIEWS
# ----------------------
@routes_bp.route('/api/products/<int:product_id>/details', methods=['GET'])
def get_product_details(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Get reviews for this product
    reviews = Review.query.filter_by(product_id=product_id).all()
    
    return jsonify({
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "rating": product.rating,
        "reviews": product.review_count,
        "category": product.category,
        "stock": product.stock,
        "image_url": product.image_url,
        "description": product.description,
        "all_reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in reviews
        ]
    })

# ----------------------
# GET PRODUCTS BY CATEGORY
# ----------------------
@routes_bp.route('/api/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    products = Product.query.filter_by(category=category).all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "rating": p.rating,
            "category": p.category,
            "image": p.image_url
        }
        for p in products
    ])

# ----------------------
# WISHLIST ROUTES
# ----------------------
@routes_bp.route('/api/wishlist', methods=['GET'])
def get_wishlist():
    # For now, we'll use user_id from query param
    # Later you can get from session/token
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({"error": "User ID required"}), 400
    
    wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
    
    # Get product details for each wishlist item
    items_with_details = []
    for item in wishlist_items:
        product = Product.query.get(item.product_id)
        if product:
            items_with_details.append({
                "wishlist_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "image": product.image_url,
                "added_at": item.added_at.isoformat() if item.added_at else None
            })
    
    return jsonify(items_with_details)

@routes_bp.route('/api/wishlist/add', methods=['POST'])
def add_to_wishlist():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    
    if not user_id or not product_id:
        return jsonify({"error": "User ID and Product ID required"}), 400
    
    # Check if already in wishlist
    existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return jsonify({"message": "Product already in wishlist"}), 200
    
    # Check if product exists
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    
    # Add to wishlist
    wishlist_item = Wishlist(user_id=user_id, product_id=product_id)
    db.session.add(wishlist_item)
    db.session.commit()
    
    return jsonify({
        "message": "Added to wishlist",
        "wishlist_id": wishlist_item.id
    })

@routes_bp.route('/api/wishlist/remove', methods=['POST'])
def remove_from_wishlist():
    data = request.json
    user_id = data.get('user_id')
    product_id = data.get('product_id')
    
    if not user_id or not product_id:
        return jsonify({"error": "User ID and Product ID required"}), 400
    
    # Find and remove
    wishlist_item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        return jsonify({"message": "Removed from wishlist"})
    
    return jsonify({"error": "Item not found in wishlist"}), 404

@routes_bp.route('/api/wishlist/check', methods=['GET'])
def check_wishlist():
    user_id = request.args.get('user_id')
    product_id = request.args.get('product_id')
    
    if not user_id or not product_id:
        return jsonify({"error": "User ID and Product ID required"}), 400
    
    exists = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first() is not None
    return jsonify({"in_wishlist": exists})

# ======================
# DEBUG & DATABASE CHECK ROUTES
# ======================

@routes_bp.route('/api/check-db')
def check_database():
    """Check if database has products"""
    try:
        product_count = Product.query.count()
        
        return jsonify({
            "status": "success",
            "product_count": product_count,
            "message": f"Found {product_count} products in database",
            "is_empty": product_count == 0
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": f"Database connection failed: {str(e)[:100]}",
            "suggestion": "Check database configuration"
        }), 500


@routes_bp.route('/api/add-sample-products')
def add_sample_products():
    """Add more sample products to empty database"""
    try:
        current_count = Product.query.count()
        
        # If we already have products, just add what's missing
        products_added = 0
        
        # EXTENDED SAMPLE ELECTRONICS PRODUCTS (25+ products)
        sample_products = [
            # Laptops
            {
                "name": "Gaming Laptop Pro",
                "price": 1299.99,
                "rating": 4.5,
                "review_count": 128,
                "category": "Laptops",
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400",
                "description": "High-performance gaming laptop with RTX 4070"
            },
            {
                "name": "MacBook Air M3",
                "price": 1099.99,
                "rating": 4.8,
                "review_count": 342,
                "category": "Laptops", 
                "stock": 20,
                "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400",
                "description": "Apple M3 chip, 13.6-inch Liquid Retina display"
            },
            {
                "name": "Dell XPS 15",
                "price": 1499.99,
                "rating": 4.6,
                "review_count": 189,
                "category": "Laptops",
                "stock": 12,
                "image_url": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=400",
                "description": "Intel Core i9, 32GB RAM, 1TB SSD"
            },
            
            # Smartphones
            {
                "name": "iPhone 15 Pro Max",
                "price": 1299.99,
                "rating": 4.8,
                "review_count": 512,
                "category": "Smartphones",
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400",
                "description": "Titanium design, A17 Pro chip, 5x telephoto"
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "price": 1199.99,
                "rating": 4.7,
                "review_count": 428,
                "category": "Smartphones",
                "stock": 18,
                "image_url": "https://images.unsplash.com/photo-1610945264815-d3e49530c1a0?w=400",
                "description": "Snapdragon 8 Gen 3, S-Pen included"
            },
            {
                "name": "Google Pixel 8 Pro",
                "price": 999.99,
                "rating": 4.6,
                "review_count": 267,
                "category": "Smartphones",
                "stock": 22,
                "image_url": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=400",
                "description": "Tensor G3 chip, Best-in-class camera"
            },
            
            # Tablets
            {
                "name": "iPad Pro 12.9-inch",
                "price": 1099.99,
                "rating": 4.8,
                "review_count": 312,
                "category": "Tablets",
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400",
                "description": "M2 chip, Liquid Retina XDR display"
            },
            {
                "name": "Samsung Galaxy Tab S9 Ultra",
                "price": 1199.99,
                "rating": 4.7,
                "review_count": 189,
                "category": "Tablets",
                "stock": 10,
                "image_url": "https://images.unsplash.com/photo-1561154464-82e9adf32764?w=400",
                "description": "14.6-inch display, S-Pen included"
            },
            
            # Audio
            {
                "name": "Sony WH-1000XM5",
                "price": 399.99,
                "rating": 4.8,
                "review_count": 623,
                "category": "Audio",
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1484704849700-f032a568e944?w=400",
                "description": "Industry-leading noise cancellation"
            },
            {
                "name": "AirPods Pro (2nd Gen)",
                "price": 249.99,
                "rating": 4.7,
                "review_count": 845,
                "category": "Audio",
                "stock": 45,
                "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400",
                "description": "Active Noise Cancellation, MagSafe"
            },
            {
                "name": "Bose QuietComfort Ultra",
                "price": 429.99,
                "rating": 4.6,
                "review_count": 278,
                "category": "Audio",
                "stock": 18,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                "description": "Immersive Audio, noise cancelling"
            },
            
            # Monitors
            {
                "name": "LG UltraGear 27GP850",
                "price": 449.99,
                "rating": 4.5,
                "review_count": 167,
                "category": "Monitors",
                "stock": 14,
                "image_url": "https://images.unsplash.com/photo-1546538915-a9e2c8d0a0b1?w=400",
                "description": "27-inch QHD, 180Hz, Nano IPS"
            },
            {
                "name": "Samsung Odyssey G9",
                "price": 1299.99,
                "rating": 4.7,
                "review_count": 89,
                "category": "Monitors",
                "stock": 6,
                "image_url": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400",
                "description": "49-inch curved, 240Hz, QLED"
            },
            
            # Accessories
            {
                "name": "Logitech MX Master 3S",
                "price": 99.99,
                "rating": 4.6,
                "review_count": 456,
                "category": "Accessories",
                "stock": 50,
                "image_url": "https://images.unsplash.com/photo-1527814050087-3793815479db?w=400",
                "description": "Wireless mouse, Darkfield tracking"
            },
            {
                "name": "Keychron K8 Pro",
                "price": 119.99,
                "rating": 4.7,
                "review_count": 289,
                "category": "Accessories",
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400",
                "description": "Mechanical keyboard, hot-swappable"
            },
            {
                "name": "Apple Magic Keyboard",
                "price": 149.99,
                "rating": 4.4,
                "review_count": 312,
                "category": "Accessories",
                "stock": 35,
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400",
                "description": "Wireless keyboard with Touch ID"
            },
            
            # Gaming
            {
                "name": "PlayStation 5",
                "price": 499.99,
                "rating": 4.8,
                "review_count": 1023,
                "category": "Gaming",
                "stock": 15,
                "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400",
                "description": "825GB SSD, DualSense controller"
            },
            {
                "name": "Xbox Series X",
                "price": 499.99,
                "rating": 4.7,
                "review_count": 876,
                "category": "Gaming",
                "stock": 12,
                "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400",
                "description": "1TB SSD, Game Pass included"
            },
            {
                "name": "Nintendo Switch OLED",
                "price": 349.99,
                "rating": 4.6,
                "review_count": 723,
                "category": "Gaming",
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1587844791456-72e29d88e673?w=400",
                "description": "7-inch OLED screen, 64GB storage"
            },
            
            # Smart Home
            {
                "name": "Amazon Echo Dot (5th Gen)",
                "price": 49.99,
                "rating": 4.3,
                "review_count": 678,
                "category": "Smart Home",
                "stock": 60,
                "image_url": "https://images.unsplash.com/photo-1589003077984-894e133dabab?w=400",
                "description": "Smart speaker with Alexa"
            },
            {
                "name": "Google Nest Hub (2nd Gen)",
                "price": 99.99,
                "rating": 4.4,
                "review_count": 342,
                "category": "Smart Home",
                "stock": 28,
                "image_url": "https://images.unsplash.com/photo-1558089687-f282ffcbc0d4?w=400",
                "description": "7-inch smart display with Assistant"
            },
            
            # Wearables
            {
                "name": "Apple Watch Series 9",
                "price": 399.99,
                "rating": 4.7,
                "review_count": 589,
                "category": "Wearables",
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1434493650001-5d43a6fea0a6?w=400",
                "description": "GPS + Cellular, 45mm, Always-On"
            },
            {
                "name": "Samsung Galaxy Watch 6 Classic",
                "price": 369.99,
                "rating": 4.5,
                "review_count": 287,
                "category": "Wearables",
                "stock": 22,
                "image_url": "https://images.unsplash.com/photo-1579586337278-3fbe9cff5dfb?w=400",
                "description": "47mm, Rotating bezel, LTE"
            },
            
            # Storage
            {
                "name": "SanDisk Extreme Portable SSD 1TB",
                "price": 99.99,
                "rating": 4.6,
                "review_count": 412,
                "category": "Storage",
                "stock": 40,
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400",
                "description": "1050MB/s read, IP65 water resistant"
            },
            {
                "name": "Samsung T7 Shield 2TB",
                "price": 149.99,
                "rating": 4.7,
                "review_count": 256,
                "category": "Storage",
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=400",
                "description": "IP65 rated, 1050MB/s transfer"
            },
            
            # Cameras
            {
                "name": "Sony Alpha 7 IV",
                "price": 2499.99,
                "rating": 4.8,
                "review_count": 189,
                "category": "Cameras",
                "stock": 8,
                "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400",
                "description": "Full-frame mirrorless camera"
            },
            {
                "name": "GoPro Hero 12",
                "price": 399.99,
                "rating": 4.5,
                "review_count": 267,
                "category": "Cameras",
                "stock": 35,
                "image_url": "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400",
                "description": "Action camera, 5.3K video"
            }
        ]
        
        # Add only products that don't exist yet
        added_count = 0
        for prod_data in sample_products:
            # Check if product already exists by name
            existing = Product.query.filter_by(name=prod_data["name"]).first()
            if not existing:
                product = Product(
                    name=prod_data["name"],
                    price=prod_data["price"],
                    rating=prod_data["rating"],
                    review_count=prod_data["review_count"],
                    category=prod_data["category"],
                    stock=prod_data["stock"],
                    image_url=prod_data["image_url"],
                    description=prod_data["description"]
                )
                db.session.add(product)
                added_count += 1
        
        db.session.commit()
        
        total_now = Product.query.count()
        
        if added_count == 0:
            return jsonify({
                "status": "info",
                "message": f"All {len(sample_products)} products already exist in database.",
                "product_count": total_now,
                "added": 0
            })
        else:
            return jsonify({
                "status": "success",
                "message": f"Added {added_count} new products to database. Total now: {total_now}",
                "total_products": total_now,
                "added": added_count,
                "skipped": len(sample_products) - added_count
            })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Failed to add sample products"
        }), 500
    
@routes_bp.route('/api/debug-info')
def debug_info():
    """Get debug information about the backend"""
    import os
    
    return jsonify({
        "backend_running": True,
        "service": "TechHaven Electronics API",
        "database_url_exists": bool(os.environ.get('DATABASE_URL')),
        "total_products": Product.query.count(),
        "total_users": User.query.count(),
        "total_orders": Order.query.count(),
        "environment": "production" if os.environ.get('DATABASE_URL') else "development"
    })
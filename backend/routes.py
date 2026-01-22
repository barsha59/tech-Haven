# routes.py
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import Product, Order, Review, User, Wishlist 
import stripe
import os

print("✅ routes.py loaded")

routes_bp = Blueprint("routes", __name__)

# Stripe test secret key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "sk_test_51Sl1TM2YdULA0kvGpfx1oZOXm23IjU8gHAuGgHnT5g6mTCwWroS2FarkOOEItnjOVvDjbakucO2nFxVepPbGeldS00tkYhBAbR")

# ----------------------
# GET all products
# ----------------------
@routes_bp.route('/api/products', methods=['GET'])
def get_products():
    sort_by = request.args.get('sort')
    
    try:
        # Try to get from database
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
        
    except Exception as e:
        print(f"Database error, returning sample data: {e}")
        # Fallback sample data
        return jsonify([
            {
                "id": 1,
                "name": "Gaming Laptop Pro",
                "price": 1299.99,
                "rating": 4.5,
                "reviews": 128,
                "category": "Electronics",
                "stock": 15,
                "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400"
            },
            {
                "id": 2,
                "name": "Wireless Mouse",
                "price": 29.99,
                "rating": 4.2,
                "reviews": 89,
                "category": "Accessories",
                "stock": 50,
                "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"
            },
            {
                "id": 3,
                "name": "Mechanical Keyboard",
                "price": 89.99,
                "rating": 4.7,
                "reviews": 203,
                "category": "Accessories",
                "stock": 25,
                "image": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400"
            }
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

# routes.py - ADD THESE NEW ROUTES

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

# routes.py - Update the check_database() function
@routes_bp.route('/api/check-db')
def check_database():
    """Check if database has products"""
    try:
        # Use the existing db connection from Flask-SQLAlchemy
        from models import Product
        product_count = Product.query.count()
        
        return jsonify({
            "status": "success",
            "product_count": product_count,
            "message": f"Found {product_count} products in database",
            "is_empty": product_count == 0
        })
    except Exception as e:
        # If query fails, database connection failed
        return jsonify({
            "status": "error",
            "error": f"Database connection failed: {str(e)[:100]}",
            "suggestion": "Check SSL configuration and Supabase IP whitelist"
        }), 500

@routes_bp.route('/api/add-sample-products')
def add_sample_products():
    """Add sample products to empty database"""
    try:
        # Try to check database connection first
        try:
            current_count = Product.query.count()
            db_connected = True
        except Exception as db_error:
            print(f"Database query failed: {db_error}")
            current_count = 0
            db_connected = False
        
        if not db_connected:
            return jsonify({
                "status": "error",
                "message": "Cannot connect to database",
                "error": "Database connection failed. Check SSL configuration and Supabase settings.",
                "suggestion": "1. Ensure DATABASE_URL has ?sslmode=require\n2. Whitelist all IPs in Supabase\n3. Try direct connection instead of pooler"
            }), 500
        
        if current_count > 0:
            return jsonify({
                "status": "info",
                "message": f"Already have {current_count} products. No need to add samples.",
                "product_count": current_count
            })
        
        # Sample products data
        sample_products = [
            {
                "id": 1,
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
                "id": 2,
                "name": "Wireless Mouse",
                "price": 29.99,
                "rating": 4.2,
                "review_count": 89,
                "category": "Accessories",
                "stock": 50,
                "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400",
                "description": "Ergonomic wireless mouse with long battery life"
            },
            {
                "id": 3,
                "name": "Mechanical Keyboard",
                "price": 89.99,
                "rating": 4.7,
                "review_count": 203,
                "category": "Accessories",
                "stock": 25,
                "image_url": "https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=400",
                "description": "RGB mechanical keyboard with blue switches"
            },
            {
                "id": 4,
                "name": "27-inch 4K Monitor",
                "price": 399.99,
                "rating": 4.4,
                "review_count": 67,
                "category": "Monitors",
                "stock": 12,
                "image_url": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=400",
                "description": "Ultra HD monitor with HDR support"
            },
            {
                "id": 5,
                "name": "Noise Cancelling Headphones",
                "price": 199.99,
                "rating": 4.8,
                "review_count": 312,
                "category": "Audio",
                "stock": 30,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400",
                "description": "Premium wireless headphones with ANC"
            }
        ]
        
        added_count = 0
        try:
            for prod_data in sample_products:
                # Create Product object
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
            
            # Commit to database
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "message": f"Added {added_count} sample products to database",
                "products_added": sample_products,
                "total_products": Product.query.count()
            })
            
        except Exception as insert_error:
            db.session.rollback()
            return jsonify({
                "status": "error",
                "message": "Failed to insert products",
                "error": str(insert_error),
                "added_before_error": added_count
            }), 500
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Unexpected error in add_sample_products"
        }), 500

@routes_bp.route('/api/debug-info')
def debug_info():
    """Get debug information about the backend"""
    import os
    
    return jsonify({
        "backend_running": True,
        "service": "tech-haven-4r4y.onrender.com",
        "database_url_exists": bool(os.environ.get('DATABASE_URL')),
        "total_products": Product.query.count(),
        "total_users": User.query.count(),
        "total_orders": Order.query.count(),
        "environment": "production"
    })
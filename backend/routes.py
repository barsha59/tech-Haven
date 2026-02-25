# routes.py - TechHaven Electronics Store
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import Product, Order, Review, User, Wishlist 
import stripe
import os


# ----------------------
# API KEY AUTH MIDDLEWARE
# ----------------------
from functools import wraps

API_KEY = os.environ.get("API_KEY")  # should be set in your .env / docker-compose
print("Loaded API_KEY:", API_KEY) 


def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("x-api-key")
        if not key or key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# -------------------------------------------------------


print("✅ TechHaven routes.py loaded")

routes_bp = Blueprint("routes", __name__)

# Stripe test secret key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
print("Stripe API Key loaded?", stripe.api_key is not None)

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
            "image": p.image_url,
            "description": p.description
        }
        for p in products
    ])


# ----------------------
# SECURE GET PRODUCTS (API KEY REQUIRED)
# ----------------------
@routes_bp.route('/api/secure/products', methods=['GET'])
@require_api_key
def get_secure_products():
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
            "image": p.image_url,
            "description": p.description
        }
        for p in products
    ])
# ------------------------------------


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
        "image_url": product.image_url,
        "description": product.description
    })


# ----------------------
# ADD SINGLE PRODUCT
# ----------------------
@routes_bp.route('/api/products/add', methods=['POST'])
def add_product():
    data = request.json
    if not data.get("name") or not data.get("price") or not data.get("category"):
        return jsonify({"error": "Name, price, and category are required"}), 400
    
    existing = Product.query.filter_by(name=data["name"]).first()
    if existing:
        return jsonify({"error": "Product already exists"}), 400

    product = Product(
        name=data["name"],
        price=data["price"],
        rating=data.get("rating", 0),
        review_count=data.get("review_count", 0),
        category=data["category"],
        stock=data.get("stock", 10),
        image_url=data.get("image_url", ""),
        description=data.get("description", "")
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added", "product_id": product.id})


# ----------------------
# BULK ADD PRODUCTS (50+)
# ----------------------
@routes_bp.route('/api/products/bulk-add', methods=['POST'])
def bulk_add_products():
    data = request.json
    if not isinstance(data, list):
        return jsonify({"error": "Expected a list of products"}), 400

    added_count = 0
    for prod_data in data:
        if Product.query.filter_by(name=prod_data.get("name")).first():
            continue

        product = Product(
            name=prod_data.get("name"),
            price=prod_data.get("price"),
            rating=prod_data.get("rating", 0),
            review_count=prod_data.get("review_count", 0),
            category=prod_data.get("category"),
            stock=prod_data.get("stock", 10),
            image_url=prod_data.get("image_url", ""),
            description=prod_data.get("description", "")
        )
        db.session.add(product)
        added_count += 1

    db.session.commit()
    return jsonify({
        "message": f"Added {added_count} products",
        "total_added": added_count
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
    cart_items = data.get("cart")  # [{"product_id":1,"quantity":2}, ...]

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

        order = Order(
            product_id=product.id,
            customer_name=customer_name,
            address=address,
            phone=phone,
            status="Pending"
        )
        db.session.add(order)
        orders_created.append(order)
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
    amount = data.get("amount")
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

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400

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
# EXISTING add-sample-products (optional)
# ----------------------
@routes_bp.route('/api/add-sample-products')
def add_sample_products():
    """Legacy endpoint - adds products one by one if DB empty"""
    return jsonify({"message": "Use /api/products/bulk-add for faster insertion"})


# ----------------------
# DEBUG INFO
# ----------------------
@routes_bp.route('/api/debug-info')
def debug_info():
    return jsonify({
        "backend_running": True,
        "service": "TechHaven Electronics API",
        "database_url_exists": bool(os.environ.get('DATABASE_URL')),
        "total_products": Product.query.count(),
        "total_users": User.query.count(),
        "total_orders": Order.query.count(),
        "environment": "production" if os.environ.get('DATABASE_URL') else "development"
    })

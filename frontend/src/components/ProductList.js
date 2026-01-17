// src/components/ProductList.js - UPDATED VERSION
import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import API_URL from "../config"; // Import API_URL from config

const ProductList = ({ addToCart }) => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [wishlistStatus, setWishlistStatus] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    fetchProducts();
  }, []);

  // Check wishlist status for each product
  useEffect(() => {
    if (products.length > 0) {
      checkAllWishlistStatus();
    }
  }, [products]);

  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/products`);
      setProducts(response.data);
      
      // Extract unique categories
      const uniqueCategories = [...new Set(response.data.map(p => p.category))];
      setCategories(uniqueCategories);
    } catch (err) {
      console.log(err);
    }
  };

  const checkAllWishlistStatus = async () => {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) return;

    const status = {};
    for (const product of products) {
      try {
        const response = await axios.get(
          `${API_URL}/api/wishlist/check?user_id=${user.id}&product_id=${product.id}`
        );
        status[product.id] = response.data.in_wishlist;
      } catch (err) {
        console.error("Error checking wishlist:", err);
        status[product.id] = false;
      }
    }
    setWishlistStatus(status);
  };

  const toggleWishlist = async (productId) => {
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
      alert("Please login to use wishlist");
      return;
    }

    try {
      const isInWishlist = wishlistStatus[productId];
      
      if (isInWishlist) {
        // Remove from wishlist
        await axios.post(`${API_URL}/api/wishlist/remove`, {
          user_id: user.id,
          product_id: productId
        });
        setWishlistStatus(prev => ({ ...prev, [productId]: false }));
        alert("Removed from wishlist");
      } else {
        // Add to wishlist
        await axios.post(`${API_URL}/api/wishlist/add`, {
          user_id: user.id,
          product_id: productId
        });
        setWishlistStatus(prev => ({ ...prev, [productId]: true }));
        alert("Added to wishlist");
      }
    } catch (err) {
      console.error("Error toggling wishlist:", err);
      alert("Error updating wishlist");
    }
  };

  const handleCategoryFilter = async (category) => {
    setSelectedCategory(category);
    try {
      const url = category 
        ? `${API_URL}/api/products/category/${category}`
        : `${API_URL}/api/products`;
      const response = await axios.get(url);
      setProducts(response.data);
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div>
      <h2>Products</h2>
      
      {/* Category Filter */}
      <div style={{ marginBottom: "20px" }}>
        <label style={{ marginRight: "10px" }}>Filter by Category:</label>
        <select 
          value={selectedCategory} 
          onChange={(e) => handleCategoryFilter(e.target.value)}
          style={{ padding: "5px" }}
        >
          <option value="">All Categories</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{cat}</option>
          ))}
        </select>
      </div>

      {/* Navigation Buttons */}
      <div style={{ marginBottom: "20px", display: "flex", gap: "10px" }}>
        <Link to="/cart">
          <button style={{ padding: "8px 16px", cursor: "pointer" }}>
            🛒 Go to Cart ({JSON.parse(localStorage.getItem("cart") || "[]").length})
          </button>
        </Link>
        
        <Link to="/wishlist">
          <button style={{ 
            padding: "8px 16px", 
            cursor: "pointer",
            background: "#ff6b6b",
            color: "white",
            border: "none",
            borderRadius: "5px"
          }}>
            ❤️ My Wishlist
          </button>
        </Link>
      </div>

      <div style={{ display: "flex", gap: "20px", flexWrap: "wrap" }}>
        {products.map(p => (
          <div key={p.id} style={{ 
            border: "1px solid #ddd", 
            padding: "15px", 
            width: "220px",
            borderRadius: "5px",
            boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
            position: "relative"
          }}>
            {/* Wishlist Heart Button */}
            <button
              onClick={() => toggleWishlist(p.id)}
              style={{
                position: "absolute",
                top: "10px",
                right: "10px",
                background: "white",
                border: "1px solid #ddd",
                borderRadius: "50%",
                width: "36px",
                height: "36px",
                fontSize: "20px",
                cursor: "pointer",
                color: wishlistStatus[p.id] ? "red" : "#ccc",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 2px 5px rgba(0,0,0,0.1)",
                zIndex: "1"
              }}
              title={wishlistStatus[p.id] ? "Remove from wishlist" : "Add to wishlist"}
            >
              {wishlistStatus[p.id] ? "♥" : "♡"}
            </button>
            
            <Link to={`/product/${p.id}`} style={{ textDecoration: "none", color: "inherit" }}>
              <img src={p.image} alt={p.name} width="200" height="200" style={{ objectFit: "cover" }} />
              <h4 style={{ margin: "10px 0", minHeight: "40px" }}>{p.name}</h4>
              <p style={{ color: "#b12704", fontSize: "18px", fontWeight: "bold" }}>₹{p.price}</p>
              <div style={{ display: "flex", alignItems: "center", marginBottom: "10px" }}>
                <span style={{ color: "#ffa41c" }}>{"★".repeat(Math.floor(p.rating))}</span>
                <span style={{ marginLeft: "5px", color: "#007185" }}>
                  {p.rating.toFixed(1)} ({p.reviews})
                </span>
              </div>
            </Link>
            
            <button 
              onClick={() => addToCart(p)} 
              style={{ 
                padding: "8px 16px", 
                cursor: "pointer",
                background: "#ffd814",
                border: "none",
                borderRadius: "20px",
                width: "100%",
                marginTop: "10px"
              }}
            >
              Add to Cart
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductList;
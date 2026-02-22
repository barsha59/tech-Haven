// src/components/ProductList.js
import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { API_URL, STRIPE_PUBLISHABLE_KEY } from '../config';

const ProductList = ({ addToCart }) => {
  const navigate = useNavigate();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [searchQuery, setSearchQuery] = useState(""); // 🔹 search query
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch products from API
  const fetchProducts = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_URL}/api/products`, {
        timeout: 10000,
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });

      if (!Array.isArray(response.data)) {
        setError("Invalid API response format");
        return;
      }

      // Transform data
      const transformed = response.data.map((p) => ({
        id: p.id,
        name: p.name,
        price: p.price,
        rating: p.rating || 4.0,
        reviews: p.review_count || p.reviews || 0,
        category: p.category || "Uncategorized",
        stock: p.stock || 0,
        image: p.image_url || p.image || "https://via.placeholder.com/200x200?text=No+Image",
        description: p.description || ""
      }));

      setProducts(transformed);

      // Unique categories
      const uniqueCats = [...new Set(transformed.map(p => p.category))];
      setCategories(uniqueCats);

    } catch (error) {
      console.error("Error fetching products:", error);
      setError(`Failed to load products: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // Category filter change
  const handleCategoryFilter = (category) => {
    setSelectedCategory(category);
  };

  // Filter products by search and category
  const filteredProducts = products.filter(p => {
    const matchesCategory = selectedCategory ? p.category === selectedCategory : true;
    const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (loading) return <div style={{ textAlign: "center", padding: "50px" }}>Loading products...</div>;
  if (error) return <div style={{ textAlign: "center", padding: "50px", color: "red" }}>{error}</div>;

  return (
    <div style={{ padding: "20px" }}>
      <h2>Products ({filteredProducts.length})</h2>

      {/* Search + Category */}
      <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f8f9fa", borderRadius: "5px", border: "1px solid #dee2e6" }}>
        {/* Search Bar */}
        <input
          type="text"
          placeholder="Search products..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={{
            padding: "10px",
            width: "100%",
            marginBottom: "10px",
            borderRadius: "5px",
            border: "1px solid #ced4da"
          }}
        />

        {/* Category Filter */}
        <div>
          <label style={{ marginRight: "10px", fontWeight: "bold" }}>Filter by Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => handleCategoryFilter(e.target.value)}
            style={{
              padding: "8px 12px",
              borderRadius: "4px",
              border: "1px solid #ced4da"
            }}
          >
            <option value="">All Categories ({products.length})</option>
            {categories.map(cat => {
              const count = products.filter(p => p.category === cat).length;
              return (
                <option key={cat} value={cat}>
                  {cat} ({count})
                </option>
              );
            })}
          </select>

          <button
            onClick={fetchProducts}
            style={{
              padding: "8px 16px",
              backgroundColor: "#28a745",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginLeft: "10px"
            }}
          >
            🔄 Refresh
          </button>
        </div>
      </div>

      {/* Product Grid */}
      {filteredProducts.length === 0 ? (
        <div style={{ textAlign: "center", padding: "50px" }}>
          <h3>No Products Found</h3>
          <p>Try changing your search or category filter.</p>
        </div>
      ) : (
        <div style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
          gap: "20px"
        }}>
          {filteredProducts.map(p => (
            <div
              key={p.id}
              style={{
                border: "1px solid #dee2e6",
                padding: "15px",
                borderRadius: "8px",
                boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                backgroundColor: "white",
                cursor: "pointer",
                transition: "transform 0.2s"
              }}
              onMouseEnter={e => e.currentTarget.style.transform = "translateY(-5px)"}
              onMouseLeave={e => e.currentTarget.style.transform = "translateY(0)"}
              onClick={() => navigate(`/product/${p.id}`)} // 🔹 click to detail
            >
              <div style={{
                height: "200px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginBottom: "15px",
                backgroundColor: "#f8f9fa",
                borderRadius: "4px",
                overflow: "hidden"
              }}>
                <img
                  src={p.image}
                  alt={p.name}
                  style={{ maxWidth: "100%", maxHeight: "100%", objectFit: "contain" }}
                  onError={(e) => e.target.src = "https://via.placeholder.com/200x200?text=No+Image"}
                />
              </div>

              <h4 style={{ margin: "0 0 10px 0", fontSize: "16px", minHeight: "40px" }}>{p.name}</h4>
              <p style={{ color: "#b12704", fontSize: "20px", fontWeight: "bold", margin: "0 0 10px 0" }}>₹{p.price}</p>
              <div style={{ display: "flex", alignItems: "center", marginBottom: "10px" }}>
                <span style={{ color: "#ffc107" }}>
                  {"★".repeat(Math.floor(p.rating))}{"☆".repeat(5 - Math.floor(p.rating))}
                </span>
                <span style={{ marginLeft: "8px", color: "#6c757d", fontSize: "14px" }}>
                  {p.rating?.toFixed(1)} ({p.reviews || 0} reviews)
                </span>
              </div>
              <div style={{
                display: "inline-block",
                padding: "4px 8px",
                backgroundColor: "#e9ecef",
                borderRadius: "12px",
                fontSize: "12px",
                color: "#495057",
                marginBottom: "15px"
              }}>
                {p.category}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  addToCart && addToCart(p);
                  alert(`Added ${p.name} to cart!`);
                }}
                style={{
                  padding: "10px",
                  cursor: "pointer",
                  background: "linear-gradient(to right, #ffd814, #f7ca00)",
                  border: "none",
                  borderRadius: "20px",
                  width: "100%",
                  fontSize: "14px",
                  fontWeight: "bold",
                  color: "#0F1111",
                  transition: "opacity 0.2s"
                }}
                onMouseEnter={e => e.currentTarget.style.opacity = "0.9"}
                onMouseLeave={e => e.currentTarget.style.opacity = "1"}
              >
                Add to Cart
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProductList;

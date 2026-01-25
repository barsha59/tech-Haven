import React, { useEffect, useState } from "react";
import axios from "axios";
import API_URL from "../config";

const ProductList = ({ addToCart }) => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Debug: Log when component mounts
  console.log("🔄 ProductList component mounted");
  console.log("📡 API_URL from config:", API_URL);
  console.log("🎯 addToCart prop:", typeof addToCart);

  useEffect(() => {
    console.log("🔍 useEffect triggered - fetching products");
    fetchProducts();
  }, []);

  // Debug: Log products state changes
  useEffect(() => {
    console.log("📦 Products state updated:", products);
    console.log("🔢 Number of products:", products.length);
    
    if (products.length > 0) {
      console.log("📝 First product details:", products[0]);
      console.log("🎨 First product image URL:", products[0].image || products[0].image_url || "NO IMAGE");
    }
  }, [products]);

  const fetchProducts = async () => {
    console.log("🚀 fetchProducts() called");
    setLoading(true);
    setError(null);
    
    try {
      console.log("🌐 Making API call to:", `${API_URL}/api/products`);
      
      const response = await axios.get(`${API_URL}/api/products`, {
        timeout: 10000,
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache'
        }
      });
      
      console.log("✅ API Response status:", response.status);
      console.log("📊 API Response data type:", typeof response.data);
      console.log("📄 API Response data:", response.data);
      
      if (!Array.isArray(response.data)) {
        console.error("❌ API response is not an array:", response.data);
        setError("Invalid API response format");
        return;
      }
      
      console.log(`📦 Received ${response.data.length} products from API`);
      
      if (response.data.length === 0) {
        console.log("⚠️ API returned empty array");
        setProducts([]);
        setCategories([]);
        setLoading(false);
        return;
      }
      
      // Check first product structure
      const firstProduct = response.data[0];
      console.log("🔍 First product from API:", firstProduct);
      console.log("🔑 Keys in first product:", Object.keys(firstProduct));
      console.log("🖼️ image_url exists:", 'image_url' in firstProduct);
      console.log("📊 review_count exists:", 'review_count' in firstProduct);
      
      // Transform data
      const transformed = response.data.map((p, index) => {
        const transformedProduct = {
          id: p.id,
          name: p.name,
          price: p.price,
          rating: p.rating || 4.0,
          reviews: p.review_count || p.reviews || 0,
          category: p.category || "Uncategorized",
          stock: p.stock || 0,
          image: p.image_url || p.image || "https://via.placeholder.com/200x200?text=No+Image",
          description: p.description || ""
        };
        
        if (index === 0) {
          console.log("🔄 Sample transformed product:", transformedProduct);
        }
        
        return transformedProduct;
      });
      
      console.log("✨ Transformed products:", transformed.length);
      
      setProducts(transformed);
      
      // Get unique categories
      const uniqueCats = [...new Set(transformed.map(p => p.category))];
      console.log("🏷️ Unique categories:", uniqueCats);
      setCategories(uniqueCats);
      
    } catch (error) {
      console.error("❌ Error in fetchProducts:", error);
      console.error("Error message:", error.message);
      console.error("Error response:", error.response?.data);
      console.error("Error status:", error.response?.status);
      
      setError(`Failed to load products: ${error.message}`);
      
      // Test with mock data to verify rendering works
      console.log("🛠️ Testing with mock data...");
      const mockProducts = [
        {
          id: 999,
          name: "Test Product",
          price: 99.99,
          rating: 4.5,
          reviews: 100,
          category: "Test",
          image: "https://via.placeholder.com/200x200?text=Test+Product",
          description: "This is a test product"
        }
      ];
      setProducts(mockProducts);
      setCategories(["Test"]);
    } finally {
      setLoading(false);
      console.log("🏁 fetchProducts completed");
    }
  };

  const handleCategoryFilter = (category) => {
    console.log("🎯 Category filter changed to:", category);
    setSelectedCategory(category);
    
    if (category) {
      // Show all products first, then filter
      fetchProducts().then(() => {
        const filtered = products.filter(p => p.category === category);
        console.log(`Filtered ${filtered.length} products for category: ${category}`);
        setProducts(filtered);
      });
    } else {
      fetchProducts();
    }
  };

  // Debug rendering
  console.log("🎨 Component rendering with:", {
    loading,
    error,
    productsCount: products.length,
    categoriesCount: categories.length,
    selectedCategory
  });

  if (loading) {
    return (
      <div style={{ 
        textAlign: "center", 
        padding: "50px",
        fontSize: "18px"
      }}>
        <div style={{ fontSize: "24px", marginBottom: "20px" }}>⏳</div>
        <p>Loading products...</p>
        <button 
          onClick={fetchProducts}
          style={{ 
            marginTop: "20px",
            padding: "10px 20px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        textAlign: "center", 
        padding: "50px",
        color: "#721c24",
        backgroundColor: "#f8d7da",
        border: "1px solid #f5c6cb",
        borderRadius: "5px",
        margin: "20px"
      }}>
        <h3>Error Loading Products</h3>
        <p>{error}</p>
        <button 
          onClick={fetchProducts}
          style={{ 
            marginTop: "20px",
            padding: "10px 20px",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: "5px",
            cursor: "pointer"
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div style={{ padding: "20px" }}>
      <h2>Products ({products.length})</h2>
      
      <div style={{ 
        marginBottom: "20px", 
        padding: "15px",
        backgroundColor: "#f8f9fa",
        borderRadius: "5px",
        border: "1px solid #dee2e6"
      }}>
        <div style={{ marginBottom: "10px" }}>
          <strong>Debug Info:</strong> Products: {products.length} | 
          Categories: {categories.length} | 
          API: {API_URL}
        </div>
        
        <div>
          <label style={{ marginRight: "10px", fontWeight: "bold" }}>
            Filter by Category: 
          </label>
          <select 
            value={selectedCategory} 
            onChange={(e) => handleCategoryFilter(e.target.value)}
            style={{ 
              padding: "8px 12px",
              marginRight: "10px",
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
              marginRight: "10px"
            }}
          >
            🔄 Refresh
          </button>
          
          <button 
            onClick={() => console.log("Current products:", products)}
            style={{ 
              padding: "8px 16px",
              backgroundColor: "#6c757d",
              color: "white",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer"
            }}
          >
            📋 Log Products
          </button>
        </div>
      </div>

      {products.length === 0 ? (
        <div style={{ 
          textAlign: "center", 
          padding: "50px",
          border: "2px dashed #dee2e6",
          borderRadius: "10px",
          backgroundColor: "#f8f9fa"
        }}>
          <div style={{ fontSize: "48px", marginBottom: "20px" }}>😕</div>
          <h3>No Products Found</h3>
          <p style={{ marginBottom: "20px" }}>
            The API returned {products.length} products.
          </p>
          <button 
            onClick={fetchProducts}
            style={{ 
              padding: "12px 24px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: "5px",
              cursor: "pointer",
              fontSize: "16px"
            }}
          >
            Load Products Again
          </button>
        </div>
      ) : (
        <div>
          <div style={{ 
            display: "grid", 
            gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))",
            gap: "20px" 
          }}>
            {products.map(p => (
              <div 
                key={p.id} 
                style={{ 
                  border: "1px solid #dee2e6", 
                  padding: "15px", 
                  borderRadius: "8px",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
                  backgroundColor: "white",
                  transition: "transform 0.2s",
                  cursor: "pointer"
                }}
                onMouseEnter={e => e.currentTarget.style.transform = "translateY(-5px)"}
                onMouseLeave={e => e.currentTarget.style.transform = "translateY(0)"}
                onClick={() => console.log("Product clicked:", p)}
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
                    style={{ 
                      maxWidth: "100%",
                      maxHeight: "100%",
                      objectFit: "contain"
                    }}
                    onError={(e) => {
                      console.log("Image failed to load for:", p.name);
                      e.target.src = "https://via.placeholder.com/200x200?text=No+Image";
                    }}
                  />
                </div>
                
                <h4 style={{ 
                  margin: "0 0 10px 0", 
                  fontSize: "16px",
                  minHeight: "40px",
                  color: "#212529"
                }}>
                  {p.name}
                </h4>
                
                <p style={{ 
                  color: "#b12704", 
                  fontSize: "20px", 
                  fontWeight: "bold",
                  margin: "0 0 10px 0"
                }}>
                  ₹{p.price}
                </p>
                
                <div style={{ 
                  display: "flex", 
                  alignItems: "center",
                  marginBottom: "10px"
                }}>
                  <span style={{ color: "#ffc107" }}>
                    {"★".repeat(Math.floor(p.rating))}
                    {"☆".repeat(5 - Math.floor(p.rating))}
                  </span>
                  <span style={{ 
                    marginLeft: "8px", 
                    color: "#6c757d",
                    fontSize: "14px"
                  }}>
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
                    console.log("Add to cart clicked for:", p.name);
                    if (addToCart) {
                      addToCart(p);
                      alert(`Added ${p.name} to cart!`);
                    } else {
                      console.error("addToCart function not provided!");
                    }
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
        </div>
      )}
    </div>
  );
};

export default ProductList;
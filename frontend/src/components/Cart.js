import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";

const Cart = () => {
  const [cart, setCart] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const storedCart = JSON.parse(localStorage.getItem("cart")) || [];
    setCart(storedCart);
  }, []);

  // Update cart in state and localStorage
  const updateCart = (newCart) => {
    setCart(newCart);
    localStorage.setItem("cart", JSON.stringify(newCart));
  };

  const increaseQuantity = (productId) => {
    const newCart = cart.map(item =>
      item.id === productId ? { ...item, quantity: item.quantity + 1 } : item
    );
    updateCart(newCart);
  };

  const decreaseQuantity = (productId) => {
    const newCart = cart.map(item =>
      item.id === productId && item.quantity > 1
        ? { ...item, quantity: item.quantity - 1 }
        : item
    );
    updateCart(newCart);
  };

  const removeItem = (productId) => {
    if (window.confirm("Are you sure you want to remove this item from cart?")) {
      const newCart = cart.filter(item => item.id !== productId);
      updateCart(newCart);
    }
  };

  const clearCart = () => {
    if (window.confirm("Are you sure you want to clear your entire cart?")) {
      updateCart([]);
    }
  };

  const totalPrice = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
  const totalItems = cart.reduce((acc, item) => acc + item.quantity, 0);

  return (
    <div style={{ 
      maxWidth: "1200px", 
      margin: "0 auto", 
      padding: "20px",
      fontFamily: "Arial, sans-serif"
    }}>
      <h1 style={{ 
        color: "#232f3e", 
        borderBottom: "2px solid #ffa41c", 
        paddingBottom: "10px",
        marginBottom: "30px"
      }}>
        🛒 Your Shopping Cart
      </h1>
      
      {cart.length === 0 ? (
        <div style={{ 
          textAlign: "center", 
          padding: "60px 20px",
          backgroundColor: "#f8f9fa",
          borderRadius: "10px",
          border: "2px dashed #ddd"
        }}>
          <div style={{ fontSize: "60px", marginBottom: "20px" }}>🛒</div>
          <h3 style={{ color: "#555", marginBottom: "15px" }}>Your cart is empty</h3>
          <p style={{ color: "#777", marginBottom: "25px" }}>Add some amazing products to your cart!</p>
          <Link to="/products">
            <button style={{
              padding: "12px 30px",
              backgroundColor: "#ffa41c",
              color: "white",
              border: "none",
              borderRadius: "25px",
              fontSize: "16px",
              cursor: "pointer",
              fontWeight: "bold"
            }}>
              Continue Shopping
            </button>
          </Link>
        </div>
      ) : (
        <div style={{ display: "flex", gap: "30px", flexWrap: "wrap" }}>
          {/* Cart Items Section */}
          <div style={{ flex: "1", minWidth: "300px" }}>
            <div style={{ 
              display: "flex", 
              justifyContent: "space-between",
              alignItems: "center",
              marginBottom: "20px"
            }}>
              <h3 style={{ color: "#232f3e" }}>
                Cart Items ({totalItems} {totalItems === 1 ? 'item' : 'items'})
              </h3>
              <button
                onClick={clearCart}
                style={{
                  padding: "8px 15px",
                  backgroundColor: "#ff6b6b",
                  color: "white",
                  border: "none",
                  borderRadius: "5px",
                  cursor: "pointer",
                  fontSize: "14px"
                }}
              >
                Clear Cart
              </button>
            </div>

            {cart.map(item => (
              <div key={item.id} style={{ 
                display: "flex",
                border: "1px solid #e0e0e0",
                borderRadius: "10px",
                padding: "20px",
                marginBottom: "20px",
                backgroundColor: "white",
                boxShadow: "0 2px 10px rgba(0,0,0,0.05)",
                alignItems: "center",
                gap: "20px"
              }}>
                {/* Product Image */}
                <div style={{ flex: "0 0 100px" }}>
                  <img 
                    src={item.image || "https://via.placeholder.com/100"} 
                    alt={item.name}
                    style={{ 
                      width: "100px", 
                      height: "100px", 
                      objectFit: "cover",
                      borderRadius: "8px"
                    }}
                  />
                </div>
                
                {/* Product Details */}
                <div style={{ flex: "1" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}>
                    <h4 style={{ margin: "0 0 10px 0", color: "#232f3e" }}>
                      {item.name}
                    </h4>
                    <button
                      onClick={() => removeItem(item.id)}
                      style={{
                        background: "transparent",
                        border: "none",
                        color: "#ff6b6b",
                        cursor: "pointer",
                        fontSize: "18px",
                        padding: "5px"
                      }}
                      title="Remove item"
                    >
                      ✕
                    </button>
                  </div>
                  
                  <p style={{ color: "#b12704", fontSize: "18px", fontWeight: "bold", margin: "10px 0" }}>
                    ₹{item.price}
                  </p>
                  
                  {/* Quantity Controls */}
                  <div style={{ 
                    display: "flex", 
                    alignItems: "center", 
                    gap: "10px",
                    marginTop: "15px"
                  }}>
                    <span style={{ color: "#555" }}>Quantity:</span>
                    <div style={{ 
                      display: "flex", 
                      alignItems: "center",
                      border: "1px solid #ddd",
                      borderRadius: "5px",
                      overflow: "hidden"
                    }}>
                      <button 
                        onClick={() => decreaseQuantity(item.id)}
                        style={{ 
                          padding: "8px 15px",
                          backgroundColor: "#f0f2f2",
                          border: "none",
                          cursor: "pointer",
                          fontSize: "16px",
                          fontWeight: "bold"
                        }}
                      >
                        −
                      </button>
                      <span style={{ 
                        padding: "8px 20px",
                        backgroundColor: "white",
                        minWidth: "50px",
                        textAlign: "center",
                        fontWeight: "bold"
                      }}>
                        {item.quantity}
                      </span>
                      <button 
                        onClick={() => increaseQuantity(item.id)}
                        style={{ 
                          padding: "8px 15px",
                          backgroundColor: "#f0f2f2",
                          border: "none",
                          cursor: "pointer",
                          fontSize: "16px",
                          fontWeight: "bold"
                        }}
                      >
                        +
                      </button>
                    </div>
                  </div>
                  
                  <div style={{ marginTop: "15px" }}>
                    <p style={{ color: "#555", fontSize: "16px" }}>
                      Subtotal: <span style={{ color: "#b12704", fontWeight: "bold" }}>
                        ₹{item.price * item.quantity}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Order Summary Section */}
          <div style={{ 
            flex: "0 0 350px",
            backgroundColor: "#f8f9fa",
            borderRadius: "10px",
            padding: "25px",
            height: "fit-content"
          }}>
            <h3 style={{ 
              color: "#232f3e", 
              borderBottom: "1px solid #ddd", 
              paddingBottom: "15px",
              marginBottom: "20px"
            }}>
              Order Summary
            </h3>
            
            <div style={{ marginBottom: "20px" }}>
              <div style={{ 
                display: "flex", 
                justifyContent: "space-between",
                marginBottom: "10px"
              }}>
                <span style={{ color: "#555" }}>Subtotal ({totalItems} items):</span>
                <span style={{ fontWeight: "bold" }}>₹{totalPrice}</span>
              </div>
              
              <div style={{ 
                display: "flex", 
                justifyContent: "space-between",
                marginBottom: "10px"
              }}>
                <span style={{ color: "#555" }}>Shipping:</span>
                <span style={{ color: "#007600", fontWeight: "bold" }}>FREE</span>
              </div>
              
              <div style={{ 
                display: "flex", 
                justifyContent: "space-between",
                marginBottom: "15px"
              }}>
                <span style={{ color: "#555" }}>Tax:</span>
                <span>₹{(totalPrice * 0.18).toFixed(2)}</span>
              </div>
              
              <div style={{ 
                display: "flex", 
                justifyContent: "space-between",
                borderTop: "2px solid #ddd",
                paddingTop: "15px",
                marginTop: "15px",
                fontSize: "18px",
                fontWeight: "bold"
              }}>
                <span>Total:</span>
                <span style={{ color: "#b12704", fontSize: "20px" }}>
                  ₹{(totalPrice * 1.18).toFixed(2)}
                </span>
              </div>
            </div>
            
            <button 
              onClick={() => navigate("/checkout")}
              style={{
                width: "100%",
                padding: "15px",
                backgroundColor: "#ffa41c",
                color: "white",
                border: "none",
                borderRadius: "25px",
                fontSize: "16px",
                cursor: "pointer",
                fontWeight: "bold",
                marginBottom: "15px",
                transition: "background-color 0.3s"
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = "#ff9900"}
              onMouseOut={(e) => e.target.style.backgroundColor = "#ffa41c"}
            >
              Proceed to Checkout
            </button>
            
            <Link to="/products">
              <button
                style={{
                  width: "100%",
                  padding: "12px",
                  backgroundColor: "transparent",
                  color: "#232f3e",
                  border: "1px solid #ddd",
                  borderRadius: "25px",
                  fontSize: "16px",
                  cursor: "pointer",
                  marginTop: "10px"
                }}
              >
                Continue Shopping
              </button>
            </Link>
            
            <div style={{ 
              marginTop: "25px", 
              padding: "15px",
              backgroundColor: "#e8f4f8",
              borderRadius: "8px",
              fontSize: "14px",
              color: "#007185"
            }}>
              <p style={{ margin: "0 0 10px 0", fontWeight: "bold" }}>
                💳 Secure Checkout
              </p>
              <p style={{ margin: "0", fontSize: "13px" }}>
                Your payment information is encrypted and secure. We accept all major credit cards.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
// src/components/Navbar.js
import React from "react";
import { Link, useNavigate } from "react-router-dom";

const Navbar = ({ user, onLogout, cartCount }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    onLogout();
    navigate("/");
  };

  return (
    <nav style={{
      background: "#232f3e",
      color: "white",
      padding: "10px 20px",
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center"
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: "30px" }}>
        <Link to="/products" style={{ color: "white", textDecoration: "none", fontSize: "20px" }}>
          🛍️  Tech Haven
        </Link>
        
        <div style={{ display: "flex", gap: "15px" }}>
          <Link to="/products" style={{ color: "white", textDecoration: "none" }}>
            Home
          </Link>
          <Link to="/cart" style={{ color: "white", textDecoration: "none" }}>
            Cart ({cartCount || 0})
          </Link>
          {/* WISHLIST LINK ADDED HERE */}
          <Link to="/wishlist" style={{ color: "white", textDecoration: "none" }}>
            ❤️ Wishlist
          </Link>
        </div>
      </div>
      
      <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
        {user ? (
          <>
            <span>Welcome, {user.name}!</span>
            <button 
              onClick={handleLogout}
              style={{
                padding: "5px 15px",
                background: "#ff6b6b",
                color: "white",
                border: "none",
                borderRadius: "3px",
                cursor: "pointer"
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login" style={{ color: "white", textDecoration: "none" }}>
              Login
            </Link>
            <Link to="/register">
              <button style={{
                padding: "5px 15px",
                background: "#4CAF50",
                color: "white",
                border: "none",
                borderRadius: "3px",
                cursor: "pointer"
              }}>
                Sign Up
              </button>
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;

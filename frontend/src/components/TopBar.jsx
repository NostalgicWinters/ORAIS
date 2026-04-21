// TopBar.jsx
import React from "react";

export default function TopBar({ activeTab, setActiveTab }) {
  const navItems = ["overview", "inventory", "orders", "suppliers"];

  return (
    <header style={{ padding: "10px 20px", borderBottom: "1px solid #222" }}>
      {navItems.map((item) => (
        <button
          key={item}
          onClick={() => setActiveTab(item)}
          style={{
            marginRight: 10,
            color: activeTab === item ? "orange" : "gray",
          }}
        >
          {item}
        </button>
      ))}
    </header>
  );
}
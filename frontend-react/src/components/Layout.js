import React from "react";
import "./Layout.css";

function Layout({ children }) {
  return (
    <div className="layout">
      <header className="layout-header">
        <h1>AI Claims Triage</h1>
      </header>

      <main className="layout-content">
        {children}
      </main>

      <footer className="layout-footer">
        <p>© 2026 AI Claims Triage</p>
      </footer>
    </div>
  );
}

export default Layout;

import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import ClaimForm from './components/ClaimForm';
import Dashboard from './components/Dashboard';
import ClaimDetail from './components/ClaimDetail';
import './App.css';

// Main App Component (after authentication)
function AuthenticatedApp() {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [apiStatus, setApiStatus] = useState('checking...');

  useEffect(() => {
    // Check backend health
    const checkHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setApiStatus('✅ Connected');
        } else {
          setApiStatus('❌ Disconnected');
        }
      } catch (err) {
        setApiStatus('❌ Disconnected');
      }
    };
    checkHealth();
  }, []);

  const handleLogout = async () => {
    await logout();
  };

  const isActive = (path) => location.pathname === path;

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-content">
          <h1>🏥 Claims Triage System</h1>
          <div className="header-right">
            <span className="api-status">{apiStatus}</span>
            <span className="user-info">
              👤 {user?.full_name} ({user?.role})
            </span>
            <button onClick={handleLogout} className="logout-btn">
              Logout
            </button>
          </div>
        </div>

        <nav className="app-nav">
          <Link to="/dashboard">
            <button className={isActive('/dashboard') ? 'active' : ''}>
              📊 Dashboard
            </button>
          </Link>
          {user?.role === 'customer' && (
            <Link to="/submit">
              <button className={isActive('/submit') ? 'active' : ''}>
                ➕ Submit Claim
              </button>
            </Link>
          )}
        </nav>
      </header>

      <main>
        <div className="page">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/submit" element={<ClaimForm />} />
            <Route path="/claims/:claimId" element={<ClaimDetail />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

// Root App with Auth Check
function App() {
  const [authMode, setAuthMode] = useState('login'); // 'login' or 'register'

  return (
    <Router>
      <AuthProvider>
        <AppContent authMode={authMode} setAuthMode={setAuthMode} />
      </AuthProvider>
    </Router>
  );
}

function AppContent({ authMode, setAuthMode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <>
        {authMode === 'login' ? (
          <Login onSwitchToRegister={() => setAuthMode('register')} />
        ) : (
          <Register onSwitchToLogin={() => setAuthMode('login')} />
        )}
      </>
    );
  }

  return <AuthenticatedApp />;
}

export default App;
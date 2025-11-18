import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LandingPage from './components/LandingPage';
import Login from './components/Auth/Login';
import CustomerLogin from './components/Auth/CustomerLogin';
import AdminLogin from './components/Auth/AdminLogin';
import Register from './components/Auth/Register';
import CustomerClaimForm from './components/customer/ClaimForm';
import CompanyClaimForm from './components/company/ClaimForm';
import CustomerDashboard from './components/customer/Dashboard';
import CompanyDashboard from './components/company/Dashboard';
import CompanyAllClaims from './components/company/AllClaims';
import CompanyAnalytics from './components/company/Analytics';
import Sidebar from './components/Sidebar';
import CustomerClaimDetail from './components/customer/ClaimDetail';
import CompanyClaimDetail from './components/company/ClaimDetail';
import './App.css';

// Main App Component (after authentication)
function AuthenticatedApp() {
  const { user, logout } = useAuth();
  const location = useLocation();

  const { isCustomer, isCompanyStaff } = useAuth();

  const DashboardToRender = isCompanyStaff ? CompanyDashboard : CustomerDashboard;
  const ClaimFormToRender = isCompanyStaff ? CompanyClaimForm : CustomerClaimForm;
  const ClaimDetailToRender = isCompanyStaff ? CompanyClaimDetail : CustomerClaimDetail;

  return (
    <div className="App">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardToRender />} />
          <Route path="/submit" element={<ClaimFormToRender />} />
          <Route path="/claims/:claimId" element={<ClaimDetailToRender />} />
          {isCompanyStaff && (
            <>
              <Route path="/claims" element={<CompanyAllClaims />} />
              <Route path="/analytics" element={<CompanyAnalytics />} />
            </>
          )}
        </Routes>
      </main>
    </div>
  );
}

// Root App with Auth Check
function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Navigate to="/login/customer" replace />} />
          <Route path="/login/customer" element={<CustomerLoginWrapper />} />
          <Route path="/login/admin" element={<AdminLoginWrapper />} />
          <Route path="/register" element={<RegisterWrapper />} />
          <Route path="/*" element={<ProtectedRoutes />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

function CustomerLoginWrapper() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <CustomerLogin />;
}

function AdminLoginWrapper() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <AdminLogin />;
}

function LoginWrapper() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Login />;
}

function RegisterWrapper() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Register />;
}

function ProtectedRoutes() {
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
    return <Navigate to="/login/customer" replace />;
  }

  return <AuthenticatedApp />;
}

export default App;
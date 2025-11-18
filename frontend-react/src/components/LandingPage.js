import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      <div className="landing-hero">
        <div className="hero-content">
          <h1>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px', display: 'inline-block', verticalAlign: 'middle', marginRight: '12px' }}>
              <path d="M3 21h18" />
              <path d="M5 21V7l8-4v18" />
              <path d="M19 21V11l-6-4" />
              <path d="M9 9v.01" />
              <path d="M9 12v.01" />
              <path d="M9 15v.01" />
              <path d="M9 18v.01" />
            </svg>
            AI Claims Triage System
          </h1>
          <p className="hero-subtitle">
            Intelligent insurance claims processing powered by machine learning
          </p>
          <p className="hero-description">
            Fast, accurate, and transparent claim assessment with real-time risk analysis
          </p>
        </div>
      </div>

      <div className="login-options">
        <div className="login-cards">
          <div className="login-card customer">
            <div className="card-header">
              <div className="card-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '48px', height: '48px' }}>
                  <circle cx="12" cy="8" r="5" />
                  <path d="M20 21a8 8 0 1 0-16 0" />
                </svg>
              </div>
              <h2>Customer Portal</h2>
            </div>
            <div className="card-body">
              <p>Submit and track your insurance claims</p>
              <ul className="features-list">
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> Submit new claims</li>
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> Upload supporting documents</li>
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> Track claim status</li>
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> View processing timeline</li>
              </ul>
              <button 
                className="login-btn customer-btn"
                onClick={() => navigate('/login/customer')}
              >
                Customer Login
              </button>
            </div>
            <div className="demo-info">
              <p><strong>Demo Account:</strong></p>
              <p>customer@demo.com / password123</p>
            </div>
          </div>

          <div className="login-card admin">
            <div className="card-header">
              <div className="card-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '48px', height: '48px' }}>
                  <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                </svg>
              </div>
              <h2>Admin Portal</h2>
            </div>
            <div className="card-body">
              <p>Manage claims and view analytics</p>
              <ul className="features-list">
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> Review all claims</li>
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> AI risk assessments</li>
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> Real-time dashboard</li>
                <li><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}><path d="M20 6 9 17l-5-5" /></svg> Performance analytics</li>
              </ul>
              <button 
                className="login-btn admin-btn"
                onClick={() => navigate('/login/admin')}
              >
                Admin Login
              </button>
            </div>
            <div className="demo-info">
              <p><strong>Demo Accounts:</strong></p>
              <p>admin@demo.com / admin123</p>
              <p>staff@demo.com / staff123</p>
            </div>
          </div>
        </div>
      </div>

      <div className="landing-features">
        <div className="feature-grid">
          <div className="feature-item">
            <div className="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '48px', height: '48px' }}>
                <rect x="4" y="4" width="16" height="16" rx="2" />
                <rect x="9" y="9" width="6" height="6" />
                <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
              </svg>
            </div>
            <h3>AI-Powered Analysis</h3>
            <p>Advanced machine learning models analyze claims for fraud detection and risk assessment</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '48px', height: '48px' }}>
                <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
              </svg>
            </div>
            <h3>Real-time Processing</h3>
            <p>Instant claim evaluation with immediate risk scoring and processing recommendations</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '48px', height: '48px' }}>
                <path d="M3 3v18h18" />
                <path d="M18 17V9M13 17V5M8 17v-3" />
              </svg>
            </div>
            <h3>Comprehensive Dashboard</h3>
            <p>Complete overview of claims, statistics, and performance metrics in one place</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '48px', height: '48px' }}>
                <rect x="3" y="11" width="18" height="11" rx="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
            <h3>Secure & Compliant</h3>
            <p>Enterprise-grade security with full audit trails and compliance reporting</p>
          </div>
        </div>
      </div>

      <footer className="landing-footer">
        <p>&copy; 2024 AI Claims Triage System. Built with advanced ML models for intelligent claim processing.</p>
      </footer>
    </div>
  );
};

export default LandingPage;
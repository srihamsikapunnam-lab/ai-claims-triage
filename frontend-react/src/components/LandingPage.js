import React from 'react';
import { useNavigate } from 'react-router-dom';
import './LandingPage.css';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="landing-container">
      <div className="landing-hero">
        <div className="hero-content">
          <h1>🏥 AI Claims Triage System</h1>
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
              <div className="card-icon">👤</div>
              <h2>Customer Portal</h2>
            </div>
            <div className="card-body">
              <p>Submit and track your insurance claims</p>
              <ul className="features-list">
                <li>✓ Submit new claims</li>
                <li>✓ Upload supporting documents</li>
                <li>✓ Track claim status</li>
                <li>✓ View processing timeline</li>
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
              <div className="card-icon">⚡</div>
              <h2>Admin Portal</h2>
            </div>
            <div className="card-body">
              <p>Manage claims and view analytics</p>
              <ul className="features-list">
                <li>✓ Review all claims</li>
                <li>✓ AI risk assessments</li>
                <li>✓ Real-time dashboard</li>
                <li>✓ Performance analytics</li>
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
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Advanced machine learning models analyze claims for fraud detection and risk assessment</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">⚡</div>
            <h3>Real-time Processing</h3>
            <p>Instant claim evaluation with immediate risk scoring and processing recommendations</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">📊</div>
            <h3>Comprehensive Dashboard</h3>
            <p>Complete overview of claims, statistics, and performance metrics in one place</p>
          </div>
          <div className="feature-item">
            <div className="feature-icon">🔒</div>
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
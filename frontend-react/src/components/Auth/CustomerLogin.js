import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Auth.css';

const CustomerLogin = () => {
  const { login, error } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [localError, setLocalError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setLocalError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setLocalError('');

    try {
      const result = await login(formData.email, formData.password);
      // Check if user is actually a customer
      if (result.user.role !== 'customer') {
        setLocalError('This login is for customers only. Please use the admin portal.');
        setIsLoading(false);
        return;
      }
      // Navigation handled by App.js based on auth state
    } catch (err) {
      setLocalError(err.message || 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-container customer-auth">
      <div className="auth-card">
        <div className="auth-header">
          <button 
            className="back-btn"
            onClick={() => navigate('/')}
          >
            ← Back
          </button>
        </div>
        
        <h2>👤 Customer Login</h2>
        <p className="auth-subtitle">Access your insurance claims dashboard</p>

        {(localError || error) && (
          <div className="error-message">
            {localError || error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="your.email@example.com"
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          <button 
            type="submit" 
            className="auth-button customer-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login as Customer'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Don't have an account?{' '}
            <button 
              onClick={() => navigate('/register')}
              className="link-button"
            >
              Register here
            </button>
          </p>
          <p>
            Are you an admin?{' '}
            <button 
              onClick={() => navigate('/login/admin')}
              className="link-button"
            >
              Admin Login
            </button>
          </p>
        </div>

        <div className="demo-credentials">
          <p><strong>Demo Customer Account:</strong></p>
          <p>customer@demo.com / password123</p>
        </div>
      </div>
    </div>
  );
};

export default CustomerLogin;
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './Auth.css';

const AdminLogin = () => {
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
      // Check if user is actually an admin/staff
      if (!['company_admin', 'company_staff'].includes(result.user.role)) {
        setLocalError('This login is for admin/staff only. Please use the customer portal.');
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
    <div className="auth-container admin-auth">
      <div className="auth-card">
        <div className="auth-header">
          <button 
            className="back-btn"
            onClick={() => navigate('/')}
          >
            ← Back
          </button>
        </div>
        
        <h2>⚡ Admin Login</h2>
        <p className="auth-subtitle">Access the claims management dashboard</p>

        {(localError || error) && (
          <div className="error-message">
            {localError || error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Admin Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="admin@company.com"
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
              placeholder="Enter your admin password"
            />
          </div>

          <button 
            type="submit" 
            className="auth-button admin-btn"
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login as Admin'}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Are you a customer?{' '}
            <button 
              onClick={() => navigate('/login/customer')}
              className="link-button"
            >
              Customer Login
            </button>
          </p>
        </div>

        <div className="demo-credentials">
          <p><strong>Demo Admin Accounts:</strong></p>
          <p>admin@demo.com / admin123</p>
          <p>staff@demo.com / staff123</p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;
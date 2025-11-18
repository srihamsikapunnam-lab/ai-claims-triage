import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../utils/apiClient';
import '../ClaimForm.css';

const ClaimFormCustomer = ({ onClaimCreated }) => {
  const { } = useAuth();
  const navigate = useNavigate();
  
  // Sidebar state
  const [sidebarExpanded, setSidebarExpanded] = useState(false);
  
  // Listen for sidebar state changes
  useEffect(() => {
    const handleSidebarToggle = (e) => {
      setSidebarExpanded(e.detail?.expanded || false);
    };
    
    window.addEventListener('sidebarToggle', handleSidebarToggle);
    
    return () => {
      window.removeEventListener('sidebarToggle', handleSidebarToggle);
    };
  }, []);
  const [formData, setFormData] = useState({
    patient_age: '',
    diagnosis: '',
    admission_date: '',
    discharge_date: '',
    claimed_amount: '',
    description: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const claimData = {
        patient_age: parseInt(formData.patient_age),
        diagnosis: formData.diagnosis,
        admission_date: formData.admission_date,
        discharge_date: formData.discharge_date,
        claimed_amount: parseFloat(formData.claimed_amount),
        description: formData.description
      };

      const result = await apiClient.post('/claims', claimData);
      
      setSuccess(
        <span>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
            <path d="M20 6 9 17l-5-5" />
          </svg>
          Claim submitted successfully! Claim ID: {result.id}
        </span>
      );
      
      if (onClaimCreated) {
        onClaimCreated(result);
      }

      // Redirect to dashboard after 1.5 seconds
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
    } catch (err) {
      setError(err.message || 'Failed to submit claim');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`claim-form-container ${sidebarExpanded ? 'sidebar-expanded' : ''}`}>
      <div className="form-header">
        <h1>Submit Medical Insurance Claim</h1>
        <p className="form-subtitle">Submit your claim for AI-powered fraud detection analysis</p>
      </div>
      
      <div className="form-wrapper">
        <div className="claim-form">

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {success && (
        <div className="success-message">
          {success}
          <p>Redirecting to dashboard...</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Patient Age *</label>
            <input
              type="number"
              name="patient_age"
              value={formData.patient_age}
              onChange={handleChange}
              required
              min="0"
              max="120"
              placeholder="Patient's age"
            />
          </div>

          <div className="form-group">
            <label>Claimed Amount (₹) *</label>
            <input
              type="number"
              name="claimed_amount"
              value={formData.claimed_amount}
              onChange={handleChange}
              required
              min="0"
              step="0.01"
              placeholder="e.g., 5000.00"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Diagnosis *</label>
          <input
            type="text"
            name="diagnosis"
            value={formData.diagnosis}
            onChange={handleChange}
            required
            placeholder="Medical diagnosis or condition"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Admission Date *</label>
            <input
              type="date"
              name="admission_date"
              value={formData.admission_date}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Discharge Date *</label>
            <input
              type="date"
              name="discharge_date"
              value={formData.discharge_date}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label>Additional Details</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="4"
            placeholder="Any additional information about the treatment or claim..."
          />
        </div>

        <button 
          type="submit" 
          className="submit-btn"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
                <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z" />
                <path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z" />
                <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0" />
                <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5" />
              </svg>
              Submit Claim for AI Review
            </>
          )}
        </button>
      </form>
        </div>
      </div>
    </div>
  );
};

export default ClaimFormCustomer;

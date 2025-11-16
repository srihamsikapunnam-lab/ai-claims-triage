import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/apiClient';
import './ClaimForm.css';

const ClaimForm = ({ onClaimCreated }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
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
      
      setSuccess(`✅ Claim submitted successfully! Claim ID: ${result.id}`);
      
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
    <div className="claim-form">
      <h2>Submit Medical Insurance Claim</h2>
      <p className="form-subtitle">Submit your claim for AI-powered fraud detection analysis</p>

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
            <label>Claimed Amount ($) *</label>
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
          {isSubmitting ? 'Submitting...' : '🚀 Submit Claim for AI Review'}
        </button>
      </form>
    </div>
  );
};

export default ClaimForm;
import React, { useState } from 'react';
<<<<<<< HEAD
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/apiClient';
import './ClaimForm.css';
=======
import './ClaimForm.css'; // Make sure you have this CSS file
>>>>>>> 5b062dd277aa485a60ac8b8567e98ee819c1ff61

const ClaimForm = ({ onClaimCreated }) => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
<<<<<<< HEAD
    patient_age: '',
    diagnosis: '',
    admission_date: '',
    discharge_date: '',
    claimed_amount: '',
    description: ''
=======
    patientName: '',
    dateOfIncident: '',
    description: '',
    claimType: '',
    amount: ''
>>>>>>> 5b062dd277aa485a60ac8b8567e98ee819c1ff61
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
<<<<<<< HEAD
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
=======
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
>>>>>>> 5b062dd277aa485a60ac8b8567e98ee819c1ff61
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
<<<<<<< HEAD
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
=======
    // Add your form submission logic here
    console.log('Form submitted:', formData);
    // Add API call for AI review here
  };

  return (
    <div className="claim-form-container">
      <h2>Submit Insurance Claim</h2>
      <form onSubmit={handleSubmit} className="claim-form">
        <div className="form-group">
          <label htmlFor="patientName">Patient Name</label>
          <input
            type="text"
            id="patientName"
            name="patientName"
            value={formData.patientName}
            onChange={handleChange}
            required
            placeholder="Enter patient's full name"
          />
        </div>

        <div className="form-group">
          <label htmlFor="dateOfIncident">Date of Incident</label>
          <input
            type="date"
            id="dateOfIncident"
            name="dateOfIncident"
            value={formData.dateOfIncident}
>>>>>>> 5b062dd277aa485a60ac8b8567e98ee819c1ff61
            onChange={handleChange}
            required
            placeholder="Medical diagnosis or condition"
          />
        </div>

<<<<<<< HEAD
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
=======
        <div className="form-group">
          <label htmlFor="claimType">Claim Type</label>
          <select
            id="claimType"
            name="claimType"
            value={formData.claimType}
            onChange={handleChange}
            required
          >
            <option value="">Select claim type</option>
            <option value="medical">Medical Treatment</option>
            <option value="accident">Accident</option>
            <option value="property">Property Damage</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="amount">Claim Amount ($)</label>
          <input
            type="number"
            id="amount"
            name="amount"
            value={formData.amount}
            onChange={handleChange}
            required
            placeholder="Enter claim amount"
            min="0"
            step="0.01"
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Incident Description</label>
>>>>>>> 5b062dd277aa485a60ac8b8567e98ee819c1ff61
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="4"
<<<<<<< HEAD
            placeholder="Any additional information about the treatment or claim..."
=======
            required
            placeholder="Describe the incident, treatment, or damages in detail..."
>>>>>>> 5b062dd277aa485a60ac8b8567e98ee819c1ff61
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
import React, { useState } from 'react';
import './ClaimForm.css';

const ClaimForm = () => {
  const [formData, setFormData] = useState({
    policyNumber: '',
    claimType: 'auto',
    claimAmount: '',
    incidentDate: '',
    description: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Claim submitted successfully!');
    console.log('Form data:', formData);
  };

  return (
    <div className="claim-form">
      <h2>Submit Insurance Claim</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Policy Number *</label>
          <input
            type="text"
            name="policyNumber"
            value={formData.policyNumber}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Claim Type *</label>
          <select name="claimType" value={formData.claimType} onChange={handleChange}>
            <option value="auto">Auto</option>
            <option value="home">Home</option>
            <option value="health">Health</option>
          </select>
        </div>

        <div className="form-group">
          <label>Claim Amount ($) *</label>
          <input
            type="number"
            name="claimAmount"
            value={formData.claimAmount}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Incident Date *</label>
          <input
            type="date"
            name="incidentDate"
            value={formData.incidentDate}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Description *</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="4"
            required
            placeholder="Describe the incident, treatment, or damages..."
          />
        </div>

        <button type="submit" className="submit-btn">
          Submit Claim for AI Review
        </button>
      </form>
    </div>
  );
};

export default ClaimForm;
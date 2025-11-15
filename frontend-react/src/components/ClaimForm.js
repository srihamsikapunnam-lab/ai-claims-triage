import React, { useState } from 'react';
import './ClaimForm.css'; // Make sure you have this CSS file

const ClaimForm = () => {
  const [formData, setFormData] = useState({
    patientName: '',
    dateOfIncident: '',
    description: '',
    claimType: '',
    amount: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevState => ({
      ...prevState,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
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
            onChange={handleChange}
            required
          />
        </div>

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
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows="4"
            required
            placeholder="Describe the incident, treatment, or damages in detail..."
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
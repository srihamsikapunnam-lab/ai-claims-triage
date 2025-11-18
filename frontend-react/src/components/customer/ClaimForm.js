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
    patient_name: '',
    patient_age: '',
    diagnosis: '',
    admission_date: '',
    discharge_date: '',
    claimed_amount: '',
    description: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [verificationInfo, setVerificationInfo] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
    setVerificationInfo(null);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf', 'text/plain'];
      if (!allowedTypes.includes(file.type)) {
        setError('Only JPG, PNG, PDF, and TXT files are allowed');
        e.target.value = '';
        return;
      }
      
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        e.target.value = '';
        return;
      }
      
      setSelectedFile(file);
      setError('');
      setVerificationInfo(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate file is selected
    if (!selectedFile) {
      setError('Please upload a supporting document (medical bill/receipt)');
      return;
    }
    
    setIsSubmitting(true);
    setError('');
    setSuccess('');
    setVerificationInfo(null);

    try {
      // Create FormData for file upload
      const formDataToSend = new FormData();
      formDataToSend.append('file', selectedFile);
      formDataToSend.append('patient_name', formData.patient_name);
      formDataToSend.append('patient_age', formData.patient_age);
      formDataToSend.append('diagnosis', formData.diagnosis);
      formDataToSend.append('amount', formData.claimed_amount);
      formDataToSend.append('admission_date', formData.admission_date);
      formDataToSend.append('discharge_date', formData.discharge_date);

      // Submit to new verified claim endpoint
      const response = await fetch('http://localhost:8000/api/submit-verified-claim', {
        method: 'POST',
        body: formDataToSend,
        // Don't set Content-Type header - browser will set it with boundary for multipart
      });

      const result = await response.json();

      if (result.success) {
        // Verification SUCCESS
        setVerificationInfo({
          ...result.verification,
          risk_score: result.risk_score,
          risk_category: result.risk_category,
          duration: result.duration_of_stay
        });
        
        const riskLabel = result.risk_score < 30 ? 'Low Risk' : 
                         result.risk_score < 70 ? 'Medium Risk' : 'High Risk';
        const riskColor = result.risk_score < 30 ? '#28a745' : 
                         result.risk_score < 70 ? '#ffc107' : '#dc3545';
        
        setSuccess(
          <span>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
              <path d="M20 6 9 17l-5-5" />
            </svg>
            Claim Verified & Submitted - <span style={{ color: riskColor, fontWeight: 'bold' }}>{riskLabel}</span>
            <div style={{ marginTop: '6px', fontSize: '0.9em' }}>Claim ID: {result.claim_id}</div>
          </span>
        );
        
        if (onClaimCreated) {
          onClaimCreated(result);
        }

        // Redirect to dashboard after 3 seconds
        setTimeout(() => {
          navigate('/dashboard');
        }, 3000);
      } else {
        // Verification FAILED
        setVerificationInfo(result.verification);
        setError(result.message);
      }
    } catch (err) {
      console.error('Submit error:', err);
      setError(err.message || 'Failed to submit claim. Please try again.');
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
          {verificationInfo && (
            <div style={{ marginTop: '12px', padding: '12px', backgroundColor: 'rgba(6, 182, 212, 0.1)', borderRadius: '8px', fontSize: '0.9em' }}>
              <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#06b6d4' }}>Verification Details:</div>
              <div>✓ Name Match: {verificationInfo.name_match}%</div>
              <div>✓ Amount Found: {verificationInfo.amount_found ? 'Yes' : 'No'}</div>
              <div>✓ OCR Score: {verificationInfo.overall_score.toFixed(1)}%</div>
              {verificationInfo.duration && <div>✓ Duration of Stay: {verificationInfo.duration} days</div>}
              {verificationInfo.risk_score !== undefined && (
                <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px solid rgba(6, 182, 212, 0.3)' }}>
                  <div style={{ fontWeight: 'bold', color: '#06b6d4' }}>AI Fraud Analysis:</div>
                  <div>Risk Score: {verificationInfo.risk_score}%</div>
                  <div>Category: {verificationInfo.risk_category}</div>
                </div>
              )}
            </div>
          )}
          <p>Redirecting to dashboard...</p>
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Patient Name *</label>
          <input
            type="text"
            name="patient_name"
            value={formData.patient_name}
            onChange={handleChange}
            required
            placeholder="Full name as on document"
          />
        </div>

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
              min={formData.admission_date}
            />
          </div>
        </div>

        <div className="form-group">
          <label>Upload Proof (Medical Bill/Receipt) *</label>
          <div style={{ marginBottom: '8px', fontSize: '0.9em', color: '#94a3b8' }}>
            Accepted formats: JPG, PNG, PDF, TXT (Max 10MB)
          </div>
          <input
            type="file"
            onChange={handleFileChange}
            required
            accept=".jpg,.jpeg,.png,.pdf,.txt"
            style={{
              width: '100%',
              padding: '12px',
              border: '2px dashed #334155',
              borderRadius: '8px',
              backgroundColor: '#0f172a',
              color: '#e2e8f0',
              cursor: 'pointer'
            }}
          />
          {selectedFile && (
            <div style={{ marginTop: '8px', fontSize: '0.9em', color: '#06b6d4' }}>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '14px', height: '14px', display: 'inline-block', verticalAlign: 'middle', marginRight: '4px' }}>
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <path d="M14 2v6h6" />
              </svg>
              {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
            </div>
          )}
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
          {isSubmitting ? (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px', animation: 'spin 1s linear infinite' }}>
                <path d="M21 12a9 9 0 1 1-6.219-8.56" />
              </svg>
              Verifying Document...
            </>
          ) : (
            <>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              Verify & Submit Claim
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

import React, { useState } from 'react';
import apiClient from '../utils/apiClient';
import './DocumentVerifier.css';

const DocumentVerifier = () => {
  const [formData, setFormData] = useState({
    patientName: '',
    amount: '',
    date: ''
  });
  const [selectedFile, setSelectedFile] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validate file type
      const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
      if (!validTypes.includes(file.type)) {
        setError('Please upload a valid image file (JPG, PNG)');
        return;
      }
      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (!formData.patientName || !formData.amount || !formData.date) {
      setError('Please fill in all fields');
      return;
    }
    
    if (!selectedFile) {
      setError('Please select a document to verify');
      return;
    }

    setIsVerifying(true);
    setError(null);
    setVerificationResult(null);

    try {
      // Create FormData
      const formDataToSend = new FormData();
      formDataToSend.append('file', selectedFile);
      formDataToSend.append('patient_name', formData.patientName);
      formDataToSend.append('amount', formData.amount);
      formDataToSend.append('date', formData.date);

      // Make API call using existing apiClient
      const response = await fetch('http://localhost:8000/api/verify-claim-document', {
        method: 'POST',
        body: formDataToSend,
        // Don't set Content-Type header - browser will set it with boundary for multipart
      });

      if (!response.ok) {
        throw new Error(`Verification failed: ${response.statusText}`);
      }

      const result = await response.json();
      setVerificationResult(result);

      // Clear form if verified successfully
      if (result.verified) {
        setTimeout(() => {
          setFormData({ patientName: '', amount: '', date: '' });
          setSelectedFile(null);
          // Reset file input
          document.getElementById('file-input').value = '';
        }, 3000);
      }

    } catch (err) {
      console.error('Verification error:', err);
      setError(err.message || 'Failed to verify document. Please try again.');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleReset = () => {
    setFormData({ patientName: '', amount: '', date: '' });
    setSelectedFile(null);
    setVerificationResult(null);
    setError(null);
    document.getElementById('file-input').value = '';
  };

  return (
    <div className="document-verifier-container">
      <div className="verifier-card">
        <div className="verifier-header">
          <h2>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="header-icon">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <path d="M14 2v6h6" />
              <path d="M9 13h6" />
              <path d="M9 17h6" />
            </svg>
            OCR Document Verification
          </h2>
          <p className="verifier-subtitle">
            Verify claim documents using AI-powered OCR and fuzzy matching
          </p>
        </div>

        <form onSubmit={handleSubmit} className="verifier-form">
          {/* Patient Name */}
          <div className="form-group">
            <label htmlFor="patientName">Patient Name *</label>
            <input
              type="text"
              id="patientName"
              name="patientName"
              value={formData.patientName}
              onChange={handleInputChange}
              placeholder="Enter patient name as shown on document"
              required
              disabled={isVerifying}
            />
          </div>

          {/* Amount */}
          <div className="form-group">
            <label htmlFor="amount">Claim Amount *</label>
            <input
              type="text"
              id="amount"
              name="amount"
              value={formData.amount}
              onChange={handleInputChange}
              placeholder="e.g., 25000 or $250.00"
              required
              disabled={isVerifying}
            />
          </div>

          {/* Date */}
          <div className="form-group">
            <label htmlFor="date">Claim Date *</label>
            <input
              type="date"
              id="date"
              name="date"
              value={formData.date}
              onChange={handleInputChange}
              required
              disabled={isVerifying}
            />
          </div>

          {/* File Upload */}
          <div className="form-group">
            <label htmlFor="file-input">Upload Document *</label>
            <div className="file-input-wrapper">
              <input
                type="file"
                id="file-input"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleFileChange}
                disabled={isVerifying}
              />
              {selectedFile && (
                <div className="file-selected">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="file-icon">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <path d="M14 2v6h6" />
                  </svg>
                  <span>{selectedFile.name}</span>
                  <span className="file-size">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
              )}
            </div>
            <small className="input-hint">Accepted: JPG, PNG (Max 10MB)</small>
          </div>

          {/* Error Message */}
          {error && (
            <div className="alert alert-error">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="alert-icon">
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="form-actions">
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isVerifying}
            >
              {isVerifying ? (
                <>
                  <div className="spinner"></div>
                  Verifying...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="btn-icon">
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.35-4.35" />
                  </svg>
                  Verify Document
                </>
              )}
            </button>
            
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleReset}
              disabled={isVerifying}
            >
              Reset
            </button>
          </div>
        </form>

        {/* Verification Result */}
        {verificationResult && (
          <div className={`verification-result ${verificationResult.verified ? 'success' : 'failed'}`}>
            <div className="result-header">
              {verificationResult.verified ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="result-icon success-icon">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                  <h3>Verification Successful!</h3>
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="result-icon error-icon">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="15" y1="9" x2="9" y2="15" />
                    <line x1="9" y1="9" x2="15" y2="15" />
                  </svg>
                  <h3>Verification Failed</h3>
                </>
              )}
            </div>

            <div className="result-details">
              <p className="result-message">{verificationResult.message}</p>
              
              <div className="scores-grid">
                <div className="score-item">
                  <span className="score-label">Name Match</span>
                  <span className={`score-value ${verificationResult.scores.name_match > 80 ? 'good' : 'bad'}`}>
                    {verificationResult.scores.name_match.toFixed(1)}%
                  </span>
                </div>
                <div className="score-item">
                  <span className="score-label">Amount Found</span>
                  <span className={`score-value ${verificationResult.scores.amount_found ? 'good' : 'bad'}`}>
                    {verificationResult.scores.amount_found ? '✓ Yes' : '✗ No'}
                  </span>
                </div>
                <div className="score-item">
                  <span className="score-label">Overall Score</span>
                  <span className={`score-value ${verificationResult.scores.overall > 80 ? 'good' : 'bad'}`}>
                    {verificationResult.scores.overall.toFixed(1)}%
                  </span>
                </div>
              </div>

              {verificationResult.extracted_text && (
                <div className="extracted-text">
                  <h4>Extracted Text:</h4>
                  <p>{verificationResult.extracted_text.substring(0, 200)}...</p>
                </div>
              )}

              {verificationResult.verified && verificationResult.record_id && (
                <div className="record-info">
                  <small>✓ Saved to training data (Record ID: {verificationResult.record_id})</small>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentVerifier;

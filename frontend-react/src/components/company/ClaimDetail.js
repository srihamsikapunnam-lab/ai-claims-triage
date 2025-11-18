import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../utils/apiClient';
import RiskDisplay from '../RiskDisplay';
import '../ClaimDetail.css';

const ClaimDetailCompany = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loadingAI, setLoadingAI] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [actionError, setActionError] = useState(null);

  useEffect(() => {
    const fetchClaim = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get(`/claims/${claimId}`);
        setClaim(res);
        
        // Fetch AI analysis
        if (res && res.id) {
          await fetchAIAnalysis(res.id);
        }
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to load claim');
      } finally {
        setLoading(false);
      }
    };

    fetchClaim();
  }, [claimId]);

  const fetchAIAnalysis = async (claimId) => {
    setLoadingAI(true);
    try {
      const analysis = await apiClient.get(`/claims/${claimId}/analysis`);
      setAiAnalysis(analysis);
    } catch (err) {
      console.warn('AI analysis not available:', err);
    } finally {
      setLoadingAI(false);
    }
  };

  const handleClaimAction = async (action, status) => {
    setActionLoading(true);
    setActionError(null);
    setActionSuccess(null);

    try {
      const response = await apiClient.patch(`/claims/${claimId}/status`, {
        status: status,
        reviewed_by: user?.id,
        notes: `Claim ${action} by ${user?.name || user?.email}`
      });

      setActionSuccess(
        <span>
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
            <path d="M20 6 9 17l-5-5" />
          </svg>
          Claim {action} successfully!
        </span>
      );
      // Refresh claim data
      const updatedClaim = await apiClient.get(`/claims/${claimId}`);
      setClaim(updatedClaim);

      // Auto-hide success message after 3 seconds
      setTimeout(() => setActionSuccess(null), 3000);
    } catch (err) {
      console.error(`Failed to ${action} claim:`, err);
      setActionError(err.message || `Failed to ${action} claim`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleApprove = () => handleClaimAction('approved', 'approved');
  const handleReject = () => handleClaimAction('rejected', 'rejected');
  const handleRequestInfo = () => handleClaimAction('review requested', 'additional_info_required');

  const formatCurrency = (amount) => {
    const num = typeof amount === 'string' ? parseFloat(amount.replace(/[^0-9.-]+/g, '')) : amount;
    try {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR'
      }).format(num || 0);
    } catch (e) {
      return `₹${Number(num || 0).toLocaleString('en-IN')}`;
    }
  };

  if (loading) return (
    <div className="claim-detail-container">
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Loading claim details...</p>
      </div>
    </div>
  );
  
  if (error) return (
    <div className="claim-detail-container">
      <div className="error-banner">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
          <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
          <line x1="12" y1="9" x2="12" y2="13" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        {error}
      </div>
    </div>
  );
  
  if (!claim) return (
    <div className="claim-detail-container">
      <div className="empty-state">Claim not found</div>
    </div>
  );

  const riskScore = claim.risk_score || aiAnalysis?.risk_score || 0;

  return (
    <div className="claim-detail-container">
      <div className="detail-header">
        <button className="back-button" onClick={() => navigate('/dashboard')}>
          ← Back to Dashboard
        </button>
        <h1>Claim Details - Company Review</h1>
        <p className="claim-id">Claim ID: {claim.id}</p>
      </div>

      <div className="detail-content">
        {/* AI Risk Analysis - Priority for Company */}
        <div className="detail-section highlight-section">
          <h2>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
              <rect x="4" y="4" width="16" height="16" rx="2" />
              <rect x="9" y="9" width="6" height="6" />
              <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
            </svg>
            AI Risk Analysis (XGBoost Model)
          </h2>
          {loadingAI ? (
            <div className="ai-loading">
              <div className="loading-spinner-small"></div>
              <p>Running AI analysis with XGBoost model...</p>
            </div>
          ) : (
            <>
              <RiskDisplay riskScore={riskScore} />
              
              {aiAnalysis && aiAnalysis.explanation && (
                <div className="ai-explanation">
                  <h3>Detailed Analysis</h3>
                  <div className="explanation-content">
                    {aiAnalysis.explanation.key_factors && (
                      <div className="factor-list">
                        <h4>
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                            <circle cx="11" cy="11" r="8" />
                            <path d="m21 21-4.35-4.35" />
                          </svg>
                          Key Risk Factors:
                        </h4>
                        <ul>
                          {aiAnalysis.explanation.key_factors.map((factor, idx) => (
                            <li key={idx} className={factor.contribution > 0 ? 'risk-increase' : 'risk-decrease'}>
                              <strong>{factor.feature}:</strong> 
                              <span className="impact-badge">
                                {factor.contribution > 0 ? '↑' : '↓'} 
                                {Math.abs(factor.contribution).toFixed(3)} impact
                              </span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {aiAnalysis.explanation.recommendation && (
                      <div className="recommendation">
                        <h4>
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                            <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
                            <path d="M9 18h6" />
                            <path d="M10 22h4" />
                          </svg>
                          AI Recommendation:
                        </h4>
                        <p>{aiAnalysis.explanation.recommendation}</p>
                      </div>
                    )}
                    {aiAnalysis.model_version && (
                      <div className="model-info">
                        <small>Model: {aiAnalysis.model_version} | Confidence: {aiAnalysis.confidence ? `${(aiAnalysis.confidence * 100).toFixed(1)}%` : 'N/A'}</small>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Main Claim Information */}
        <div className="detail-section">
          <h2>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
              <rect x="8" y="2" width="8" height="4" rx="1" />
            </svg>
            Claim Information
          </h2>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">User ID</span>
              <span className="detail-value">{claim.user_id}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Patient Age</span>
              <span className="detail-value">{claim.patient_age} years</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Claimed Amount</span>
              <span className="detail-value amount-highlight">{formatCurrency(claim.claimed_amount)}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Diagnosis</span>
              <span className="detail-value">{claim.diagnosis}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Status</span>
              <span className="detail-value status-badge">{claim.status}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Date Submitted</span>
              <span className="detail-value">{new Date(claim.created_at || claim.date).toLocaleString()}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Last Updated</span>
              <span className="detail-value">{new Date(claim.updated_at || claim.date).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {/* Documents */}
        {claim.documents && claim.documents.length > 0 && (
          <div className="detail-section">
            <h2>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
                <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
              Supporting Documents
            </h2>
            <div className="documents-list">
              {claim.documents.map((doc, idx) => (
                <div key={idx} className="document-item">
                  <span className="doc-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}>
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                      <path d="M14 2v6h6" />
                    </svg>
                  </span>
                  <span className="doc-name">{doc.filename || `Document ${idx + 1}`}</span>
                  <span className="doc-size">{doc.size ? `(${(doc.size / 1024).toFixed(1)} KB)` : ''}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons for Company */}
        <div className="detail-section">
          <h2>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
              <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
              <circle cx="12" cy="12" r="3" />
            </svg>
            Actions
          </h2>
          
          {actionSuccess && (
            <div className="action-message success-message">
              {actionSuccess}
            </div>
          )}
          
          {actionError && (
            <div className="action-message error-message">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              {actionError}
            </div>
          )}
          
          <div className="action-buttons">
            <button 
              className="action-btn approve-btn" 
              onClick={handleApprove}
              disabled={actionLoading || claim.status === 'approved'}
            >
              {actionLoading ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12 6 12 12 16 14" />
                  </svg>
                  Processing...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                    <path d="M20 6 9 17l-5-5" />
                  </svg>
                  Approve Claim
                </>
              )}
            </button>
            <button 
              className="action-btn reject-btn" 
              onClick={handleReject}
              disabled={actionLoading || claim.status === 'rejected'}
            >
              {actionLoading ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12 6 12 12 16 14" />
                  </svg>
                  Processing...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                    <path d="M18 6 6 18M6 6l12 12" />
                  </svg>
                  Reject Claim
                </>
              )}
            </button>
            <button 
              className="action-btn review-btn" 
              onClick={handleRequestInfo}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                    <circle cx="12" cy="12" r="10" />
                    <polyline points="12 6 12 12 16 14" />
                  </svg>
                  Processing...
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                    <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8" />
                    <path d="M21 3v5h-5" />
                  </svg>
                  Request More Info
                </>
              )}
            </button>
          </div>
          
          <div className="action-note">
            <p>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
                <path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5" />
                <path d="M9 18h6" />
                <path d="M10 22h4" />
              </svg>
              Current Status: <strong>{claim.status}</strong>
            </p>
            <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginTop: '0.5rem' }}>
              Actions will update the claim status and notify the customer.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClaimDetailCompany;

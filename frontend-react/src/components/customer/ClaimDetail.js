import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../utils/apiClient';
import RiskDisplay from '../RiskDisplay';
import ProgressTracker from '../ProgressTracker';
import '../ClaimDetail.css';

const ClaimDetailCustomer = () => {
  const { claimId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [aiAnalysis, setAiAnalysis] = useState(null);
  const [loadingAI, setLoadingAI] = useState(false);

  useEffect(() => {
    const fetchClaim = async () => {
      setLoading(true);
      try {
        console.log('[ClaimDetail] fetching claim id=', claimId);
        const res = await apiClient.get(`/claims/${claimId}`);
        console.log('[ClaimDetail] api response', res);
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
        <h1>Claim Details</h1>
        <p className="claim-id">Claim ID: {claim.id}</p>
      </div>

      {/* Progress Tracker */}
      <ProgressTracker currentStatus={claim.status} />

      <div className="detail-content">
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
              <span className="detail-label">Patient Age</span>
              <span className="detail-value">{claim.patient_age} years</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Claimed Amount</span>
              <span className="detail-value">{formatCurrency(claim.claimed_amount)}</span>
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

        {/* AI Risk Analysis */}
        <div className="detail-section">
          <h2>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
              <rect x="4" y="4" width="16" height="16" rx="2" />
              <rect x="9" y="9" width="6" height="6" />
              <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
            </svg>
            AI Risk Analysis
          </h2>
          {loadingAI ? (
            <div className="ai-loading">
              <div className="loading-spinner-small"></div>
              <p>Analyzing claim with XGBoost model...</p>
            </div>
          ) : (
            <>
              <RiskDisplay riskScore={riskScore} />
              
              {aiAnalysis && aiAnalysis.explanation && (
                <div className="ai-explanation">
                  <h3>Analysis Details</h3>
                  <div className="explanation-content">
                    {aiAnalysis.explanation.key_factors && (
                      <div className="factor-list">
                        <h4>Key Factors:</h4>
                        <ul>
                          {aiAnalysis.explanation.key_factors.map((factor, idx) => (
                            <li key={idx}>
                              <strong>{factor.feature}:</strong> {factor.contribution > 0 ? '↑' : '↓'} 
                              {Math.abs(factor.contribution).toFixed(2)} impact
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {aiAnalysis.explanation.recommendation && (
                      <div className="recommendation">
                        <h4>Recommendation:</h4>
                        <p>{aiAnalysis.explanation.recommendation}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </>
          )}
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
      </div>
    </div>
  );
};

export default ClaimDetailCustomer;

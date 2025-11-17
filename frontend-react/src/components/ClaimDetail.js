import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import apiClient from '../utils/apiClient';
import './ClaimDetail.css';

const ClaimDetail = () => {
  const { claimId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchClaimDetail();
  }, [claimId]);

  const fetchClaimDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.get(`/claims/${claimId}`);
      setClaim(data);
    } catch (err) {
      setError(err.message || 'Failed to load claim details');
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (newStatus) => {
    if (!window.confirm(`Are you sure you want to ${newStatus} this claim?`)) {
      return;
    }

    setActionLoading(true);
    try {
      await apiClient.patch(`/claims/${claimId}/status`, { status: newStatus });
      
      // Refresh claim data
      await fetchClaimDetail();
      
      alert(`✅ Claim ${newStatus} successfully!`);
    } catch (err) {
      alert(`❌ Failed to update claim: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getRiskColor = (score) => {
    if (score >= 70) return '#ef4444';
    if (score >= 40) return '#f59e0b';
    return '#10b981';
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'approved': return '#10b981';
      case 'rejected': return '#ef4444';
      case 'under_review': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return (
      <div className="claim-detail-page">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading claim details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="claim-detail-page">
        <div className="error-container">
          <h2>⚠️ Error</h2>
          <p>{error}</p>
          <button onClick={() => navigate('/dashboard')} className="btn-back">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!claim) {
    return (
      <div className="claim-detail-page">
        <div className="error-container">
          <h2>Claim Not Found</h2>
          <button onClick={() => navigate('/dashboard')} className="btn-back">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const canTakeAction = user?.role === 'company_admin' || user?.role === 'company_staff';
  const isUnderReview = claim.status?.toLowerCase() === 'under_review';

  return (
    <div className="claim-detail-page">
      <div className="claim-detail-header">
        <button onClick={() => navigate('/dashboard')} className="btn-back">
          ← Back to Dashboard
        </button>
        <h1>Claim Details</h1>
        <div className="claim-id">ID: {claim.id}</div>
      </div>

      <div className="claim-detail-container">
        {/* Left Column: Claim Information */}
        <div className="claim-info-section">
          <div className="info-card">
            <h2>📋 Claim Information</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Patient Name:</span>
                <span className="info-value">{claim.full_name || 'N/A'}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Patient Age:</span>
                <span className="info-value">{claim.patient_age} years</span>
              </div>
              <div className="info-item">
                <span className="info-label">Diagnosis:</span>
                <span className="info-value">{claim.diagnosis}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Claimed Amount:</span>
                <span className="info-value amount">{formatCurrency(claim.claimed_amount)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Admission Date:</span>
                <span className="info-value">{formatDate(claim.admission_date)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Discharge Date:</span>
                <span className="info-value">{formatDate(claim.discharge_date)}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Length of Stay:</span>
                <span className="info-value">{claim.length_of_stay} days</span>
              </div>
              <div className="info-item">
                <span className="info-label">Status:</span>
                <span 
                  className="info-value status-badge"
                  style={{ 
                    backgroundColor: getStatusColor(claim.status),
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '4px'
                  }}
                >
                  {claim.status?.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Submitted:</span>
                <span className="info-value">{formatDate(claim.created_at)}</span>
              </div>
            </div>
            
            {claim.description && (
              <div className="description-section">
                <h3>Description:</h3>
                <p>{claim.description}</p>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          {canTakeAction && isUnderReview && (
            <div className="action-buttons">
              <button
                onClick={() => handleStatusUpdate('approved')}
                disabled={actionLoading}
                className="btn-approve"
              >
                ✅ Approve Claim
              </button>
              <button
                onClick={() => handleStatusUpdate('rejected')}
                disabled={actionLoading}
                className="btn-reject"
              >
                ❌ Reject Claim
              </button>
              <button
                onClick={() => handleStatusUpdate('flagged')}
                disabled={actionLoading}
                className="btn-flag"
              >
                🚩 Flag for Manual Review
              </button>
            </div>
          )}
        </div>

        {/* Right Column: AI Risk Assessment */}
        <div className="risk-assessment-section">
          <div className="risk-card">
            <h2>🤖 Live AI Risk Assessment</h2>
            
            {/* Risk Score Display */}
            <div className="risk-score-display">
              <div 
                className="risk-score-circle"
                style={{
                  background: `conic-gradient(${getRiskColor(claim.risk_score || 0)} ${(claim.risk_score || 0) * 3.6}deg, #f3f4f6 0deg)`
                }}
              >
                <div className="risk-score-inner">
                  <span className="score-number">{Math.round(claim.risk_score || 0)}%</span>
                  <span className="score-label">Risk Score</span>
                </div>
              </div>
              
              <div className="risk-category">
                <span className="category-label">Risk Category:</span>
                <span 
                  className="category-value"
                  style={{ color: getRiskColor(claim.risk_score || 0) }}
                >
                  {claim.risk_category || 'Unknown'}
                </span>
              </div>
            </div>

            {/* Model Prediction */}
            <div className="prediction-info">
              <h3>Model Prediction</h3>
              <div className="prediction-badge" style={{
                backgroundColor: claim.prediction === 'Fraud' ? '#fee2e2' : '#d1fae5',
                color: claim.prediction === 'Fraud' ? '#991b1b' : '#065f46',
                padding: '12px',
                borderRadius: '8px',
                textAlign: 'center',
                fontWeight: 'bold'
              }}>
                {claim.prediction || 'N/A'}
              </div>
            </div>

            {/* LIME Explanations */}
            {claim.lime_explanation && claim.lime_explanation.length > 0 && (
              <div className="lime-explanations">
                <h3>🕵️ AI Reasoning (LIME Analysis)</h3>
                <p className="explanation-subtitle">
                  Top factors influencing the AI's risk assessment:
                </p>
                <div className="lime-features">
                  {claim.lime_explanation.map((exp, index) => (
                    <div key={index} className="lime-feature">
                      <div className="feature-rank">#{index + 1}</div>
                      <div className="feature-content">
                        <div className="feature-name">{exp.feature}</div>
                        <div className="feature-bar-container">
                          <div 
                            className="feature-bar"
                            style={{
                              width: `${Math.abs(exp.contribution) * 100}%`,
                              backgroundColor: exp.contribution > 0 ? '#ef4444' : '#10b981'
                            }}
                          ></div>
                        </div>
                        <div 
                          className="feature-contribution"
                          style={{ color: exp.contribution > 0 ? '#ef4444' : '#10b981' }}
                        >
                          {exp.contribution > 0 ? '+' : ''}{exp.contribution.toFixed(3)}
                          <span className="contribution-label">
                            {exp.contribution > 0 ? ' (increases risk)' : ' (decreases risk)'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Human-Readable Explanations */}
            {claim.explanation && claim.explanation.length > 0 && (
              <div className="explanations">
                <h3>📝 Key Findings</h3>
                <ul className="explanation-list">
                  {claim.explanation.map((exp, index) => (
                    <li key={index}>{exp}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Model Info */}
            <div className="model-info">
              <small>Model: {claim.model_version || 'XGBoost_Production_v2.0'}</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClaimDetail;

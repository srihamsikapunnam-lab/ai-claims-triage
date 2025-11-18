import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiClient from '../../utils/apiClient';
import '../ClaimDetail.css';

const ClaimDetailCustomer = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [claim, setClaim] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchClaim = async () => {
      setLoading(true);
      try {
        const res = await apiClient.get(`/claims/${id}`);
        setClaim(res);
      } catch (err) {
        console.error(err);
        setError(err.message || 'Failed to load claim');
      } finally {
        setLoading(false);
      }
    };

    fetchClaim();
  }, [id]);

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

  if (loading) return <div className="loading">Loading claim...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!claim) return <div className="empty">Claim not found</div>;

  return (
    <div className="claim-detail-container">
      <div className="detail-header">
        <h2>Claim Details (Customer)</h2>
      </div>

      <div className="detail-grid">
        <div className="detail-card">
          <div className="detail-row">
            <div className="detail-label">Patient Age</div>
            <div className="detail-value">{claim.patient_age} years</div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Claimed Amount</div>
            <div className="detail-value">{formatCurrency(claim.claimed_amount)}</div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Diagnosis</div>
            <div className="detail-value">{claim.diagnosis}</div>
          </div>
        </div>

        <div className="detail-card">
          <div className="detail-row">
            <div className="detail-label">Status</div>
            <div className="detail-value">{claim.status}</div>
          </div>

          <div className="detail-row">
            <div className="detail-label">Date Submitted</div>
            <div className="detail-value">{new Date(claim.date).toLocaleDateString()}</div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default ClaimDetailCustomer;

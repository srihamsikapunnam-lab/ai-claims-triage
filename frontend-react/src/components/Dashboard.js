import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import ProgressTracker from './ProgressTracker';
import dashboardService from '../services/dashboardService';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [dashboardData, setDashboardData] = useState({
    totalClaims: 0,
    pendingReview: 0,
    highRisk: 0,
    approved: 0,
    rejected: 0,
    totalAmount: 0,
    avgProcessingTime: 0,
    approvalRate: 0
  });

  const [recentClaims, setRecentClaims] = useState([]);
  const [allClaims, setAllClaims] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        let claims = [];

        if (user?.role === 'company_admin' || user?.role === 'company_staff') {
          claims = await dashboardService.getAllClaims({ limit: 100 });
        } else {
          claims = await dashboardService.getUserClaims();
        }

        const formattedClaims = claims.map(c =>
          dashboardService.formatClaimForDisplay(c)
        );

        const metrics = dashboardService.calculateDashboardMetrics(claims);

        setDashboardData({
          totalClaims: claims.length,
          pendingReview: claims.filter(c => c.status === 'under_review').length,
          highRisk: claims.filter(c => c.risk_category === 'high').length,
          approved: claims.filter(c => c.status === 'approved').length,
          rejected: claims.filter(c => c.status === 'rejected').length,
          totalAmount: metrics.totalAmount,
          avgProcessingTime: metrics.avgProcessingTime,
          approvalRate: metrics.approvalRate
        });

        setAllClaims(formattedClaims);

        setRecentClaims(
          formattedClaims
            .sort((a, b) => new Date(b.date) - new Date(a.date))
            .slice(0, 5)
        );
      } catch (err) {
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  const formatCurrency = (amount) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);

  const safePercent = (value) =>
    dashboardData.totalClaims === 0
      ? 0
      : Math.round((value / dashboardData.totalClaims) * 100);

  if (loading) {
    return <div className="dashboard-page">Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Claims Dashboard</h1>
        <p className="dashboard-subtitle">
          {user?.role === 'company_admin' || user?.role === 'company_staff'
            ? 'Overview of all claims and system metrics'
            : 'Your submitted claims and current status'}
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="dashboard-tabs">
        <button
          className={activeTab === 'overview' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={activeTab === 'allClaims' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('allClaims')}
        >
          All Claims
        </button>
      </div>

      {activeTab === 'overview' && (
        <>
          {/* TOP STAT CARDS */}
          <div className="stats-grid">
            <div className="stat-card">
              <h3>Total Claims</h3>
              <p className="stat-number">{dashboardData.totalClaims}</p>
            </div>

            <div className="stat-card">
              <h3>Pending Review</h3>
              <p className="stat-number">{dashboardData.pendingReview}</p>
            </div>

            <div className="stat-card">
              <h3>High Risk</h3>
              <p className="stat-number">{dashboardData.highRisk}</p>
            </div>

            <div className="stat-card">
              <h3>Total Claim Value</h3>
              <p className="stat-number">
                {formatCurrency(dashboardData.totalAmount)}
              </p>
            </div>
          </div>

          {/* MAIN CONTENT */}
          <div className="dashboard-content">
            {/* LEFT */}
            <div>
              <div className="statistics-section">
                <h3>Claims Distribution</h3>

                <div className="distribution-bar approved">
                  Approved ({dashboardData.approved}) — {safePercent(dashboardData.approved)}%
                </div>

                <div className="distribution-bar pending">
                  Pending ({dashboardData.pendingReview}) — {safePercent(dashboardData.pendingReview)}%
                </div>

                <div className="distribution-bar high-risk">
                  High Risk ({dashboardData.highRisk}) — {safePercent(dashboardData.highRisk)}%
                </div>

                <div className="distribution-bar rejected">
                  Rejected ({dashboardData.rejected}) — {safePercent(dashboardData.rejected)}%
                </div>
              </div>

              <ProgressTracker />
            </div>

            {/* RIGHT */}
            <div className="recent-claims">
              <h3>Recent Claims</h3>

              {recentClaims.map((claim) => (
                <div
                  key={claim.id}
                  className="claim-item"
                  onClick={() => navigate(`/claims/${claim.id}`)}
                >
                  <div className="claim-main">
                    <span>{claim.id}</span>
                    <strong>{formatCurrency(claim.amount)}</strong>
                  </div>
                  <div className="claim-patient">{claim.patient}</div>
                  <div className="claim-date">{claim.date}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {activeTab === 'allClaims' && (
        <div className="claims-table-container">
          <table className="claims-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {allClaims.map((claim) => (
                <tr key={claim.id}>
                  <td>{claim.id}</td>
                  <td>{claim.patient}</td>
                  <td>{formatCurrency(claim.amount)}</td>
                  <td>{claim.status}</td>
                  <td>{claim.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Dashboard;

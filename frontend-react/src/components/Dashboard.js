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
    avgProcessingTime: 0
  });

  const [recentClaims, setRecentClaims] = useState([]);
  const [allClaims, setAllClaims] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statsTimeframe, setStatsTimeframe] = useState('month'); // month, quarter, year

  // Fetch real data from backend
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        let claims = [];
        let stats = null;

        // Check user role and fetch appropriate data
        if (user?.role === 'company_admin' || user?.role === 'company_staff') {
          // Company users get all claims and dashboard stats
          [claims, stats] = await Promise.all([
            dashboardService.getAllClaims({ limit: 100 }),
            dashboardService.getDashboardStats()
          ]);
        } else {
          // Regular customers get only their claims
          claims = await dashboardService.getUserClaims();
        }

        // Format claims for display
        const formattedClaims = claims.map(claim => 
          dashboardService.formatClaimForDisplay(claim)
        );

        // Calculate metrics from claims data
        const metrics = dashboardService.calculateDashboardMetrics(claims);

        // Build dashboard data
        const dashData = {
          totalClaims: stats?.total_claims || claims.length,
          pendingReview: stats?.pending_review || claims.filter(c => c.status === 'under_review').length,
          highRisk: stats?.high_risk || claims.filter(c => c.risk_category === 'high').length,
          approved: stats?.approved || claims.filter(c => c.status === 'approved').length,
          rejected: stats?.rejected || claims.filter(c => c.status === 'rejected').length,
          totalAmount: metrics.totalAmount,
          avgProcessingTime: parseFloat(metrics.avgProcessingTime),
          monthlyTrend: metrics.monthlyTrend,
          riskTrend: stats ? ((stats.high_risk / stats.total_claims) * 100).toFixed(0) : 0,
          approvalRate: metrics.approvalRate
        };

        setDashboardData(dashData);
        setAllClaims(formattedClaims);
        
        // Get 5 most recent claims
        const recent = formattedClaims
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, 5);
        setRecentClaims(recent);
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err.message);
        
        // Set empty data on error
        setDashboardData({
          totalClaims: 0,
          pendingReview: 0,
          highRisk: 0,
          approved: 0,
          rejected: 0,
          totalAmount: 0,
          avgProcessingTime: 0,
          monthlyTrend: 0,
          riskTrend: 0,
          approvalRate: 0
        });
        setAllClaims([]);
        setRecentClaims([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [statsTimeframe, user]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Approved': return '✅';
      case 'Rejected': return '❌';
      case 'Flagged': return '🚩';
      case 'Under Review': return '🔍';
      default: return '📄';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Approved': return '#10b981';
      case 'Rejected': return '#ef4444';
      case 'Flagged': return '#f59e0b';
      case 'Under Review': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const renderStatistics = () => (
    <div className="statistics-section">
      <div className="section-header">
        <h3>📈 Performance Metrics</h3>
        <div className="timeframe-selector">
          <button 
            className={statsTimeframe === 'month' ? 'active' : ''}
            onClick={() => setStatsTimeframe('month')}
          >
            Month
          </button>
          <button 
            className={statsTimeframe === 'quarter' ? 'active' : ''}
            onClick={() => setStatsTimeframe('quarter')}
          >
            Quarter
          </button>
          <button 
            className={statsTimeframe === 'year' ? 'active' : ''}
            onClick={() => setStatsTimeframe('year')}
          >
            Year
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Approval Rate</span>
            <span className={`metric-trend ${dashboardData.monthlyTrend > 0 ? 'positive' : 'negative'}`}>
              {dashboardData.monthlyTrend > 0 ? '↗' : '↘'} {Math.abs(dashboardData.monthlyTrend)}%
            </span>
          </div>
          <div className="metric-value">{dashboardData.approvalRate}%</div>
          <div className="metric-progress">
            <div 
              className="progress-bar" 
              style={{ width: `${dashboardData.approvalRate}%` }}
            ></div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Total Claims Value</span>
            <span className="metric-trend positive">↗ 8%</span>
          </div>
          <div className="metric-value">{formatCurrency(dashboardData.totalAmount)}</div>
          <div className="metric-subtitle">Across all claims</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Avg Processing Time</span>
            <span className="metric-trend positive">↘ 12%</span>
          </div>
          <div className="metric-value">{dashboardData.avgProcessingTime} days</div>
          <div className="metric-subtitle">Industry avg: 4.5 days</div>
        </div>

        <div className="metric-card">
          <div className="metric-header">
            <span className="metric-title">Risk Level Trend</span>
            <span className={`metric-trend ${dashboardData.riskTrend < 0 ? 'positive' : 'negative'}`}>
              {dashboardData.riskTrend < 0 ? '↘' : '↗'} {Math.abs(dashboardData.riskTrend)}%
            </span>
          </div>
          <div className="metric-value">{dashboardData.highRisk} high risk</div>
          <div className="metric-subtitle">Of {dashboardData.totalClaims} total</div>
        </div>
      </div>
    </div>
  );

  const renderAllClaims = () => (
    <div className="all-claims-section">
      <div className="section-header">
        <h3>All Claims ({allClaims.length})</h3>
        <div className="claims-actions">
          <button className="btn-primary">Export CSV</button>
          <button className="btn-secondary">Filter</button>
        </div>
      </div>

      <div className="claims-table-container">
        <table className="claims-table">
          <thead>
            <tr>
              <th>Claim ID</th>
              <th>Patient</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Risk Score</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {allClaims.map(claim => (
              <tr key={claim.id}>
                <td className="claim-id">{claim.id}</td>
                <td className="patient-name">{claim.patient}</td>
                <td className="claim-type">{claim.type}</td>
                <td className="claim-amount">{formatCurrency(claim.amount)}</td>
                <td>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(claim.status) }}
                  >
                    {getStatusIcon(claim.status)} {claim.status}
                  </span>
                </td>
                <td>
                  <div className="risk-score-container">
                    <span className={`risk-score risk-${claim.risk < 30 ? 'low' : claim.risk < 70 ? 'medium' : 'high'}`}>
                      {claim.risk}%
                    </span>
                    <div className="risk-bar">
                      <div 
                        className={`risk-fill risk-${claim.risk < 30 ? 'low' : claim.risk < 70 ? 'medium' : 'high'}`}
                        style={{ width: `${claim.risk}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
                <td className="claim-date">{claim.date}</td>
                <td>
                  <button 
                    className="btn-action"
                    onClick={() => navigate(`/claims/${claim.id}`)}
                  >
                    View Details
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderOverview = () => (
    <>
      {/* Statistics Cards - Updated with more metrics */}
      <div className="stats-grid">
        <div className="stat-card total-claims">
          <div className="stat-icon">📋</div>
          <div className="stat-content">
            <h3>Total Claims</h3>
            <p className="stat-number">{dashboardData.totalClaims}</p>
            <span className="stat-trend">+12% this month</span>
          </div>
        </div>

        <div className="stat-card pending">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <h3>Pending Review</h3>
            <p className="stat-number">{dashboardData.pendingReview}</p>
            <span className="stat-trend">{Math.round((dashboardData.pendingReview / dashboardData.totalClaims) * 100)}% of total</span>
          </div>
        </div>

        <div className="stat-card high-risk">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <h3>High Risk</h3>
            <p className="stat-number">{dashboardData.highRisk}</p>
            <span className="stat-trend">Requires immediate attention</span>
          </div>
        </div>

        <div className="stat-card financial">
          <div className="stat-icon">💰</div>
          <div className="stat-content">
            <h3>Total Value</h3>
            <p className="stat-number">{formatCurrency(dashboardData.totalAmount)}</p>
            <span className="stat-trend">Across all claims</span>
          </div>
        </div>
      </div>

      {renderStatistics()}

      <div className="dashboard-content">
        <div className="content-left">
          <div className="chart-section">
            <h3>Claims Distribution</h3>
            <div className="distribution-chart">
              <div className="chart-bar approved" style={{ width: `${(dashboardData.approved / dashboardData.totalClaims) * 100}%` }}>
                <span>Approved ({dashboardData.approved})</span>
              </div>
              <div className="chart-bar pending" style={{ width: `${(dashboardData.pendingReview / dashboardData.totalClaims) * 100}%` }}>
                <span>Pending ({dashboardData.pendingReview})</span>
              </div>
              <div className="chart-bar high-risk" style={{ width: `${(dashboardData.highRisk / dashboardData.totalClaims) * 100}%` }}>
                <span>High Risk ({dashboardData.highRisk})</span>
              </div>
              <div className="chart-bar rejected" style={{ width: `${(dashboardData.rejected / dashboardData.totalClaims) * 100}%` }}>
                <span>Rejected ({dashboardData.rejected})</span>
              </div>
            </div>
          </div>

          <ProgressTracker />
        </div>

        <div className="content-right">
          <div className="recent-claims">
            <div className="section-header">
              <h3>Recent Claims</h3>
              <span className="view-all" onClick={() => setActiveTab('allClaims')}>View All →</span>
            </div>
            <div className="claims-list">
              {recentClaims.map(claim => (
                <div 
                  key={claim.id} 
                  className="claim-item"
                  onClick={() => navigate(`/claims/${claim.id}`)}
                  style={{ cursor: 'pointer' }}
                >
                  <div className="claim-main">
                    <div className="claim-id">{claim.id}</div>
                    <div className="claim-amount">{formatCurrency(claim.amount)}</div>
                  </div>
                  <div className="claim-patient">{claim.patient}</div>
                  <div className="claim-details">
                    <span 
                      className="claim-status"
                      style={{ color: getStatusColor(claim.status) }}
                    >
                      {getStatusIcon(claim.status)} {claim.status}
                    </span>
                    <span className={`risk-badge risk-${claim.risk < 30 ? 'low' : claim.risk < 70 ? 'medium' : 'high'}`}>
                      {claim.risk}% risk
                    </span>
                  </div>
                  <div className="claim-date">{claim.date}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </>
  );

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>📊 Claims Dashboard</h1>
        <p className="dashboard-subtitle">
          {user?.role === 'company_admin' || user?.role === 'company_staff' 
            ? 'Comprehensive overview of all insurance claims and analytics'
            : 'Your personal claims overview and status tracking'
          }
        </p>
      </div>

      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      )}

      <div className="dashboard-tabs">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📈 Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'allClaims' ? 'active' : ''}`}
          onClick={() => setActiveTab('allClaims')}
        >
          📋 All Claims ({allClaims.length})
        </button>
        <button 
          className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          📊 Analytics
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'allClaims' && renderAllClaims()}
        {activeTab === 'analytics' && renderStatistics()}
      </div>
    </div>
  );
};

export default Dashboard;
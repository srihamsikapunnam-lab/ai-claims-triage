import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import dashboardService from '../services/dashboardService';
import './DashboardNew.css';

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Claims data states
  const [allClaims, setAllClaims] = useState([]);
  const [filteredClaims, setFilteredClaims] = useState([]);
  const [activeCategory, setActiveCategory] = useState('all');
  
  // UI states
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch claims data
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        let claims = [];

        // Check user role and fetch appropriate data
        if (user?.role === 'company_admin' || user?.role === 'company_staff') {
          // Company users get all claims
          claims = await dashboardService.getAllClaims({ limit: 100 });
        } else {
          // Regular customers get only their claims
          claims = await dashboardService.getUserClaims();
        }

        // Format claims for display
        const formattedClaims = claims.map(claim => 
          dashboardService.formatClaimForDisplay(claim)
        );

        setAllClaims(formattedClaims);
        setFilteredClaims(formattedClaims);
        
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err.message);
        
        // Set empty data on error
        setAllClaims([]);
        setFilteredClaims([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, [user]);

  // Filter claims based on active category
  useEffect(() => {
    switch (activeCategory) {
      case 'pending':
        setFilteredClaims(allClaims.filter(c => 
          c.status === 'Under Review' || c.status === 'Pending'
        ));
        break;
      case 'approved':
        setFilteredClaims(allClaims.filter(c => c.status === 'Approved'));
        break;
      case 'rejected':
        setFilteredClaims(allClaims.filter(c => 
          c.status === 'Rejected' || c.status === 'Flagged'
        ));
        break;
      case 'high-risk':
        setFilteredClaims(allClaims.filter(c => c.riskScore >= 70));
        break;
      case 'recent':
        const recent = [...allClaims]
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, 20);
        setFilteredClaims(recent);
        break;
      default:
        setFilteredClaims(allClaims);
    }
  }, [activeCategory, allClaims]);

  // Helper functions
  const getCategoryCount = (category) => {
    switch (category) {
      case 'pending':
        return allClaims.filter(c => 
          c.status === 'Under Review' || c.status === 'Pending'
        ).length;
      case 'approved':
        return allClaims.filter(c => c.status === 'Approved').length;
      case 'rejected':
        return allClaims.filter(c => 
          c.status === 'Rejected' || c.status === 'Flagged'
        ).length;
      case 'high-risk':
        return allClaims.filter(c => {
          const score = c.riskScore < 1 ? c.riskScore * 100 : c.riskScore;
          return score >= 70;
        }).length;
      case 'recent':
        return Math.min(allClaims.length, 20);
      default:
        return allClaims.length;
    }
  };

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

  const getRiskClass = (score) => {
    // Normalize score if it's in 0-1 range
    const normalizedScore = score < 1 ? score * 100 : score;
    if (normalizedScore >= 70) return 'risk-high';
    if (normalizedScore >= 40) return 'risk-medium';
    return 'risk-low';
  };

  // Helper to get expected status based on risk score
  const getExpectedStatus = (riskScore) => {
    const normalizedScore = riskScore < 1 ? riskScore * 100 : riskScore;
    if (normalizedScore >= 70) return 'flagged';
    return 'submitted';
  };

  // Helper to validate if status matches risk score
  const isStatusInconsistent = (claim) => {
    const normalizedScore = claim.riskScore < 1 ? claim.riskScore * 100 : claim.riskScore;
    const expectedStatus = getExpectedStatus(normalizedScore);
    const actualStatus = claim.status.toLowerCase();
    
    // Flagged status should only appear for high risk (>=70%)
    if (actualStatus === 'flagged' && normalizedScore < 70) return true;
    // High risk should be flagged, not approved
    if (actualStatus === 'approved' && normalizedScore >= 70) return true;
    
    return false;
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

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const handleClaimClick = (claimId) => {
    navigate(`/claims/${claimId}`);
  };

  const handleRetry = () => {
    window.location.reload();
  };

  const renderClaimCard = (claim) => (
    <div 
      key={claim.id} 
      className="claim-card-new"
      onClick={() => handleClaimClick(claim.id)}
    >
      <div className="card-header">
        <div className="claim-id">
          <div className="id-label">Claim ID</div>
          <div className="id-value">#{claim.id}</div>
        </div>
        <div className="claim-amount">
          <div className="amount-value">
            {formatCurrency(claim.claimAmount)}
          </div>
        </div>
      </div>

      <div className="card-body">
        <div className="patient-info">
          <div className="patient-name">
            {claim.patientName || 'Patient Information'}
          </div>
          <div className="claim-type">
            {claim.claimType || claim.procedureCode || 'General Claim'}
          </div>
        </div>
      </div>

      <div className="status-section">
        <div 
          className="status-badge-new"
          style={{ background: getStatusColor(claim.status) }}
        >
          <span>{getStatusIcon(claim.status)}</span>
          {claim.status}
          {isStatusInconsistent(claim) && (
            <span title="Status doesn't match risk score" style={{ marginLeft: '4px', fontSize: '14px' }}>⚠️</span>
          )}
        </div>
        
        <div className="risk-info">
          <div className="risk-label">Risk Score</div>
          <div className={`risk-score-small ${getRiskClass(claim.riskScore)}`}>
            {Math.round(claim.riskScore < 1 ? claim.riskScore * 100 : claim.riskScore)}%
          </div>
        </div>
      </div>

      <div className="card-footer">
        <div className="claim-date">
          {formatDate(claim.date)}
        </div>
        <div className="view-details">
          View Details →
        </div>
      </div>
    </div>
  );


  const renderClaimsGrid = () => {
    if (loading) {
      return (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading claims...</p>
        </div>
      );
    }

    if (filteredClaims.length === 0) {
      return (
        <div className="empty-state">
          <div className="empty-icon">📄</div>
          <h3>No Claims Found</h3>
          <p>
            {activeCategory === 'all' 
              ? "You don't have any claims yet." 
              : `No claims found in the ${activeCategory} category.`
            }
          </p>
          {activeCategory === 'all' && (
            <button 
              className="btn-submit-claim"
              onClick={() => navigate('/submit-claim')}
            >
              Submit Your First Claim
            </button>
          )}
        </div>
      );
    }

    return (
      <div className="claims-grid-new">
        {filteredClaims.map(renderClaimCard)}
      </div>
    );
  };

  return (
    <div className="dashboard-new">
      {/* Header */}
      <div className="dashboard-header-new">
        <div className="header-content">
          <h1>Claims Dashboard</h1>
          <p className="header-subtitle">
            Welcome back, {user?.name || user?.username}
          </p>
        </div>
        <div className="header-actions">
          <button 
            className="btn-primary-new"
            onClick={() => navigate('/submit-claim')}
          >
            <span className="btn-icon">+</span>
            New Claim
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="error-banner-new">
          <span className="error-icon">⚠️</span>
          <span className="error-message">
            Failed to load dashboard data: {error}
          </span>
          <button className="error-retry" onClick={handleRetry}>
            Retry
          </button>
        </div>
      )}

      {/* Category Navigation */}
      {renderCategoryNav()}

      {/* Claims Section */}
      <div className="claims-section-new">
        <div className="section-header-new">
          <h2>
            {activeCategory === 'all' ? 'All Claims' : 
             activeCategory.charAt(0).toUpperCase() + activeCategory.slice(1).replace('-', ' ') + ' Claims'}
          </h2>
          <div className="claims-count">
            {filteredClaims.length} {filteredClaims.length === 1 ? 'claim' : 'claims'}
          </div>
        </div>

        {renderClaimsGrid()}
      </div>
    </div>
  );
};

export default Dashboard;
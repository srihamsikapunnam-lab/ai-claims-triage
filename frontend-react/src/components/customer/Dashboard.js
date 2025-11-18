import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import dashboardService from '../../services/dashboardService';
import '../Dashboard.css';

const DashboardCustomer = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // Sidebar state - detect from window or use default
  const [sidebarExpanded, setSidebarExpanded] = useState(() => {
    if (typeof window !== 'undefined') {
      return window.innerWidth > 768;
    }
    return false;
  });
  
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
  
  // Claims data states
  const [allClaims, setAllClaims] = useState([]);
  const [filteredClaims, setFilteredClaims] = useState([]);
  const [activeCategory, setActiveCategory] = useState('all');
  
  // Statistics states
  const [statistics, setStatistics] = useState({
    totalClaims: 0,
    pendingCount: 0,
    approvedCount: 0,
    rejectedCount: 0,
  });
  
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

        // Customers get only their claims
        claims = await dashboardService.getUserClaims();

        // Format claims for display
        const formattedClaims = claims.map(claim => 
          dashboardService.formatClaimForDisplay(claim)
        );

        setAllClaims(formattedClaims);
        setFilteredClaims(formattedClaims);
        
        // Calculate statistics
        const stats = {
          totalClaims: formattedClaims.length,
          totalAmount: formattedClaims.reduce((sum, claim) => sum + (claim.claimAmount || 0), 0),
          pendingCount: formattedClaims.filter(c => c.status === 'Under Review' || c.status === 'Pending').length,
          approvedCount: formattedClaims.filter(c => c.status === 'Approved').length,
          rejectedCount: formattedClaims.filter(c => c.status === 'Rejected' || c.status === 'Flagged').length,
          highRiskCount: formattedClaims.filter(c => c.riskScore >= 70).length,
          averageRiskScore: formattedClaims.length > 0 ? 
            Math.round(formattedClaims.reduce((sum, claim) => sum + (claim.riskScore || 0), 0) / formattedClaims.length) : 0
        };
        setStatistics(stats);
        
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
      case 'recent':
        const recent = [...allClaims]
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, 5);
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
        return allClaims.filter(c => c.riskScore >= 70).length;
      case 'recent':
        return Math.min(allClaims.length, 5);
      default:
        return allClaims.length;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'Approved': return <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle' }}><path d="M20 6 9 17l-5-5" /></svg>;
      case 'Rejected': return <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle' }}><path d="M18 6 6 18M6 6l12 12" /></svg>;
      case 'Flagged': return <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle' }}><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z" /><line x1="4" y1="22" x2="4" y2="15" /></svg>;
      case 'Under Review': return <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle' }}><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg>;
      default: return <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle' }}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><path d="M14 2v6h6" /></svg>;
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
    if (score >= 70) return 'risk-high';
    if (score >= 40) return 'risk-medium';
    return 'risk-low';
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
    if (!claimId) {
      console.warn('[Dashboard] handleClaimClick called without id', claimId);
      return;
    }
    navigate(`/claims/${claimId}`);
  };
  
  const handleNewClaim = () => {
    navigate('/submit');
  };

  const handleRetry = () => {
    window.location.reload();
  };

  const renderClaimCard = (claim) => (
    <div 
      key={claim.id || Math.random()} 
      className="claim-card-new"
      onClick={(e) => { console.log('[Dashboard] card clicked', claim); handleClaimClick(claim.id); }}
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
        </div>
        
        <div className="risk-info">
          <div className="risk-label">Risk Score</div>
          <div className={`risk-score-small ${getRiskClass(claim.riskScore)}`}>
            {claim.riskScore}%
          </div>
        </div>
      </div>

      <div className="card-footer">
        <div className="claim-date">
          {formatDate(claim.date)}
        </div>
        <div className="card-documents">
          {claim.documents && claim.documents.length > 0 ? (
            <div className="doc-summary">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '4px' }}>
                <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
              {claim.documents.length} document{claim.documents.length > 1 ? 's' : ''}
              {claim.documents[0] && (` — ${claim.documents[0].filename}`)}
            </div>
          ) : (
            <div className="doc-summary empty">No documents</div>
          )}
        </div>
        <div className="view-details">
          View Details →
        </div>
      </div>
    </div>
  );

  const renderStatistics = () => {
    const statCards = [
      {
        title: 'Total Claims',
        value: statistics.totalClaims.toLocaleString(),
        icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" /><rect x="8" y="2" width="8" height="4" rx="1" /></svg>,
        color: '#06b6d4'
      },
      {
        title: 'Total Amount',
        value: formatCurrency(statistics.totalAmount),
        icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}><circle cx="12" cy="12" r="10" /><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8" /><path d="M12 18V6" /></svg>,
        color: '#22c55e'
      },
      {
        title: 'Pending',
        value: statistics.pendingCount.toLocaleString(),
        icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>,
        color: '#f97316'
      },
      {
        title: 'Approved',
        value: statistics.approvedCount.toLocaleString(),
        icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}><path d="M20 6 9 17l-5-5" /></svg>,
        color: '#10b981'
      },
    ];

    return (
      <div className="statistics-section-new">
        <div className="section-header-new">
          <h2>Customer Dashboard Overview</h2>
        </div>
        <div className="statistics-grid-new">
          {statCards.map((stat, index) => (
            <div key={index} className="stat-card-new" style={{'--accent-color': stat.color}}>
              <div className="stat-icon-new">{stat.icon}</div>
              <div className="stat-content">
                <div className="stat-value">{stat.value}</div>
                <div className="stat-title">{stat.title}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderCategoryNav = () => {
    const categories = [
      { key: 'all', label: 'All Claims'},
      { key: 'recent', label: 'Recent' },
      { key: 'pending', label: 'Pending' },
      { key: 'approved', label: 'Approved' },
      { key: 'rejected', label: 'Rejected' }
    ];

    return (
      <div className="category-nav-new">
        {categories.map(category => (
          <div
            key={category.key}
            className={`nav-item-new ${activeCategory === category.key ? 'active' : ''}`}
            onClick={() => setActiveCategory(category.key)}
          >
            <span className="nav-icon-new">{category.icon}</span>
            <span className="nav-text">{category.label}</span>
            <span className="nav-count">{getCategoryCount(category.key)}</span>
          </div>
        ))}
      </div>
    );
  };

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
          <div className="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '64px', height: '64px' }}>
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <path d="M14 2v6h6" />
            </svg>
          </div>
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
              onClick={handleNewClaim}
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
    <div className={`dashboard-new ${sidebarExpanded ? 'sidebar-expanded' : ''}`}>
      {/* Header */}
      <div className="dashboard-header-new">
        <div className="header-content">
          <h1>Claims Dashboard (Customer)</h1>
          <p className="header-subtitle">
            Welcome back, {user?.name || user?.username}
          </p>
        </div>
        <div className="header-actions">
          <button 
            className="btn-primary-new"
            onClick={handleNewClaim}
          >
            <span className="btn-icon">+</span>
            New Claim
          </button>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="error-banner-new">
          <span className="error-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}>
              <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
              <line x1="12" y1="9" x2="12" y2="13" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
          </span>
          <span className="error-message">
            Failed to load dashboard data: {error}
          </span>
          <button className="error-retry" onClick={handleRetry}>
            Retry
          </button>
        </div>
      )}

      {/* Statistics Overview */}
      {!loading && !error && renderStatistics()}

      {/* Category Navigation */}
      {renderCategoryNav()}

      {/* Claims Grid */}
      <div className="content-area-new">
        {renderClaimsGrid()}
      </div>
    </div>
  );
};

export default DashboardCustomer;

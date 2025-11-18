import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import dashboardService from '../../services/dashboardService';
import '../Dashboard.css';

const DashboardCompany = () => {
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
  
  // Search & Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  
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
        // Company users get all claims (page 1)
        const rawClaims = await dashboardService.getAllClaims({ page: 1, page_size: 200 });

        // Format claims for display
        const formattedClaims = rawClaims.map(claim => 
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
          highRiskCount: formattedClaims.filter(c => {
            const score = c.riskScore < 1 ? c.riskScore * 100 : c.riskScore;
            return score >= 70;
          }).length,
          averageRiskScore: formattedClaims.length > 0 ? 
            Math.round(formattedClaims.reduce((sum, claim) => {
              const score = claim.riskScore < 1 ? claim.riskScore * 100 : claim.riskScore;
              return sum + score;
            }, 0) / formattedClaims.length) : 0
        };
        setStatistics(stats);
        
        // Fetch backend-calculated metrics
        try {
          const [apr, totalVal, avgTime] = await Promise.all([
            dashboardService.getApprovalRate(),
            dashboardService.getTotalValue(),
            dashboardService.getAvgProcessingTime()
          ]);

          // merge into statistics for display
          setStatistics(prev => ({
            ...prev,
            approvalRate: apr.approval_rate,
            totalValueBackend: totalVal.total_value,
            avgProcessingDays: avgTime.avg_days
          }));
        } catch (e) {
          console.warn('Failed to fetch backend metrics', e);
        }
        
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

  // Filter claims based on active category, search, and sort
  useEffect(() => {
    let filtered = [...allClaims];
    
    // Apply category filter
    switch (activeCategory) {
      case 'pending':
        filtered = filtered.filter(c => 
          c.status === 'Under Review' || c.status === 'Pending'
        );
        break;
      case 'approved':
        filtered = filtered.filter(c => c.status === 'Approved');
        break;
      case 'rejected':
        filtered = filtered.filter(c => 
          c.status === 'Rejected' || c.status === 'Flagged'
        );
        break;
      case 'recent':
        filtered = filtered
          .sort((a, b) => new Date(b.date) - new Date(a.date))
          .slice(0, 20);
        break;
      case 'all':
      default:
        // Show all claims
        break;
    }
    
    // Apply search filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(claim => 
        claim.id.toLowerCase().includes(term) ||
        (claim.patientName && claim.patientName.toLowerCase().includes(term)) ||
        (claim.claimType && claim.claimType.toLowerCase().includes(term)) ||
        claim.status.toLowerCase().includes(term)
      );
    }
    
    // Apply sorting
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.date) - new Date(b.date);
          break;
        case 'amount':
          comparison = (a.claimAmount || 0) - (b.claimAmount || 0);
          break;
        case 'risk':
          comparison = (a.riskScore || 0) - (b.riskScore || 0);
          break;
        case 'status':
          comparison = a.status.localeCompare(b.status);
          break;
        default:
          comparison = 0;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    
    setFilteredClaims(filtered);
  }, [activeCategory, allClaims, searchTerm, sortBy, sortOrder]);

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
        return Math.min(allClaims.length, 20);
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
          <div className={`risk-score-small ${getRiskClass(claim.riskScore < 1 ? claim.riskScore * 100 : claim.riskScore)}`}>
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
          <h2>Company Dashboard Overview</h2>
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

  const renderSearchAndFilters = () => {
    return (
      <div className="search-filter-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search by ID, patient name, or status..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-controls">
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="date">Sort by Date</option>
            <option value="amount">Sort by Amount</option>
            <option value="risk">Sort by Risk Score</option>
            <option value="status">Sort by Status</option>
          </select>
          <button 
            className="sort-order-btn"
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
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
              ? "No claims available." 
              : `No claims found in the ${activeCategory} category.`
            }
          </p>
          {activeCategory === 'all' && (
            <button 
              className="btn-submit-claim"
              onClick={() => navigate('/submit')}
            >
              View All Claims
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
          <h1>Claims Dashboard (Company)</h1>
          <p className="header-subtitle">
            Welcome back, {user?.name || user?.username}
          </p>
        </div>
        <div className="header-actions">
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

      {/* Search and Filters */}
      {!loading && !error && renderSearchAndFilters()}

      {/* Category Navigation */}
      {renderCategoryNav()}

      {/* Claims Grid */}
      <div className="content-area-new">
        {renderClaimsGrid()}
      </div>
    </div>
  );
};

export default DashboardCompany;

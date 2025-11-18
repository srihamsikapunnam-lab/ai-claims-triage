// Legacy backup moved to `legacy/Dashboard_backup.js`.
// This file now re-exports the legacy backup to avoid breaking direct imports.

export { default } from './legacy/Dashboard_backup';
          >
            ➕ Submit New Claim
          </button>
        )}
      </div>

      {claims.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No claims found</h3>
          <p>There are no claims in this category yet.</p>
        </div>
      ) : (
        <div className="claims-table-wrapper">
          <table className="modern-claims-table">
            <thead>
              <tr>
                <th className="col-id">Claim ID</th>
                <th className="col-patient">Patient / Type</th>
                <th className="col-amount">Amount</th>
                <th className="col-status">Status</th>
                <th className="col-risk">Risk Score</th>
                <th className="col-date">Date</th>
                <th className="col-actions">Actions</th>
              </tr>
            </thead>
            <tbody>
              {claims.map(claim => (
                <tr 
                  key={claim.id} 
                  className="claim-row"
                  onClick={() => navigate(`/claims/${claim.id}`)}
                >
                  <td className="col-id">
                    <div className="claim-id-cell">
                      <span className="id-short">{claim.id.substring(0, 8)}</span>
                      <span className="id-full">{claim.id}</span>
                    </div>
                  </td>
                  <td className="col-patient">
                    <div className="patient-cell">
                      <div className="patient-name">{claim.patient}</div>
                      <div className="patient-type">{claim.type}</div>
                    </div>
                  </td>
                  <td className="col-amount">
                    <span className="amount-value">{formatCurrency(claim.amount)}</span>
                  </td>
                  <td className="col-status">
                    <span 
                      className="status-badge modern"
                      style={{ backgroundColor: getStatusColor(claim.status) }}
                    >
                      {getStatusIcon(claim.status)} {claim.status}
                    </span>
                  </td>
                  <td className="col-risk">
                    <div className="risk-indicator">
                      <div className="risk-score-box">
                        <span className={`score-number risk-${claim.risk < 30 ? 'low' : claim.risk < 70 ? 'medium' : 'high'}`}>
                          {claim.risk}%
                        </span>
                      </div>
                      <div className="risk-bar-mini">
                        <div 
                          className={`risk-fill-mini risk-${claim.risk < 30 ? 'low' : claim.risk < 70 ? 'medium' : 'high'}`}
                          style={{ width: `${claim.risk}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="col-date">
                    <span className="date-value">{claim.date}</span>
                  </td>
                  <td className="col-actions">
                    <button 
                      className="btn-view-details"
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/claims/${claim.id}`);
                      }}
                    >
                      View →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  return (
    <div className="dashboard-new">
      {/* Main Header */}
      <header className="dashboard-header-new">
        <div className="header-content">
          <h1>Dashboard</h1>
          <p className="header-subtitle">
            {user?.role === 'customer' ? 'Manage your insurance claims' : 'Oversee all claims and analytics'}
          </p>
        </div>
        
        {user?.role === 'customer' && (
          <div className="header-actions">
            <button 
              className="btn-primary-new"
              onClick={() => navigate('/submit')}
            >
              <span className="btn-icon">➕</span>
              Submit Claim
            </button>
          </div>
        )}
      </header>

      {error && (
        <div className="error-banner-new">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{error}</span>
          <button 
            className="error-retry"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      )}

      {/* Category Navigation */}
      <div className="category-nav-new">
        <button 
          className={`nav-item-new ${activeTab === 'recent' ? 'active' : ''}`}
          onClick={() => setActiveTab('recent')}
        >
          <span className="nav-icon-new">🕐</span>
          <span className="nav-text">Recent</span>
          <span className="nav-count">{recentClaims.length}</span>
        </button>
        <button 
          className={`nav-item-new ${activeTab === 'pending' ? 'active' : ''}`}
          onClick={() => setActiveTab('pending')}
        >
          <span className="nav-icon-new">⏳</span>
          <span className="nav-text">Pending</span>
          <span className="nav-count">{pendingClaims.length}</span>
        </button>
        <button 
          className={`nav-item-new ${activeTab === 'approved' ? 'active' : ''}`}
          onClick={() => setActiveTab('approved')}
        >
          <span className="nav-icon-new">✅</span>
          <span className="nav-text">Approved</span>
          <span className="nav-count">{approvedClaims.length}</span>
        </button>
        <button 
          className={`nav-item-new ${activeTab === 'rejected' ? 'active' : ''}`}
          onClick={() => setActiveTab('rejected')}
        >
          <span className="nav-icon-new">❌</span>
          <span className="nav-text">Rejected</span>
          <span className="nav-count">{rejectedClaims.length}</span>
        </button>
        <button 
          className={`nav-item-new ${activeTab === 'all' ? 'active' : ''}`}
          onClick={() => setActiveTab('all')}
        >
          <span className="nav-icon-new">📋</span>
          <span className="nav-text">All Claims</span>
          <span className="nav-count">{allClaims.length}</span>
        </button>
      </div>

      {/* Claims Display */}
      <div className="claims-section-new">
        <div className="section-header-new">
          <h2>
            {activeTab === 'recent' ? 'Recent Claims' :
             activeTab === 'pending' ? 'Pending Claims' :
             activeTab === 'approved' ? 'Approved Claims' :
             activeTab === 'rejected' ? 'Rejected Claims' :
             'All Claims'}
          </h2>
          <span className="claims-count">
            {getClaimsToDisplay().length} {getClaimsToDisplay().length === 1 ? 'claim' : 'claims'}
          </span>
        </div>
        
        {renderClaimsGrid()}
      </div>
    </div>
  );
};

export default Dashboard;
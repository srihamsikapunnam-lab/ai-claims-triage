import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import dashboardService from '../../services/dashboardService';
import '../Dashboard.css';

const Analytics = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    approvalRate: 0,
    totalValue: 0,
    avgProcessingTime: 0,
    totalClaims: 0
  });
  const [claimsData, setClaimsData] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const [approvalData, totalValueData, avgTimeData, claims] = await Promise.all([
          dashboardService.getApprovalRate(),
          dashboardService.getTotalValue(),
          dashboardService.getAvgProcessingTime(),
          dashboardService.getAllClaims({ page: 1, page_size: 100 })
        ]);

        setMetrics({
          approvalRate: approvalData.approval_rate || 0,
          totalValue: totalValueData.total_value || 0,
          avgProcessingTime: avgTimeData.avg_days || 0,
          approvalTrend: approvalData.trend || 0,
          valueTrend: totalValueData.trend || 0,
          timeTrend: avgTimeData.trend || 0
        });
        
        setClaimsData(claims || []);
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="dashboard-new">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-new">
      <div className="dashboard-header-new">
        <div className="header-content">
          <h1>Analytics Dashboard</h1>
          <p className="header-subtitle">
            Performance metrics and insights
          </p>
        </div>
      </div>

      {error && (
        <div className="error-banner-new">
          <span className="error-icon">!</span>
          <span className="error-message">
            Failed to load analytics: {error}
          </span>
        </div>
      )}

      <div className="statistics-section-new">
        <div className="section-header-new">
          <h2>Key Metrics</h2>
        </div>
        <div className="statistics-grid-new">
          <div className="stat-card-new" style={{'--accent-color': '#10b981'}}>
            <div className="stat-icon-new"></div>
            <div className="stat-content">
              <div className="stat-value">{metrics.approvalRate.toFixed(1)}%</div>
              <div className="stat-title">Approval Rate</div>
              {metrics.approvalTrend !== 0 && (
                <div className="stat-trend" style={{ color: metrics.approvalTrend > 0 ? '#10b981' : '#ef4444' }}>
                  {metrics.approvalTrend > 0 ? '↑' : '↓'} {Math.abs(metrics.approvalTrend).toFixed(1)}%
                </div>
              )}
            </div>
          </div>

          <div className="stat-card-new" style={{'--accent-color': '#06b6d4'}}>
            <div className="stat-icon-new"></div>
            <div className="stat-content">
              <div className="stat-value">{formatCurrency(metrics.totalValue)}</div>
              <div className="stat-title">Total Claims Value</div>
              {metrics.valueTrend !== 0 && (
                <div className="stat-trend" style={{ color: metrics.valueTrend > 0 ? '#10b981' : '#ef4444' }}>
                  {metrics.valueTrend > 0 ? '↑' : '↓'} {formatCurrency(Math.abs(metrics.valueTrend))}
                </div>
              )}
            </div>
          </div>

          <div className="stat-card-new" style={{'--accent-color': '#f59e0b'}}>
            <div className="stat-icon-new"></div>
            <div className="stat-content">
              <div className="stat-value">{metrics.avgProcessingTime.toFixed(2)}</div>
              <div className="stat-title">Avg Processing Days</div>
              {metrics.timeTrend !== 0 && (
                <div className="stat-trend" style={{ color: metrics.timeTrend < 0 ? '#10b981' : '#ef4444' }}>
                  {metrics.timeTrend > 0 ? '↑' : '↓'} {Math.abs(metrics.timeTrend).toFixed(2)}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Model Performance Visualization */}
      <div className="content-area-new">
        <div className="model-graph-section">
          <div className="section-header-new">
            <h2>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
                <rect x="4" y="4" width="16" height="16" rx="2" />
                <rect x="9" y="9" width="6" height="6" />
                <path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" />
              </svg>
              ML Model Performance
            </h2>
          </div>
          
          <div className="model-cards-grid">
            {/* Risk Distribution Chart */}
            <div className="model-card">
              <h3>Risk Score Distribution</h3>
              <div className="risk-distribution-chart">
                {(() => {
                  const lowRisk = claimsData.filter(c => (c.risk_score || 0) < 30).length;
                  const mediumRisk = claimsData.filter(c => (c.risk_score || 0) >= 30 && (c.risk_score || 0) < 70).length;
                  const highRisk = claimsData.filter(c => (c.risk_score || 0) >= 70).length;
                  const total = claimsData.length || 1;
                  
                  return (
                    <>
                      <div className="bar-chart">
                        <div className="bar-item">
                          <div className="bar-label">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px', color: '#10b981' }}>
                              <circle cx="12" cy="12" r="10" />
                            </svg>
                            Low Risk
                          </div>
                          <div className="bar-container">
                            <div 
                              className="bar-fill low-risk" 
                              style={{ width: `${(lowRisk / total) * 100}%` }}
                            ></div>
                            <span className="bar-value">{lowRisk}</span>
                          </div>
                        </div>
                        <div className="bar-item">
                          <div className="bar-label">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px', color: '#f59e0b' }}>
                              <circle cx="12" cy="12" r="10" />
                            </svg>
                            Medium Risk
                          </div>
                          <div className="bar-container">
                            <div 
                              className="bar-fill medium-risk" 
                              style={{ width: `${(mediumRisk / total) * 100}%` }}
                            ></div>
                            <span className="bar-value">{mediumRisk}</span>
                          </div>
                        </div>
                        <div className="bar-item">
                          <div className="bar-label">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px', color: '#ef4444' }}>
                              <circle cx="12" cy="12" r="10" />
                            </svg>
                            High Risk
                          </div>
                          <div className="bar-container">
                            <div 
                              className="bar-fill high-risk" 
                              style={{ width: `${(highRisk / total) * 100}%` }}
                            ></div>
                            <span className="bar-value">{highRisk}</span>
                          </div>
                        </div>
                      </div>
                    </>
                  );
                })()}
              </div>
            </div>

            {/* Status Distribution */}
            <div className="model-card">
              <h3>Claims Status Breakdown</h3>
              <div className="status-distribution">
                {(() => {
                  const pending = claimsData.filter(c => ['pending', 'under_review'].includes(c.status?.toLowerCase())).length;
                  const approved = claimsData.filter(c => c.status?.toLowerCase() === 'approved').length;
                  const rejected = claimsData.filter(c => ['rejected', 'flagged'].includes(c.status?.toLowerCase())).length;
                  const total = claimsData.length || 1;
                  
                  return (
                    <div className="donut-chart">
                      <div className="donut-segment-info">
                        <div className="segment-item">
                          <span className="segment-color pending"></span>
                          <span>Pending: {pending} ({((pending/total)*100).toFixed(1)}%)</span>
                        </div>
                        <div className="segment-item">
                          <span className="segment-color approved"></span>
                          <span>Approved: {approved} ({((approved/total)*100).toFixed(1)}%)</span>
                        </div>
                        <div className="segment-item">
                          <span className="segment-color rejected"></span>
                          <span>Rejected: {rejected} ({((rejected/total)*100).toFixed(1)}%)</span>
                        </div>
                      </div>
                      <div className="donut-visual">
                        <svg viewBox="0 0 200 200" className="donut-svg">
                          <circle cx="100" cy="100" r="80" fill="none" stroke="#1e293b" strokeWidth="40"/>
                          {(() => {
                            let offset = 0;
                            const circumference = 2 * Math.PI * 80;
                            const segments = [
                              { value: pending, color: '#f59e0b' },
                              { value: approved, color: '#10b981' },
                              { value: rejected, color: '#ef4444' }
                            ];
                            
                            return segments.map((seg, i) => {
                              const percentage = seg.value / total;
                              const dashLength = circumference * percentage;
                              const result = (
                                <circle
                                  key={i}
                                  cx="100"
                                  cy="100"
                                  r="80"
                                  fill="none"
                                  stroke={seg.color}
                                  strokeWidth="40"
                                  strokeDasharray={`${dashLength} ${circumference}`}
                                  strokeDashoffset={-offset}
                                  transform="rotate(-90 100 100)"
                                />
                              );
                              offset += dashLength;
                              return result;
                            });
                          })()}
                        </svg>
                        <div className="donut-center">
                          <div className="donut-total">{claimsData.length}</div>
                          <div className="donut-label">Total Claims</div>
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          </div>

          {/* Model Accuracy Metrics */}
          <div className="model-metrics-card">
            <h3>
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
                <path d="M3 3v18h18" />
                <path d="M18 17V9M13 17V5M8 17v-3" />
              </svg>
              Model Accuracy & Performance
            </h3>
            <div className="metrics-grid">
              <div className="metric-box">
                <div className="metric-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}>
                    <circle cx="12" cy="12" r="10" />
                    <circle cx="12" cy="12" r="6" />
                    <circle cx="12" cy="12" r="2" />
                  </svg>
                </div>
                <div className="metric-content">
                  <div className="metric-value">
                    {claimsData.length > 0 ? 
                      ((claimsData.filter(c => c.status?.toLowerCase() === 'approved').length / claimsData.length) * 100).toFixed(1) 
                      : 0}%
                  </div>
                  <div className="metric-label">Prediction Accuracy</div>
                </div>
              </div>
              <div className="metric-box">
                <div className="metric-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}>
                    <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
                  </svg>
                </div>
                <div className="metric-content">
                  <div className="metric-value">{claimsData.length}</div>
                  <div className="metric-label">Total Predictions</div>
                </div>
              </div>
              <div className="metric-box">
                <div className="metric-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}>
                    <circle cx="11" cy="11" r="8" />
                    <path d="m21 21-4.35-4.35" />
                  </svg>
                </div>
                <div className="metric-content">
                  <div className="metric-value">
                    {claimsData.length > 0 ? 
                      (claimsData.reduce((sum, c) => sum + (c.risk_score || 0), 0) / claimsData.length).toFixed(1) 
                      : 0}
                  </div>
                  <div className="metric-label">Avg Risk Score</div>
                </div>
              </div>
              <div className="metric-box">
                <div className="metric-icon">
                  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '32px', height: '32px' }}>
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                  </svg>
                </div>
                <div className="metric-content">
                  <div className="metric-value">XGBoost</div>
                  <div className="metric-label">Model Type</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;

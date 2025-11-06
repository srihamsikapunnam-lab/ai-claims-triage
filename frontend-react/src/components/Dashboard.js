import React from 'react';
import ProgressTracker from './ProgressTracker';
import RiskDisplay from './RiskDisplay';
import './Dashboard.css';

const Dashboard = () => {
  const sampleClaims = [
    { id: 'CLM-001', status: 'Under Review', risk: 45 },
    { id: 'CLM-002', status: 'Approved', risk: 15 },
    { id: 'CLM-003', status: 'Flagged', risk: 85 }
  ];

  return (
    <div className="dashboard-page">
      <h2>📊 Claims Dashboard</h2>
      <div className="stats">
        <div className="stat-card">
          <h3>Total Claims</h3>
          <p>24</p>
        </div>
        <div className="stat-card">
          <h3>Pending Review</h3>
          <p>8</p>
        </div>
        <div className="stat-card">
          <h3>High Risk</h3>
          <p>3</p>
        </div>
      </div>
      
      <ProgressTracker />
      <RiskDisplay riskScore={45} />
      
      <div className="recent-claims">
        <h3>Recent Claims</h3>
        <table>
          <thead>
            <tr>
              <th>Claim ID</th>
              <th>Status</th>
              <th>Risk Score</th>
            </tr>
          </thead>
          <tbody>
            {sampleClaims.map(claim => (
              <tr key={claim.id}>
                <td>{claim.id}</td>
                <td>{claim.status}</td>
                <td>
                  <span className={`risk-badge risk-${claim.risk < 30 ? 'low' : claim.risk < 70 ? 'medium' : 'high'}`}>
                    {claim.risk}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Dashboard;
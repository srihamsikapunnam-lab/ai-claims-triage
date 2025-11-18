import React from 'react';
import './RiskDisplay.css';

const RiskDisplay = ({ riskScore = 65, claimId = "CLM-2024-001" }) => {
  const getRiskLevel = (score) => {
    if (score < 30) return { level: "Low", color: "#28a745", emoji: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#28a745" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle' }}><circle cx="12" cy="12" r="10" /></svg> };
    if (score < 70) return { level: "Medium", color: "#ffc107", emoji: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ffc107" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle' }}><circle cx="12" cy="12" r="10" /></svg> };
    return { level: "High", color: "#dc3545", emoji: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#dc3545" style={{ width: '16px', height: '16px', display: 'inline-block', verticalAlign: 'middle' }}><circle cx="12" cy="12" r="10" /></svg> };
  };

  const riskInfo = getRiskLevel(riskScore);

  return (
    <div className="risk-display">
      <h3>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
          <circle cx="12" cy="12" r="10" />
          <circle cx="12" cy="12" r="6" />
          <circle cx="12" cy="12" r="2" />
        </svg>
        AI Risk Assessment
      </h3>
      <div className="risk-card">
        <div className="risk-score">
          <div className="score-circle" style={{ borderColor: riskInfo.color }}>
            <span style={{ color: riskInfo.color }}>{riskScore}</span>
          </div>
          <div className="risk-level">
            <span className="level-badge" style={{ backgroundColor: riskInfo.color }}>
              {riskInfo.emoji} {riskInfo.level} Risk
            </span>
          </div>
        </div>
        
        <div className="risk-factors">
          <h4>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            Key Risk Factors:
          </h4>
          <ul>
            <li>Claim amount higher than policy average</li>
            <li>Multiple claims from same provider</li>
            <li>Unusual billing patterns detected</li>
            <li>Geographic inconsistency in service location</li>
          </ul>
        </div>

        <div className="recommendation">
          <h4>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '18px', height: '18px', display: 'inline-block', verticalAlign: 'middle', marginRight: '6px' }}>
              <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
              <rect x="8" y="2" width="8" height="4" rx="1" />
            </svg>
            Recommendation:
          </h4>
          <p>
            {riskScore < 30 ? "Auto-approve claim" : 
             riskScore < 70 ? "Schedule for manual review" : 
             "Flag for immediate investigation"}
          </p>
        </div>
      </div>
    </div>
  );
};

export default RiskDisplay;
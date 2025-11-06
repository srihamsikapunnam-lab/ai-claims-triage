import React from 'react';
import './RiskDisplay.css';

const RiskDisplay = ({ riskScore = 65, claimId = "CLM-2024-001" }) => {
  const getRiskLevel = (score) => {
    if (score < 30) return { level: "Low", color: "#28a745", emoji: "🟢" };
    if (score < 70) return { level: "Medium", color: "#ffc107", emoji: "🟡" };
    return { level: "High", color: "#dc3545", emoji: "🔴" };
  };

  const riskInfo = getRiskLevel(riskScore);

  return (
    <div className="risk-display">
      <h3>🎯 AI Risk Assessment</h3>
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
          <h4>🔍 Key Risk Factors:</h4>
          <ul>
            <li>Claim amount higher than policy average</li>
            <li>Multiple claims from same provider</li>
            <li>Unusual billing patterns detected</li>
            <li>Geographic inconsistency in service location</li>
          </ul>
        </div>

        <div className="recommendation">
          <h4>📋 Recommendation:</h4>
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
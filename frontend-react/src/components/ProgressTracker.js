import React from 'react';

const ProgressTracker = ({ status }) => {
  const stages = [
    { key: 'not_submitted', name: 'Not Submitted', icon: '⚪' },
    { key: 'submitted', name: 'Submitted', icon: '📨' },
    { key: 'processing', name: 'AI Processing', icon: '🤖' },
    { key: 'assessment', name: 'Risk Assessment', icon: '🔍' },
    { key: 'review', name: 'Final Review', icon: '✅' }
  ];

  const currentIndex = stages.findIndex(stage => stage.key === status);

  return (
    <div className="progress-tracker">
      <h2>📊 Claim Status</h2>
      <div className="progress-stages">
        {stages.map((stage, index) => (
          <div
            key={stage.key}
            className={`stage ${
              index < currentIndex ? 'completed' : 
              index === currentIndex ? 'current' : 'pending'
            }`}
          >
            <div className="stage-icon">{stage.icon}</div>
            <div className="stage-name">{stage.name}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressTracker;
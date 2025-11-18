import React from 'react';

const ProgressTracker = ({ status }) => {
  const stages = [
    { key: 'not_submitted', name: 'Not Submitted', icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#cbd5e1" style={{ width: '24px', height: '24px' }}><circle cx="12" cy="12" r="10" /></svg> },
    { key: 'submitted', name: 'Submitted', icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px' }}><rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg> },
    { key: 'processing', name: 'AI Processing', icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px' }}><rect x="4" y="4" width="16" height="16" rx="2" /><rect x="9" y="9" width="6" height="6" /><path d="M9 1v3M15 1v3M9 20v3M15 20v3M20 9h3M20 14h3M1 9h3M1 14h3" /></svg> },
    { key: 'assessment', name: 'Risk Assessment', icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px' }}><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg> },
    { key: 'review', name: 'Final Review', icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px' }}><path d="M20 6 9 17l-5-5" /></svg> }
  ];

  const currentIndex = stages.findIndex(stage => stage.key === status);

  return (
    <div className="progress-tracker">
      <h2>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px', display: 'inline-block', verticalAlign: 'middle', marginRight: '8px' }}>
          <path d="M3 3v18h18" />
          <path d="M18 17V9M13 17V5M8 17v-3" />
        </svg>
        Claim Status
      </h2>
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
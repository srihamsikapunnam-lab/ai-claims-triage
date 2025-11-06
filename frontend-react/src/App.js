import React, { useState } from 'react';
import ClaimForm from './components/ClaimForm';
import Dashboard from './components/Dashboard';
import ProgressTracker from './components/ProgressTracker';
import RiskDisplay from './components/RiskDisplay';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const renderPage = () => {
    switch(currentPage) {
      case 'submit':
        return (
          <div className="page">
            <ProgressTracker />
            <ClaimForm />
          </div>
        );
      case 'dashboard':
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Claims Triage System</h1>
        <nav className="app-nav">
          <button 
            className={currentPage === 'dashboard' ? 'active' : ''}
            onClick={() => setCurrentPage('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={currentPage === 'submit' ? 'active' : ''}
            onClick={() => setCurrentPage('submit')}
          >
            📋 Submit Claim
          </button>
        </nav>
      </header>
      <main>
        {renderPage()}
      </main>
    </div>
  );
}

export default App;

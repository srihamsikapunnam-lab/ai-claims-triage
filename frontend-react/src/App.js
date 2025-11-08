import React, { useEffect, useState } from 'react';
import ClaimsAPI from './services/api';
import './App.css';

function App() {
  const [apiStatus, setApiStatus] = useState('checking...');

  useEffect(() => {
    const testConnection = async () => {
      const isHealthy = await ClaimsAPI.checkHealth();
      setApiStatus(isHealthy ? '✅ Backend Connected' : '❌ Backend Disconnected');
    };
    
    testConnection();
  }, []);

  return (
    <div className="App">
      <div style={{padding: '10px', background: '#f0f0f0', marginBottom: '20px'}}>
        <strong>API Status:</strong> {apiStatus}
      </div>
      
      <h1>Claims Triage System</h1>
      {/* Your existing form and components will go here later */}
    </div>
  );
}

export default App;
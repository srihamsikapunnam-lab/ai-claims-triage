// components/BackendTester.js - COMPLETELY NEW FILE
import React, { useState } from 'react';
import ClaimsAPI from '../services/api';

const BackendTester = () => {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState(false);

  const testAllEndpoints = async () => {
    setLoading(true);
    const testResults = {};
    
    // Test health endpoint
    try {
      testResults.health = await ClaimsAPI.checkHealth();
    } catch (error) {
      testResults.health = { error: error.message };
    }
    
    // Test claim submission
    try {
      testResults.submission = await ClaimsAPI.submitClaim({
        title: "Week 4 Test Claim",
        description: "Testing backend integration",
        category: "medical",
        amount: "1500",
        claimant: "Test User"
      });
    } catch (error) {
      testResults.submission = { error: error.message };
    }
    
    // Test prediction
    try {
      testResults.prediction = await ClaimsAPI.predictClaim({
        description: "Test claim for prediction"
      });
    } catch (error) {
      testResults.prediction = { error: error.message };
    }
    
    setResults(testResults);
    setLoading(false);
  };

  return (
    <div style={{border: '1px solid #28a745', padding: '15px', margin: '10px 0', background: '#f8f9fa'}}>
      <h4>🚀 Week 4 - Backend Integration Tester</h4>
      <button onClick={testAllEndpoints} disabled={loading}>
        {loading ? 'Testing Endpoints...' : 'Test All Backend Endpoints'}
      </button>
      
      {Object.keys(results).length > 0 && (
        <div style={{marginTop: '15px'}}>
          <h5>Test Results:</h5>
          {Object.entries(results).map(([endpoint, result]) => (
            <div key={endpoint} style={{marginBottom: '10px'}}>
              <strong>{endpoint.toUpperCase()}:</strong>
              <pre style={{background: 'white', padding: '5px', fontSize: '12px'}}>
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BackendTester;
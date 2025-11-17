import React, { useState, useEffect } from 'react';
import ClaimsAPI from '../services/api';

const BackendStatus = () => {
  const [status, setStatus] = useState('checking');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const checkBackendStatus = async () => {
      try {
        const response = await ClaimsAPI.healthCheck();
        setStatus('connected');
        setMessage('Backend is connected and responsive');
      } catch (error) {
        setStatus('error');
        setMessage('Backend connection failed: ' + error.message);
      }
    };

    checkBackendStatus();
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'connected':
        return '#28a745'; // Green
      case 'error':
        return '#dc3545'; // Red
      case 'checking':
        return '#ffc107'; // Yellow
      default:
        return '#6c757d'; // Gray
    }
  };

  return (
    <div style={{
      padding: '10px',
      margin: '10px 0',
      border: `2px solid ${getStatusColor()}`,
      borderRadius: '5px',
      backgroundColor: '#f8f9fa'
    }}>
      <strong>Backend Status: </strong>
      <span style={{ color: getStatusColor(), fontWeight: 'bold' }}>
        {status.toUpperCase()}
      </span>
      {message && <p style={{ margin: '5px 0 0 0', fontSize: '14px' }}>{message}</p>}
    </div>
  );
};

export default BackendStatus;
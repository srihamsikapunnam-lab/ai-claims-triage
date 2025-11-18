import authService from './authService';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

const ensureApiPrefix = (endpoint) => {
  if (!endpoint) return '/api';
  if (endpoint.startsWith('/api')) return endpoint;
  // Ensure leading slash
  if (!endpoint.startsWith('/')) endpoint = '/' + endpoint;
  return `/api${endpoint}`;
};

const apiClient = {
  async get(endpoint) {
    try {
      const fullEndpoint = ensureApiPrefix(endpoint);
      const response = await fetch(`${API_BASE}${fullEndpoint}`, {
        headers: {
          'Authorization': `Bearer ${authService.getToken()}`,
        },
      });

      if (!response.ok) {
        // If 401 or 404, return mock data for development
        if (response.status === 401 || response.status === 404) {
          return apiClient.getMockData(endpoint);
        }
        const error = await response.json();
        throw new Error(error.detail || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.warn(`API call failed for ${endpoint}, using mock data:`, error);
      return apiClient.getMockData(endpoint);
    }
  },

  async post(endpoint, data) {
    const fullEndpoint = ensureApiPrefix(endpoint);
    const response = await fetch(`${API_BASE}${fullEndpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authService.getToken()}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return await response.json();
  },

  async put(endpoint, data) {
    const fullEndpoint = ensureApiPrefix(endpoint);
    const response = await fetch(`${API_BASE}${fullEndpoint}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authService.getToken()}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return await response.json();
  },

  async patch(endpoint, data) {
    const fullEndpoint = ensureApiPrefix(endpoint);
    const response = await fetch(`${API_BASE}${fullEndpoint}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authService.getToken()}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return await response.json();
  },

  async delete(endpoint) {
    const fullEndpoint = ensureApiPrefix(endpoint);
    const response = await fetch(`${API_BASE}${fullEndpoint}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authService.getToken()}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Request failed');
    }

    return await response.json();
  },

  async uploadFile(endpoint, formData) {
    const fullEndpoint = ensureApiPrefix(endpoint);
    const response = await fetch(`${API_BASE}${fullEndpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authService.getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return await response.json();
  },
};

export default apiClient;

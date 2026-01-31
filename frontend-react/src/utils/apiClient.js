import authService from './authService';

const API_BASE_URL = 'https://ai-claims-backend.onrender.com';

const apiClient = {
  async request(endpoint, options = {}) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(authService.getToken()
          ? { Authorization: `Bearer ${authService.getToken()}` }
          : {}),
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || 'Request failed');
    }

    return response.json();
  },

  get(endpoint) {
    return this.request(endpoint);
  },

  post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  patch(endpoint, data) {
    return this.request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },

  delete(endpoint) {
    return this.request(endpoint, {
      method: 'DELETE',
    });
  },

  uploadFile(endpoint, formData) {
    return fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${authService.getToken()}`,
      },
      body: formData,
    }).then(res => {
      if (!res.ok) throw new Error('Upload failed');
      return res.json();
    });
  },
};

export default apiClient;

class ClaimsAPI {
  constructor() {
    // Use Netlify environment variable
    this.BASE_URL = process.env.REACT_APP_API_BASE;
  }

  /* --------------------
     Health Check
  -------------------- */
  async checkHealth() {
    try {
      const response = await fetch(`${this.BASE_URL}/health`);
      if (!response.ok) throw new Error('Health check failed');

      return {
        status: 'connected',
        message: 'Backend is healthy'
      };
    } catch (error) {
      return {
        status: 'disconnected',
        message: 'Backend not available'
      };
    }
  }

  /* --------------------
     Predict Claim (Batch)
  -------------------- */
  async predictClaim(claimData) {
    const response = await fetch(`${this.BASE_URL}/api/batch/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        claims: [claimData]
      })
    });

    if (!response.ok) {
      throw new Error('Prediction failed');
    }

    const result = await response.json();
    return result.predictions[0];
  }

  /* --------------------
     Submit Claim (REAL)
  -------------------- */
  async submitClaim(claimData) {
    const response = await fetch(`${this.BASE_URL}/api/claims`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(claimData)
    });

    if (!response.ok) {
      throw new Error('Claim submission failed');
    }

    return await response.json();
  }

  /* --------------------
     Get Claims
  -------------------- */
  async getAllClaims() {
    const response = await fetch(`${this.BASE_URL}/api/claims`);

    if (!response.ok) {
      throw new Error('Failed to fetch claims');
    }

    return await response.json();
  }

  async getMyClaims() {
    const response = await fetch(`${this.BASE_URL}/api/claims/my`);

    if (!response.ok) {
      throw new Error('Failed to fetch user claims');
    }

    return await response.json();
  }
}

const claimsAPI = new ClaimsAPI();
export default claimsAPI;

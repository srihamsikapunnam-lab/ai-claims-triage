class ClaimsAPI {
  constructor() {
    // Render backend URL (NO trailing slash)
    this.BASE_URL = 'https://ai-claims-backend.onrender.com';
  }

  /* ======================
     HEALTH CHECK
     ====================== */
  async checkHealth() {
    try {
      const res = await fetch(`${this.BASE_URL}/health`);
      if (!res.ok) throw new Error('Health check failed');

      return {
        status: 'connected',
        message: 'Backend is healthy'
      };
    } catch (err) {
      console.error('Health check error:', err);
      return {
        status: 'disconnected',
        message: 'Backend not available'
      };
    }
  }

  /* ======================
     AI PREDICTION (BATCH)
     ====================== */
  async predictClaim(claimData) {
    try {
      const res = await fetch(`${this.BASE_URL}/api/batch/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          claims: [claimData] // backend expects an array
        })
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || 'Prediction failed');
      }

      const data = await res.json();
      return data.predictions?.[0];
    } catch (err) {
      console.error('Predict claim error:', err);
      throw err;
    }
  }

  /* ======================
     SUBMIT CLAIM (DATABASE)
     ====================== */
  async submitClaim(claimData) {
    try {
      const res = await fetch(`${this.BASE_URL}/api/claims`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(claimData)
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || 'Claim submission failed');
      }

      return await res.json();
    } catch (err) {
      console.error('Submit claim error:', err);
      throw err;
    }
  }

  /* ======================
     GET ALL CLAIMS (ADMIN)
     ====================== */
  async getAllClaims() {
    try {
      const res = await fetch(`${this.BASE_URL}/api/claims`);

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || 'Failed to fetch claims');
      }

      return await res.json();
    } catch (err) {
      console.error('Get all claims error:', err);
      throw err;
    }
  }

  /* ======================
     GET USER CLAIMS
     ====================== */
  async getMyClaims() {
    try {
      const res = await fetch(`${this.BASE_URL}/api/claims/my`);

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || 'Failed to fetch user claims');
      }

      return await res.json();
    } catch (err) {
      console.error('Get my claims error:', err);
      throw err;
    }
  }
}

const claimsAPI = new ClaimsAPI();
export default claimsAPI;

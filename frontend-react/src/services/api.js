class ClaimsAPI {
    constructor() {
        this.BASE_URL = 'http://localhost:8000';
    }

    async checkHealth() {
        try {
            const response = await fetch(`${this.BASE_URL}/health`);
            return { 
                status: response.ok ? 'connected' : 'error',
                message: response.ok ? 'Backend is healthy' : 'Backend error'
            };
        } catch (error) {
            return { 
                status: 'disconnected', 
                message: 'Backend not available' 
            };
        }
    }

    // Use the batch predict endpoint instead of /predict
    async predictClaim(claimData) {
        try {
            const response = await fetch(`${this.BASE_URL}/api/batch/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    claims: [claimData]  // Wrap in array for batch endpoint
                })
            });
            const result = await response.json();
            return result.predictions ? result.predictions[0] : result;
        } catch (error) {
            console.error('API Error:', error);
            return this.getMockPrediction(claimData);
        }
    }

    // Submit claim - may need adjustment based on actual endpoints
    async submitClaim(claimData) {
        try {
            // Try using batch predict for now since no direct submit endpoint
            const response = await fetch(`${this.BASE_URL}/api/batch/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    claims: [{
                        title: claimData.title,
                        description: claimData.description,
                        category: claimData.category,
                        amount: claimData.amount,
                        claimant: claimData.claimant
                    }]
                })
            });
            const result = await response.json();
            return result.predictions ? result.predictions[0] : result;
        } catch (error) {
            console.error('Submit Claim Error:', error);
            return this.getMockSubmission(claimData);
        }
    }

    // Get all claims - may not be available
    async getClaims() {
        try {
            // Try root endpoint or return empty
            const response = await fetch(`${this.BASE_URL}/`);
            return await response.json();
        } catch (error) {
            console.error('Get Claims Error:', error);
            return { claims: [], note: 'Using mock data - endpoint may not exist' };
        }
    }

    // Mock data for development
    getMockPrediction(claimData) {
        return {
            prediction: 'MEDIUM_PRIORITY',
            confidence: 0.76,
            triage_score: 65,
            message: 'Mock prediction - backend not available'
        };
    }

    getMockSubmission(claimData) {
        return {
            id: `mock-${Date.now()}`,
            status: 'submitted',
            triage_score: Math.floor(Math.random() * 100),
            category: claimData.category || 'general',
            confidence: 0.85,
            note: 'Mock submission - backend integration in progress'
        };
    }
}

export default new ClaimsAPI();
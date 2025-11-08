// src/services/api.js
class ClaimsAPI {
    async predictClaim(claimData) {
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(claimData)
            });
            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            return { error: 'Failed to connect to backend' };
        }
    }

    async checkHealth() {
        try {
            const response = await fetch('/health');
            return response.ok;
        } catch (error) {
            return false;
        }
    }
}

export default new ClaimsAPI();
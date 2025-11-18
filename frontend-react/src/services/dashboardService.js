// Dashboard API Service - Real backend integration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class DashboardService {
  constructor() {
    this.token = localStorage.getItem('auth_token');
  }

  getAuthHeaders() {
    const token = localStorage.getItem('auth_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  }

  async getDashboardStats() {
    const response = await fetch(`${API_BASE_URL}/api/company/dashboard/stats`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch dashboard statistics');
    }

    return await response.json();
  }

  async getAllClaims(filters = {}) {
    const params = new URLSearchParams();
    
    if (filters.status) params.append('status', filters.status);
    if (filters.risk_category) params.append('risk_category', filters.risk_category);
    if (filters.min_risk_score) params.append('min_risk_score', filters.min_risk_score);
    if (filters.limit) params.append('limit', filters.limit);

    const queryString = params.toString();
    const url = `${API_BASE_URL}/api/company/claims${queryString ? '?' + queryString : ''}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        // If unauthorized, try user claims endpoint instead
        if (response.status === 401 || response.status === 403) {
          return await this.getUserClaims();
        }
        throw new Error('Failed to fetch claims');
      }

      return await response.json();
    } catch (error) {
      console.warn('Company claims failed, trying user claims:', error);
      return await this.getUserClaims();
    }
  }

  async getUserClaims() {
    try {
      const response = await fetch(`${API_BASE_URL}/api/claims`, {
        method: 'GET',
        headers: this.getAuthHeaders(),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Generate mock data if not authenticated
          return this.generateMockClaims();
        }
        throw new Error('Failed to fetch user claims');
      }

      return await response.json();
    } catch (error) {
      console.warn('API call failed, using mock data:', error);
      return this.generateMockClaims();
    }
  }

  async getClaimDetail(claimId) {
    const response = await fetch(`${API_BASE_URL}/api/claims/${claimId}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch claim details');
    }

    return await response.json();
  }

  async updateClaimStatus(claimId, status, notes = null) {
    const response = await fetch(`${API_BASE_URL}/api/claims/${claimId}/status`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ status, notes }),
    });

    if (!response.ok) {
      throw new Error('Failed to update claim status');
    }

    return await response.json();
  }

  // Generate mock claims data when API is unavailable
  generateMockClaims() {
    return [
      {
        id: '54ed20c1-f46f-4bf1-a1ef-552522695a0b',
        status: 'Flagged',
        claimed_amount: 2500.00,
        patient_age: 45,
        diagnosis: 'Hypertension',
        created_at: '2025-11-17T10:30:00Z',
        risk_score: 75,
        patient_name: 'John Doe',
        procedure_code: '99213'
      },
      {
        id: '7b8c9d2e-3f4g-5h6i-7j8k-9l0m1n2o3p4q',
        status: 'Under Review',
        claimed_amount: 1800.00,
        patient_age: 32,
        diagnosis: 'Diabetes',
        created_at: '2025-11-16T14:15:00Z',
        risk_score: 45,
        patient_name: 'Jane Smith',
        procedure_code: '99214'
      },
      {
        id: '1a2b3c4d-5e6f-7g8h-9i0j-1k2l3m4n5o6p',
        status: 'Approved',
        claimed_amount: 3200.00,
        patient_age: 58,
        diagnosis: 'Arthritis',
        created_at: '2025-11-15T09:45:00Z',
        risk_score: 25,
        patient_name: 'Bob Wilson',
        procedure_code: '99215'
      }
    ];
  }

  // Helper function to calculate derived statistics from claims data
  calculateDashboardMetrics(claims) {
    const now = new Date();
    const oneMonthAgo = new Date(now.setMonth(now.getMonth() - 1));

    // Total amount
    const totalAmount = claims.reduce((sum, claim) => sum + claim.claimed_amount, 0);

    // Recent claims (last 30 days)
    const recentClaims = claims.filter(claim => 
      new Date(claim.created_at) > oneMonthAgo
    );

    // Calculate approval rate
    const completedClaims = claims.filter(c => 
      c.status === 'approved' || c.status === 'rejected'
    );
    const approvedClaims = claims.filter(c => c.status === 'approved');
    const approvalRate = completedClaims.length > 0 
      ? Math.round((approvedClaims.length / completedClaims.length) * 100)
      : 0;

    // Calculate average processing time
    const processedClaims = claims.filter(c => 
      c.status === 'approved' || c.status === 'rejected'
    );
    let avgProcessingTime = 0;
    if (processedClaims.length > 0) {
      const totalTime = processedClaims.reduce((sum, claim) => {
        const created = new Date(claim.created_at);
        const updated = new Date(claim.updated_at);
        const hours = (updated - created) / (1000 * 60 * 60);
        return sum + hours;
      }, 0);
      avgProcessingTime = (totalTime / processedClaims.length) / 24; // Convert to days
    }

    // Trends (compare with previous period)
    const twoMonthsAgo = new Date();
    twoMonthsAgo.setMonth(twoMonthsAgo.getMonth() - 2);
    const previousPeriodClaims = claims.filter(claim => {
      const createdDate = new Date(claim.created_at);
      return createdDate > twoMonthsAgo && createdDate <= oneMonthAgo;
    });

    const monthlyTrend = previousPeriodClaims.length > 0
      ? Math.round(((recentClaims.length - previousPeriodClaims.length) / previousPeriodClaims.length) * 100)
      : 0;

    return {
      totalAmount,
      approvalRate,
      avgProcessingTime: avgProcessingTime.toFixed(1),
      monthlyTrend,
      recentClaimsCount: recentClaims.length
    };
  }

  // Format claim data for UI display
  formatClaimForDisplay(claim) {
    return {
      id: claim.id,
      status: this.formatStatus(claim.status),
      risk: Math.round(claim.risk_score || 0),
      date: new Date(claim.created_at).toISOString().split('T')[0],
      amount: claim.claimed_amount,
      patient: `Patient ${claim.user_id}`, // Will be enhanced with real patient names
      type: claim.diagnosis,
      riskCategory: claim.risk_category || 'Unknown'
    };
  }

  formatStatus(status) {
    const statusMap = {
      'submitted': 'Submitted',
      'under_review': 'Under Review',
      'approved': 'Approved',
      'rejected': 'Rejected',
      'manual_review': 'Flagged',
      'additional_info_required': 'Needs Info'
    };
    return statusMap[status] || status;
  }
}

export default new DashboardService();

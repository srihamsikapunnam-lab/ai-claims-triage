// Dashboard API Service - Real backend integration
const API_BASE_URL = 'https://ai-claims-backend.onrender.com/api';

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
    console.log('Fetching dashboard stats from:', `${API_BASE_URL}/company/dashboard/stats`);
    const response = await fetch(`${API_BASE_URL}/company/dashboard/stats`, {
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
    const url = `${API_BASE_URL}/company/claims${queryString ? '?' + queryString : ''}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch claims');
    }

    return await response.json();
  }

  async getUserClaims() {
    const response = await fetch(`${API_BASE_URL}/claims`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch user claims');
    }

    return await response.json();
  }

  async getClaimDetail(claimId) {
    const response = await fetch(`${API_BASE_URL}/claims/${claimId}`, {
      method: 'GET',
      headers: this.getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch claim details');
    }

    return await response.json();
  }

  async updateClaimStatus(claimId, status, notes = null) {
    const response = await fetch(`${API_BASE_URL}/claims/${claimId}/status`, {
      method: 'PUT',
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ status, notes }),
    });

    if (!response.ok) {
      throw new Error('Failed to update claim status');
    }

    return await response.json();
  }

  // Calculate derived statistics from claims data
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

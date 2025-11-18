import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import dashboardService from '../services/dashboardService';
import '../Dashboard.css';

// Legacy backup of the older dashboard implementation.
// Moved here to keep the main components folder clean.

const Dashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState({
    totalClaims: 0,
    pendingReview: 0,
    highRisk: 0,
    approved: 0,
    rejected: 0,
    totalAmount: 0,
    avgProcessingTime: 0
  });

  const [recentClaims, setRecentClaims] = useState([]);
  const [allClaims, setAllClaims] = useState([]);
  const [pendingClaims, setPendingClaims] = useState([]);
  const [approvedClaims, setApprovedClaims] = useState([]);
  const [rejectedClaims, setRejectedClaims] = useState([]);
  const [activeTab, setActiveTab] = useState('recent');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        let claims = [];
        if (user?.role === 'company_admin' || user?.role === 'company_staff') {
          claims = await dashboardService.getAllClaims({ limit: 100 });
        } else {
          claims = await dashboardService.getUserClaims();
        }
        const formattedClaims = claims.map(claim => dashboardService.formatClaimForDisplay(claim));
        setAllClaims(formattedClaims);
        const recent = formattedClaims.sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 10);
        setRecentClaims(recent);
        setPendingClaims(formattedClaims.filter(c => c.status === 'Under Review' || c.status === 'Pending'));
        setApprovedClaims(formattedClaims.filter(c => c.status === 'Approved'));
        setRejectedClaims(formattedClaims.filter(c => c.status === 'Rejected' || c.status === 'Flagged'));
      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError(err.message);
        setAllClaims([]);
        setRecentClaims([]);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, [user]);

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-legacy">
      <h2>Legacy Dashboard (backup)</h2>
      <p>This is the moved backup version of the dashboard kept for reference.</p>
    </div>
  );
};

export default Dashboard;

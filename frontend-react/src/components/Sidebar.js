import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import './Sidebar.css';

const Sidebar = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuth();
  
  // Dispatch sidebar state changes
  useEffect(() => {
    const event = new CustomEvent('sidebarToggle', { 
      detail: { expanded: isExpanded } 
    });
    window.dispatchEvent(event);
  }, [isExpanded]);

  const menuItems = [
    {
      icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /></svg>,
      label: 'Dashboard',
      path: '/dashboard',
      roles: ['customer', 'company_admin', 'company_staff']
    },
    {
      icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}><path d="M12 5v14M5 12h14" /></svg>,
      label: 'Submit Claim',
      path: '/submit',
      roles: ['customer']
    },
    {
      icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" /><rect x="8" y="2" width="8" height="4" rx="1" /></svg>,
      label: 'All Claims',
      path: '/claims',
      roles: ['company_admin', 'company_staff']
    },
    {
      icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}><path d="M3 3v18h18" /><path d="M18 17V9M13 17V5M8 17v-3" /></svg>,
      label: 'Analytics',
      path: '/analytics',
      roles: ['company_admin', 'company_staff']
    },
    {
      icon: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}><circle cx="11" cy="11" r="8" /><path d="m21 21-4.35-4.35" /></svg>,
      label: 'OCR Verify',
      path: '/verify',
      roles: ['customer', 'company_admin', 'company_staff']
    }
  ];

  const isActive = (path) => location.pathname === path;


  

  
  const handleNavigation = (path) => {
    navigate(path);
    if (window.innerWidth <= 768) {
      setIsExpanded(false);
    }
  };

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.role)
  );

  return (
    <>
      <div 
        className={`sidebar ${isExpanded ? 'expanded' : 'collapsed'}`}
        onMouseEnter={() => setIsExpanded(true)}
        onMouseLeave={() => setIsExpanded(false)}
      >
        {/* Logo Section */}
        <div className="sidebar-header">
          <div className="logo-container">
            <span className="logo-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px' }}>
                <path d="M3 21h18" />
                <path d="M5 21V7l8-4v18" />
                <path d="M19 21V11l-6-4" />
                <path d="M9 9v.01" />
                <path d="M9 12v.01" />
                <path d="M9 15v.01" />
                <path d="M9 18v.01" />
              </svg>
            </span>
            {isExpanded && (
              <span className="logo-text">Claims Triage</span>
            )}
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="sidebar-nav">
          {filteredMenuItems.map((item, index) => (
            <button
              key={index}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
              onClick={() => handleNavigation(item.path)}
              title={!isExpanded ? item.label : ''}
            >
              <span className="nav-icon">{item.icon}</span>
              {isExpanded && (
                <span className="nav-label">{item.label}</span>
              )}
            </button>
          ))}
        </nav>

        {/* User Section */}
        <div className="sidebar-footer">
          <div className="user-section">
            <div className="user-avatar">
              <span className="avatar-icon">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '24px', height: '24px' }}>
                  <circle cx="12" cy="8" r="5" />
                  <path d="M20 21a8 8 0 1 0-16 0" />
                </svg>
              </span>
            </div>
            {isExpanded && (
              <div className="user-info">
                <div className="user-name">{user?.full_name || user?.email}</div>
                <div className="user-role">{user?.role?.replace('_', ' ')}</div>
              </div>
            )}
          </div>
          
          <button
            className="logout-btn"
            onClick={logout}
            title={!isExpanded ? 'Logout' : ''}
          >
            <span className="logout-icon">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ width: '20px', height: '20px' }}>
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                <polyline points="16 17 21 12 16 7" />
                <line x1="21" y1="12" x2="9" y2="12" />
              </svg>
            </span>
            {isExpanded && (
              <span className="logout-label">Logout</span>
            )}
          </button>
        </div>

        {/* Toggle Button */}
        <button 
          className="sidebar-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <span className={`toggle-icon ${isExpanded ? 'expanded' : ''}`}>
            ◀
          </span>
        </button>
      </div>

      {/* Mobile Overlay */}
      {isExpanded && (
        <div 
          className="sidebar-overlay"
          onClick={() => setIsExpanded(false)}
        />
      )}
    </>
  );
};

export default Sidebar;
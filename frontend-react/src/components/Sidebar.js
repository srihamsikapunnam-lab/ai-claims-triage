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
      icon: '📊',
      label: 'Dashboard',
      path: '/dashboard',
      roles: ['customer', 'company_admin', 'company_staff']
    },
    {
      icon: '➕',
      label: 'Submit Claim',
      path: '/submit',
      roles: ['customer']
    },
    {
      icon: '📋',
      label: 'All Claims',
      path: '/claims',
      roles: ['company_admin', 'company_staff']
    },
    {
      icon: '📈',
      label: 'Analytics',
      path: '/analytics',
      roles: ['company_admin', 'company_staff']
    }
  ];

  const isActive = (path) => location.pathname === path;

  const handleMouseEnter = () => {
    if (window.innerWidth > 768) {
      setIsExpanded(true);
    }
  };
  
  const handleMouseLeave = () => {
    if (window.innerWidth > 768) {
      setIsExpanded(false);
    }
  };
  
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
            <span className="logo-icon">🏥</span>
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
              <span className="avatar-icon">👤</span>
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
            <span className="logout-icon">🚪</span>
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
import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth }   from '../context/AuthContext';
import { useFarmer } from '../context/FarmerContext';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/',           icon: '🏠', label: 'Dashboard'   },
  { to: '/chat',       icon: '🤖', label: 'AI Chat'      },
  { to: '/crops',      icon: '🌾', label: 'Crops'        },
  { to: '/soil',       icon: '🪱', label: 'Soil Analysis'},
  { to: '/pests',      icon: '🐛', label: 'Pest & Disease'},
  { to: '/fertilizer', icon: '🧪', label: 'Fertilizer'  },
  { to: '/irrigation', icon: '💧', label: 'Irrigation'   },
  { to: '/market',     icon: '📊', label: 'Market Prices'},
];

const BOTTOM_ITEMS = [
  { to: '/profile',  icon: '👨‍🌾', label: 'Profile'  },
  { to: '/settings', icon: '⚙️',  label: 'Settings' },
];

export default function Sidebar({ collapsed, onToggle }) {
  const { user, logout } = useAuth();
  const { profile }      = useFarmer();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <aside className={`sidebar${collapsed ? ' collapsed' : ''}`}>
      {/* Brand */}
      <div className="sidebar-brand">
        <span className="brand-icon">🌱</span>
        {!collapsed && <span className="brand-name">FarmAdvisor</span>}
        <button className="sidebar-toggle" onClick={onToggle} title="Toggle sidebar">
          {collapsed ? '›' : '‹'}
        </button>
      </div>

      {/* Farmer quick info */}
      {!collapsed && (
        <div className="sidebar-farmer">
          <div className="farmer-avatar">{user?.name?.[0]?.toUpperCase() || 'F'}</div>
          <div className="farmer-info">
            <p className="farmer-name">{user?.name || 'Farmer'}</p>
            <p className="farmer-location">
              {profile?.district && profile?.state
                ? `${profile.district}, ${profile.state}`
                : 'Set your location'}
            </p>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            title={collapsed ? item.label : ''}
          >
            <span className="nav-icon">{item.icon}</span>
            {!collapsed && <span className="nav-label">{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Bottom */}
      <div className="sidebar-bottom">
        {BOTTOM_ITEMS.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            title={collapsed ? item.label : ''}
          >
            <span className="nav-icon">{item.icon}</span>
            {!collapsed && <span className="nav-label">{item.label}</span>}
          </NavLink>
        ))}
        <button className="nav-item logout-btn" onClick={handleLogout} title="Logout">
          <span className="nav-icon">🚪</span>
          {!collapsed && <span className="nav-label">Logout</span>}
        </button>
      </div>
    </aside>
  );
}

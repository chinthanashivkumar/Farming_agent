import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth }   from '../context/AuthContext';
import { useFarmer } from '../context/FarmerContext';
import './TopBar.css';

const LANG_LABELS = { en: '🇬🇧 EN', hi: '🇮🇳 HI', kn: 'ಕ KN' };

export default function TopBar({ onMenuClick }) {
  const { user }                     = useAuth();
  const { language, changeLanguage, darkMode, toggleDark } = useFarmer();
  const navigate = useNavigate();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <button className="topbar-menu-btn" onClick={onMenuClick} title="Toggle menu">
          <span className="hamburger-icon">☰</span>
        </button>
        <button className="topbar-chat-btn btn btn-primary btn-sm" onClick={() => navigate('/chat')}>
          🤖 Ask AI
        </button>
      </div>

      <div className="topbar-right">
        {/* Language selector */}
        <select
          className="lang-select"
          value={language}
          onChange={e => changeLanguage(e.target.value)}
          title="Select language"
        >
          {Object.entries(LANG_LABELS).map(([code, label]) => (
            <option key={code} value={code}>{label}</option>
          ))}
        </select>

        {/* Dark mode toggle */}
        <button
          className="topbar-icon-btn"
          onClick={toggleDark}
          title={darkMode ? 'Light mode' : 'Dark mode'}
        >
          {darkMode ? '☀️' : '🌙'}
        </button>

        {/* Notifications */}
        <button className="topbar-icon-btn notif-btn" title="Notifications">
          🔔
          <span className="notif-dot" />
        </button>

        {/* User avatar */}
        <div className="topbar-avatar" title={user?.email}>
          {user?.name?.[0]?.toUpperCase() || 'F'}
        </div>
      </div>
    </header>
  );
}

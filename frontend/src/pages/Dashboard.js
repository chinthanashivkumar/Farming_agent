import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { marketService } from '../services/api';
import { useFarmer } from '../context/FarmerContext';
import './Dashboard.css';

const QUICK_ACTIONS = [
  { icon: '🤖', label: 'AI Chat',       to: '/chat',       color: '#dcfce7' },
  { icon: '🌾', label: 'Crop Advisor',  to: '/crops',      color: '#fef3c7' },
  { icon: '🪱', label: 'Soil Test',     to: '/soil',       color: '#fde8d8' },
  { icon: '🐛', label: 'Pest Check',    to: '/pests',      color: '#fce7f3' },
  { icon: '🧪', label: 'Fertilizer',    to: '/fertilizer', color: '#ede9fe' },
  { icon: '💧', label: 'Irrigation',    to: '/irrigation', color: '#e0f2fe' },
  { icon: '📊', label: 'Market Price',  to: '/market',     color: '#ecfdf5' },
];

const FARMING_TIPS = [
  'Test your soil every season to optimize fertilizer use and improve yield.',
  'Integrated Pest Management (IPM) reduces pesticide use by 30–50%.',
  'Drip irrigation saves up to 50% water compared to flood irrigation.',
  'Crop rotation improves soil health and reduces pest pressure naturally.',
  'Sow cover crops during fallow periods to prevent soil erosion.',
];

export default function Dashboard() {
  const { profile } = useFarmer();
  const [prices, setPrices] = useState([]);
  const [tipIdx, setTipIdx] = useState(0);

  // Cycle farming tips
  useEffect(() => {
    const id = setInterval(() => setTipIdx(i => (i + 1) % FARMING_TIPS.length), 6000);
    return () => clearInterval(id);
  }, []);

  // Fetch sample market prices
  useEffect(() => {
    marketService.prices('tomato').then(r => setPrices(r.data.prices?.slice(0, 3) || [])).catch(() => {});
  }, []);

  const season = (() => {
    const m = new Date().getMonth() + 1;
    if (m >= 6 && m <= 10) return 'Kharif';
    if (m >= 11 || m <= 3) return 'Rabi';
    return 'Summer';
  })();

  return (
    <div className="dashboard">
      {/* Header */}
      <div className="dash-header">
        <div>
          <h1 className="page-title">🏠 Dashboard</h1>
          <p className="page-subtitle">
            {profile?.district
              ? `${profile.district}, ${profile.state} · ${season} Season`
              : 'Welcome to Smart Farming Advisor'}
          </p>
        </div>
        <Link to="/chat" className="btn btn-primary">
          🤖 Ask AI Now
        </Link>
      </div>

      {/* Farming tip banner */}
      <div className="tip-banner">
        <span className="tip-icon">💡</span>
        <p className="tip-text">{FARMING_TIPS[tipIdx]}</p>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon amber">🌾</div>
          <div className="stat-info">
            <p className="stat-label">Active Season</p>
            <p className="stat-value">{season}</p>
            <p className="stat-change">{new Date().toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon brown">🏡</div>
          <div className="stat-info">
            <p className="stat-label">Farm Size</p>
            <p className="stat-value">{profile?.farm_size_acres ? `${profile.farm_size_acres} ac` : 'Set profile'}</p>
            <p className="stat-change">{profile?.soil_type || 'Unknown soil'}</p>
          </div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="section-title">Quick Actions</div>
      <div className="quick-actions-grid">
        {QUICK_ACTIONS.map(a => (
          <Link key={a.to} to={a.to} className="quick-action-card" style={{ '--card-color': a.color }}>
            <span className="qa-icon">{a.icon}</span>
            <span className="qa-label">{a.label}</span>
          </Link>
        ))}
      </div>

      {/* Bottom panels */}
      <div className="dash-bottom-grid">
        {/* Market prices */}
        <div className="card">
          <div className="card-title">
            <span className="icon">📊</span> Live Mandi Prices
            <Link to="/market" className="btn btn-ghost btn-sm" style={{ marginLeft:'auto' }}>View all →</Link>
          </div>
          {prices.length === 0 && <p className="empty-text">Loading market data…</p>}
          {prices.map((p, i) => (
            <div key={i} className="price-row">
              <div>
                <p className="price-commodity">{p.commodity}</p>
                <p className="price-market">{p.market}</p>
              </div>
              <div className="price-value">₹{p.modal_price?.toLocaleString()}<span>/qt</span></div>
            </div>
          ))}
        </div>

        {/* AI insight card */}
        <div className="card ai-insight-card">
          <div className="card-title"><span className="icon">🤖</span> AI Farming Insight</div>
          <div className="ai-insight-body">
            <p className="ai-insight-text">
              {season === 'Kharif'
                ? 'Kharif season: Soybean and Maize show strong price trends. Ensure adequate irrigation before sowing. Check soil moisture levels.'
                : season === 'Rabi'
                ? 'Rabi season underway: Wheat and Mustard are top choices. Monitor night temperatures for frost risk. Apply phosphorus fertilizer at sowing.'
                : 'Summer crops like Sunflower and Moong are profitable now. Drip irrigation is highly recommended to conserve water.'}
            </p>
            <Link to="/chat" className="btn btn-primary btn-sm" style={{ marginTop: '1rem' }}>
              Ask AI for detailed advice →
            </Link>
          </div>
        </div>

        {/* Crop calendar */}
        <div className="card">
          <div className="card-title"><span className="icon">🗓️</span> Crop Calendar</div>
          {[
            { crop: 'Rice (Paddy)', action: 'Transplanting', days: '+5 days', color: '#16a34a' },
            { crop: 'Maize',        action: 'Fertilizer due', days: 'Today',    color: '#d97706' },
            { crop: 'Tomato',       action: 'Harvest ready', days: '+2 days', color: '#dc2626' },
            { crop: 'Cotton',       action: 'Pest scouting', days: 'Today',    color: '#7c3aed' },
          ].map(item => (
            <div key={item.crop} className="calendar-row">
              <div className="calendar-dot" style={{ background: item.color }} />
              <div className="calendar-info">
                <p className="calendar-crop">{item.crop}</p>
                <p className="calendar-action">{item.action}</p>
              </div>
              <span className="calendar-days" style={{ color: item.days === 'Today' ? item.color : 'var(--color-text-muted)' }}>
                {item.days}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

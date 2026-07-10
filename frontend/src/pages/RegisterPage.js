import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './AuthPage.css';

const LANGS = [
  { value: 'en', label: 'English' },
  { value: 'hi', label: 'हिन्दी (Hindi)' },
  { value: 'kn', label: 'ಕನ್ನಡ (Kannada)' },
  { value: 'ta', label: 'தமிழ் (Tamil)' },
  { value: 'te', label: 'తెలుగు (Telugu)' },
];

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate     = useNavigate();
  const [form, setForm] = useState({
    name: '', email: '', phone: '', password: '', confirm: '', preferred_language: 'en',
  });
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.name || !form.email || !form.password) {
      toast.error('Name, email and password are required'); return;
    }
    if (form.password !== form.confirm) {
      toast.error('Passwords do not match'); return;
    }
    if (form.password.length < 6) {
      toast.error('Password must be at least 6 characters'); return;
    }
    setLoading(true);
    try {
      const { confirm, ...payload } = form;
      await register(payload);
      toast.success('Account created! Welcome to FarmAdvisor 🌾');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      <div className="auth-hero">
        <div className="auth-hero-icon">👨‍🌾</div>
        <h2 className="auth-hero-title">Join Thousands of Smart Farmers</h2>
        <p className="auth-hero-desc">
          Get personalized AI crop advice, live market prices, soil analysis, and more — completely free.
        </p>
        <div className="auth-features">
          {[
            ['🌐', 'Support in 5 Indian languages'],
            ['🎤', 'Voice input & audio responses'],
            ['📍', 'Location-aware recommendations'],
            ['💾', 'Save your chat & farm history'],
          ].map(([icon, text]) => (
            <div key={text} className="auth-feature-item">
              <span>{icon}</span><span>{text}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="auth-form-panel">
        <div className="auth-box">
          <div className="auth-logo"><span>🌿</span> FarmAdvisor</div>
          <h1>Create account</h1>
          <p className="sub">Start getting AI-powered farming guidance</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="input-row" style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem' }}>
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input name="name" placeholder="Ramesh Kumar" value={form.name} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Phone (optional)</label>
                <input name="phone" placeholder="+91 98765 43210" value={form.phone} onChange={handleChange} />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Email address</label>
              <input name="email" type="email" placeholder="you@example.com" value={form.email} onChange={handleChange} />
            </div>

            <div className="form-group">
              <label className="form-label">Preferred Language</label>
              <select name="preferred_language" value={form.preferred_language} onChange={handleChange}>
                {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
            </div>

            <div className="input-row" style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem' }}>
              <div className="form-group">
                <label className="form-label">Password</label>
                <div className="password-field">
                  <input name="password" type={showPwd ? 'text' : 'password'} placeholder="Min 6 chars"
                    value={form.password} onChange={handleChange} />
                  <button type="button" className="password-toggle" onClick={() => setShowPwd(p => !p)}>
                    {showPwd ? '🙈' : '👁️'}
                  </button>
                </div>
              </div>
              <div className="form-group">
                <label className="form-label">Confirm Password</label>
                <input name="confirm" type={showPwd ? 'text' : 'password'} placeholder="Repeat password"
                  value={form.confirm} onChange={handleChange} />
              </div>
            </div>

            <button type="submit" className="btn btn-primary submit-btn" disabled={loading}>
              {loading ? <><span className="spinner" /> Creating account…</> : 'Create Account →'}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to="/login">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './AuthPage.css';

export default function LoginPage() {
  const { login }   = useAuth();
  const navigate    = useNavigate();
  const [form, setForm]       = useState({ email: '', password: '' });
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.email || !form.password) { toast.error('Please fill in all fields'); return; }
    setLoading(true);
    try {
      await login(form.email, form.password);
      toast.success('Welcome back! 🌱');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed. Check your credentials.');
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-page">
      {/* Left hero */}
      <div className="auth-hero">
        <div className="auth-hero-icon">🌱</div>
        <h2 className="auth-hero-title">Smart Farming Advisor</h2>
        <p className="auth-hero-desc">
          AI-powered agricultural guidance for every small-scale farmer — in your language, at your fingertips.
        </p>
        <div className="auth-features">
          {[
            ['🤖', 'IBM Granite AI crop recommendations'],
            ['📊', 'Live mandi market prices'],
            ['🌾', 'Soil, pest & fertilizer advisory'],
            ['💧', 'Smart irrigation scheduling'],
          ].map(([icon, text]) => (
            <div key={text} className="auth-feature-item">
              <span>{icon}</span><span>{text}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Right form */}
      <div className="auth-form-panel">
        <div className="auth-box">
          <div className="auth-logo"><span>🌿</span> FarmAdvisor</div>
          <h1>Welcome back</h1>
          <p className="sub">Sign in to your farmer account</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="email">Email address</label>
              <input
                id="email" name="email" type="email"
                placeholder="you@example.com"
                value={form.email} onChange={handleChange} autoComplete="email"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <div className="password-field">
                <input
                  id="password" name="password"
                  type={showPwd ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={form.password} onChange={handleChange} autoComplete="current-password"
                />
                <button type="button" className="password-toggle" onClick={() => setShowPwd(p => !p)}>
                  {showPwd ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button type="submit" className="btn btn-primary submit-btn" disabled={loading}>
              {loading ? <><span className="spinner" /> Signing in…</> : 'Sign In →'}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account? <Link to="/register">Create account</Link>
          </p>
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { soilService } from '../services/api';
import toast from 'react-hot-toast';
import './PageCommon.css';

const SOIL_TYPES = [
  { value: '',              label: 'I don\'t know / Not sure' },
  { value: 'black cotton',  label: 'Black / Dark soil (sticks when wet)' },
  { value: 'red laterite',  label: 'Red / Reddish soil' },
  { value: 'alluvial',      label: 'Brown / River plain soil' },
  { value: 'sandy loam',    label: 'Sandy / Light soil (drains fast)' },
  { value: 'clay',          label: 'Heavy clay (waterlogged easily)' },
  { value: 'loamy',         label: 'Loamy / Mixed soil' },
];

const STATES = [
  '', 'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Gujarat', 'Haryana',
  'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
  'Maharashtra', 'Manipur', 'Meghalaya', 'Odisha', 'Punjab', 'Rajasthan',
  'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
];

// Simple level → kg/ha midpoint for API
const N_MAP   = { low: 200,  medium: 400,  high: 600 };
const P_MAP   = { low: 6,    medium: 17,   high: 30  };
const K_MAP   = { low: 80,   medium: 190,  high: 320 };
const OC_MAP  = { low: 0.3,  medium: 0.6,  high: 0.9 };

export default function SoilPage() {
  const [form, setForm] = useState({
    ph: '',
    nitrogen_level: '',
    phosphorus_level: '',
    potassium_level: '',
    organic_carbon_level: '',
    soil_type: '',
    state: '',
    has_soil_card: '',
  });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true); setResult(null);
    try {
      // Build numeric payload from simple levels
      const payload = {};
      if (form.soil_type)  payload.soil_type        = form.soil_type;
      if (form.state)       payload.state            = form.state;
      if (form.ph)          payload.ph               = +form.ph;
      if (form.nitrogen_level)         payload.nitrogen         = N_MAP[form.nitrogen_level];
      if (form.phosphorus_level)       payload.phosphorus       = P_MAP[form.phosphorus_level];
      if (form.potassium_level)        payload.potassium        = K_MAP[form.potassium_level];
      if (form.organic_carbon_level)   payload.organic_carbon   = OC_MAP[form.organic_carbon_level];

      const res = await soilService.analyze(payload);
      setResult(res.data);
    } catch { toast.error('Soil analysis failed. Please try again.'); }
    finally  { setLoading(false); }
  };

  const phStatus = (() => {
    if (!form.ph) return null;
    const n = +form.ph;
    if (n < 5.5) return { label: 'Acidic — needs lime', color: '#dc2626', bg: '#fef2f2' };
    if (n > 7.5) return { label: 'Alkaline — needs gypsum', color: '#d97706', bg: '#fffbeb' };
    return { label: 'Optimal ✅', color: '#16a34a', bg: '#f0fdf4' };
  })();

  const LevelPicker = ({ name, label, emoji, hint }) => (
    <div className="form-group">
      <label className="form-label">{emoji} {label}</label>
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        {['low', 'medium', 'high'].map(lvl => (
          <button
            key={lvl}
            type="button"
            onClick={() => setForm(f => ({ ...f, [name]: f[name] === lvl ? '' : lvl }))}
            style={{
              flex: 1, minWidth: 70, padding: '0.5rem 0.25rem',
              borderRadius: 8, border: '2px solid',
              cursor: 'pointer', fontWeight: 700, fontSize: '0.82rem',
              borderColor: form[name] === lvl
                ? (lvl === 'low' ? '#dc2626' : lvl === 'medium' ? '#d97706' : '#16a34a')
                : 'var(--color-border)',
              background: form[name] === lvl
                ? (lvl === 'low' ? '#fef2f2' : lvl === 'medium' ? '#fffbeb' : '#f0fdf4')
                : 'var(--color-surface)',
              color: form[name] === lvl
                ? (lvl === 'low' ? '#dc2626' : lvl === 'medium' ? '#d97706' : '#16a34a')
                : 'var(--color-text-muted)',
            }}
          >
            {lvl === 'low' ? '🔴 Low' : lvl === 'medium' ? '🟡 Medium' : '🟢 High'}
          </button>
        ))}
      </div>
      {hint && <p className="form-hint" style={{ marginTop: 4 }}>{hint}</p>}
    </div>
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">🪱 Soil Analysis</h1>
          <p className="page-subtitle">Answer a few simple questions — AI will recommend the best crops and fertilizers</p>
        </div>
      </div>

      {/* Soil Health Card tip */}
      <div className="alert alert-info" style={{ marginBottom: '1.25rem', display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
        <span style={{ fontSize: '1.4rem' }}>💡</span>
        <div>
          <strong>Don't know your soil values?</strong> Get a <strong>free Soil Health Card</strong> from your nearest
          KVK (Krishi Vigyan Kendra) or Agriculture Department office. It gives your exact NPK, pH values.
          Even without it, just pick what looks closest — AI will still give useful advice!
          <br /><span style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)' }}>📞 Kisan Call Centre: 1800-180-1551 (Free, 24×7)</span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
        {/* Form */}
        <div className="card">
          <div className="card-title">🌱 Tell us about your soil</div>
          <form onSubmit={handleSubmit}>

            {/* Soil Type */}
            <div className="form-group">
              <label className="form-label">🪨 What does your soil look like?</label>
              <select name="soil_type" value={form.soil_type} onChange={handleChange}>
                {SOIL_TYPES.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>

            {/* State */}
            <div className="form-group">
              <label className="form-label">📍 Your State</label>
              <select name="state" value={form.state} onChange={handleChange}>
                <option value="">Select your state…</option>
                {STATES.filter(Boolean).map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>

            {/* pH — simple slider */}
            <div className="form-group">
              <label className="form-label">
                ⚗️ Soil pH (acidity)
                {phStatus && (
                  <span style={{ marginLeft: 8, fontWeight: 700, color: phStatus.color }}>
                    — {phStatus.label}
                  </span>
                )}
              </label>
              <input
                name="ph" type="range" min="4" max="10" step="0.5"
                value={form.ph || 6.5} onChange={handleChange}
                style={{ width: '100%', accentColor: phStatus?.color || '#2d7a3a' }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--color-text-muted)', marginTop: 2 }}>
                <span>4 — Very Acidic</span>
                <span style={{ fontWeight: 700, color: phStatus?.color || 'var(--color-text)' }}>
                  pH {form.ph || 6.5}
                </span>
                <span>10 — Very Alkaline</span>
              </div>
              <p className="form-hint">If you don't know, leave at 6.5 (most common). Check Soil Health Card for exact value.</p>
            </div>

            {/* NPK — simple level buttons */}
            <LevelPicker name="nitrogen_level"       emoji="🌿" label="Nitrogen (N) level"       hint="Low = plants look pale/yellow. High = very dark green lush growth." />
            <LevelPicker name="phosphorus_level"     emoji="🔵" label="Phosphorus (P) level"     hint="Low = poor root growth, delayed flowering. Not sure? Pick Medium." />
            <LevelPicker name="potassium_level"      emoji="🟡" label="Potassium (K) level"      hint="Low = weak stems, brown leaf edges. Not sure? Pick Medium." />
            <LevelPicker name="organic_carbon_level" emoji="🤎" label="Organic matter / Compost"  hint="Low = never added FYM/compost. High = added regularly for years." />

            <button type="submit" className="btn btn-primary w-full" style={{ marginTop: '1rem' }} disabled={loading}>
              {loading ? <><span className="spinner" /> Analyzing your soil…</> : '🪱 Get My Soil Advice'}
            </button>
          </form>
        </div>

        {/* Right panel — guide + result */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

          {/* Quick guide */}
          <div className="card">
            <div className="card-title">📖 How to read your Soil Health Card</div>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {[
                { icon: '🌿', label: 'Nitrogen (N)', low: '< 280 kg/ha', med: '280–560', high: '> 560' },
                { icon: '🔵', label: 'Phosphorus (P)', low: '< 10 kg/ha', med: '10–25', high: '> 25' },
                { icon: '🟡', label: 'Potassium (K)', low: '< 110 kg/ha', med: '110–280', high: '> 280' },
                { icon: '🤎', label: 'Organic Carbon', low: '< 0.5%', med: '0.5–0.75%', high: '> 0.75%' },
                { icon: '⚗️', label: 'Soil pH', low: '< 5.5 Acidic', med: '6.0–7.0 ✅', high: '> 7.5 Alkaline' },
              ].map(r => (
                <div key={r.label} style={{ display: 'grid', gridTemplateColumns: '1.5rem 6rem 1fr 1fr 1fr', gap: '0.25rem 0.5rem', alignItems: 'center', borderBottom: '1px solid var(--color-border)', paddingBottom: '0.4rem' }}>
                  <span>{r.icon}</span>
                  <span style={{ fontWeight: 600, color: 'var(--color-text)' }}>{r.label}</span>
                  <span style={{ color: '#dc2626', fontSize: '0.78rem' }}>🔴 {r.low}</span>
                  <span style={{ color: '#d97706', fontSize: '0.78rem' }}>🟡 {r.med}</span>
                  <span style={{ color: '#16a34a', fontSize: '0.78rem' }}>🟢 {r.high}</span>
                </div>
              ))}
            </div>
          </div>

          {/* AI Result */}
          {result && (
            <div className="result-card">
              <h3>🤖 AI Soil Analysis & Advice</h3>
              <p className="result-text">{result.analysis}</p>
              {result.sources?.length > 0 && (
                <div className="sources-row">
                  {result.sources.map((s, i) => <span key={i} className="source-badge">📚 {s.source}</span>)}
                </div>
              )}
            </div>
          )}

          {/* No result yet — show prompt */}
          {!result && !loading && (
            <div className="card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-muted)' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>🌱</div>
              <p style={{ fontSize: '0.9rem' }}>Fill in the form on the left and tap<br /><strong>"Get My Soil Advice"</strong> to see AI recommendations.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

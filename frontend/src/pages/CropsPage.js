import React, { useState, useEffect } from 'react';
import { cropService } from '../services/api';
import { useFarmer } from '../context/FarmerContext';
import toast from 'react-hot-toast';
import './PageCommon.css';

export default function CropsPage() {
  const { profile } = useFarmer();
  const [seasons, setSeasons] = useState([]);
  const [form, setForm] = useState({
    season: 'kharif',
    soil_type: profile?.soil_type || '',
    state: profile?.state || '',
    rainfall_mm: '',
    temperature_c: '',
    water_availability: 'moderate',
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    cropService.seasons().then(r => setSeasons(r.data.seasons)).catch(() => {});
    if (profile) setForm(f => ({ ...f, soil_type: profile.soil_type || '', state: profile.state || '' }));
  }, [profile]);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const res = await cropService.recommend({
        ...form,
        rainfall_mm:   form.rainfall_mm   ? +form.rainfall_mm   : null,
        temperature_c: form.temperature_c ? +form.temperature_c : null,
      });
      setResult(res.data);
    } catch { toast.error('Could not get crop recommendation'); }
    finally  { setLoading(false); }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">🌾 Crop Recommendation</h1>
          <p className="page-subtitle">AI-powered crop selection based on season, soil, and climate</p>
        </div>
      </div>

      {/* Season quick-select */}
      <div style={{ display:'flex', gap:'0.75rem', marginBottom:'1.25rem', flexWrap:'wrap' }}>
        {seasons.map(s => (
          <button
            key={s.id}
            className={`btn${form.season === s.id ? ' btn-primary' : ' btn-secondary'}`}
            onClick={() => setForm(f => ({ ...f, season: s.id }))}
          >
            {s.id === 'kharif' ? '☔' : s.id === 'rabi' ? '❄️' : '☀️'} {s.name}
          </button>
        ))}
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.5rem' }}>
        {/* Form */}
        <div className="card">
          <div className="card-title">🌱 Farm Details</div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">State / Region</label>
              <input name="state" placeholder="e.g. Karnataka" value={form.state} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Soil Type</label>
              <select name="soil_type" value={form.soil_type} onChange={handleChange}>
                <option value="">Select soil type</option>
                {['Black Cotton', 'Red Laterite', 'Alluvial', 'Sandy Loam', 'Clay', 'Loamy'].map(s =>
                  <option key={s} value={s.toLowerCase()}>{s}</option>)}
              </select>
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem' }}>
              <div className="form-group">
                <label className="form-label">Expected Rainfall (mm)</label>
                <input name="rainfall_mm" type="number" placeholder="e.g. 800" value={form.rainfall_mm} onChange={handleChange} />
              </div>
              <div className="form-group">
                <label className="form-label">Avg Temperature (°C)</label>
                <input name="temperature_c" type="number" placeholder="e.g. 28" value={form.temperature_c} onChange={handleChange} />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Water Availability</label>
              <select name="water_availability" value={form.water_availability} onChange={handleChange}>
                <option value="good">Good (canal/borewell)</option>
                <option value="moderate">Moderate</option>
                <option value="scarce">Scarce (rainfed only)</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? <><span className="spinner" /> Getting recommendations…</> : '🌾 Get Crop Recommendation'}
            </button>
          </form>
        </div>

        {/* Seasonal crop guide */}
        <div className="card">
          <div className="card-title">📋 {seasons.find(s=>s.id===form.season)?.name || 'Season'} Crops</div>
          <div style={{ display:'flex', flexWrap:'wrap', gap:'0.5rem' }}>
            {(seasons.find(s=>s.id===form.season)?.crops || []).map(c => (
              <span key={c} className="badge badge-green" style={{ fontSize:'0.85rem', padding:'0.35em 0.9em' }}>🌱 {c}</span>
            ))}
          </div>
          {result && (
            <div className="result-card">
              <h3>🤖 AI Recommendation</h3>
              <p className="result-text">{result.recommendation}</p>
              {result.sources?.length > 0 && (
                <div className="sources-row">
                  {result.sources.map((s, i) => <span key={i} className="source-badge">📚 {s.source}</span>)}
                </div>
              )}
            </div>
          )}
          {loading && (
            <div style={{ display:'flex', alignItems:'center', gap:'0.5rem', marginTop:'1rem', color:'var(--color-text-secondary)' }}>
              <span className="spinner" /> Consulting IBM Granite AI…
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

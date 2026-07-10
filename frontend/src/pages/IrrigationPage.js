import React, { useState } from 'react';
import { irrigationService } from '../services/api';
import toast from 'react-hot-toast';
import './PageCommon.css';

export default function IrrigationPage() {
  const [form, setForm] = useState({
    crop:'', growth_stage:'vegetative', soil_type:'', irrigation_type:'drip',
    soil_moisture_percent:'', rainfall_expected:false, temperature_c:'',
  });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.crop) { toast.error('Enter a crop name'); return; }
    setLoading(true); setResult(null);
    try {
      const res = await irrigationService.schedule({
        ...form,
        soil_moisture_percent: form.soil_moisture_percent ? +form.soil_moisture_percent : null,
        temperature_c:         form.temperature_c ? +form.temperature_c : null,
      });
      setResult(res.data);
    } catch { toast.error('Irrigation schedule failed'); }
    finally  { setLoading(false); }
  };

  const IRRIG_TYPES = [
    { id:'drip',      icon:'💧', label:'Drip Irrigation' },
    { id:'sprinkler', icon:'🌀', label:'Sprinkler' },
    { id:'flood',     icon:'🌊', label:'Flood/Furrow' },
    { id:'rainfed',   icon:'🌧️', label:'Rainfed Only' },
  ];

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">💧 Irrigation Advisor</h1>
          <p className="page-subtitle">AI-generated irrigation schedules based on crop, soil type, and growth stage</p>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.5rem' }}>
        <div className="card">
          <div className="card-title">🚿 Irrigation Details</div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Crop</label>
              <input name="crop" placeholder="e.g. Paddy, Wheat, Tomato" value={form.crop} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Irrigation Method</label>
              <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.5rem' }}>
                {IRRIG_TYPES.map(t => (
                  <button key={t.id} type="button"
                    className={`btn btn-sm${form.irrigation_type === t.id ? ' btn-primary' : ' btn-secondary'}`}
                    onClick={() => setForm(f => ({ ...f, irrigation_type: t.id }))}
                    style={{ justifyContent:'flex-start' }}
                  >
                    {t.icon} {t.label}
                  </button>
                ))}
              </div>
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.75rem' }}>
              <div className="form-group" style={{marginBottom:0}}>
                <label className="form-label">Growth Stage</label>
                <select name="growth_stage" value={form.growth_stage} onChange={handleChange}>
                  {['sowing','vegetative','flowering','fruiting','maturity'].map(s =>
                    <option key={s} value={s}>{s.charAt(0).toUpperCase()+s.slice(1)}</option>)}
                </select>
              </div>
              <div className="form-group" style={{marginBottom:0}}>
                <label className="form-label">Soil Type</label>
                <select name="soil_type" value={form.soil_type} onChange={handleChange}>
                  <option value="">Select…</option>
                  {['Sandy','Loamy','Clay','Black Cotton','Alluvial'].map(s =>
                    <option key={s} value={s.toLowerCase()}>{s}</option>)}
                </select>
              </div>
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'0.75rem', marginTop:'0.75rem' }}>
              <div className="form-group" style={{marginBottom:0}}>
                <label className="form-label">Soil Moisture (%)</label>
                <input name="soil_moisture_percent" type="number" min="0" max="100" placeholder="e.g. 35" value={form.soil_moisture_percent} onChange={handleChange} />
              </div>
              <div className="form-group" style={{marginBottom:0}}>
                <label className="form-label">Temperature (°C)</label>
                <input name="temperature_c" type="number" placeholder="e.g. 32" value={form.temperature_c} onChange={handleChange} />
              </div>
            </div>
            <div style={{ display:'flex', alignItems:'center', gap:'0.5rem', marginTop:'0.85rem' }}>
              <input type="checkbox" id="rain" name="rainfall_expected" checked={form.rainfall_expected} onChange={handleChange} style={{ width:'auto' }} />
              <label htmlFor="rain" style={{ fontSize:'0.88rem', color:'var(--color-text-secondary)', cursor:'pointer' }}>
                🌧️ Rainfall expected in next 2 days
              </label>
            </div>
            <button type="submit" className="btn btn-primary w-full" style={{marginTop:'1.1rem'}} disabled={loading}>
              {loading ? <><span className="spinner" /> Calculating…</> : '💧 Get Irrigation Schedule'}
            </button>
          </form>
        </div>

        <div className="card">
          <div className="card-title">💡 Water Saving Tips</div>
          {[
            ['💧','Drip irrigation saves 40–60% water vs. flood irrigation.'],
            ['🌅','Irrigate in early morning or evening to reduce evaporation.'],
            ['🌡️','Sandy soils need more frequent irrigation than clay soils.'],
            ['🌧️','Skip irrigation if 10+ mm rain is forecast within 24 hours.'],
            ['📊','Use tensiometers to measure actual soil moisture levels.'],
          ].map(([icon,tip]) => (
            <div key={tip} style={{ display:'flex', gap:'0.6rem', padding:'0.6rem 0', borderBottom:'1px solid var(--color-border)', fontSize:'0.87rem', color:'var(--color-text-secondary)', lineHeight:1.5 }}>
              <span style={{flexShrink:0}}>{icon}</span><span>{tip}</span>
            </div>
          ))}
          {result && (
            <div className="result-card">
              <h3>🤖 AI Irrigation Schedule</h3>
              <p className="result-text">{result.schedule}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

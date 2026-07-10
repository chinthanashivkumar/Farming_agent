import React, { useState } from 'react';
import { fertilizerService } from '../services/api';
import toast from 'react-hot-toast';
import './PageCommon.css';

const GROWTH_STAGES = ['sowing','vegetative','flowering','fruiting','maturity'];
const COMMON_CROPS  = ['Rice','Wheat','Maize','Cotton','Sugarcane','Tomato','Onion','Potato','Soybean','Mustard'];

export default function FertilizerPage() {
  const [form, setForm] = useState({ crop:'', growth_stage:'vegetative', nitrogen:'', phosphorus:'', potassium:'', soil_type:'', area_acres:'1' });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.crop) { toast.error('Select a crop'); return; }
    setLoading(true); setResult(null);
    try {
      const res = await fertilizerService.recommend({
        ...form,
        nitrogen:   form.nitrogen   ? +form.nitrogen   : null,
        phosphorus: form.phosphorus ? +form.phosphorus : null,
        potassium:  form.potassium  ? +form.potassium  : null,
        area_acres: +form.area_acres,
      });
      setResult(res.data);
    } catch { toast.error('Fertilizer recommendation failed'); }
    finally  { setLoading(false); }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">🧪 Fertilizer Advisor</h1>
          <p className="page-subtitle">Get precise fertilizer recommendations based on crop, soil, and growth stage</p>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.5rem' }}>
        <div className="card">
          <div className="card-title">🌱 Crop Details</div>

          {/* Quick crop select */}
          <div style={{ display:'flex', flexWrap:'wrap', gap:'0.4rem', marginBottom:'1rem' }}>
            {COMMON_CROPS.map(c => (
              <button key={c} className={`btn btn-sm${form.crop === c ? ' btn-primary' : ' btn-secondary'}`}
                onClick={() => setForm(f => ({ ...f, crop: c }))}>
                {c}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Crop Name</label>
              <input name="crop" placeholder="Or type crop name" value={form.crop} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Growth Stage</label>
              <div style={{ display:'flex', gap:'0.4rem', flexWrap:'wrap' }}>
                {GROWTH_STAGES.map(s => (
                  <button key={s} type="button"
                    className={`btn btn-sm${form.growth_stage === s ? ' btn-primary' : ' btn-secondary'}`}
                    onClick={() => setForm(f => ({ ...f, growth_stage: s }))}>
                    {s.charAt(0).toUpperCase()+s.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Farm Area (acres)</label>
              <input name="area_acres" type="number" step="0.1" value={form.area_acres} onChange={handleChange} />
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr 1fr', gap:'0.75rem' }}>
              {[['nitrogen','N (kg/ha)'],['phosphorus','P (kg/ha)'],['potassium','K (kg/ha)']].map(([n,l]) => (
                <div key={n} className="form-group" style={{marginBottom:0}}>
                  <label className="form-label">{l}</label>
                  <input name={n} type="number" placeholder="optional" value={form[n]} onChange={handleChange} />
                </div>
              ))}
            </div>
            <button type="submit" className="btn btn-primary w-full" style={{marginTop:'1.1rem'}} disabled={loading}>
              {loading ? <><span className="spinner" /> Analyzing…</> : '🧪 Get Fertilizer Plan'}
            </button>
          </form>
        </div>

        <div className="card">
          <div className="card-title">📋 Fertilizer Quick Reference</div>
          <table style={{ width:'100%', fontSize:'0.82rem', borderCollapse:'collapse' }}>
            <thead>
              <tr style={{ borderBottom:'2px solid var(--color-border)' }}>
                <th style={{ textAlign:'left', padding:'0.5rem', color:'var(--color-text-muted)' }}>Fertilizer</th>
                <th style={{ textAlign:'left', padding:'0.5rem', color:'var(--color-text-muted)' }}>NPK %</th>
                <th style={{ textAlign:'left', padding:'0.5rem', color:'var(--color-text-muted)' }}>Best For</th>
              </tr>
            </thead>
            <tbody>
              {[['Urea','46-0-0','N boost, top dressing'],['DAP','18-46-0','Sowing, root dev.'],['MOP','0-0-60','Fruiting, K deficiency'],['NPK 17:17:17','17-17-17','Balanced, all stages'],['SSP','0-16-0','P deficient soils']].map(([n,...v]) => (
                <tr key={n} style={{ borderBottom:'1px solid var(--color-border)' }}>
                  <td style={{ padding:'0.45rem', fontWeight:600 }}>{n}</td>
                  {v.map(val => <td key={val} style={{ padding:'0.45rem', color:'var(--color-text-secondary)' }}>{val}</td>)}
                </tr>
              ))}
            </tbody>
          </table>
          {result && (
            <div className="result-card">
              <h3>🤖 AI Fertilizer Plan</h3>
              <p className="result-text">{result.recommendation}</p>
              {result.sources?.length > 0 && (
                <div className="sources-row">
                  {result.sources.map((s, i) => <span key={i} className="source-badge">📚 {s.source}</span>)}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

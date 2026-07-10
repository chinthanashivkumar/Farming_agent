import React, { useState, useRef } from 'react';
import { pestService } from '../services/api';
import toast from 'react-hot-toast';
import './PageCommon.css';

const COMMON_PESTS = [
  { name:'Aphids',        symptoms:'Curled yellow leaves, sticky residue on plant', crop:'Multiple' },
  { name:'Leaf Spot',     symptoms:'Brown/black circular spots on leaves',          crop:'Tomato, Potato' },
  { name:'Downy Mildew',  symptoms:'Yellow patches on upper leaf, grey fungus below',crop:'Grape, Onion' },
  { name:'Bollworm',      symptoms:'Holes in cotton bolls, frass visible',           crop:'Cotton' },
  { name:'Stem Borer',    symptoms:'Dead heart in young plants, hollow stems',       crop:'Rice, Maize' },
  { name:'White Fly',     symptoms:'Yellowing leaves, white insects on underside',   crop:'Tomato, Chilli' },
];

export default function PestPage() {
  const [form, setForm] = useState({ symptoms:'', crop:'', location:'' });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const fileRef = useRef(null);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleImage = e => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = ev => setImagePreview(ev.target.result);
    reader.readAsDataURL(file);
  };

  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.symptoms && !imageFile) { toast.error('Describe symptoms or upload an image'); return; }
    setLoading(true); setResult(null);
    try {
      let res;
      if (imageFile) {
        const fd = new FormData();
        fd.append('crop', form.crop || 'unknown');
        fd.append('symptoms', form.symptoms);
        fd.append('image', imageFile);
        res = await pestService.diagnoseImage(fd);
        setResult({ diagnosis: res.data.diagnosis, sources: [] });
      } else {
        res = await pestService.diagnose(form);
        setResult(res.data);
      }
    } catch { toast.error('Pest diagnosis failed'); }
    finally  { setLoading(false); }
  };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">🐛 Pest & Disease Diagnosis</h1>
          <p className="page-subtitle">Describe symptoms or upload a crop photo for AI diagnosis</p>
        </div>
      </div>

      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1.5rem' }}>
        {/* Form */}
        <div className="card">
          <div className="card-title">🔍 Describe the Problem</div>
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Crop Name</label>
              <input name="crop" placeholder="e.g. Tomato, Cotton, Rice" value={form.crop} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Symptoms</label>
              <textarea name="symptoms" rows={4} placeholder="Describe what you see: leaf color, spots, wilting, insects…" value={form.symptoms} onChange={handleChange}
                style={{ resize:'vertical' }} />
            </div>

            {/* Image upload */}
            <div className="form-group">
              <label className="form-label">📸 Upload Crop Photo (optional)</label>
              <div
                style={{ border:'2px dashed var(--color-border)', borderRadius:'var(--radius-sm)', padding:'1rem', textAlign:'center', cursor:'pointer', background:'var(--color-surface-2)' }}
                onClick={() => fileRef.current?.click()}
              >
                {imagePreview
                  ? <img src={imagePreview} alt="crop" style={{ maxHeight:120, borderRadius:'var(--radius-sm)', margin:'0 auto' }} />
                  : <p style={{ color:'var(--color-text-muted)', fontSize:'0.88rem' }}>📷 Click to upload or drag & drop</p>
                }
              </div>
              <input ref={fileRef} type="file" accept="image/*" style={{ display:'none' }} onChange={handleImage} />
            </div>

            <button type="submit" className="btn btn-primary w-full" disabled={loading}>
              {loading ? <><span className="spinner" /> Diagnosing…</> : '🔬 Diagnose Pest / Disease'}
            </button>
          </form>
        </div>

        {/* Common pests reference */}
        <div className="card">
          <div className="card-title">📚 Common Pests Reference</div>
          <div style={{ display:'flex', flexDirection:'column', gap:'0.6rem' }}>
            {COMMON_PESTS.map(p => (
              <div key={p.name}
                style={{ padding:'0.65rem 0.8rem', borderRadius:'var(--radius-sm)', background:'var(--color-surface-2)', border:'1px solid var(--color-border)', cursor:'pointer' }}
                onClick={() => setForm(f => ({ ...f, symptoms: p.symptoms, crop: p.crop.split(',')[0].trim() }))}
              >
                <p style={{ fontWeight:700, fontSize:'0.88rem', color:'var(--color-text)' }}>🐛 {p.name}</p>
                <p style={{ fontSize:'0.78rem', color:'var(--color-text-secondary)', marginTop:2 }}>{p.symptoms}</p>
                <p style={{ fontSize:'0.72rem', color:'var(--color-text-muted)', marginTop:2 }}>Affects: {p.crop}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Result */}
      {result && (
        <div className="result-card">
          <h3>🤖 AI Diagnosis</h3>
          <p className="result-text">{result.diagnosis}</p>
          {result.sources?.length > 0 && (
            <div className="sources-row">
              {result.sources.map((s, i) => <span key={i} className="source-badge">📚 {s.source}</span>)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

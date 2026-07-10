import React, { useState } from 'react';
import { useFarmer } from '../context/FarmerContext';
import { useAuth }   from '../context/AuthContext';
import toast from 'react-hot-toast';
import './PageCommon.css';

const LANGUAGES = [
  { code:'en', label:'English',            flag:'🇬🇧' },
  { code:'hi', label:'हिन्दी (Hindi)',     flag:'🇮🇳' },
  { code:'kn', label:'ಕನ್ನಡ (Kannada)',   flag:'🇮🇳' },
  { code:'ta', label:'தமிழ் (Tamil)',      flag:'🇮🇳' },
  { code:'te', label:'తెలుగు (Telugu)',    flag:'🇮🇳' },
];

export default function SettingsPage() {
  const { language, changeLanguage, darkMode, toggleDark } = useFarmer();
  const { user } = useAuth();
  const [saved, setSaved] = useState(false);

  const handleSave = () => { setSaved(true); toast.success('Settings saved!'); setTimeout(() => setSaved(false), 2000); };

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">⚙️ Settings</h1>
          <p className="page-subtitle">Customize your FarmAdvisor experience</p>
        </div>
        <button className="btn btn-primary" onClick={handleSave}>{saved ? '✅ Saved' : '💾 Save Settings'}</button>
      </div>

      {/* Language */}
      <div className="card" style={{marginBottom:'1.25rem'}}>
        <div className="card-title">🌐 Language Preference</div>
        <div style={{ display:'flex', gap:'0.6rem', flexWrap:'wrap' }}>
          {LANGUAGES.map(l => (
            <button key={l.code}
              className={`btn${language === l.code ? ' btn-primary' : ' btn-secondary'}`}
              onClick={() => changeLanguage(l.code)}
            >
              {l.flag} {l.label}
            </button>
          ))}
        </div>
        <p className="form-hint" style={{marginTop:'0.75rem'}}>
          AI responses will be generated in your selected language using automatic translation.
        </p>
      </div>

      {/* Appearance */}
      <div className="card" style={{marginBottom:'1.25rem'}}>
        <div className="card-title">🎨 Appearance</div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'0.5rem 0' }}>
          <div>
            <p style={{ fontWeight:600, fontSize:'0.9rem' }}>{darkMode ? '🌙 Dark Mode' : '☀️ Light Mode'}</p>
            <p className="form-hint" style={{marginTop:2}}>Switch between light and dark themes</p>
          </div>
          <div
            onClick={toggleDark}
            style={{
              width:52, height:28, borderRadius:14,
              background: darkMode ? 'var(--color-primary)' : 'var(--color-border)',
              cursor:'pointer', position:'relative', transition:'background .2s',
            }}
          >
            <div style={{
              position:'absolute', top:3, left: darkMode ? 26 : 3,
              width:22, height:22, borderRadius:'50%', background:'#fff',
              transition:'left .2s', boxShadow:'0 1px 3px rgba(0,0,0,.2)',
            }} />
          </div>
        </div>
      </div>

      {/* Notifications */}
      <div className="card" style={{marginBottom:'1.25rem'}}>
        <div className="card-title">🔔 Notifications</div>
        {[
          { label:'Pest Alerts',     hint:'Receive alerts about pest outbreaks in your region' },
          { label:'Market Updates',  hint:'Daily price updates for your crops' },
          { label:'AI Suggestions',  hint:'Periodic AI-powered farming tips' },
        ].map(n => (
          <div key={n.label} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'0.6rem 0', borderBottom:'1px solid var(--color-border)' }}>
            <div>
              <p style={{ fontSize:'0.9rem', fontWeight:600 }}>{n.label}</p>
              <p className="form-hint" style={{marginTop:2}}>{n.hint}</p>
            </div>
            <span className="badge badge-green">On</span>
          </div>
        ))}
      </div>

      {/* API Status */}
      <div className="card">
        <div className="card-title">🔌 API & Integration Status</div>
        {[
          { service:'IBM WatsonX (Granite AI)', status:'Configure in backend/.env', color:'amber' },
          { service:'AgMarkNet (Market Data)',  status:'Configure AGMARKNET_API_KEY', color:'amber' },
          { service:'ChromaDB Vector Store',    status:'Auto-initialized on startup', color:'green' },
          { service:'PostgreSQL Database',      status:'Configure DATABASE_URL', color:'amber' },
        ].map(s => (
          <div key={s.service} style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'0.55rem 0', borderBottom:'1px solid var(--color-border)' }}>
            <span style={{ fontSize:'0.88rem', color:'var(--color-text)' }}>🔗 {s.service}</span>
            <span className={`badge badge-${s.color}`}>{s.status}</span>
          </div>
        ))}
        <div className="alert alert-info" style={{marginTop:'1rem', fontSize:'0.83rem'}}>
          📝 Add your API keys to <strong>backend/.env</strong> and restart the server to activate integrations.
        </div>
      </div>
    </div>
  );
}

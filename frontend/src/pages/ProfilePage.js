import React, { useState, useEffect } from 'react';
import { useFarmer } from '../context/FarmerContext';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import './PageCommon.css';

const SOIL_TYPES = ['black cotton','red laterite','alluvial','sandy loam','clay','loamy','silty'];
const IRRIG_TYPES = ['drip','flood','sprinkler','rainfed'];
const WATER_SOURCES = ['borewell','canal','river','rainwater','pond'];

export default function ProfilePage() {
  const { user } = useAuth();
  const { profile, updateProfile } = useFarmer();
  const [form, setForm] = useState({
    state:'', district:'', village:'', pincode:'',
    latitude:'', longitude:'',
    farm_size_acres:'', soil_type:'', irrigation_type:'', water_source:'',
    primary_crops:'', soil_ph:'', soil_nitrogen:'', soil_phosphorus:'',
    soil_potassium:'', soil_organic_carbon:'',
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!profile) return;
    setForm({
      state:               profile.state || '',
      district:            profile.district || '',
      village:             profile.village || '',
      pincode:             profile.pincode || '',
      latitude:            profile.latitude || '',
      longitude:           profile.longitude || '',
      farm_size_acres:     profile.farm_size_acres || '',
      soil_type:           profile.soil_type || '',
      irrigation_type:     profile.irrigation_type || '',
      water_source:        profile.water_source || '',
      primary_crops:       (profile.primary_crops || []).join(', '),
      soil_ph:             profile.soil_ph || '',
      soil_nitrogen:       profile.soil_nitrogen || '',
      soil_phosphorus:     profile.soil_phosphorus || '',
      soil_potassium:      profile.soil_potassium || '',
      soil_organic_carbon: profile.soil_organic_carbon || '',
    });
  }, [profile]);

  const handleChange = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const handleSave = async e => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {};
      Object.entries(form).forEach(([k, v]) => {
        if (v === '' || v === null) return;
        if (k === 'primary_crops') { payload[k] = v.split(',').map(x => x.trim()).filter(Boolean); return; }
        payload[k] = isNaN(v) || v === '' ? v : +v;
      });
      await updateProfile(payload);
      toast.success('Profile saved! ✅');
    } catch { toast.error('Failed to save profile'); }
    finally  { setSaving(false); }
  };

  const getGPS = () => {
    if (!navigator.geolocation) { toast.error('Geolocation not supported'); return; }
    navigator.geolocation.getCurrentPosition(
      pos => {
        setForm(f => ({ ...f, latitude: pos.coords.latitude.toFixed(6), longitude: pos.coords.longitude.toFixed(6) }));
        toast.success('📍 Location detected!');
      },
      () => toast.error('Location access denied')
    );
  };

  const InputField = ({ name, label, ...props }) => (
    <div className="form-group" style={{marginBottom:0}}>
      <label className="form-label">{label}</label>
      <input name={name} value={form[name]} onChange={handleChange} {...props} />
    </div>
  );

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">👨‍🌾 Farmer Profile</h1>
          <p className="page-subtitle">Personalize your recommendations by filling in your farm details</p>
        </div>
        <button type="button" className="btn btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? <><span className="spinner" /> Saving…</> : '💾 Save Profile'}
        </button>
      </div>

      <form onSubmit={handleSave}>
        {/* Account info */}
        <div className="card" style={{marginBottom:'1.25rem'}}>
          <div className="card-title">👤 Account Information</div>
          <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:'1rem' }}>
            <div className="form-group" style={{marginBottom:0}}>
              <label className="form-label">Full Name</label>
              <input value={user?.name || ''} disabled style={{opacity:.7}} />
            </div>
            <div className="form-group" style={{marginBottom:0}}>
              <label className="form-label">Email</label>
              <input value={user?.email || ''} disabled style={{opacity:.7}} />
            </div>
          </div>
        </div>

        {/* Location */}
        <div className="card" style={{marginBottom:'1.25rem'}}>
          <div className="card-title" style={{justifyContent:'space-between'}}>
            📍 Location
            <button type="button" className="btn btn-secondary btn-sm" onClick={getGPS}>📍 Auto-detect GPS</button>
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'1rem' }}>
            <InputField name="state"    label="State"    placeholder="Karnataka" />
            <InputField name="district" label="District" placeholder="Bangalore Rural" />
            <InputField name="village"  label="Village"  placeholder="Doddaballapur" />
            <InputField name="pincode"  label="Pincode"  placeholder="562101" />
            <InputField name="latitude" label="Latitude" type="number" step="any" placeholder="12.9716" />
            <InputField name="longitude" label="Longitude" type="number" step="any" placeholder="77.5946" />
          </div>
        </div>

        {/* Farm details */}
        <div className="card" style={{marginBottom:'1.25rem'}}>
          <div className="card-title">🏡 Farm Details</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:'1rem' }}>
            <InputField name="farm_size_acres" label="Farm Size (acres)" type="number" step="0.1" placeholder="5" />
            <div className="form-group" style={{marginBottom:0}}>
              <label className="form-label">Soil Type</label>
              <select name="soil_type" value={form.soil_type} onChange={handleChange}>
                <option value="">Select…</option>
                {SOIL_TYPES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase()+s.slice(1)}</option>)}
              </select>
            </div>
            <div className="form-group" style={{marginBottom:0}}>
              <label className="form-label">Irrigation Type</label>
              <select name="irrigation_type" value={form.irrigation_type} onChange={handleChange}>
                <option value="">Select…</option>
                {IRRIG_TYPES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase()+s.slice(1)}</option>)}
              </select>
            </div>
            <div className="form-group" style={{marginBottom:0}}>
              <label className="form-label">Water Source</label>
              <select name="water_source" value={form.water_source} onChange={handleChange}>
                <option value="">Select…</option>
                {WATER_SOURCES.map(s => <option key={s} value={s}>{s.charAt(0).toUpperCase()+s.slice(1)}</option>)}
              </select>
            </div>
            <div className="form-group" style={{marginBottom:0, gridColumn:'1/-1'}}>
              <label className="form-label">Primary Crops (comma-separated)</label>
              <input name="primary_crops" placeholder="e.g. Rice, Wheat, Tomato" value={form.primary_crops} onChange={handleChange} />
            </div>
          </div>
        </div>

        {/* Soil health */}
        <div className="card">
          <div className="card-title">🧪 Soil Health (Last Test)</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:'1rem' }}>
            <InputField name="soil_ph"             label="pH"               type="number" step="0.1" placeholder="6.5" />
            <InputField name="soil_nitrogen"        label="Nitrogen (kg/ha)" type="number" step="0.1" placeholder="250" />
            <InputField name="soil_phosphorus"      label="Phosphorus (kg/ha)" type="number" step="0.1" placeholder="20" />
            <InputField name="soil_potassium"       label="Potassium (kg/ha)" type="number" step="0.1" placeholder="150" />
            <InputField name="soil_organic_carbon"  label="Organic Carbon (%)" type="number" step="0.01" placeholder="0.6" />
          </div>
        </div>
      </form>
    </div>
  );
}

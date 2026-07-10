import React, { useState, useEffect } from 'react';
import { marketService } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import toast from 'react-hot-toast';
import './PageCommon.css';

export default function MarketPage() {
  const [commodities, setCommodities] = useState([]);
  const [selected, setSelected]       = useState('tomato');
  const [state, setState]             = useState('');
  const [prices, setPrices]           = useState([]);
  const [loading, setLoading]         = useState(false);

  useEffect(() => {
    marketService.commodities()
      .then(r => setCommodities(r.data.commodities))
      .catch(() => {});
    fetchPrices('tomato');
  }, []);

  const fetchPrices = async (commodity, st = '') => {
    setLoading(true);
    try {
      const res = await marketService.prices(commodity, st || undefined);
      setPrices(res.data.prices || []);
    } catch { toast.error('Market data unavailable'); }
    finally  { setLoading(false); }
  };

  const handleSearch = e => {
    e.preventDefault();
    fetchPrices(selected, state);
  };

  const chartData = prices.slice(0, 8).map(p => ({
    market: p.market.length > 10 ? p.market.slice(0, 10) + '…' : p.market,
    price:  p.modal_price,
  }));

  const avgPrice = prices.length
    ? Math.round(prices.reduce((s, p) => s + p.modal_price, 0) / prices.length)
    : null;
  const maxPrice = prices.length ? Math.max(...prices.map(p => p.modal_price)) : null;
  const minPrice = prices.length ? Math.min(...prices.map(p => p.modal_price)) : null;

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1 className="page-title">📊 Market Prices</h1>
          <p className="page-subtitle">Live mandi prices from AgMarkNet — plan your selling strategy</p>
        </div>
      </div>

      {/* Search bar */}
      <div className="card" style={{ marginBottom:'1.25rem' }}>
        <form onSubmit={handleSearch} style={{ display:'flex', gap:'0.75rem', flexWrap:'wrap', alignItems:'flex-end' }}>
          <div className="form-group" style={{ flex:1, minWidth:160, marginBottom:0 }}>
            <label className="form-label">Commodity</label>
            <select value={selected} onChange={e => setSelected(e.target.value)}>
              {commodities.map(c => <option key={c} value={c.toLowerCase()}>{c}</option>)}
            </select>
          </div>
          <div className="form-group" style={{ flex:1, minWidth:140, marginBottom:0 }}>
            <label className="form-label">State (optional)</label>
            <input placeholder="e.g. Karnataka" value={state} onChange={e => setState(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <><span className="spinner" /> Loading…</> : '📊 Get Prices'}
          </button>
        </form>
      </div>

      {/* Quick commodity buttons */}
      <div style={{ display:'flex', gap:'0.5rem', flexWrap:'wrap', marginBottom:'1.25rem' }}>
        {['Tomato','Onion','Potato','Rice','Wheat','Cotton'].map(c => (
          <button key={c}
            className={`btn btn-sm${selected === c.toLowerCase() ? ' btn-primary' : ' btn-secondary'}`}
            onClick={() => { setSelected(c.toLowerCase()); fetchPrices(c.toLowerCase(), state); }}>
            {c}
          </button>
        ))}
      </div>

      {prices.length > 0 && (
        <>
          {/* Stats */}
          <div className="stats-grid" style={{ marginBottom:'1.25rem' }}>
            <div className="stat-card"><div className="stat-icon green">📊</div><div className="stat-info"><p className="stat-label">Average Price</p><p className="stat-value">₹{avgPrice?.toLocaleString()}</p><p className="stat-change">per quintal</p></div></div>
            <div className="stat-card"><div className="stat-icon amber">📈</div><div className="stat-info"><p className="stat-label">Highest Price</p><p className="stat-value">₹{maxPrice?.toLocaleString()}</p></div></div>
            <div className="stat-card"><div className="stat-icon blue">📉</div><div className="stat-info"><p className="stat-label">Lowest Price</p><p className="stat-value">₹{minPrice?.toLocaleString()}</p></div></div>
            <div className="stat-card"><div className="stat-icon brown">🏪</div><div className="stat-info"><p className="stat-label">Markets Found</p><p className="stat-value">{prices.length}</p></div></div>
          </div>

          {/* Chart */}
          {chartData.length > 1 && (
            <div className="card" style={{ marginBottom:'1.25rem' }}>
              <div className="card-title">📊 Price Comparison by Market</div>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={chartData} margin={{ bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="market" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 10 }} tickFormatter={v => `₹${(v/1000).toFixed(1)}k`} />
                  <Tooltip formatter={v => [`₹${v.toLocaleString()} /qt`]} />
                  <Bar dataKey="price" fill="#2d7a3a" radius={[4,4,0,0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Table */}
          <div className="card">
            <div className="card-title">🏪 Mandi-wise Prices — {selected.charAt(0).toUpperCase()+selected.slice(1)}</div>
            <div style={{ overflowX:'auto' }}>
              <table className="market-table">
                <thead>
                  <tr>
                    <th>Market</th><th>State</th><th>Variety</th><th>Min (₹/qt)</th><th>Max (₹/qt)</th><th>Modal (₹/qt)</th><th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {prices.map((p, i) => (
                    <tr key={i}>
                      <td style={{ fontWeight:600 }}>{p.market}</td>
                      <td>{p.state}</td>
                      <td>{p.variety || 'Common'}</td>
                      <td>{p.min_price?.toLocaleString()}</td>
                      <td>{p.max_price?.toLocaleString()}</td>
                      <td style={{ fontWeight:700, color:'var(--color-primary)' }}>₹{p.modal_price?.toLocaleString()}</td>
                      <td style={{ color:'var(--color-text-muted)', fontSize:'0.8rem' }}>{p.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

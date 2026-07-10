/**
 * Axios API client — all calls go through here.
 * The base URL is read from REACT_APP_API_BASE_URL (set in frontend/.env).
 * The JWT token is injected from localStorage via a request interceptor.
 * On 401 the user is automatically logged out.
 */
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Request interceptor: attach Bearer token ───────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('sfa_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (err) => Promise.reject(err)
);

// ── Response interceptor: handle 401 ──────────────────────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('sfa_token');
      localStorage.removeItem('sfa_user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

// ── Named service helpers ──────────────────────────────────────────────────

export const authService = {
  login:    (email, password) =>
    api.post('/auth/login', new URLSearchParams({ username: email, password }),
      { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }),
  register: (data) => api.post('/auth/register', data),
};

export const chatService = {
  send:        (payload)    => api.post('/chat/', payload),
  getSessions: ()           => api.get('/chat/sessions'),
  getMessages: (sessionId)  => api.get(`/chat/sessions/${sessionId}/messages`),
};

export const cropService = {
  recommend: (data)  => api.post('/crops/recommend', data),
  seasons:   ()      => api.get('/crops/seasons'),
};

export const soilService = {
  analyze: (data) => api.post('/soil/analyze', data),
};

export const pestService = {
  diagnose:      (data) => api.post('/pests/diagnose', data),
  diagnoseImage: (form) => api.post('/pests/diagnose-image', form,
    { headers: { 'Content-Type': 'multipart/form-data' } }),
};

export const fertilizerService = {
  recommend: (data) => api.post('/fertilizer/recommend', data),
};

export const irrigationService = {
  schedule: (data) => api.post('/irrigation/schedule', data),
};

export const marketService = {
  prices:      (commodity, state) => api.get(`/market/prices?commodity=${commodity}${state ? `&state=${state}` : ''}`),
  commodities: ()                 => api.get('/market/commodities'),
};

export const profileService = {
  get:    ()     => api.get('/profile/'),
  update: (data) => api.put('/profile/', data),
};

export const speechService = {
  tts: (text, language) => api.post('/speech/tts', { text, language }),
  stt: (form)           => api.post('/speech/stt', form,
    { headers: { 'Content-Type': 'multipart/form-data' } }),
};

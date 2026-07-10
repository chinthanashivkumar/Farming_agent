import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [loading, setLoading] = useState(true);

  // Re-hydrate from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('sfa_user');
    if (stored) setUser(JSON.parse(stored));
    setLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await authService.login(email, password);
    const userData = {
      id:    res.data.user_id,
      name:  res.data.name,
      email: res.data.email,
    };
    localStorage.setItem('sfa_token', res.data.access_token);
    localStorage.setItem('sfa_user',  JSON.stringify(userData));
    setUser(userData);
    return userData;
  }, []);

  const register = useCallback(async (payload) => {
    const res = await authService.register(payload);
    const userData = {
      id:    res.data.user_id,
      name:  res.data.name,
      email: res.data.email,
    };
    localStorage.setItem('sfa_token', res.data.access_token);
    localStorage.setItem('sfa_user',  JSON.stringify(userData));
    setUser(userData);
    return userData;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('sfa_token');
    localStorage.removeItem('sfa_user');
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
};

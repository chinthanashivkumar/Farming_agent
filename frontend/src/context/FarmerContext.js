import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { profileService } from '../services/api';
import { useAuth } from './AuthContext';

const FarmerContext = createContext(null);

export function FarmerProvider({ children }) {
  const { user } = useAuth();
  const [profile, setProfile]   = useState(null);
  const [language, setLanguage] = useState(
    localStorage.getItem('sfa_lang') || 'en'
  );
  const [darkMode, setDarkMode] = useState(
    localStorage.getItem('sfa_dark') === 'true'
  );

  const fetchProfile = useCallback(async () => {
    if (!user) return;
    try {
      const res = await profileService.get();
      setProfile(res.data);
    } catch { /* profile may not exist yet */ }
  }, [user]);

  useEffect(() => { fetchProfile(); }, [fetchProfile]);

  // Apply dark-mode class to root
  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('sfa_dark', darkMode);
  }, [darkMode]);

  const changeLanguage = (lang) => {
    setLanguage(lang);
    localStorage.setItem('sfa_lang', lang);
  };

  const toggleDark = () => setDarkMode(prev => !prev);

  const updateProfile = async (data) => {
    await profileService.update(data);
    await fetchProfile();
  };

  return (
    <FarmerContext.Provider value={{
      profile, fetchProfile, updateProfile,
      language, changeLanguage,
      darkMode, toggleDark,
    }}>
      {children}
    </FarmerContext.Provider>
  );
}

export const useFarmer = () => {
  const ctx = useContext(FarmerContext);
  if (!ctx) throw new Error('useFarmer must be used inside FarmerProvider');
  return ctx;
};

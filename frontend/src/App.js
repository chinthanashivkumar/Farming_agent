import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { FarmerProvider } from './context/FarmerContext';
import ProtectedRoute from './components/ProtectedRoute';
import AppLayout from './components/AppLayout';

// Pages
import LoginPage    from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard    from './pages/Dashboard';
import ChatPage     from './pages/ChatPage';
import CropsPage    from './pages/CropsPage';
import SoilPage     from './pages/SoilPage';
import PestPage     from './pages/PestPage';
import FertilizerPage   from './pages/FertilizerPage';
import IrrigationPage   from './pages/IrrigationPage';
import MarketPage   from './pages/MarketPage';
import ProfilePage  from './pages/ProfilePage';
import SettingsPage from './pages/SettingsPage';

export default function App() {
  return (
    <AuthProvider>
      <FarmerProvider>
        <BrowserRouter>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 3500,
              style: {
                borderRadius: '10px',
                fontFamily: 'inherit',
                fontSize: '0.9rem',
              },
              success: { iconTheme: { primary: '#2d7a3a', secondary: '#fff' } },
            }}
          />
          <Routes>
            {/* Public routes */}
            <Route path="/login"    element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* Protected routes wrapped in sidebar layout */}
            <Route element={<ProtectedRoute />}>
              <Route element={<AppLayout />}>
                <Route path="/"             element={<Dashboard />} />
                <Route path="/chat"         element={<ChatPage />} />
                <Route path="/crops"        element={<CropsPage />} />
                <Route path="/soil"         element={<SoilPage />} />
                <Route path="/pests"        element={<PestPage />} />
                <Route path="/fertilizer"   element={<FertilizerPage />} />
                <Route path="/irrigation"   element={<IrrigationPage />} />
                <Route path="/market"       element={<MarketPage />} />
                <Route path="/profile"      element={<ProfilePage />} />
                <Route path="/settings"     element={<SettingsPage />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </FarmerProvider>
    </AuthProvider>
  );
}

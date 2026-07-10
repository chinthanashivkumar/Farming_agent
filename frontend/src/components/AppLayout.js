import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar  from './TopBar';
import './AppLayout.css';

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="app-layout">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(p => !p)} />
      <div className={`main-content${collapsed ? ' sidebar-collapsed' : ''}`}>
        <TopBar onMenuClick={() => setCollapsed(p => !p)} />
        <main className="page-body">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

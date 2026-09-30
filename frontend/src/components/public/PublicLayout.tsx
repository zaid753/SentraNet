import React from 'react';
import { Outlet } from 'react-router-dom';
import { PublicNavbar } from './PublicNavbar';
import { PublicFooter } from './PublicFooter';

export const PublicLayout: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen bg-[#070B14] text-[var(--color-text-primary)] font-sans selection:bg-blue-500/30 selection:text-blue-200">
      <PublicNavbar />
      <main className="flex-1 flex flex-col">
        <Outlet />
      </main>
      <PublicFooter />
    </div>
  );
};

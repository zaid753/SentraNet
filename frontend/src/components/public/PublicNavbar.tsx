import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export const PublicNavbar: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-[var(--color-border)] bg-[#070B14]/80 backdrop-blur-md">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-3">
          <Shield className="w-5 h-5 text-blue-400" />
          <span className="font-bold tracking-wider text-sm text-white">SENTRANET</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          <Link to="/features" className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-white transition-colors">Product</Link>
          <Link to="/how-it-works" className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-white transition-colors">How It Works</Link>
          <Link to="/technology" className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-white transition-colors">Technology</Link>
          <Link to="/security" className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-white transition-colors">Security</Link>
          <Link to="/docs" className="text-sm font-medium text-[var(--color-text-secondary)] hover:text-white transition-colors">Documentation</Link>
        </nav>

        <div className="flex items-center gap-4">
          <Link to="/login" className="hidden sm:block text-sm font-medium text-[var(--color-text-secondary)] hover:text-white transition-colors">
            Sign In
          </Link>
          <Link to="/signup" className="text-sm font-bold bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg transition-colors border border-blue-500/50">
            Launch SOC
          </Link>
        </div>
      </div>
    </header>
  );
};

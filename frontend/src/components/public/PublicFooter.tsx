import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export const PublicFooter: React.FC = () => {
  return (
    <footer className="border-t border-[var(--color-border)] bg-[#070B14] py-12 mt-auto">
      <div className="container mx-auto px-4 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="flex flex-col gap-4">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-400" />
            <span className="font-bold tracking-wider text-sm text-white">SENTRANET</span>
          </div>
          <p className="text-sm text-[var(--color-text-secondary)]">
            "From detecting attacks to forecasting them."
          </p>
        </div>

        <div>
          <h4 className="font-bold text-white mb-4 uppercase tracking-wider text-xs">Product</h4>
          <ul className="space-y-2 text-sm text-[var(--color-text-secondary)]">
            <li><Link to="/features" className="hover:text-blue-400 transition-colors">Features</Link></li>
            <li><Link to="/how-it-works" className="hover:text-blue-400 transition-colors">How It Works</Link></li>
            <li><Link to="/technology" className="hover:text-blue-400 transition-colors">Technology</Link></li>
            <li><Link to="/security" className="hover:text-blue-400 transition-colors">Security</Link></li>
            <li><Link to="/docs" className="hover:text-blue-400 transition-colors">Documentation</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white mb-4 uppercase tracking-wider text-xs">Application</h4>
          <ul className="space-y-2 text-sm text-[var(--color-text-secondary)]">
            <li><Link to="/signup" className="hover:text-blue-400 transition-colors">Launch SOC</Link></li>
            <li><Link to="/login" className="hover:text-blue-400 transition-colors">Sign In</Link></li>
            <li><Link to="/demo" className="hover:text-blue-400 transition-colors">Simulation Demo</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold text-white mb-4 uppercase tracking-wider text-xs">Project</h4>
          <ul className="space-y-2 text-sm text-[var(--color-text-secondary)]">
            <li><a href="https://github.com/zaid753/SentraNet" target="_blank" rel="noreferrer" className="hover:text-blue-400 transition-colors">GitHub Repository</a></li>
            <li><span className="text-[var(--color-text-secondary)]">SIH26153 OUTLIERS</span></li>
          </ul>
        </div>
      </div>
      <div className="container mx-auto px-4 mt-12 pt-8 border-t border-[var(--color-border)] text-xs text-[var(--color-text-secondary)] text-center font-mono">
        &copy; {new Date().getFullYear()} SENTRANET PROJECT. ALL RIGHTS RESERVED.
      </div>
    </footer>
  );
};

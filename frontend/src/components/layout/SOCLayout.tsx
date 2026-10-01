import React, { useState } from 'react';
import { 
  Activity, Shield, Target, AlertTriangle, Clock, 
  BarChart2, FileSearch, Database, Cpu, Settings, 
  Menu, X, ChevronLeft, ChevronRight, Server
} from 'lucide-react';
import { cn } from '../../utils/formatters';
import { TopCommandHeader } from './TopCommandHeader';
import { useSystemStatus } from '../../hooks/useSystemStatus';

interface SOCLayoutProps {
  children: React.ReactNode;
  activeView: string;
  onViewChange: (view: string) => void;
}

const navItems = [
  { id: 'dashboard', label: 'Overview', icon: Activity, group: 'OVERVIEW' },
  
  { id: 'telemetry', label: 'Live Telemetry', icon: Database, group: 'MONITOR' },
  { id: 'traffic', label: 'Traffic Analysis', icon: Activity, group: 'MONITOR' },
  { id: 'threats', label: 'Threats', icon: Shield, group: 'MONITOR' },

  { id: 'incidents', label: 'Incidents', icon: Shield, group: 'INVESTIGATE' },
  { id: 'alerts', label: 'Alerts', icon: AlertTriangle, group: 'INVESTIGATE' },
  { id: 'timeline', label: 'Attack Timeline', icon: Clock, group: 'INVESTIGATE' },
  { id: 'explainability', label: 'Evidence', icon: FileSearch, group: 'INVESTIGATE' },

  { id: 'forecast', label: 'Forecasting', icon: Target, group: 'INTELLIGENCE' },
  { id: 'analytics', label: 'Analytics', icon: BarChart2, group: 'INTELLIGENCE' },
  { id: 'evaluation', label: 'Evaluation', icon: BarChart2, group: 'INTELLIGENCE' },

  { id: 'integrations', label: 'Integrations', icon: Cpu, group: 'PLATFORM' },
  { id: 'api', label: 'API', icon: Server, group: 'PLATFORM' },
  { id: 'team', label: 'Team', icon: Shield, group: 'PLATFORM' },
  { id: 'audit', label: 'Audit Logs', icon: FileSearch, group: 'PLATFORM' },

  { id: 'health', label: 'System Health', icon: Activity, group: 'SYSTEM' },
  { id: 'settings', label: 'Settings', icon: Settings, group: 'SYSTEM' },
];

export const SOCLayout: React.FC<SOCLayoutProps> = ({ children, activeView, onViewChange }) => {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { systemStatus, connectionState } = useSystemStatus();

  // Group navigation items
  const groupedNav = navItems.reduce((acc, item) => {
    if (!acc[item.group]) acc[item.group] = [];
    acc[item.group].push(item);
    return acc;
  }, {} as Record<string, typeof navItems>);

  return (
    <div className="flex h-screen bg-[var(--color-bg)] text-[var(--color-text-primary)] font-sans overflow-hidden selection:bg-blue-500/30 selection:text-blue-200">
      
      {/* Mobile Sidebar Overlay */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/60 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <aside 
        className={cn(
          "fixed lg:static inset-y-0 left-0 z-50 flex flex-col bg-[var(--color-surface)] border-r border-[var(--color-border)] transition-all duration-300 ease-in-out",
          isSidebarOpen ? "w-64" : "w-20",
          isMobileMenuOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Sidebar Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-[var(--color-border)]">
          <div className={cn("flex items-center gap-3 overflow-hidden", !isSidebarOpen && "justify-center w-full")}>
            <div className="w-8 h-8 rounded bg-blue-500/10 border border-blue-500/30 flex items-center justify-center shrink-0">
              <Shield className="w-4 h-4 text-blue-400" />
            </div>
            {isSidebarOpen && (
              <div className="flex flex-col whitespace-nowrap">
                <span className="font-bold tracking-wider text-sm">SENTRANET</span>
                <span className="text-[10px] text-[var(--color-text-secondary)] font-mono">SOC PLATFORM</span>
              </div>
            )}
          </div>
          {isSidebarOpen && (
            <button 
              className="lg:hidden p-1 text-[var(--color-text-secondary)] hover:text-white"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Sidebar Navigation */}
        <div className="flex-1 overflow-y-auto py-4 custom-scrollbar">
          {Object.entries(groupedNav).map(([group, items]) => (
            <div key={group} className="mb-6">
              {isSidebarOpen ? (
                <div className="px-6 mb-2 text-[10px] font-bold uppercase tracking-wider text-[var(--color-text-secondary)]">
                  {group}
                </div>
              ) : (
                <div className="w-full flex justify-center mb-2">
                  <div className="w-4 h-px bg-[var(--color-border)]" />
                </div>
              )}
              <ul className="space-y-1 px-3">
                {items.map((item) => {
                  const Icon = item.icon;
                  const isActive = activeView === item.id || (activeView === 'foundation' && item.id === 'architecture');
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => {
                          onViewChange(item.id);
                          setIsMobileMenuOpen(false);
                        }}
                        className={cn(
                          "w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group relative",
                          isActive 
                            ? "bg-blue-500/10 text-blue-400" 
                            : "text-[var(--color-text-secondary)] hover:bg-[var(--color-elevated)] hover:text-[var(--color-text-primary)]",
                          !isSidebarOpen && "justify-center"
                        )}
                        title={!isSidebarOpen ? item.label : undefined}
                      >
                        <Icon className={cn("w-4 h-4 shrink-0", isActive ? "text-blue-400" : "text-slate-400 group-hover:text-slate-300")} />
                        {isSidebarOpen && (
                          <span className="text-sm font-medium whitespace-nowrap">{item.label}</span>
                        )}
                        
                        {isActive && isSidebarOpen && (
                          <div className="absolute right-2 w-1.5 h-1.5 rounded-full bg-blue-500" />
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        {/* Sidebar Footer / Toggle */}
        <div className="p-4 border-t border-[var(--color-border)] flex items-center justify-between">
          {isSidebarOpen && (
            <div className="text-[10px] font-mono text-[var(--color-text-secondary)]">
              SIH26153
            </div>
          )}
          <button 
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="hidden lg:flex p-1.5 rounded bg-[var(--color-elevated)] hover:bg-slate-800 text-[var(--color-text-secondary)] hover:text-white border border-[var(--color-border)]"
          >
            {isSidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
        {/* Mobile Header (Only visible on small screens) */}
        <header className="lg:hidden h-16 flex items-center justify-between px-4 bg-[var(--color-surface)] border-b border-[var(--color-border)] shrink-0">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-1.5 -ml-1.5 text-[var(--color-text-secondary)] hover:text-white"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div className="font-bold tracking-wider text-sm flex items-center gap-2">
              <Shield className="w-4 h-4 text-blue-400" />
              SENTRANET
            </div>
          </div>
        </header>

        {/* Desktop Header */}
        <div className="hidden lg:block">
          <TopCommandHeader status={systemStatus} isLoading={connectionState === 'LOADING'} />
        </div>

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto custom-scrollbar soc-grid-bg bg-[var(--color-bg)]">
          <div className="min-h-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

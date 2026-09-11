import React from 'react';
import {
  LayoutDashboard,
  GitCommit,
  Package,
  Server,
  ShieldAlert,
  Sliders,
  History,
  Workflow,
  FlaskConical,
  Lock
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Executive Overview', icon: LayoutDashboard },
    { id: 'pipeline', label: 'Visual Pipeline', icon: Workflow },
    { id: 'runs', label: 'Validation Runs', icon: History },
    { id: 'commit', label: 'Commit Verifier', icon: GitCommit },
    { id: 'dependencies', label: 'Dependency Inspector', icon: Package },
    { id: 'runner', label: 'Runner Integrity', icon: Server },
    { id: 'events', label: 'Security Events Log', icon: ShieldAlert },
    { id: 'config', label: 'Policy & Whitelist', icon: Sliders },
    { id: 'demo', label: 'Attack Simulation Lab', icon: FlaskConical },
  ];

  return (
    <aside className="w-64 bg-[#0D1322] border-r border-slate-800 flex flex-col justify-between h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-lg shadow-lg shadow-cyan-500/20">
              <Lock className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="font-extrabold tracking-wider text-white text-sm font-['JetBrains_Mono']">
                ZERO-TRUST
              </div>
              <div className="text-[11px] text-cyan-400 font-medium tracking-wide">
                CI/CD VALIDATOR
              </div>
            </div>
          </div>
          <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            MODE: FAIL-CLOSED
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="p-3 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 ${
                  isActive
                    ? 'bg-cyan-500/15 text-cyan-300 border border-cyan-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer info */}
      <div className="p-4 border-t border-slate-800/80 bg-[#0A0F1D]">
        <div className="text-[11px] text-slate-400">
          <div className="text-slate-300 font-semibold mb-0.5">Engine v1.0.0</div>
          <div>Cryptographic Guard Layer</div>
          <div className="mt-2 text-[10px] text-slate-500">
            Contributors: Hari & Dhanush
          </div>
        </div>
      </div>
    </aside>
  );
};

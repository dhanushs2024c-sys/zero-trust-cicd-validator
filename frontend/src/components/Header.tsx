import React from 'react';
import { RefreshCw, Play, Shield, Terminal } from 'lucide-react';

interface HeaderProps {
  title: string;
  subtitle: string;
  onValidate: () => void;
  onRefresh: () => void;
  isValidating?: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  title,
  subtitle,
  onValidate,
  onRefresh,
  isValidating = false,
}) => {
  return (
    <header className="h-16 bg-[#0B101E]/90 backdrop-blur border-b border-slate-800 px-6 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-base font-bold text-white tracking-wide">{title}</h1>
        <p className="text-xs text-slate-400">{subtitle}</p>
      </div>

      <div className="flex items-center gap-3">
        {/* Terminal/CLI indicator */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
          <Terminal className="w-3.5 h-3.5 text-cyan-400" />
          <span>zt-validator validate</span>
        </div>

        {/* Refresh Button */}
        <button
          onClick={onRefresh}
          className="p-2 text-slate-400 hover:text-white bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-lg transition-colors text-xs flex items-center gap-1.5"
          title="Refresh Data"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Refresh</span>
        </button>

        {/* Trigger Validation Button */}
        <button
          onClick={onValidate}
          disabled={isValidating}
          className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-xs rounded-lg shadow-lg shadow-cyan-500/20 flex items-center gap-2 transition-all disabled:opacity-50"
        >
          {isValidating ? (
            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Play className="w-3.5 h-3.5 fill-current" />
          )}
          <span>{isValidating ? 'Verifying Pipeline...' : 'Run Pipeline Validation'}</span>
        </button>
      </div>
    </header>
  );
};

import React, { useState, useEffect } from 'react';
import { Package, ShieldCheck, ShieldAlert, AlertTriangle, RefreshCw, Search, Check, AlertCircle } from 'lucide-react';
import { DependencyVerificationResult, DependencyItem } from '../types';
import { api } from '../services/api';

interface DependencyInspectorPageProps {
  initialResult?: DependencyVerificationResult | null;
}

export const DependencyInspectorPage: React.FC<DependencyInspectorPageProps> = ({ initialResult }) => {
  const [data, setData] = useState<DependencyVerificationResult | null>(initialResult || null);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [search, setSearch] = useState('');

  const fetchDeps = async () => {
    setLoading(true);
    try {
      const res = await api.getDependencies();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!data) {
      fetchDeps();
    }
  }, []);

  const items: DependencyItem[] = data?.items || [];

  const filteredItems = items.filter((item) => {
    if (statusFilter !== 'ALL' && item.status !== statusFilter) return false;
    if (search && !item.name.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">Dependency Integrity Inspector</h2>
          <p className="text-xs text-slate-400">
            Cryptographic hash verification across Python and Node.js lockfile manifests
          </p>
        </div>
        <button
          onClick={fetchDeps}
          disabled={loading}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-scan Dependencies</span>
        </button>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-slate-400 font-mono">TOTAL PACKAGES</div>
          <div className="text-2xl font-bold text-white mt-1 font-mono">
            {data?.total_dependencies ?? 0}
          </div>
        </div>

        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-emerald-400 font-mono">CRYPTOGRAPHICALLY VERIFIED</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1 font-mono">
            {data?.verified_count ?? 0}
          </div>
        </div>

        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-red-400 font-mono">HASH MISMATCHES</div>
          <div className="text-2xl font-bold text-red-400 mt-1 font-mono">
            {data?.mismatched_count ?? 0}
          </div>
        </div>

        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="text-xs text-amber-400 font-mono">UNVERIFIED PACKAGES</div>
          <div className="text-2xl font-bold text-amber-400 mt-1 font-mono">
            {data?.unverified_count ?? 0}
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search package name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-full font-mono"
          />
        </div>

        <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs">
          {['ALL', 'VERIFIED', 'MISMATCH', 'UNVERIFIED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1 rounded-md font-mono text-[11px] font-semibold transition-colors ${
                statusFilter === st
                  ? 'bg-cyan-500/20 text-cyan-300'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Dependency Table */}
      <div className="bg-[#0F1629] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0A0F1D] border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="p-3.5">Package</th>
                <th className="p-3.5">Version</th>
                <th className="p-3.5">Ecosystem</th>
                <th className="p-3.5">Manifest</th>
                <th className="p-3.5">Verification Method</th>
                <th className="p-3.5">Cryptographic Hash</th>
                <th className="p-3.5">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 font-mono">
              {filteredItems.map((item, idx) => {
                const isVerified = item.status === 'VERIFIED';
                const isMismatch = item.status === 'MISMATCH';
                const isUnverified = item.status === 'UNVERIFIED';

                return (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3.5 font-bold text-white font-sans">{item.name}</td>
                    <td className="p-3.5 text-slate-300">{item.version || 'unpinned'}</td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-300 uppercase font-semibold">
                        {item.ecosystem}
                      </span>
                    </td>
                    <td className="p-3.5 text-slate-400 text-[11px]">{item.manifest_file}</td>
                    <td className="p-3.5 text-cyan-400 text-[11px]">{item.verification_method}</td>
                    <td className="p-3.5 text-slate-400 text-[10px] max-w-xs truncate">
                      {item.expected_hash ? (
                        <span title={item.expected_hash}>{item.expected_hash}</span>
                      ) : (
                        <span className="text-slate-600 italic">none (unpinned)</span>
                      )}
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          isVerified
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : isMismatch
                            ? 'bg-red-500/15 text-red-400 border border-red-500/30'
                            : 'bg-amber-500/15 text-amber-400 border border-amber-500/30'
                        }`}
                      >
                        {isVerified && <Check className="w-3 h-3" />}
                        {isMismatch && <ShieldAlert className="w-3 h-3" />}
                        {isUnverified && <AlertCircle className="w-3 h-3" />}
                        {item.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {filteredItems.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500 font-sans">
                    No dependencies match the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

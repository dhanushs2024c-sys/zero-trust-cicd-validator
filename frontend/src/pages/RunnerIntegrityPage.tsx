import React, { useState, useEffect } from 'react';
import { Server, ShieldCheck, ShieldAlert, AlertTriangle, RefreshCw, Cpu, Database, Check, AlertCircle } from 'lucide-react';
import { RunnerIntegrityResult } from '../types';
import { api } from '../services/api';

interface RunnerIntegrityPageProps {
  initialRunner?: RunnerIntegrityResult | null;
}

export const RunnerIntegrityPage: React.FC<RunnerIntegrityPageProps> = ({ initialRunner }) => {
  const [data, setData] = useState<RunnerIntegrityResult | null>(initialRunner || null);
  const [loading, setLoading] = useState(false);
  const [generatingBaseline, setGeneratingBaseline] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const fetchRunner = async () => {
    setLoading(true);
    try {
      const res = await api.getRunnerStatus();
      setData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateBaseline = async () => {
    setGeneratingBaseline(true);
    try {
      const res = await api.generateBaseline();
      setMessage(`Baseline updated for ${res.total_files_hashed} critical files.`);
      await fetchRunner();
      setTimeout(() => setMessage(null), 4000);
    } catch (e) {
      console.error(e);
    } finally {
      setGeneratingBaseline(false);
    }
  };

  useEffect(() => {
    if (!data) {
      fetchRunner();
    }
  }, []);

  const isClean = data?.status === 'CLEAN';
  const isWarning = data?.status === 'WARNING';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">CI/CD Runner Host Integrity</h2>
          <p className="text-xs text-slate-400">
            Cryptographic baseline comparison, process monitoring, and environment variable audits
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleGenerateBaseline}
            disabled={generatingBaseline}
            className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <Database className="w-3.5 h-3.5" />
            <span>{generatingBaseline ? 'Hashing Files...' : 'Re-baseline Hashes'}</span>
          </button>

          <button
            onClick={fetchRunner}
            disabled={loading}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Audit Runner</span>
          </button>
        </div>
      </div>

      {message && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-lg text-xs font-semibold">
          {message}
        </div>
      )}

      {/* Mandatory Scope Disclaimer */}
      <div className="p-4 bg-slate-900/90 border border-amber-500/40 rounded-xl text-xs text-slate-300 flex items-start gap-3 shadow-md">
        <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="text-amber-400 font-bold font-mono">TECHNICAL INTEGRITY DISCLAIMER:</strong>{' '}
          {data?.disclaimer ||
            'Runner integrity checks provide evidence of tampering within the configured detection scope; they cannot mathematically prove that the entire host is uncompromised.'}
        </div>
      </div>

      {/* Status Banner */}
      <div
        className={`p-5 rounded-xl border flex items-center justify-between gap-4 ${
          isClean
            ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
            : isWarning
            ? 'bg-amber-950/20 border-amber-500/40 text-amber-300'
            : 'bg-red-950/20 border-red-500/40 text-red-300'
        }`}
      >
        <div className="flex items-center gap-3">
          <div
            className={`p-2.5 rounded-lg ${
              isClean
                ? 'bg-emerald-500/20 text-emerald-400'
                : isWarning
                ? 'bg-amber-500/20 text-amber-400'
                : 'bg-red-500/20 text-red-400'
            }`}
          >
            {isClean ? (
              <ShieldCheck className="w-7 h-7" />
            ) : (
              <ShieldAlert className="w-7 h-7" />
            )}
          </div>
          <div>
            <div className="text-xs font-mono font-bold uppercase tracking-wider">
              Environment Status: {data?.status}
            </div>
            <div className="text-sm font-semibold text-white mt-0.5">
              {data?.details}
            </div>
          </div>
        </div>

        <div className="text-right font-mono">
          <div className="text-xs text-slate-400">Integrity Score</div>
          <div className="text-2xl font-extrabold text-white">
            {data?.integrity_score ?? 100}/100
          </div>
        </div>
      </div>

      {/* Monitored Baseline Files Table */}
      <div className="bg-[#0F1629] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="font-bold text-white text-xs font-mono tracking-wider uppercase">
            Monitored Baseline Files ({data?.file_checks.length || 0})
          </div>
          <div className="text-xs text-slate-400 font-mono">
            Baseline: {data?.baseline_file_used || 'configs/integrity_baseline.json'}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0A0F1D] border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="p-3.5">Monitored Path</th>
                <th className="p-3.5">Baseline Hash (SHA-256)</th>
                <th className="p-3.5">Current Hash (SHA-256)</th>
                <th className="p-3.5 text-right">Integrity Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 font-mono">
              {data?.file_checks.map((f, idx) => {
                const isMatch = f.status === 'MATCH';
                return (
                  <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3.5 font-bold text-white font-sans">{f.path}</td>
                    <td className="p-3.5 text-slate-400 text-[11px] truncate max-w-xs">
                      {f.expected_hash ? f.expected_hash.slice(0, 24) + '...' : 'none'}
                    </td>
                    <td className="p-3.5 text-slate-400 text-[11px] truncate max-w-xs">
                      {f.actual_hash ? f.actual_hash.slice(0, 24) + '...' : 'missing'}
                    </td>
                    <td className="p-3.5 text-right">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          isMatch
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : 'bg-red-500/15 text-red-400 border border-red-500/30'
                        }`}
                      >
                        {isMatch ? <Check className="w-3 h-3" /> : <AlertCircle className="w-3 h-3" />}
                        {f.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Environment Variable Anomaly Audit */}
      <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-5 space-y-3">
        <div className="font-bold text-white text-xs font-mono tracking-wider uppercase flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          Environment Variable Hijacking Audit ({data?.env_checks.length || 0} flagged)
        </div>

        {data?.env_checks && data.env_checks.length > 0 ? (
          <div className="space-y-2">
            {data.env_checks.map((env, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-red-950/20 border border-red-500/30 text-xs font-mono flex items-start justify-between gap-4"
              >
                <div>
                  <div className="font-bold text-red-400">{env.variable} = "{env.value}"</div>
                  <div className="text-slate-300 font-sans text-[11px] mt-1">{env.reason}</div>
                </div>
                <span className="px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-[10px] font-bold shrink-0">
                  {env.severity}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-4 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-400 font-mono">
            ✓ No suspicious dynamic linker (LD_PRELOAD, DYLD_INSERT_LIBRARIES) or interpreter hook variables detected.
          </div>
        )}
      </div>
    </div>
  );
};

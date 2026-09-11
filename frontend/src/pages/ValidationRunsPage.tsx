import React, { useState } from 'react';
import { ValidationRun } from '../types';
import { CheckCircle2, XCircle, Clock, ExternalLink, X, Eye } from 'lucide-react';

interface ValidationRunsPageProps {
  runs: ValidationRun[];
  selectedRunId?: string | null;
  onSelectRun: (id: string | null) => void;
}

export const ValidationRunsPage: React.FC<ValidationRunsPageProps> = ({
  runs,
  selectedRunId,
  onSelectRun,
}) => {
  const [filter, setFilter] = useState<'ALL' | 'ALLOW' | 'BLOCK'>('ALL');
  const [search, setSearch] = useState('');

  const filteredRuns = runs.filter((r) => {
    if (filter !== 'ALL' && r.final_decision !== filter) return false;
    if (search && !r.run_id.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  const activeRun = runs.find((r) => r.run_id === selectedRunId);

  return (
    <div className="space-y-6">
      {/* Header controls */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">Validation History</h2>
          <p className="text-xs text-slate-400">
            Immutable audit record of all pipeline security verification executions
          </p>
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto">
          <input
            type="text"
            placeholder="Search Run ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-full sm:w-48 font-mono"
          />

          <div className="flex bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs">
            {(['ALL', 'ALLOW', 'BLOCK'] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setFilter(mode)}
                className={`px-3 py-1 rounded-md font-mono font-semibold transition-colors ${
                  filter === mode
                    ? mode === 'ALLOW'
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : mode === 'BLOCK'
                      ? 'bg-red-500/20 text-red-400'
                      : 'bg-cyan-500/20 text-cyan-300'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-[#0F1629] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0A0F1D] border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="p-3.5">Run ID</th>
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5">Commit Status</th>
                <th className="p-3.5">Dependency Status</th>
                <th className="p-3.5">Runner Status</th>
                <th className="p-3.5">Decision</th>
                <th className="p-3.5">Score</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredRuns.map((r) => {
                const isPass = r.final_decision === 'ALLOW';
                return (
                  <tr
                    key={r.run_id}
                    className="hover:bg-slate-800/40 transition-colors font-mono"
                  >
                    <td className="p-3.5 font-bold text-white">{r.run_id}</td>
                    <td className="p-3.5 text-slate-400 font-sans">
                      {new Date(r.timestamp).toLocaleString()}
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          r.commit_status === 'PASS'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}
                      >
                        {r.commit_status}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          r.dependency_status === 'PASS'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}
                      >
                        {r.dependency_status}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          r.runner_status === 'CLEAN'
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : r.runner_status === 'WARNING'
                            ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                            : 'bg-red-500/10 text-red-400 border border-red-500/20'
                        }`}
                      >
                        {r.runner_status}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-bold ${
                          isPass
                            ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                            : 'bg-red-500/15 text-red-400 border border-red-500/30'
                        }`}
                      >
                        {isPass ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                        {r.final_decision}
                      </span>
                    </td>
                    <td className="p-3.5 font-bold text-slate-200">
                      {r.score ?? r.policy?.score ?? 0}/100
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => onSelectRun(r.run_id)}
                        className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded text-xs transition-colors flex items-center gap-1 ml-auto"
                      >
                        <Eye className="w-3 h-3" />
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
              {filteredRuns.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-slate-500 font-sans">
                    No validation runs found matching your filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal / Drawer for inspecting run details */}
      {activeRun && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F1629] border border-slate-700 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl">
            {/* Modal Header */}
            <div className="p-5 border-b border-slate-800 flex items-center justify-between bg-[#0B101E]">
              <div>
                <div className="text-xs text-slate-400 font-mono">Run Inspector</div>
                <div className="text-lg font-bold text-white font-mono flex items-center gap-2">
                  <span>{activeRun.run_id}</span>
                  <span
                    className={`text-xs px-2.5 py-0.5 rounded-full font-bold ${
                      activeRun.final_decision === 'ALLOW'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-red-500/20 text-red-400'
                    }`}
                  >
                    {activeRun.final_decision}
                  </span>
                </div>
              </div>
              <button
                onClick={() => onSelectRun(null)}
                className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-5 text-xs">
              {/* Policy Decision Summary */}
              <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                <div className="font-bold text-white uppercase tracking-wider font-mono text-[11px]">
                  Policy Evaluation
                </div>
                <ul className="space-y-1 text-slate-300">
                  {activeRun.policy?.reasons?.map((reason: string, idx: number) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-cyan-400 font-bold">•</span>
                      <span>{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Commit Details */}
              <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                <div className="font-bold text-white uppercase tracking-wider font-mono text-[11px]">
                  Commit Verification
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-300 font-mono">
                  <div>Commit Hash: {activeRun.commit_hash || activeRun.commit?.commit_hash}</div>
                  <div>Status: {activeRun.commit_status || activeRun.commit?.status}</div>
                  <div>Author: {activeRun.commit?.author_email || 'N/A'}</div>
                  <div>Signed: {activeRun.commit?.signed ? 'Yes' : 'No'}</div>
                </div>
                {activeRun.commit?.details && (
                  <p className="text-slate-400 text-[11px] mt-1">{activeRun.commit.details}</p>
                )}
              </div>

              {/* Dependencies Details */}
              <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                <div className="font-bold text-white uppercase tracking-wider font-mono text-[11px]">
                  Dependency Verification
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-300 font-mono">
                  <div>Status: {activeRun.dependency_status || activeRun.dependencies?.status}</div>
                  <div>Verified: {activeRun.dependencies?.verified_count ?? 'N/A'}</div>
                  <div>Mismatches: {activeRun.dependencies?.mismatched_count ?? 'N/A'}</div>
                  <div>Unverified: {activeRun.dependencies?.unverified_count ?? 'N/A'}</div>
                </div>
                {activeRun.dependencies?.details && (
                  <p className="text-slate-400 text-[11px] mt-1">{activeRun.dependencies.details}</p>
                )}
              </div>

              {/* Runner Details */}
              <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-2">
                <div className="font-bold text-white uppercase tracking-wider font-mono text-[11px]">
                  Runner Host Integrity
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-300 font-mono">
                  <div>Status: {activeRun.runner_status || activeRun.runner?.status}</div>
                  <div>Matched Files: {activeRun.runner?.matched_files_count ?? 'N/A'}</div>
                  <div>Tampered Files: {activeRun.runner?.tampered_files_count ?? 'N/A'}</div>
                  <div>Score: {activeRun.runner?.integrity_score ?? 'N/A'}/100</div>
                </div>
                {activeRun.runner?.details && (
                  <p className="text-slate-400 text-[11px] mt-1">{activeRun.runner.details}</p>
                )}
              </div>
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-slate-800 bg-[#0B101E] flex justify-end">
              <button
                onClick={() => onSelectRun(null)}
                className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

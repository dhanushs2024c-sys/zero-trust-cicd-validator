import React from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  GitCommit,
  Package,
  Server,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ExternalLink,
  Lock,
  Flame,
  ArrowUpRight
} from 'lucide-react';
import { ValidationRun, SecurityEvent } from '../types';
import { VisualPipeline } from '../components/VisualPipeline';

interface DashboardPageProps {
  latestRun: ValidationRun | null;
  recentRuns: ValidationRun[];
  recentEvents: SecurityEvent[];
  onSelectRun: (runId: string) => void;
  onNavigateTab: (tab: string) => void;
  onRunDemo: (type: 'legit' | 'dep' | 'commit' | 'runner') => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  latestRun,
  recentRuns,
  recentEvents,
  onSelectRun,
  onNavigateTab,
  onRunDemo
}) => {
  const isAllowed = latestRun?.final_decision === 'ALLOW';
  const score = latestRun?.policy?.score ?? latestRun?.score ?? 0;

  return (
    <div className="space-y-6">
      {/* 1. Executive Build Status Banner */}
      <div
        className={`p-6 rounded-2xl border transition-all ${
          isAllowed
            ? 'bg-gradient-to-r from-[#0C1A1A] via-[#0E2320] to-[#0A1620] border-emerald-500/50 glow-emerald'
            : 'bg-gradient-to-r from-[#1E0C11] via-[#2A1017] to-[#180A12] border-red-500/50 glow-danger'
        }`}
      >
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div
              className={`p-3.5 rounded-xl ${
                isAllowed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
              }`}
            >
              {isAllowed ? (
                <ShieldCheck className="w-8 h-8" />
              ) : (
                <ShieldAlert className="w-8 h-8" />
              )}
            </div>
            <div>
              <div className="text-xs font-mono font-bold tracking-widest text-slate-400 uppercase">
                Zero-Trust Pipeline Decision
              </div>
              <div className="text-2xl md:text-3xl font-extrabold text-white tracking-tight flex items-center gap-3 mt-0.5">
                <span>{isAllowed ? 'BUILD ALLOWED' : 'BUILD BLOCKED'}</span>
                <span
                  className={`text-xs px-2.5 py-1 rounded-md font-mono font-semibold ${
                    isAllowed ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'
                  }`}
                >
                  Exit Code: {latestRun?.exit_code ?? 1}
                </span>
              </div>
              <div className="text-xs text-slate-300 mt-1.5 max-w-2xl">
                {latestRun?.policy?.reasons?.[0] || 'Pipeline evaluation completed under strict Zero-Trust policy.'}
              </div>
            </div>
          </div>

          {/* Security Score Badge */}
          <div className="bg-[#0B101D]/80 backdrop-blur border border-slate-800 rounded-xl p-4 text-center min-w-[150px]">
            <div className="text-[11px] font-mono text-slate-400 font-semibold uppercase">
              Security Score
            </div>
            <div
              className={`text-3xl font-black font-mono mt-1 ${
                score >= 80 ? 'text-emerald-400' : score >= 50 ? 'text-amber-400' : 'text-red-400'
              }`}
            >
              {score}
              <span className="text-sm text-slate-500 font-normal">/100</span>
            </div>
            <div className="text-[9px] text-slate-400 mt-1 leading-tight">
              Policy Compliance Index
            </div>
          </div>
        </div>
      </div>

      {/* 2. Main 4 Pillars Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Build Gate */}
        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase font-mono">Build Stage</span>
            <Lock className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-lg font-bold text-white">
            {isAllowed ? 'GATED: PASSED' : 'GATED: BLOCKED'}
          </div>
          <div className="text-xs text-slate-400 mt-1">
            Run ID: <span className="font-mono text-slate-300">{latestRun?.run_id || 'N/A'}</span>
          </div>
        </div>

        {/* Card 2: Commit Signature */}
        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase font-mono">Commit Signature</span>
            <GitCommit className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-center gap-2">
            {latestRun?.commit?.status === 'PASS' || latestRun?.commit_status === 'PASS' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <XCircle className="w-5 h-5 text-red-400" />
            )}
            <span className="text-lg font-bold text-white">
              {latestRun?.commit?.signed ? `${latestRun.commit.signature_type} VERIFIED` : 'UNSIGNED'}
            </span>
          </div>
          <div className="text-xs text-slate-400 mt-1 truncate">
            {latestRun?.commit?.author_email || 'No author detected'}
          </div>
        </div>

        {/* Card 3: Dependencies */}
        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase font-mono">Dependency Hashes</span>
            <Package className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-center gap-2">
            {latestRun?.dependencies?.status === 'PASS' || latestRun?.dependency_status === 'PASS' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (
              <XCircle className="w-5 h-5 text-red-400" />
            )}
            <span className="text-lg font-bold text-white">
              {(latestRun?.dependencies?.status || latestRun?.dependency_status) === 'PASS'
                ? 'INTEGRITY OK'
                : `${latestRun?.dependencies?.mismatched_count || 0} MISMATCH`}
            </span>
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {latestRun?.dependencies?.verified_count || 0} locked packages verified
          </div>
        </div>

        {/* Card 4: Runner Integrity */}
        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase font-mono">Runner Environment</span>
            <Server className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-center gap-2">
            {(latestRun?.runner?.status || latestRun?.runner_status) === 'CLEAN' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : (latestRun?.runner?.status || latestRun?.runner_status) === 'WARNING' ? (
              <AlertTriangle className="w-5 h-5 text-amber-400" />
            ) : (
              <XCircle className="w-5 h-5 text-red-400" />
            )}
            <span className="text-lg font-bold text-white">
              {latestRun?.runner?.status || latestRun?.runner_status || 'UNKNOWN'}
            </span>
          </div>
          <div className="text-xs text-slate-400 mt-1">
            {latestRun?.runner?.matched_files_count || 0} baseline files verified
          </div>
        </div>
      </div>

      {/* 3. Visual Pipeline Flow */}
      <VisualPipeline currentRun={latestRun} />

      {/* 4. Scope Disclaimer Banner (Mandatory requirement) */}
      <div className="p-3 bg-slate-900/60 border border-slate-800 rounded-lg text-xs text-slate-400 flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
        <div className="leading-relaxed">
          <strong className="text-slate-300">Technical Scope Disclaimer:</strong>{' '}
          {latestRun?.runner?.disclaimer ||
            'Runner integrity checks provide evidence of tampering within the configured detection scope; they cannot mathematically prove that the entire host is uncompromised.'}
        </div>
      </div>


      {/* 5. Quick Attack Simulation Controls */}
      <div className="bg-[#0D1424] border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Flame className="w-4 h-4 text-cyan-400" />
            <h3 className="text-xs font-bold text-white tracking-wider uppercase font-mono">
              Quick Attack Simulation Controls
            </h3>
          </div>
          <button
            onClick={() => onNavigateTab('demo')}
            className="text-xs text-cyan-400 hover:underline flex items-center gap-1 font-semibold"
          >
            Open Full Lab <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          <button
            onClick={() => onRunDemo('legit')}
            className="p-3 rounded-lg bg-slate-900 hover:bg-emerald-950/40 border border-slate-800 hover:border-emerald-500/50 text-left transition-all group"
          >
            <div className="text-xs font-bold text-white group-hover:text-emerald-300">
              ✓ Run Secure Build
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Verified commit + deps + clean host
            </div>
          </button>

          <button
            onClick={() => onRunDemo('dep')}
            className="p-3 rounded-lg bg-slate-900 hover:bg-red-950/40 border border-slate-800 hover:border-red-500/50 text-left transition-all group"
          >
            <div className="text-xs font-bold text-white group-hover:text-red-300">
              ⚠ Dependency Attack
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Simulates hash mismatch in lockfile
            </div>
          </button>

          <button
            onClick={() => onRunDemo('commit')}
            className="p-3 rounded-lg bg-slate-900 hover:bg-red-950/40 border border-slate-800 hover:border-red-500/50 text-left transition-all group"
          >
            <div className="text-xs font-bold text-white group-hover:text-red-300">
              ⚠ Forged Commit Attack
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Simulates unsigned or untrusted author
            </div>
          </button>

          <button
            onClick={() => onRunDemo('runner')}
            className="p-3 rounded-lg bg-slate-900 hover:bg-red-950/40 border border-slate-800 hover:border-red-500/50 text-left transition-all group"
          >
            <div className="text-xs font-bold text-white group-hover:text-red-300">
              ⚠ Runner Tampering
            </div>
            <div className="text-[10px] text-slate-400 mt-0.5">
              Alters baseline + injects LD_PRELOAD
            </div>
          </button>
        </div>
      </div>

      {/* 6. Recent Runs & Security Events (Two Column) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Validation Runs */}
        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-bold text-white tracking-wider uppercase font-mono">
              Recent Validation Runs
            </h3>
            <button
              onClick={() => onNavigateTab('runs')}
              className="text-xs text-cyan-400 hover:underline font-semibold"
            >
              View All
            </button>
          </div>

          <div className="space-y-2">
            {recentRuns.slice(0, 5).map((run) => (
              <div
                key={run.run_id}
                onClick={() => onSelectRun(run.run_id)}
                className="p-3 rounded-lg bg-slate-900/80 hover:bg-slate-800/80 border border-slate-800/80 cursor-pointer flex items-center justify-between text-xs transition-colors"
              >
                <div>
                  <div className="font-mono font-bold text-white">{run.run_id}</div>
                  <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                    {new Date(run.timestamp).toLocaleTimeString()} · {run.target_directory.split('/').pop() || 'repo'}
                  </div>
                </div>
                <div className="text-right">
                  <span
                    className={`inline-block px-2.5 py-0.5 rounded-full font-mono text-[10px] font-bold ${
                      run.final_decision === 'ALLOW'
                        ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        : 'bg-red-500/15 text-red-400 border border-red-500/30'
                    }`}
                  >
                    {run.final_decision}
                  </span>
                  <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                    Score: {run.policy?.score ?? 0}/100
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Security Events */}
        <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-bold text-white tracking-wider uppercase font-mono">
              Security Audit Trail (Append-Only)
            </h3>
            <button
              onClick={() => onNavigateTab('events')}
              className="text-xs text-cyan-400 hover:underline font-semibold"
            >
              View All
            </button>
          </div>

          <div className="space-y-2">
            {recentEvents.slice(0, 5).map((evt, idx) => (
              <div
                key={evt.id || idx}
                className="p-3 rounded-lg bg-slate-900/80 border border-slate-800/80 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                      evt.severity === 'CRITICAL'
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : evt.severity === 'HIGH'
                        ? 'bg-orange-500/20 text-orange-400'
                        : evt.severity === 'MEDIUM'
                        ? 'bg-amber-500/20 text-amber-400'
                        : 'bg-cyan-500/20 text-cyan-400'
                    }`}
                  >
                    {evt.severity}
                  </span>
                  <span className="text-[10px] font-mono text-slate-400">
                    {new Date(evt.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div className="font-semibold text-slate-200 mt-1.5 line-clamp-1">
                  {evt.message}
                </div>
                <div className="text-[10px] text-slate-400 font-mono mt-0.5 flex items-center justify-between">
                  <span>Category: {evt.category}</span>
                  <span className="text-slate-500">Action: {evt.action}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

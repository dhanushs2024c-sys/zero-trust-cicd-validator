import React from 'react';
import { GitCommit, Package, Server, ShieldCheck, CheckCircle2, XCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { ValidationRun } from '../types';

interface VisualPipelineProps {
  currentRun?: ValidationRun | null;
}

export const VisualPipeline: React.FC<VisualPipelineProps> = ({ currentRun }) => {
  if (!currentRun) {
    return (
      <div className="bg-[#10172A] border border-slate-800 rounded-xl p-6 text-center text-slate-400">
        No validation run available to render pipeline graph.
      </div>
    );
  }

  const isAllowed = currentRun.final_decision === 'ALLOW';
  const commit = currentRun.commit || {
    signed: false,
    signature_type: 'NONE' as const,
    status: (currentRun.commit_status || 'FAIL') as 'PASS' | 'FAIL' | 'WARNING',
    trusted_developer: false,
  };
  const dependencies = currentRun.dependencies || {
    verified_count: 0,
    total_dependencies: 0,
    status: (currentRun.dependency_status || 'FAIL') as 'PASS' | 'FAIL' | 'WARNING',
    mismatched_count: 0,
  };
  const runner = currentRun.runner || {
    status: (currentRun.runner_status || 'TAMPERED') as 'CLEAN' | 'WARNING' | 'TAMPERED',
    matched_files_count: 0,
  };
  const policy = currentRun.policy || {
    score: currentRun.score || 0,
  };

  const stages = [
    {
      id: 'commit',
      title: '1. Commit Verification',
      subtitle: commit.signed ? `${commit.signature_type} Signed` : 'Unsigned',
      status: commit.status,
      icon: GitCommit,
      meta: commit.trusted_developer ? 'Trusted Key' : 'Untrusted Author',
    },
    {
      id: 'deps',
      title: '2. Dependencies',
      subtitle: `${dependencies.verified_count}/${dependencies.total_dependencies} Verified`,
      status: dependencies.status,
      icon: Package,
      meta: dependencies.mismatched_count > 0 ? `${dependencies.mismatched_count} Mismatch!` : 'Hashes Locked',
    },
    {
      id: 'runner',
      title: '3. Runner Integrity',
      subtitle: runner.status,
      status: runner.status === 'CLEAN' ? 'PASS' : runner.status === 'WARNING' ? 'WARNING' : 'FAIL',
      icon: Server,
      meta: `${runner.matched_files_count} Hashes OK`,
    },
    {
      id: 'policy',
      title: '4. Policy Engine',
      subtitle: isAllowed ? 'Policy Satisfied' : 'Rule Violation',
      status: isAllowed ? 'PASS' : 'FAIL',
      icon: ShieldCheck,
      meta: `Score: ${policy.score}/100`,
    },
  ];


  return (
    <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white tracking-wide uppercase font-mono">
            Zero-Trust Pipeline Execution Graph
          </h3>
          <p className="text-xs text-slate-400">
            Sequential cryptographic verification gates before build stage
          </p>
        </div>
        <div
          className={`px-3 py-1 rounded-full text-xs font-mono font-bold tracking-wider ${
            isAllowed
              ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 glow-emerald'
              : 'bg-red-500/15 text-red-400 border border-red-500/30 glow-danger'
          }`}
        >
          {isAllowed ? '✓ BUILD ALLOWED' : '✗ BUILD BLOCKED'}
        </div>
      </div>

      {/* Interactive Diagram Pipeline Flow */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3 py-2">
        {stages.map((stage, idx) => {
          const Icon = stage.icon;
          const isPass = stage.status === 'PASS';
          const isWarn = stage.status === 'WARNING';

          return (
            <React.Fragment key={stage.id}>
              {/* Node Card */}
              <div
                className={`flex-1 p-3.5 rounded-lg border transition-all duration-200 ${
                  isPass
                    ? 'bg-slate-900/90 border-emerald-500/40 text-slate-100 shadow-sm shadow-emerald-500/10'
                    : isWarn
                    ? 'bg-slate-900/90 border-amber-500/40 text-slate-100 shadow-sm shadow-amber-500/10'
                    : 'bg-red-950/20 border-red-500/50 text-slate-100 shadow-sm shadow-red-500/20'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="p-1.5 rounded-md bg-slate-800 text-cyan-400">
                    <Icon className="w-4 h-4" />
                  </div>
                  {isPass ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : isWarn ? (
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-400" />
                  )}
                </div>

                <div className="text-[11px] font-bold tracking-tight text-white mb-0.5 truncate">
                  {stage.title}
                </div>
                <div className="text-[11px] font-mono font-medium text-slate-300">
                  {stage.subtitle}
                </div>
                <div
                  className={`text-[10px] mt-1 font-semibold ${
                    isPass ? 'text-emerald-400' : isWarn ? 'text-amber-400' : 'text-red-400'
                  }`}
                >
                  {stage.meta}
                </div>
              </div>

              {/* Arrow connector */}
              <div className="hidden lg:flex justify-center text-slate-600 px-1">
                <ArrowRight className="w-4 h-4 text-slate-600" />
              </div>
            </React.Fragment>
          );
        })}

        {/* Final Decision Node */}
        <div
          className={`flex-1 p-3.5 rounded-lg border transition-all ${
            isAllowed
              ? 'bg-emerald-950/25 border-emerald-500/60 glow-emerald text-emerald-300'
              : 'bg-red-950/30 border-red-500/60 glow-danger text-red-300'
          }`}
        >
          <div className="text-[10px] font-mono tracking-wider uppercase font-bold text-slate-400 mb-1">
            Build Stage Gate
          </div>
          <div className="text-sm font-extrabold tracking-wide font-mono flex items-center gap-1.5">
            {isAllowed ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>ALLOW</span>
              </>
            ) : (
              <>
                <XCircle className="w-4 h-4 text-red-400 shrink-0" />
                <span>BLOCKED</span>
              </>
            )}
          </div>
          <div className="text-[10px] text-slate-400 mt-1 font-mono">
            Exit Code: {currentRun.exit_code}
          </div>
        </div>
      </div>

    </div>
  );
};

import React, { useState } from 'react';
import {
  FlaskConical,
  ShieldCheck,
  ShieldAlert,
  RotateCcw,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Play,
  Terminal,
  FileCode
} from 'lucide-react';
import { ValidationRun } from '../types';
import { api } from '../services/api';

interface DemoLabPageProps {
  onRunFinished?: (run: ValidationRun) => void;
}

export const DemoLabPage: React.FC<DemoLabPageProps> = ({ onRunFinished }) => {
  const [activeScenario, setActiveScenario] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [runResult, setRunResult] = useState<ValidationRun | null>(null);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  const handleRunScenario = async (type: 'legit' | 'dep' | 'commit' | 'runner' | 'reset') => {
    setLoading(true);
    setActiveScenario(type);
    setResetMessage(null);

    try {
      let res: ValidationRun | null = null;
      if (type === 'legit') {
        res = await api.demoLegitimate();
      } else if (type === 'dep') {
        res = await api.demoDependencyAttack();
      } else if (type === 'commit') {
        res = await api.demoInvalidCommit();
      } else if (type === 'runner') {
        res = await api.demoRunnerTampering();
      } else if (type === 'reset') {
        const resetRes = await api.demoReset();
        setResetMessage(resetRes.message);
        setRunResult(null);
      }

      if (res) {
        setRunResult(res);
        if (onRunFinished) onRunFinished(res);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const isAllowed = runResult?.final_decision === 'ALLOW';

  return (
    <div className="space-y-6">
      {/* Simulation Warning Banner (MANDATORY REQUIREMENT) */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-amber-500/15 via-red-500/15 to-amber-500/15 border-2 border-amber-500/60 shadow-lg glow-danger">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-6 h-6 text-amber-400 shrink-0 animate-pulse" />
          <div>
            <div className="text-xs font-mono font-black text-amber-400 uppercase tracking-widest">
              SIMULATION ONLY
            </div>
            <div className="text-sm font-bold text-white mt-0.5">
              No real malware or external systems are affected. All simulation scenarios execute inside safe, isolated local harnesses.
            </div>
          </div>
        </div>
      </div>

      {/* Header */}
      <div>
        <h2 className="text-lg font-bold text-white tracking-wide">Interactive Attack Simulation Lab</h2>
        <p className="text-xs text-slate-400">
          Demonstrate Zero-Trust CI/CD pipeline enforcement against simulated supply-chain attacks and host tampering
        </p>
      </div>

      {/* Action Buttons Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {/* Button 1 */}
        <button
          onClick={() => handleRunScenario('legit')}
          disabled={loading}
          className="p-4 rounded-xl bg-slate-900 hover:bg-emerald-950/40 border border-slate-800 hover:border-emerald-500 text-left transition-all group disabled:opacity-50"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </span>
            <span className="text-[10px] font-mono font-bold text-emerald-400">SCENARIO 1</span>
          </div>
          <div className="text-xs font-bold text-white group-hover:text-emerald-300">
            Run Secure Build
          </div>
          <div className="text-[11px] text-slate-400 mt-1 leading-snug">
            Signed commit + trusted developer + valid dependencies + clean runner
          </div>
          <div className="mt-3 text-[10px] font-mono text-emerald-400 font-bold flex items-center gap-1">
            → Expect: BUILD ALLOWED
          </div>
        </button>

        {/* Button 2 */}
        <button
          onClick={() => handleRunScenario('dep')}
          disabled={loading}
          className="p-4 rounded-xl bg-slate-900 hover:bg-red-950/40 border border-slate-800 hover:border-red-500 text-left transition-all group disabled:opacity-50"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="p-2 rounded-lg bg-red-500/10 text-red-400">
              <ShieldAlert className="w-5 h-5" />
            </span>
            <span className="text-[10px] font-mono font-bold text-red-400">SCENARIO 2</span>
          </div>
          <div className="text-xs font-bold text-white group-hover:text-red-300">
            Simulate Dependency Attack
          </div>
          <div className="text-[11px] text-slate-400 mt-1 leading-snug">
            Injects mismatched package hash in lockfile (supply-chain package substitution)
          </div>
          <div className="mt-3 text-[10px] font-mono text-red-400 font-bold flex items-center gap-1">
            → Expect: BUILD BLOCKED
          </div>
        </button>

        {/* Button 3 */}
        <button
          onClick={() => handleRunScenario('commit')}
          disabled={loading}
          className="p-4 rounded-xl bg-slate-900 hover:bg-red-950/40 border border-slate-800 hover:border-red-500 text-left transition-all group disabled:opacity-50"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="p-2 rounded-lg bg-red-500/10 text-red-400">
              <ShieldAlert className="w-5 h-5" />
            </span>
            <span className="text-[10px] font-mono font-bold text-red-400">SCENARIO 3</span>
          </div>
          <div className="text-xs font-bold text-white group-hover:text-red-300">
            Simulate Invalid Commit
          </div>
          <div className="text-[11px] text-slate-400 mt-1 leading-snug">
            Attempts build from unsigned commit or untrusted author identity
          </div>
          <div className="mt-3 text-[10px] font-mono text-red-400 font-bold flex items-center gap-1">
            → Expect: BUILD BLOCKED
          </div>
        </button>

        {/* Button 4 */}
        <button
          onClick={() => handleRunScenario('runner')}
          disabled={loading}
          className="p-4 rounded-xl bg-slate-900 hover:bg-red-950/40 border border-slate-800 hover:border-red-500 text-left transition-all group disabled:opacity-50"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="p-2 rounded-lg bg-red-500/10 text-red-400">
              <ShieldAlert className="w-5 h-5" />
            </span>
            <span className="text-[10px] font-mono font-bold text-red-400">SCENARIO 4</span>
          </div>
          <div className="text-xs font-bold text-white group-hover:text-red-300">
            Simulate Runner Tampering
          </div>
          <div className="text-[11px] text-slate-400 mt-1 leading-snug">
            Modifies baseline config and injects LD_PRELOAD environment variable
          </div>
          <div className="mt-3 text-[10px] font-mono text-red-400 font-bold flex items-center gap-1">
            → Expect: BUILD BLOCKED
          </div>
        </button>

        {/* Button 5: Reset */}
        <button
          onClick={() => handleRunScenario('reset')}
          disabled={loading}
          className="p-4 rounded-xl bg-slate-900 hover:bg-cyan-950/40 border border-slate-800 hover:border-cyan-500 text-left transition-all group disabled:opacity-50"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
              <RotateCcw className="w-5 h-5" />
            </span>
            <span className="text-[10px] font-mono font-bold text-cyan-400">MAINTENANCE</span>
          </div>
          <div className="text-xs font-bold text-white group-hover:text-cyan-300">
            Reset Demo Environment
          </div>
          <div className="text-[11px] text-slate-400 mt-1 leading-snug">
            Restores clean baseline hashes and resets all demo variables
          </div>
          <div className="mt-3 text-[10px] font-mono text-cyan-400 font-bold flex items-center gap-1">
            → Restores Clean State
          </div>
        </button>
      </div>

      {resetMessage && (
        <div className="p-4 bg-cyan-950/30 border border-cyan-500/40 rounded-xl text-cyan-300 text-xs font-semibold flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{resetMessage}</span>
        </div>
      )}

      {/* Simulation Execution Output */}
      {runResult && (
        <div className="bg-[#0F1629] border border-slate-800 rounded-2xl p-6 space-y-5 shadow-2xl">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div
                className={`p-2.5 rounded-xl ${
                  isAllowed ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                }`}
              >
                {isAllowed ? <CheckCircle2 className="w-6 h-6" /> : <XCircle className="w-6 h-6" />}
              </div>
              <div>
                <div className="text-xs font-mono font-bold text-slate-400 uppercase">
                  Simulation Result ({runResult.run_id})
                </div>
                <div className="text-xl font-extrabold text-white tracking-wide mt-0.5">
                  FINAL DECISION: {runResult.final_decision === 'ALLOW' ? 'BUILD ALLOWED' : 'BUILD BLOCKED'}
                </div>
              </div>
            </div>

            <div className="text-right">
              <div className="text-[11px] text-slate-400 font-mono">Exit Code</div>
              <div
                className={`text-xl font-black font-mono ${
                  runResult.exit_code === 0 ? 'text-emerald-400' : 'text-red-400'
                }`}
              >
                {runResult.exit_code}
              </div>
            </div>
          </div>

          {/* Detailed Rationale Box */}
          <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <div className="text-xs font-bold text-slate-200 uppercase font-mono tracking-wider">
              Enforcement Evaluation:
            </div>
            <ul className="space-y-1 text-xs">
              {runResult.policy?.reasons?.map((r, i) => (
                <li
                  key={i}
                  className={`flex items-start gap-2 font-medium ${
                    isAllowed ? 'text-emerald-300' : 'text-red-300'
                  }`}
                >
                  <span className="font-bold">{isAllowed ? '✓' : '✗'}</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Attack Specific Details Display */}
          {activeScenario === 'dep' && (
            <div className="p-4 rounded-xl bg-red-950/30 border border-red-500/40 text-xs font-mono space-y-2">
              <div className="font-bold text-red-400 uppercase tracking-wider">
                ⚠ SIMULATED SUPPLY-CHAIN ATTACK DETAIL
              </div>
              <p className="text-slate-300 font-sans text-xs">
                Dependency integrity mismatch detected on package <code className="text-cyan-300">malicious-crypto-helper</code>:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px] pt-1">
                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                  <div className="text-slate-500">EXPECTED HASH (Lockfile):</div>
                  <div className="text-emerald-400 break-all select-all font-bold">
                    sha256:aaa111222333444555666777888999000aaabbbcccdddeeefff0001112223334
                  </div>
                </div>
                <div className="p-3 bg-slate-900 rounded border border-slate-800">
                  <div className="text-slate-500">DETECTED HASH (Tampered Artifact):</div>
                  <div className="text-red-400 break-all select-all font-bold">
                    sha256:TAMPERED_bbb222333444555666777888999000aaabbbcccdddeeefff0001112223334
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeScenario === 'commit' && (
            <div className="p-4 rounded-xl bg-red-950/30 border border-red-500/40 text-xs font-mono space-y-2">
              <div className="font-bold text-red-400 uppercase tracking-wider">
                ⚠ FORGED / UNSIGNED COMMIT ATTACK DETAIL
              </div>
              <p className="text-slate-300 font-sans text-xs">
                Commit <code className="text-cyan-300">deadbee</code> author{' '}
                <code className="text-red-400">untrusted-attacker@darkweb-exploit.org</code> is not authorized in{' '}
                <code className="text-slate-300">configs/trusted_developers.yaml</code>.
              </p>
            </div>
          )}

          {activeScenario === 'runner' && (
            <div className="p-4 rounded-xl bg-red-950/30 border border-red-500/40 text-xs font-mono space-y-2">
              <div className="font-bold text-red-400 uppercase tracking-wider">
                ⚠ RUNNER TAMPERING ATTACK DETAIL
              </div>
              <p className="text-slate-300 font-sans text-xs">
                Cryptographic baseline hash mismatch on <code className="text-cyan-300">configs/policy.yaml</code> and dynamic linker variable <code className="text-red-400">LD_PRELOAD=/tmp/attacker_hook.so</code> detected.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

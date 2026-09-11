import React, { useState, useEffect } from 'react';
import { GitCommit, ShieldCheck, ShieldAlert, Key, UserCheck, UserX, RefreshCw } from 'lucide-react';
import { CommitVerificationResult } from '../types';
import { api } from '../services/api';

interface CommitVerifierPageProps {
  initialCommit?: CommitVerificationResult | null;
}

export const CommitVerifierPage: React.FC<CommitVerifierPageProps> = ({ initialCommit }) => {
  const [commitData, setCommitData] = useState<CommitVerificationResult | null>(initialCommit || null);
  const [loading, setLoading] = useState(false);

  const fetchCommit = async () => {
    setLoading(true);
    try {
      const data = await api.getCommitStatus();
      setCommitData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!commitData) {
      fetchCommit();
    }
  }, []);

  const isPass = commitData?.status === 'PASS';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">Commit Signature Verification</h2>
          <p className="text-xs text-slate-400">
            Cryptographically verify latest Git commit signatures (SSH & GPG) against trusted developers
          </p>
        </div>
        <button
          onClick={fetchCommit}
          disabled={loading}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Re-verify Commit</span>
        </button>
      </div>

      {commitData ? (
        <>
          {/* Status Banner */}
          <div
            className={`p-5 rounded-xl border flex items-start gap-4 ${
              isPass
                ? 'bg-emerald-950/20 border-emerald-500/40 text-emerald-300'
                : 'bg-red-950/20 border-red-500/40 text-red-300'
            }`}
          >
            <div className={`p-2 rounded-lg ${isPass ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
              {isPass ? <ShieldCheck className="w-6 h-6" /> : <ShieldAlert className="w-6 h-6" />}
            </div>
            <div>
              <div className="text-xs font-mono font-bold uppercase tracking-wider">
                Verification Verdict: {commitData.status}
              </div>
              <div className="text-sm font-semibold mt-0.5 text-white">
                {commitData.details}
              </div>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {/* Commit Metadata Card */}
            <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center gap-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
                <GitCommit className="w-4 h-4" />
                Commit Metadata
              </div>

              <div className="space-y-2.5 text-xs">
                <div>
                  <div className="text-slate-500 font-mono text-[10px]">COMMIT HASH</div>
                  <div className="font-mono text-slate-200 break-all select-all font-semibold">
                    {commitData.commit_hash}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <div className="text-slate-500 font-mono text-[10px]">AUTHOR</div>
                    <div className="text-slate-200 font-medium">
                      {commitData.author_name || 'N/A'} &lt;{commitData.author_email || 'N/A'}&gt;
                    </div>
                  </div>
                  <div>
                    <div className="text-slate-500 font-mono text-[10px]">COMMIT DATE</div>
                    <div className="text-slate-200">{commitData.commit_date || 'N/A'}</div>
                  </div>
                </div>

                <div>
                  <div className="text-slate-500 font-mono text-[10px]">MESSAGE</div>
                  <div className="p-2.5 bg-slate-900 rounded-lg text-slate-300 font-mono text-xs border border-slate-800">
                    {commitData.commit_message || 'No commit message'}
                  </div>
                </div>
              </div>
            </div>

            {/* Cryptographic Signature Card */}
            <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center gap-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
                <Key className="w-4 h-4" />
                Cryptographic Signature
              </div>

              <div className="space-y-3 text-xs">
                <div className="flex items-center justify-between p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                  <span className="text-slate-400">Signature Presence:</span>
                  <span
                    className={`font-mono font-bold ${
                      commitData.signed ? 'text-emerald-400' : 'text-red-400'
                    }`}
                  >
                    {commitData.signed ? `YES (${commitData.signature_type})` : 'UNSIGNED'}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                  <span className="text-slate-400">Cryptographic Integrity:</span>
                  <span
                    className={`font-mono font-bold ${
                      commitData.signature_valid ? 'text-emerald-400' : 'text-red-400'
                    }`}
                  >
                    {commitData.signature_valid ? 'VALID & VERIFIED' : 'INVALID / FORGED'}
                  </span>
                </div>

                <div className="flex items-center justify-between p-2.5 bg-slate-900 rounded-lg border border-slate-800">
                  <span className="text-slate-400">Developer Whitelist Match:</span>
                  <span
                    className={`font-mono font-bold flex items-center gap-1 ${
                      commitData.trusted_developer ? 'text-emerald-400' : 'text-red-400'
                    }`}
                  >
                    {commitData.trusted_developer ? (
                      <>
                        <UserCheck className="w-3.5 h-3.5" />
                        TRUSTED
                      </>
                    ) : (
                      <>
                        <UserX className="w-3.5 h-3.5" />
                        UNAUTHORIZED
                      </>
                    )}
                  </span>
                </div>

                <div>
                  <div className="text-slate-500 font-mono text-[10px]">SIGNER IDENTITY / KEY</div>
                  <div className="p-2 bg-slate-900 rounded font-mono text-[11px] text-slate-300 break-all border border-slate-800">
                    {commitData.signer_identity || commitData.signer_key_id || 'None detected'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="p-8 text-center text-slate-500 bg-[#0F1629] border border-slate-800 rounded-xl">
          Loading commit signature data...
        </div>
      )}
    </div>
  );
};

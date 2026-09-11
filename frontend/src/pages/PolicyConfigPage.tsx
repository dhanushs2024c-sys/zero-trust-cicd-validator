import React, { useState, useEffect } from 'react';
import { Sliders, Users, ShieldCheck, Lock, CheckCircle2, RefreshCw } from 'lucide-react';
import { TrustedDeveloper } from '../types';
import { api } from '../services/api';

export const PolicyConfigPage: React.FC = () => {
  const [config, setConfig] = useState<{ policy: any; trusted_developers: TrustedDeveloper[] } | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const data = await api.getConfig();
      setConfig(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  const policy = config?.policy || {};
  const developers = config?.trusted_developers || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-white tracking-wide">Security Policy & Trust Configuration</h2>
          <p className="text-xs text-slate-400">
            Declarative rules in configs/policy.yaml and developer whitelist in configs/trusted_developers.yaml
          </p>
        </div>
        <button
          onClick={fetchConfig}
          disabled={loading}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Reload Config</span>
        </button>
      </div>

      {/* Policy Rules Grid */}
      <div className="bg-[#0F1629] border border-slate-800 rounded-xl p-5 space-y-4 shadow-lg">
        <div className="flex items-center gap-2 text-xs font-mono font-bold text-cyan-400 uppercase tracking-wider">
          <Sliders className="w-4 h-4" />
          Active Policy Rules (configs/policy.yaml)
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 text-xs">
          {[
            {
              rule: 'fail_closed',
              label: 'Fail-Closed Enforcement',
              value: policy.fail_closed,
              desc: 'Any error or missing check automatically BLOCKS the build.'
            },
            {
              rule: 'require_signed_commit',
              label: 'Mandatory Signed Commit',
              value: policy.require_signed_commit,
              desc: 'Unsigned commits are rejected without exception.'
            },
            {
              rule: 'require_trusted_developer',
              label: 'Author Whitelist Verification',
              value: policy.require_trusted_developer,
              desc: 'Signing key must be registered in trusted_developers.yaml.'
            },
            {
              rule: 'block_unverified_dependencies',
              label: 'Block Unpinned Dependencies',
              value: policy.block_unverified_dependencies,
              desc: 'Dependencies without locked cryptographic hashes are blocked.'
            },
            {
              rule: 'block_dependency_mismatch',
              label: 'Block Hash Mismatch',
              value: policy.block_dependency_mismatch,
              desc: 'Any lockfile tamper or substitution blocks the pipeline.'
            },
            {
              rule: 'require_runner_integrity',
              label: 'Enforce Runner Integrity',
              value: policy.require_runner_integrity,
              desc: `Runner status must meet ${policy.runner_severity_threshold || 'WARNING'} threshold.`
            }
          ].map((item) => (
            <div
              key={item.rule}
              className="p-3.5 rounded-lg bg-slate-900 border border-slate-800 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-white font-sans">{item.label}</span>
                  <span
                    className={`font-mono text-[10px] font-bold px-2 py-0.5 rounded ${
                      item.value
                        ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {item.value ? 'ENFORCED' : 'OFF'}
                  </span>
                </div>
                <div className="text-[11px] text-slate-400 leading-relaxed font-sans">
                  {item.desc}
                </div>
              </div>
              <div className="mt-2 text-[10px] font-mono text-cyan-400">
                policy.{item.rule} = {String(item.value)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trusted Developers Whitelist Table */}
      <div className="bg-[#0F1629] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="p-4 border-b border-slate-800 flex items-center justify-between">
          <div className="font-bold text-white text-xs font-mono tracking-wider uppercase flex items-center gap-2">
            <Users className="w-4 h-4 text-cyan-400" />
            Trusted Developers Whitelist ({developers.length} registered)
          </div>
          <div className="text-xs text-slate-400 font-mono">
            configs/trusted_developers.yaml
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0A0F1D] border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="p-3.5">Developer Name</th>
                <th className="p-3.5">Email Identity</th>
                <th className="p-3.5">Key Type</th>
                <th className="p-3.5">Role</th>
                <th className="p-3.5">Key ID / Public Key Fingerprint</th>
                <th className="p-3.5 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80 font-mono">
              {developers.map((dev, idx) => (
                <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                  <td className="p-3.5 font-bold text-white font-sans">{dev.name}</td>
                  <td className="p-3.5 text-slate-300">{dev.email}</td>
                  <td className="p-3.5">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-cyan-400 uppercase font-bold text-[10px]">
                      {dev.type}
                    </span>
                  </td>
                  <td className="p-3.5 text-slate-400 font-sans">{dev.role || 'Developer'}</td>
                  <td className="p-3.5 text-slate-400 text-[10px] max-w-xs truncate">
                    <span title={dev.key_id}>{dev.fingerprint || dev.key_id}</span>
                  </td>
                  <td className="p-3.5 text-right">
                    <span
                      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                        dev.enabled
                          ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {dev.enabled ? 'ACTIVE' : 'REVOKED'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

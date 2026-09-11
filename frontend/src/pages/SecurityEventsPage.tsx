import React, { useState, useEffect } from 'react';
import { ShieldAlert, Shield, Search, RefreshCw, Eye, Lock, Filter } from 'lucide-react';
import { SecurityEvent } from '../types';
import { api } from '../services/api';

interface SecurityEventsPageProps {
  initialEvents?: SecurityEvent[];
}

export const SecurityEventsPage: React.FC<SecurityEventsPageProps> = ({ initialEvents }) => {
  const [events, setEvents] = useState<SecurityEvent[]>(initialEvents || []);
  const [loading, setLoading] = useState(false);
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [search, setSearch] = useState('');
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await api.getEvents(100, severityFilter === 'ALL' ? undefined : severityFilter);
      setEvents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [severityFilter]);

  const filteredEvents = events.filter((e) => {
    if (search) {
      const q = search.toLowerCase();
      return (
        e.event.toLowerCase().includes(q) ||
        e.message.toLowerCase().includes(q) ||
        (e.run_id && e.run_id.toLowerCase().includes(q))
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-bold text-white tracking-wide">Append-Only Security Audit Trail</h2>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 text-[10px] font-mono font-bold">
              <Lock className="w-3 h-3" /> IMMUTABLE
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Cryptographic and policy audit events written to append-only database & JSONL ledger
          </p>
        </div>

        <button
          onClick={fetchEvents}
          disabled={loading}
          className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit Logs</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            placeholder="Search event, message, run ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 pr-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-full font-mono"
          />
        </div>

        <div className="flex flex-wrap bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-xs">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'INFO'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-3 py-1 rounded-md font-mono text-[11px] font-semibold transition-colors ${
                severityFilter === sev
                  ? sev === 'CRITICAL'
                    ? 'bg-red-500/20 text-red-400'
                    : sev === 'HIGH'
                    ? 'bg-orange-500/20 text-orange-400'
                    : sev === 'MEDIUM'
                    ? 'bg-amber-500/20 text-amber-400'
                    : 'bg-cyan-500/20 text-cyan-300'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-[#0F1629] border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0A0F1D] border-b border-slate-800 text-slate-400 font-mono uppercase text-[10px]">
              <tr>
                <th className="p-3.5">Timestamp</th>
                <th className="p-3.5">Severity</th>
                <th className="p-3.5">Category</th>
                <th className="p-3.5">Event Name</th>
                <th className="p-3.5">Message</th>
                <th className="p-3.5">Pipeline Action</th>
                <th className="p-3.5 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredEvents.map((evt, idx) => {
                const isCrit = evt.severity === 'CRITICAL';
                const isHigh = evt.severity === 'HIGH';
                const isMed = evt.severity === 'MEDIUM';

                return (
                  <tr key={evt.id || idx} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3.5 text-slate-400 font-mono text-[11px] whitespace-nowrap">
                      {new Date(evt.timestamp).toLocaleString()}
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`px-2 py-0.5 rounded font-mono font-bold text-[10px] ${
                          isCrit
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                            : isHigh
                            ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                            : isMed
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                        }`}
                      >
                        {evt.severity}
                      </span>
                    </td>
                    <td className="p-3.5">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px] uppercase font-bold">
                        {evt.category}
                      </span>
                    </td>
                    <td className="p-3.5 font-mono font-bold text-white text-[11px]">
                      {evt.event}
                    </td>
                    <td className="p-3.5 text-slate-300 max-w-md line-clamp-1 font-sans">
                      {evt.message}
                    </td>
                    <td className="p-3.5">
                      <span
                        className={`font-mono text-[10px] font-bold ${
                          evt.action === 'BUILD_ALLOWED'
                            ? 'text-emerald-400'
                            : evt.action === 'BUILD_BLOCKED'
                            ? 'text-red-400'
                            : 'text-slate-400'
                        }`}
                      >
                        {evt.action}
                      </span>
                    </td>
                    <td className="p-3.5 text-right">
                      <button
                        onClick={() => setSelectedEvent(evt)}
                        className="px-2 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded text-xs transition-colors inline-flex items-center gap-1"
                      >
                        <Eye className="w-3 h-3" />
                        JSON
                      </button>
                    </td>
                  </tr>
                );
              })}
              {filteredEvents.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-slate-500 font-sans">
                    No security events found matching the criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* JSON Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F1629] border border-slate-700 rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col shadow-2xl">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between bg-[#0B101E]">
              <div className="font-mono text-sm font-bold text-white flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-cyan-400" />
                <span>Audit Event Record ({selectedEvent.event})</span>
              </div>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-slate-400 hover:text-white text-xs px-2 py-1 bg-slate-800 rounded"
              >
                Close
              </button>
            </div>
            <div className="p-4 overflow-y-auto">
              <pre className="bg-[#080C16] p-4 rounded-xl text-cyan-300 font-mono text-xs overflow-x-auto border border-slate-800">
                {JSON.stringify(selectedEvent, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

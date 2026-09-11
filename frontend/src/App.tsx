import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { VisualPipeline } from './components/VisualPipeline';
import { ValidationRunsPage } from './pages/ValidationRunsPage';
import { CommitVerifierPage } from './pages/CommitVerifierPage';
import { DependencyInspectorPage } from './pages/DependencyInspectorPage';
import { RunnerIntegrityPage } from './pages/RunnerIntegrityPage';
import { SecurityEventsPage } from './pages/SecurityEventsPage';
import { PolicyConfigPage } from './pages/PolicyConfigPage';
import { DemoLabPage } from './pages/DemoLabPage';
import { ValidationRun, SecurityEvent } from './types';
import { api } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [latestRun, setLatestRun] = useState<ValidationRun | null>(null);
  const [recentRuns, setRecentRuns] = useState<ValidationRun[]>([]);
  const [recentEvents, setRecentEvents] = useState<SecurityEvent[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState<boolean>(false);

  const loadData = async () => {
    try {
      const [runsData, eventsData] = await Promise.all([
        api.getRuns(50),
        api.getEvents(50)
      ]);
      setRecentRuns(runsData);
      if (runsData.length > 0) {
        // Fetch detailed data for the latest run
        const latestDetail = await api.getRun(runsData[0].run_id);
        setLatestRun(latestDetail);
      }
      setRecentEvents(eventsData);
    } catch (e) {
      console.error('Error loading initial data:', e);
    }
  };

  const handleValidate = async () => {
    setIsValidating(true);
    try {
      const result = await api.validate();
      setLatestRun(result);
      await loadData();
    } catch (e) {
      console.error('Validation error:', e);
    } finally {
      setIsValidating(false);
    }
  };

  const handleRunDemo = async (type: 'legit' | 'dep' | 'commit' | 'runner') => {
    setIsValidating(true);
    try {
      let res: ValidationRun;
      if (type === 'legit') res = await api.demoLegitimate();
      else if (type === 'dep') res = await api.demoDependencyAttack();
      else if (type === 'commit') res = await api.demoInvalidCommit();
      else res = await api.demoRunnerTampering();

      setLatestRun(res);
      await loadData();
    } catch (e) {
      console.error('Demo error:', e);
    } finally {
      setIsValidating(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const tabTitles: Record<string, { title: string; subtitle: string }> = {
    dashboard: {
      title: 'Executive Security Dashboard',
      subtitle: 'Zero-Trust pre-build gate verification and telemetry'
    },
    pipeline: {
      title: 'Visual Execution Pipeline',
      subtitle: 'Sequential verification graph and stage gates'
    },
    runs: {
      title: 'Validation Runs Audit',
      subtitle: 'Historical execution logs and decision rationales'
    },
    commit: {
      title: 'Commit Signature Verifier',
      subtitle: 'Cryptographic Git commit validation (SSH / GPG)'
    },
    dependencies: {
      title: 'Dependency Integrity Inspector',
      subtitle: 'Package lockfile hash verification (Python & Node.js)'
    },
    runner: {
      title: 'Runner Host Integrity',
      subtitle: 'Baseline hashing, environment variables, and process telemetry'
    },
    events: {
      title: 'Security Events Log',
      subtitle: 'Append-only structured security audit ledger'
    },
    config: {
      title: 'Policy & Whitelist Management',
      subtitle: 'Declarative policy rules and trusted developer configuration'
    },
    demo: {
      title: 'Attack Simulation Lab',
      subtitle: 'Harmless, local demonstration of 4 supply-chain attack scenarios'
    }
  };

  const currentHeader = tabTitles[activeTab] || tabTitles.dashboard;

  return (
    <div className="flex min-h-screen bg-[#080B11]">
      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          title={currentHeader.title}
          subtitle={currentHeader.subtitle}
          onValidate={handleValidate}
          onRefresh={loadData}
          isValidating={isValidating}
        />

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {activeTab === 'dashboard' && (
            <DashboardPage
              latestRun={latestRun}
              recentRuns={recentRuns}
              recentEvents={recentEvents}
              onSelectRun={(id) => {
                setSelectedRunId(id);
                setActiveTab('runs');
              }}
              onNavigateTab={setActiveTab}
              onRunDemo={handleRunDemo}
            />
          )}

          {activeTab === 'pipeline' && (
            <div className="space-y-6">
              <VisualPipeline currentRun={latestRun} />
              {latestRun && (
                <div className="p-5 bg-[#0F1629] border border-slate-800 rounded-xl space-y-3 text-xs">
                  <div className="font-bold text-white uppercase font-mono tracking-wider">
                    Current Execution Decision Rationale
                  </div>
                  <ul className="space-y-1.5 font-medium">
                    {latestRun.policy?.reasons?.map((r, i) => (
                      <li
                        key={i}
                        className={`flex items-start gap-2 ${
                          latestRun.final_decision === 'ALLOW' ? 'text-emerald-300' : 'text-red-300'
                        }`}
                      >
                        <span className="font-bold">{latestRun.final_decision === 'ALLOW' ? '✓' : '✗'}</span>
                        <span>{r}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {activeTab === 'runs' && (
            <ValidationRunsPage
              runs={recentRuns}
              selectedRunId={selectedRunId}
              onSelectRun={setSelectedRunId}
            />
          )}

          {activeTab === 'commit' && (
            <CommitVerifierPage initialCommit={latestRun?.commit} />
          )}

          {activeTab === 'dependencies' && (
            <DependencyInspectorPage initialResult={latestRun?.dependencies} />
          )}

          {activeTab === 'runner' && (
            <RunnerIntegrityPage initialRunner={latestRun?.runner} />
          )}

          {activeTab === 'events' && (
            <SecurityEventsPage initialEvents={recentEvents} />
          )}

          {activeTab === 'config' && (
            <PolicyConfigPage />
          )}

          {activeTab === 'demo' && (
            <DemoLabPage onRunFinished={(r) => {
              setLatestRun(r);
              loadData();
            }} />
          )}
        </main>
      </div>
    </div>
  );
};

import {
  ValidationRun,
  SecurityEvent,
  SystemStatus,
  DependencyVerificationResult,
  CommitVerificationResult,
  RunnerIntegrityResult,
  TrustedDeveloper
} from '../types';

const API_BASE = '/api';

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  async getStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/status`);
    return res.json();
  },

  async getRuns(limit = 50): Promise<ValidationRun[]> {
    const res = await fetch(`${API_BASE}/runs?limit=${limit}`);
    return res.json();
  },

  async getRun(runId: string): Promise<any> {
    const res = await fetch(`${API_BASE}/runs/${runId}`);
    if (!res.ok) throw new Error('Run not found');
    return res.json();
  },

  async getEvents(limit = 100, severity?: string, category?: string): Promise<SecurityEvent[]> {
    const params = new URLSearchParams({ limit: limit.toString() });
    if (severity) params.append('severity', severity);
    if (category) params.append('category', category);
    const res = await fetch(`${API_BASE}/events?${params.toString()}`);
    return res.json();
  },

  async validate(targetDirectory?: string, commitRef = 'HEAD'): Promise<ValidationRun> {
    const res = await fetch(`${API_BASE}/validate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ target_directory: targetDirectory, commit_ref: commitRef })
    });
    return res.json();
  },

  async generateBaseline(): Promise<any> {
    const res = await fetch(`${API_BASE}/baseline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    return res.json();
  },

  async getDependencies(): Promise<DependencyVerificationResult> {
    const res = await fetch(`${API_BASE}/dependencies`);
    return res.json();
  },

  async getCommitStatus(): Promise<CommitVerificationResult> {
    const res = await fetch(`${API_BASE}/commits`);
    return res.json();
  },

  async getRunnerStatus(): Promise<RunnerIntegrityResult> {
    const res = await fetch(`${API_BASE}/runner`);
    return res.json();
  },

  async getConfig(): Promise<{ policy: any; trusted_developers: TrustedDeveloper[] }> {
    const res = await fetch(`${API_BASE}/config`);
    return res.json();
  },

  // Demo actions
  async demoLegitimate(): Promise<ValidationRun> {
    const res = await fetch(`${API_BASE}/demo/run-legitimate`, { method: 'POST' });
    return res.json();
  },

  async demoDependencyAttack(): Promise<ValidationRun> {
    const res = await fetch(`${API_BASE}/demo/simulate-dependency-attack`, { method: 'POST' });
    return res.json();
  },

  async demoInvalidCommit(): Promise<ValidationRun> {
    const res = await fetch(`${API_BASE}/demo/simulate-invalid-commit`, { method: 'POST' });
    return res.json();
  },

  async demoRunnerTampering(): Promise<ValidationRun> {
    const res = await fetch(`${API_BASE}/demo/simulate-runner-tampering`, { method: 'POST' });
    return res.json();
  },

  async demoReset(): Promise<any> {
    const res = await fetch(`${API_BASE}/demo/reset`, { method: 'POST' });
    return res.json();
  }
};

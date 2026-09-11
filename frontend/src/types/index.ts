export interface CommitVerificationResult {
  commit_hash: string;
  short_hash: string;
  author_name: string;
  author_email: string;
  committer_name: string;
  committer_email: string;
  commit_date: string;
  commit_message: string;
  signed: boolean;
  signature_type: 'GPG' | 'SSH' | 'NONE';
  signature_valid: boolean;
  trusted_developer: boolean;
  signer_identity?: string | null;
  signer_key_id?: string | null;
  status: 'PASS' | 'FAIL' | 'WARNING';
  details: string;
}

export interface DependencyItem {
  name: string;
  version?: string | null;
  ecosystem: 'python' | 'npm';
  manifest_file: string;
  expected_hash?: string | null;
  actual_hash?: string | null;
  algorithm?: string | null;
  verification_method: string;
  status: 'VERIFIED' | 'UNVERIFIED' | 'MISMATCH' | 'MISSING' | 'ERROR';
  details?: string | null;
}

export interface DependencyVerificationResult {
  status: 'PASS' | 'FAIL' | 'WARNING';
  total_dependencies: number;
  verified_count: number;
  unverified_count: number;
  mismatched_count: number;
  missing_count: number;
  ecosystems_detected: string[];
  items: DependencyItem[];
  details: string;
}

export interface RunnerFileCheck {
  path: string;
  expected_hash?: string | null;
  actual_hash?: string | null;
  status: 'MATCH' | 'MODIFIED' | 'DELETED' | 'NEW';
}

export interface RunnerEnvCheck {
  variable: string;
  value: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  reason: string;
}

export interface RunnerProcessCheck {
  pid: number;
  name: string;
  cmdline: string;
  status: 'SUSPICIOUS' | 'NORMAL';
  reason?: string | null;
}

export interface RunnerIntegrityResult {
  status: 'CLEAN' | 'WARNING' | 'TAMPERED';
  integrity_score: number;
  baseline_file_used?: string | null;
  monitored_files_count: number;
  matched_files_count: number;
  tampered_files_count: number;
  missing_files_count: number;
  suspicious_env_vars_count: number;
  suspicious_processes_count: number;
  file_checks: RunnerFileCheck[];
  env_checks: RunnerEnvCheck[];
  process_checks: RunnerProcessCheck[];
  disclaimer: string;
  details: string;
}

export interface PolicyDecision {
  decision: 'ALLOW' | 'BLOCK' | 'WARNING';
  score: number;
  reasons: string[];
  rules_evaluated: Record<string, boolean>;
}

export interface ValidationRun {
  run_id: string;
  id?: string;
  timestamp: string;
  target_directory: string;
  commit?: CommitVerificationResult;
  dependencies?: DependencyVerificationResult;
  runner?: RunnerIntegrityResult;
  policy?: PolicyDecision;
  commit_hash?: string;
  commit_status?: string;
  dependency_status?: string;
  runner_status?: string;
  score?: number;
  final_decision: 'ALLOW' | 'BLOCK';
  exit_code: number;
  execution_time_ms: number;
}

export interface SecurityEvent {
  id?: string;
  event_id?: string;
  run_id?: string;
  timestamp: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  category: 'COMMIT' | 'DEPENDENCY' | 'RUNNER' | 'POLICY' | 'SYSTEM';
  event: string;
  source: string;
  message: string;
  details?: any;
  action: 'BUILD_ALLOWED' | 'BUILD_BLOCKED' | 'MONITOR_LOGGED';
}

export interface SystemStatus {
  status: string;
  policy: {
    require_signed_commit: boolean;
    require_trusted_developer: boolean;
    allowed_signature_types: string[];
    require_dependency_integrity: boolean;
    block_unverified_dependencies: boolean;
    block_dependency_mismatch: boolean;
    require_runner_integrity: boolean;
    runner_severity_threshold: string;
    fail_closed: boolean;
  };
  trusted_developers_count: number;
  baseline_configured: boolean;
  database_connected: boolean;
}

export interface TrustedDeveloper {
  name: string;
  email: string;
  key_id: string;
  fingerprint?: string;
  type: string;
  role?: string;
  enabled: boolean;
}

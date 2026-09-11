"""
Zero-Trust CI/CD Pipeline Validator CLI
Command-line security enforcement tool that runs before build execution.
Exits with code 0 (BUILD ALLOWED) or 1 (BUILD BLOCKED) to halt pipelines on failure.
"""

import sys
import os
import argparse
from pathlib import Path

# Add project root to sys.path so validator can be executed from anywhere
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from backend.app.config import (
    load_policy,
    load_trusted_developers,
    DEFAULT_POLICY_PATH,
    DEFAULT_TRUSTED_DEVS_PATH,
    DEFAULT_BASELINE_PATH
)
from backend.app.services.validator import PipelineValidator
from backend.app.services.commit_verifier import CommitVerifier
from backend.app.services.dependency_verifier import DependencyVerifier
from backend.app.services.runner_integrity import RunnerIntegrityVerifier


BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║          ZERO-TRUST CI/CD PIPELINE VALIDATOR                  ║
║      Cryptographic Verification & Tamper-Proofing             ║
╚═══════════════════════════════════════════════════════════════╝
"""


def format_status(status: str) -> str:
    if status in ("PASS", "CLEAN", "ALLOW"):
        return f"[ \033[92m{status}\033[0m ]"
    elif status == "WARNING":
        return f"[ \033[93m{status}\033[0m ]"
    else:
        return f"[ \033[91m{status}\033[0m ]"


def cmd_validate(args):
    """Execute complete 3-stage validation and enforce policy."""
    try:
        project_path = Path(args.path).resolve() if args.path else PROJECT_ROOT
        policy_path = Path(args.policy).resolve() if args.policy else DEFAULT_POLICY_PATH
        devs_path = Path(args.trusted_devs).resolve() if args.trusted_devs else DEFAULT_TRUSTED_DEVS_PATH
        baseline_path = Path(args.baseline).resolve() if args.baseline else DEFAULT_BASELINE_PATH

        if not policy_path.exists():
            print(f"Configuration Error: Policy file not found at '{policy_path}'", file=sys.stderr)
            sys.exit(2)

        print(BANNER)
        print(f"Target Directory : {project_path}")
        print(f"Policy Source    : {policy_path}")
        print(f"Commit Ref       : {args.commit}\n")

        validator = PipelineValidator(
            project_root=project_path,
            policy_path=policy_path,
            trusted_devs_path=devs_path,
            baseline_path=baseline_path
        )

        res = validator.validate(commit_ref=args.commit)

        # 1. Commit Verification Output
        print("[1/3] Commit Verification")
        c = res.commit
        if c.signed:
            print(f"      ✓ Signed with {c.signature_type}")
        else:
            print(f"      ✗ Unsigned commit")

        if c.signature_valid:
            print(f"      ✓ Cryptographic signature valid")
        elif c.signed:
            print(f"      ✗ Cryptographic signature INVALID")

        if c.trusted_developer:
            print(f"      ✓ Trusted developer: {c.author_email}")
        else:
            print(f"      ✗ Developer '{c.author_email}' not in trusted developers list")

        print(f"      Status: {format_status(c.status)}\n")

        # 2. Dependency Verification Output
        print("[2/3] Dependency Verification")
        d = res.dependencies
        print(f"      Total dependencies scanned : {d.total_dependencies}")
        print(f"      Cryptographically verified : {d.verified_count}")
        if d.unverified_count > 0:
            print(f"      ⚠ Unverified dependencies  : {d.unverified_count}")
        if d.mismatched_count > 0:
            print(f"      ✗ Hash mismatches          : {d.mismatched_count}")
        if d.missing_count > 0:
            print(f"      ✗ Missing lockfiles        : {d.missing_count}")
        print(f"      Status: {format_status(d.status)}\n")

        # 3. Runner Integrity Output
        print("[3/3] Runner Integrity")
        r = res.runner
        print(f"      Baseline files checked     : {r.monitored_files_count}")
        print(f"      Matching baseline hashes   : {r.matched_files_count}")
        if r.tampered_files_count > 0:
            print(f"      ✗ Tampered baseline files  : {r.tampered_files_count}")
        if r.missing_files_count > 0:
            print(f"      ✗ Missing baseline files   : {r.missing_files_count}")
        if r.suspicious_env_vars_count > 0:
            print(f"      ⚠ Suspicious env variables : {r.suspicious_env_vars_count}")
        if r.suspicious_processes_count > 0:
            print(f"      ⚠ Suspicious processes     : {r.suspicious_processes_count}")
        print(f"      Integrity Score            : {r.integrity_score}/100")
        print(f"      Status: {format_status(r.status)}\n")

        # Final Decision
        print("=" * 63)
        if res.final_decision == "ALLOW":
            print(f"\033[92mFINAL DECISION: BUILD ALLOWED (Score: {res.policy.score}/100)\033[0m")
            print("=" * 63)
            print("Reason:")
            for reason in res.policy.reasons:
                print(f"  ✓ {reason}")
            print(f"\nAudit Run ID: {res.run_id}")
            sys.exit(0)
        else:
            print(f"\033[91mFINAL DECISION: BUILD BLOCKED (Score: {res.policy.score}/100)\033[0m")
            print("=" * 63)
            print("Reason(s):")
            for reason in res.policy.reasons:
                print(f"  ✗ {reason}")
            print(f"\nAudit Run ID: {res.run_id}")
            sys.exit(1)

    except SystemExit:
        raise
    except FileNotFoundError as fnf:
        print(f"Configuration Error: {fnf}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Internal Validator Error: {e}", file=sys.stderr)
        sys.exit(3)


def cmd_verify_commit(args):
    """Verify Git commit signature."""
    try:
        project_path = Path(args.path).resolve() if args.path else PROJECT_ROOT
        devs_path = Path(args.trusted_devs).resolve() if args.trusted_devs else DEFAULT_TRUSTED_DEVS_PATH
        verifier = CommitVerifier(repo_path=project_path, trusted_devs_path=devs_path)
        c = verifier.verify_commit(commit_ref=args.commit)

        print(BANNER)
        print("--- COMMIT VERIFICATION ---")
        print(f"Commit Hash       : {c.commit_hash}")
        print(f"Author            : {c.author_name} <{c.author_email}>")
        print(f"Signed            : {c.signed}")
        print(f"Signature Type    : {c.signature_type}")
        print(f"Signature Valid   : {c.signature_valid}")
        print(f"Trusted Developer : {c.trusted_developer}")
        print(f"Status            : {format_status(c.status)}")
        print(f"Details           : {c.details}")

        sys.exit(0 if c.status == "PASS" else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


def cmd_verify_dependencies(args):
    """Verify dependencies across lockfiles."""
    try:
        project_path = Path(args.path).resolve() if args.path else PROJECT_ROOT
        verifier = DependencyVerifier(project_path=project_path)
        d = verifier.verify_dependencies(block_unverified=not args.allow_unverified)

        print(BANNER)
        print("--- DEPENDENCY INTEGRITY VERIFICATION ---")
        print(f"Total Scanned : {d.total_dependencies}")
        print(f"Verified      : {d.verified_count}")
        print(f"Unverified    : {d.unverified_count}")
        print(f"Mismatched    : {d.mismatched_count}")
        print(f"Status        : {format_status(d.status)}")
        print(f"Details       : {d.details}")

        sys.exit(0 if d.status == "PASS" else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


def cmd_verify_runner(args):
    """Verify runner environment integrity against baseline."""
    try:
        project_path = Path(args.path).resolve() if args.path else PROJECT_ROOT
        baseline_path = Path(args.baseline).resolve() if args.baseline else DEFAULT_BASELINE_PATH
        verifier = RunnerIntegrityVerifier(project_root=project_path, baseline_path=baseline_path)
        r = verifier.verify_runner()

        print(BANNER)
        print("--- RUNNER INTEGRITY VERIFICATION ---")
        print(f"Baseline File     : {r.baseline_file_used}")
        print(f"Monitored Files   : {r.monitored_files_count}")
        print(f"Matched Hashes    : {r.matched_files_count}")
        print(f"Tampered Files    : {r.tampered_files_count}")
        print(f"Missing Files     : {r.missing_files_count}")
        print(f"Suspicious Env    : {r.suspicious_env_vars_count}")
        print(f"Integrity Score   : {r.integrity_score}/100")
        print(f"Status            : {format_status(r.status)}")
        print(f"Details           : {r.details}")
        print(f"\nDisclaimer: {r.disclaimer}")

        sys.exit(0 if r.status == "CLEAN" else 1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


def cmd_baseline(args):
    """Generate runner integrity baseline hashes."""
    try:
        project_path = Path(args.path).resolve() if args.path else PROJECT_ROOT
        output_path = Path(args.output).resolve() if args.output else DEFAULT_BASELINE_PATH
        verifier = RunnerIntegrityVerifier(project_root=project_path, baseline_path=output_path)
        data = verifier.create_baseline(output_path=output_path)

        print(BANNER)
        print("--- GENERATED RUNNER INTEGRITY BASELINE ---")
        print(f"Saved To     : {output_path}")
        print(f"Files Hashed : {len(data.get('files', {}))}")
        for rel_path, h in data.get("files", {}).items():
            print(f"  • {rel_path} -> {h[:16]}...")
        print("\nBaseline generated successfully.")
        sys.exit(0)
    except Exception as e:
        print(f"Error generating baseline: {e}", file=sys.stderr)
        sys.exit(3)


def cmd_status(args):
    """Display current validator configuration and status."""
    try:
        policy = load_policy()
        devs = load_trusted_developers()
        print(BANNER)
        print("--- CURRENT POLICY & TRUST STATUS ---")
        print(f"Fail Closed                   : {policy.fail_closed}")
        print(f"Require Signed Commit         : {policy.require_signed_commit}")
        print(f"Require Trusted Developer     : {policy.require_trusted_developer}")
        print(f"Block Unverified Dependencies : {policy.block_unverified_dependencies}")
        print(f"Block Dependency Mismatch     : {policy.block_dependency_mismatch}")
        print(f"Require Runner Integrity      : {policy.require_runner_integrity}")
        print(f"Runner Severity Threshold     : {policy.runner_severity_threshold}")
        print(f"\nTrusted Developers ({len(devs)} registered):")
        for d in devs:
            status_tag = "ENABLED" if d.enabled else "DISABLED"
            print(f"  • {d.name} <{d.email}> [{d.type.upper()}] - {status_tag}")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        prog="zt-validator",
        description="Zero-Trust CI/CD Pipeline Validator: Cryptographic Verification and Tamper-Proofing"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # validate
    p_val = subparsers.add_parser("validate", help="Execute complete 3-stage validation pipeline")
    p_val.add_argument("--path", "-p", help="Target project/repo directory path")
    p_val.add_argument("--commit", "-c", default="HEAD", help="Git commit ref to verify (default: HEAD)")
    p_val.add_argument("--policy", help="Path to policy.yaml")
    p_val.add_argument("--trusted-devs", help="Path to trusted_developers.yaml")
    p_val.add_argument("--baseline", help="Path to integrity_baseline.json")
    p_val.set_defaults(func=cmd_validate)

    # verify-commit
    p_com = subparsers.add_parser("verify-commit", help="Verify latest or specified Git commit signature")
    p_com.add_argument("--path", "-p", help="Git repository directory path")
    p_com.add_argument("--commit", "-c", default="HEAD", help="Commit ref to verify (default: HEAD)")
    p_com.add_argument("--trusted-devs", help="Path to trusted_developers.yaml")
    p_com.set_defaults(func=cmd_verify_commit)

    # verify-dependencies
    p_dep = subparsers.add_parser("verify-dependencies", help="Verify project dependency lockfiles and hashes")
    p_dep.add_argument("--path", "-p", help="Target project directory path")
    p_dep.add_argument("--allow-unverified", action="store_true", help="Do not block unverified dependencies")
    p_dep.set_defaults(func=cmd_verify_dependencies)

    # verify-runner
    p_run = subparsers.add_parser("verify-runner", help="Verify runner environment integrity against baseline")
    p_run.add_argument("--path", "-p", help="Project directory path")
    p_run.add_argument("--baseline", help="Path to integrity_baseline.json")
    p_run.set_defaults(func=cmd_verify_runner)

    # baseline
    p_base = subparsers.add_parser("baseline", help="Generate or update cryptographic runner baseline")
    p_base.add_argument("--path", "-p", help="Project root directory path")
    p_base.add_argument("--output", "-o", help="Output path for baseline JSON file")
    p_base.set_defaults(func=cmd_baseline)

    # status
    p_stat = subparsers.add_parser("status", help="Print active policy and trusted developer configuration")
    p_stat.set_defaults(func=cmd_status)

    args = parser.parse_args()

    if not args.command:
        # Default action: run validate
        parser.print_help()
        sys.exit(0)

    if hasattr(args, "func"):
        args.func(args)


if __name__ == "__main__":
    main()

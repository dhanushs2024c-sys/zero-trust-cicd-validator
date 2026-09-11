"""
Zero-Trust Policy Engine
Evaluates commit verification, dependency verification, and runner integrity
against configured policy rules in configs/policy.yaml.
Enforces strict fail-closed Zero-Trust evaluation: all required checks must pass.
"""

from typing import List, Dict, Tuple, Optional
from backend.app.config import PolicyRules, load_policy
from backend.app.schemas.validation import (
    CommitVerificationResult,
    DependencyVerificationResult,
    RunnerIntegrityResult,
    PolicyDecision
)
from backend.app.services.audit_logger import audit_logger


class PolicyEngine:
    def __init__(self, policy: Optional[PolicyRules] = None):
        self.policy = policy or load_policy()

    def evaluate(
        self,
        commit_res: CommitVerificationResult,
        dep_res: DependencyVerificationResult,
        runner_res: RunnerIntegrityResult
    ) -> PolicyDecision:
        """
        Evaluate all verification results against policy.
        Returns final decision (ALLOW/BLOCK), security score (0-100), and rationale.
        """
        reasons: List[str] = []
        rules_evaluated: Dict[str, bool] = {}
        is_blocked = False

        # ---------------------------------------------------------------------
        # 1. Commit Verification Policy Evaluation
        # ---------------------------------------------------------------------
        if self.policy.require_signed_commit:
            commit_signed_ok = commit_res.signed and commit_res.signature_valid
            rules_evaluated["require_signed_commit"] = commit_signed_ok
            if not commit_signed_ok:
                is_blocked = True
                if not commit_res.signed:
                    reasons.append("Commit Verification Failure: Commit is unsigned. Policy requires cryptographic signatures.")
                else:
                    reasons.append(f"Commit Verification Failure: Cryptographic signature is invalid or forged ({commit_res.signature_type}).")

        if self.policy.require_trusted_developer:
            developer_trusted_ok = commit_res.trusted_developer
            rules_evaluated["require_trusted_developer"] = developer_trusted_ok
            if not developer_trusted_ok:
                is_blocked = True
                reasons.append(f"Commit Verification Failure: Signer '{commit_res.author_email}' is not in authorized trusted_developers.yaml.")

        # ---------------------------------------------------------------------
        # 2. Dependency Verification Policy Evaluation
        # ---------------------------------------------------------------------
        if self.policy.block_dependency_mismatch:
            no_mismatch = (dep_res.mismatched_count == 0)
            rules_evaluated["block_dependency_mismatch"] = no_mismatch
            if not no_mismatch:
                is_blocked = True
                reasons.append(f"Dependency Integrity Failure: {dep_res.mismatched_count} dependency hash mismatch(es) detected.")

        if self.policy.block_unverified_dependencies:
            no_unverified = (dep_res.unverified_count == 0 and dep_res.missing_count == 0)
            rules_evaluated["block_unverified_dependencies"] = no_unverified
            if not no_unverified:
                is_blocked = True
                reasons.append(f"Dependency Integrity Failure: {dep_res.unverified_count} unverified or {dep_res.missing_count} missing lockfile dependencies.")

        # ---------------------------------------------------------------------
        # 3. Runner Integrity Policy Evaluation
        # ---------------------------------------------------------------------
        if self.policy.require_runner_integrity:
            if self.policy.runner_severity_threshold == "WARNING":
                runner_ok = (runner_res.status == "CLEAN")
                if not runner_ok:
                    is_blocked = True
                    reasons.append(f"Runner Integrity Failure: Environment status is '{runner_res.status}'. Policy requires CLEAN runner.")
            else:
                runner_ok = (runner_res.status != "TAMPERED")
                if not runner_ok:
                    is_blocked = True
                    reasons.append("Runner Integrity Failure: Runner environment is TAMPERED. Baseline files modified or critical variables hijacked.")
            rules_evaluated["require_runner_integrity"] = runner_ok

        # ---------------------------------------------------------------------
        # 4. Fail-Closed Default Evaluation
        # ---------------------------------------------------------------------
        if not reasons and not is_blocked:
            final_decision = "ALLOW"
            reasons.append("All Zero-Trust security checks passed. Build environment and code integrity verified.")
        else:
            final_decision = "BLOCK"

        # 5. Calculate Security Score (0 to 100)
        score = self._calculate_security_score(commit_res, dep_res, runner_res, final_decision)

        decision_obj = PolicyDecision(
            decision=final_decision,
            score=score,
            reasons=reasons,
            rules_evaluated=rules_evaluated
        )

        audit_logger.log_event(
            event_name=f"POLICY_DECISION_{final_decision}",
            severity="INFO" if final_decision == "ALLOW" else "CRITICAL",
            category="POLICY",
            message=f"Final Pipeline Policy Decision: {final_decision}. Score: {score}/100.",
            details={"reasons": reasons, "rules": rules_evaluated},
            action="BUILD_ALLOWED" if final_decision == "ALLOW" else "BUILD_BLOCKED"
        )

        return decision_obj

    def _calculate_security_score(
        self,
        commit: CommitVerificationResult,
        deps: DependencyVerificationResult,
        runner: RunnerIntegrityResult,
        decision: str
    ) -> int:
        """
        Calculate composite security score (0 - 100).
        Note: Does not mathematically prove host security; reflects policy compliance level.
        """
        commit_score = 0
        if commit.signed and commit.signature_valid:
            commit_score += 20
        if commit.trusted_developer:
            commit_score += 15

        dep_score = 0
        if deps.status == "PASS":
            dep_score = 35
        elif deps.status == "WARNING":
            dep_score = 20
        elif deps.status == "FAIL":
            dep_score = max(0, 15 - (deps.mismatched_count * 15))

        runner_score = 0
        if runner.status == "CLEAN":
            runner_score = 30
        elif runner.status == "WARNING":
            runner_score = 15
        elif runner.status == "TAMPERED":
            runner_score = 0

        total = commit_score + dep_score + runner_score
        return min(100, max(0, total))

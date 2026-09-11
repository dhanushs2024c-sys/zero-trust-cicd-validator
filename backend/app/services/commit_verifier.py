"""
Zero-Trust Commit Verification Engine
Cryptographically verifies Git commit signatures (GPG and SSH) and checks against
authorized developer whitelist in configs/trusted_developers.yaml.
Strict Zero-Trust: Never assumes commit authenticity without valid cryptographic proof.
"""

import os
import re
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from backend.app.config import load_trusted_developers, TrustedDeveloper, DEFAULT_TRUSTED_DEVS_PATH
from backend.app.schemas.validation import CommitVerificationResult
from backend.app.services.audit_logger import audit_logger


class CommitVerifier:
    def __init__(
        self,
        repo_path: Optional[Path] = None,
        trusted_devs_path: Optional[Path] = None
    ):
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.trusted_devs_path = Path(trusted_devs_path) if trusted_devs_path else DEFAULT_TRUSTED_DEVS_PATH
        self.trusted_developers: List[TrustedDeveloper] = load_trusted_developers(self.trusted_devs_path)

    def verify_commit(self, commit_ref: str = "HEAD") -> CommitVerificationResult:
        """
        Main entry point for commit verification.
        Inspects commit metadata, cryptographic signature, and author identity against policy.
        """
        # 1. Check if git is available and target is a git repository
        if not self._is_git_repository():
            result = CommitVerificationResult(
                commit_hash="UNKNOWN",
                short_hash="UNKNOWN",
                author_name="",
                author_email="",
                committer_name="",
                committer_email="",
                commit_date="",
                commit_message="",
                signed=False,
                signature_type="NONE",
                signature_valid=False,
                trusted_developer=False,
                status="FAIL",
                details=f"Target directory '{self.repo_path}' is not a valid Git repository."
            )
            audit_logger.log_event(
                event_name="COMMIT_NOT_IN_GIT_REPO",
                severity="HIGH",
                category="COMMIT",
                message=result.details,
                action="BUILD_BLOCKED"
            )
            return result

        # 2. Extract commit metadata and raw object
        metadata = self._get_commit_metadata(commit_ref)
        if not metadata:
            result = CommitVerificationResult(
                commit_hash="UNKNOWN",
                short_hash="UNKNOWN",
                author_name="",
                author_email="",
                committer_name="",
                committer_email="",
                commit_date="",
                commit_message="",
                signed=False,
                signature_type="NONE",
                signature_valid=False,
                trusted_developer=False,
                status="FAIL",
                details=f"Could not read commit metadata for reference '{commit_ref}'."
            )
            audit_logger.log_event(
                event_name="COMMIT_METADATA_READ_FAILED",
                severity="HIGH",
                category="COMMIT",
                message=result.details,
                action="BUILD_BLOCKED"
            )
            return result

        # 3. Detect signature existence and type from raw commit object
        raw_commit = self._get_raw_commit(metadata["commit_hash"])
        sig_type, sig_payload = self._detect_signature(raw_commit)

        if sig_type == "NONE":
            result = CommitVerificationResult(
                commit_hash=metadata["commit_hash"],
                short_hash=metadata["short_hash"],
                author_name=metadata["author_name"],
                author_email=metadata["author_email"],
                committer_name=metadata["committer_name"],
                committer_email=metadata["committer_email"],
                commit_date=metadata["commit_date"],
                commit_message=metadata["commit_message"],
                signed=False,
                signature_type="NONE",
                signature_valid=False,
                trusted_developer=False,
                status="FAIL",
                details=f"Commit {metadata['short_hash']} is unsigned. Zero-Trust policy mandates cryptographic signatures."
            )
            audit_logger.log_event(
                event_name="COMMIT_UNSIGNED",
                severity="HIGH",
                category="COMMIT",
                message=result.details,
                details={"commit": metadata["commit_hash"], "author": metadata["author_email"]},
                action="BUILD_BLOCKED"
            )
            return result

        # 4. Perform cryptographic verification
        is_valid, signer_info, signer_key = self._verify_signature(
            commit_ref=metadata["commit_hash"],
            sig_type=sig_type,
            sig_payload=sig_payload,
            author_email=metadata["author_email"]
        )

        # 5. Check signer against trusted developers whitelist
        is_trusted, matched_dev = self._check_trusted_developer(
            author_email=metadata["author_email"],
            signer_info=signer_info,
            signer_key=signer_key,
            sig_type=sig_type
        )

        # 6. Synthesize final status
        if not is_valid:
            status = "FAIL"
            details = f"Commit {metadata['short_hash']} has an invalid or forged {sig_type} cryptographic signature."
            severity = "CRITICAL"
        elif not is_trusted:
            status = "FAIL"
            details = (
                f"Commit {metadata['short_hash']} signature is valid, but signer "
                f"'{signer_info or metadata['author_email']}' is not authorized in trusted_developers.yaml."
            )
            severity = "HIGH"
        else:
            status = "PASS"
            dev_name = matched_dev.name if matched_dev else "Authorized Developer"
            details = f"Commit {metadata['short_hash']} cryptographically verified with {sig_type} signature by {dev_name}."
            severity = "INFO"

        result = CommitVerificationResult(
            commit_hash=metadata["commit_hash"],
            short_hash=metadata["short_hash"],
            author_name=metadata["author_name"],
            author_email=metadata["author_email"],
            committer_name=metadata["committer_name"],
            committer_email=metadata["committer_email"],
            commit_date=metadata["commit_date"],
            commit_message=metadata["commit_message"],
            signed=True,
            signature_type=sig_type,
            signature_valid=is_valid,
            trusted_developer=is_trusted,
            signer_identity=signer_info,
            signer_key_id=signer_key,
            status=status,
            details=details
        )

        audit_logger.log_event(
            event_name=f"COMMIT_VERIFICATION_{status}",
            severity=severity,
            category="COMMIT",
            message=details,
            details={
                "commit": metadata["commit_hash"],
                "signature_type": sig_type,
                "valid": is_valid,
                "trusted": is_trusted,
                "signer": signer_info
            },
            action="BUILD_ALLOWED" if status == "PASS" else "BUILD_BLOCKED"
        )

        return result

    def _is_git_repository(self) -> bool:
        """Check if target path is a git repository without invoking shell."""
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            return res.returncode == 0 and res.stdout.strip() == "true"
        except Exception:
            return False

    def _get_commit_metadata(self, commit_ref: str) -> Optional[Dict[str, str]]:
        """Retrieve structured metadata for the commit."""
        format_spec = "%H%x00%h%x00%an%x00%ae%x00%cn%x00%ce%x00%cD%x00%s"
        try:
            res = subprocess.run(
                ["git", "log", "-1", f"--format={format_spec}", commit_ref],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode != 0 or not res.stdout.strip():
                return None
            parts = res.stdout.strip().split("\x00")
            if len(parts) < 8:
                return None
            return {
                "commit_hash": parts[0],
                "short_hash": parts[1],
                "author_name": parts[2],
                "author_email": parts[3],
                "committer_name": parts[4],
                "committer_email": parts[5],
                "commit_date": parts[6],
                "commit_message": parts[7]
            }
        except Exception:
            return None

    def _get_raw_commit(self, commit_hash: str) -> str:
        """Extract raw commit object including headers and signature block."""
        try:
            res = subprocess.run(
                ["git", "cat-file", "-p", commit_hash],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            return res.stdout if res.returncode == 0 else ""
        except Exception:
            return ""

    def _detect_signature(self, raw_commit: str) -> Tuple[str, Optional[str]]:
        """Detect signature type (SSH, GPG) and extract signature payload."""
        if not raw_commit:
            return "NONE", None

        # Check for SSH signature block
        if "BEGIN SSH SIGNATURE" in raw_commit:
            match = re.search(r"(-----BEGIN SSH SIGNATURE-----[^-]+-----END SSH SIGNATURE-----)", raw_commit, re.DOTALL)
            sig_payload = match.group(1) if match else None
            return "SSH", sig_payload

        # Check for PGP/GPG signature block
        if "BEGIN PGP SIGNATURE" in raw_commit:
            match = re.search(r"(-----BEGIN PGP SIGNATURE-----[^-]+-----END PGP SIGNATURE-----)", raw_commit, re.DOTALL)
            sig_payload = match.group(1) if match else None
            return "GPG", sig_payload

        return "NONE", None

    def _verify_signature(
        self,
        commit_ref: str,
        sig_type: str,
        sig_payload: Optional[str],
        author_email: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Cryptographically verify the signature.
        Uses Git's native signature verification with allowed_signers for SSH,
        and GPG CLI / Git verification for GPG.
        """
        if sig_type == "SSH":
            return self._verify_ssh_signature(commit_ref, author_email)
        elif sig_type == "GPG":
            return self._verify_gpg_signature(commit_ref)
        return False, None, None

    def _verify_ssh_signature(
        self,
        commit_ref: str,
        author_email: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Verify SSH commit signature using Git with temporary allowed_signers file."""
        # Create temporary allowed_signers file from trusted_developers
        temp_allowed_signers = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".allowed_signers") as tf:
                temp_allowed_signers = tf.name
                for dev in self.trusted_developers:
                    if dev.enabled and dev.type.lower() == "ssh":
                        # Format: <email> <key_id/public_key>
                        # e.g., dev@example.com ssh-ed25519 AAAAC...
                        key_content = dev.key_id.strip()
                        tf.write(f"{dev.email} {key_content}\n")
                        tf.write(f"* {key_content}\n")  # Allow wildcard match on key

            # Format fields: %G? (verification status), %GK (key ID), %GS (signer), %GF (fingerprint)
            cmd = [
                "git",
                "-c", f"gpg.ssh.allowedSignersFile={temp_allowed_signers}",
                "log", "-1",
                "--format=%G?%x00%GK%x00%GS%x00%GF",
                commit_ref
            ]

            res = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False
            )

            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split("\x00")
                status_code = parts[0] if len(parts) > 0 else "N"
                signer_key = parts[1] if len(parts) > 1 else None
                signer_info = parts[2] if len(parts) > 2 else None
                fingerprint = parts[3] if len(parts) > 3 else None

                # Git status codes:
                # G = Good (valid and trusted via allowed_signers)
                # U = Good (cryptographically valid signature with untrusted key)
                # B = Bad signature
                # N = No signature
                # E = Cannot be checked
                if status_code == "G":
                    return True, signer_info or author_email, fingerprint or signer_key
                elif status_code == "U":
                    # Valid crypto signature, but key was not in allowed_signers
                    return True, signer_info or "Untrusted Key", fingerprint or signer_key
                elif status_code in ("B", "E"):
                    return False, "Invalid/Unchecked Signature", None

            # Fallback: check with git verify-commit
            verify_cmd = [
                "git",
                "-c", f"gpg.ssh.allowedSignersFile={temp_allowed_signers}",
                "verify-commit",
                commit_ref
            ]
            v_res = subprocess.run(
                verify_cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            if v_res.returncode == 0:
                return True, author_email, None

            # If ssh-keygen is available, examine stderr for "Good" or "signature by"
            combined_err = (v_res.stderr + " " + (res.stderr if 'res' in locals() else "")).lower()
            if "good \"git\" signature" in combined_err or "good ssh signature" in combined_err:
                return True, author_email, None

            return False, None, None

        except Exception as e:
            return False, f"Verification error: {str(e)}", None
        finally:
            if temp_allowed_signers and os.path.exists(temp_allowed_signers):
                try:
                    os.unlink(temp_allowed_signers)
                except Exception:
                    pass

    def _verify_gpg_signature(
        self,
        commit_ref: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Verify GPG/OpenPGP commit signature."""
        try:
            # First attempt with git verify-commit
            cmd = ["git", "log", "-1", "--format=%G?%x00%GK%x00%GS%x00%GF", commit_ref]
            res = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False
            )

            if res.returncode == 0 and res.stdout.strip():
                parts = res.stdout.strip().split("\x00")
                status_code = parts[0] if len(parts) > 0 else "N"
                signer_key = parts[1] if len(parts) > 1 else None
                signer_info = parts[2] if len(parts) > 2 else None
                fingerprint = parts[3] if len(parts) > 3 else None

                if status_code in ("G", "U"):
                    return True, signer_info or "GPG Signer", fingerprint or signer_key
                elif status_code == "B":
                    return False, "Bad GPG Signature", None
                elif status_code == "E":
                    # Missing public key or gpg missing
                    return False, "GPG Key Not In Keyring", signer_key

            # Fallback direct git verify-commit
            v_res = subprocess.run(
                ["git", "verify-commit", commit_ref],
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False
            )
            if v_res.returncode == 0:
                return True, "Verified GPG Signer", None

            return False, "Unverified GPG Signature", None
        except Exception as e:
            return False, f"GPG verification error: {str(e)}", None

    def _check_trusted_developer(
        self,
        author_email: str,
        signer_info: Optional[str],
        signer_key: Optional[str],
        sig_type: str
    ) -> Tuple[bool, Optional[TrustedDeveloper]]:
        """
        Check whether the commit signer is present in configs/trusted_developers.yaml.
        Compares email, key_id, fingerprint, and identity string.
        """
        for dev in self.trusted_developers:
            if not dev.enabled:
                continue

            # Check email match
            if dev.email.lower() == author_email.lower():
                return True, dev

            # Check signer_info match if identity is present
            if signer_info and dev.email.lower() in signer_info.lower():
                return True, dev

            # Check key fingerprint or key_id match
            if signer_key:
                clean_signer_key = signer_key.replace("SHA256:", "").strip()
                if dev.key_id and (dev.key_id in signer_key or clean_signer_key in dev.key_id):
                    return True, dev
                if dev.fingerprint and (clean_signer_key in dev.fingerprint or dev.fingerprint in signer_key):
                    return True, dev

        return False, None

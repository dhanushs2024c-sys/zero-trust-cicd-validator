"""
Zero-Trust CI/CD Pipeline Validator Configuration Loader
Loads and validates policy, trusted developers, and runner baseline configurations.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import os
import yaml
from pydantic import BaseModel, Field


# Base project directory resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = Path(os.getenv("ZT_CONFIG_DIR", str(PROJECT_ROOT / "configs")))
DEFAULT_POLICY_PATH = Path(os.getenv("ZT_POLICY_PATH", str(CONFIG_DIR / "policy.yaml")))
DEFAULT_TRUSTED_DEVS_PATH = Path(os.getenv("ZT_TRUSTED_DEVS_PATH", str(CONFIG_DIR / "trusted_developers.yaml")))
DEFAULT_BASELINE_PATH = Path(os.getenv("ZT_BASELINE_PATH", str(CONFIG_DIR / "integrity_baseline.json")))
DEFAULT_DB_PATH = Path(os.getenv("ZT_DB_PATH", str(PROJECT_ROOT / "validator.db")))
DEFAULT_LOG_DIR = Path(os.getenv("ZT_LOG_DIR", str(PROJECT_ROOT / "logs")))


class TrustedDeveloper(BaseModel):
    name: str
    email: str
    key_id: str
    fingerprint: Optional[str] = None
    type: str = "ssh"  # 'ssh' or 'gpg'
    role: Optional[str] = "Developer"
    enabled: bool = True


class PolicyRules(BaseModel):
    require_signed_commit: bool = True
    require_trusted_developer: bool = True
    allowed_signature_types: List[str] = Field(default_factory=lambda: ["ssh", "gpg"])

    require_dependency_integrity: bool = True
    block_unverified_dependencies: bool = True
    block_dependency_mismatch: bool = True
    allowed_hash_algorithms: List[str] = Field(default_factory=lambda: ["sha256", "sha512"])

    require_runner_integrity: bool = True
    runner_severity_threshold: str = "WARNING"  # WARNING or TAMPERED
    check_environment_variables: bool = True
    check_processes: bool = True
    check_path_anomalies: bool = True

    fail_closed: bool = True


class ValidatorSettings(BaseModel):
    project_root: Path = PROJECT_ROOT
    config_dir: Path = CONFIG_DIR
    policy_path: Path = DEFAULT_POLICY_PATH
    trusted_devs_path: Path = DEFAULT_TRUSTED_DEVS_PATH
    baseline_path: Path = DEFAULT_BASELINE_PATH
    db_path: Path = DEFAULT_DB_PATH
    log_dir: Path = DEFAULT_LOG_DIR


def load_policy(path: Optional[Path] = None) -> PolicyRules:
    """Load policy rules from YAML file with safe defaults."""
    target_path = path or DEFAULT_POLICY_PATH
    if not target_path.exists():
        # Fallback to safe strict defaults (fail-closed)
        return PolicyRules()
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            raw_policy = data.get("policy", data)
            return PolicyRules(**raw_policy)
    except Exception as e:
        # On error reading policy, fail closed with default strict rules
        return PolicyRules(fail_closed=True)


def load_trusted_developers(path: Optional[Path] = None) -> List[TrustedDeveloper]:
    """Load trusted developers list from YAML configuration."""
    target_path = path or DEFAULT_TRUSTED_DEVS_PATH
    if not target_path.exists():
        return []
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            raw_devs = data.get("developers", [])
            return [TrustedDeveloper(**dev) for dev in raw_devs]
    except Exception as e:
        return []

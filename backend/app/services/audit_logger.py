"""
Append-Only Security Audit Logger for Zero-Trust CI/CD Pipeline Validator
Writes immutable structured audit events to SQLite database and append-only JSONL files.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from backend.app.config import DEFAULT_LOG_DIR
from backend.app.schemas.validation import SecurityEvent
from backend.app.models.database import db

logger = logging.getLogger("zero_trust.audit")


class AuditLogger:
    def __init__(self, log_dir: Path = DEFAULT_LOG_DIR):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_jsonl_path = self.log_dir / "audit.jsonl"

    def log_event(
        self,
        event_name: str,
        severity: str,
        category: str,
        message: str,
        run_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        action: str = "MONITOR_LOGGED",
        source: str = "zt-validator"
    ) -> SecurityEvent:
        """
        Record an immutable append-only audit event to both JSONL file and SQLite.
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        event_obj = SecurityEvent(
            run_id=run_id,
            timestamp=timestamp,
            severity=severity.upper(),
            category=category.upper(),
            event=event_name,
            source=source,
            message=message,
            details=details or {},
            action=action
        )

        # 1. Append to SQLite
        try:
            db.save_event(event_obj)
        except Exception as e:
            logger.error(f"Failed to persist audit event to database: {e}")

        # 2. Append to immutable JSONL audit file
        try:
            with open(self.audit_jsonl_path, "a", encoding="utf-8") as f:
                f.write(event_obj.model_dump_json() + "\n")
        except Exception as e:
            logger.error(f"Failed to append audit event to {self.audit_jsonl_path}: {e}")

        return event_obj


# Global audit logger instance
audit_logger = AuditLogger()

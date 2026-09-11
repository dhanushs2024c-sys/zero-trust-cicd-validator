"""
SQLite Database Layer for Zero-Trust CI/CD Pipeline Validator
Manages validation runs, audit logs, and security events.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.app.config import DEFAULT_DB_PATH
from backend.app.schemas.validation import SecurityEvent, ValidationRunResponse


class DatabaseManager:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Validation runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS validation_runs (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    target_directory TEXT,
                    commit_hash TEXT,
                    commit_status TEXT,
                    dependency_status TEXT,
                    runner_status TEXT,
                    final_decision TEXT NOT NULL,
                    exit_code INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    commit_data TEXT,
                    dependency_data TEXT,
                    runner_data TEXT,
                    policy_data TEXT,
                    execution_time_ms REAL
                )
            """)

            # Append-only Security events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS security_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE,
                    run_id TEXT,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    category TEXT NOT NULL,
                    event TEXT NOT NULL,
                    source TEXT NOT NULL,
                    message TEXT NOT NULL,
                    details TEXT,
                    action TEXT NOT NULL
                )
            """)

            # Baseline audit history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runner_baselines (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    generated_at TEXT NOT NULL,
                    generator TEXT,
                    total_files INTEGER,
                    data TEXT NOT NULL
                )
            """)

            conn.commit()

    def save_run(self, run: ValidationRunResponse):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO validation_runs (
                    id, timestamp, target_directory, commit_hash, commit_status,
                    dependency_status, runner_status, final_decision, exit_code,
                    score, commit_data, dependency_data, runner_data, policy_data,
                    execution_time_ms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.run_id,
                run.timestamp,
                run.target_directory,
                run.commit.commit_hash,
                run.commit.status,
                run.dependencies.status,
                run.runner.status,
                run.final_decision,
                run.exit_code,
                run.policy.score,
                run.commit.model_dump_json(),
                run.dependencies.model_dump_json(),
                run.runner.model_dump_json(),
                run.policy.model_dump_json(),
                run.execution_time_ms
            ))
            conn.commit()

    def save_event(self, event: SecurityEvent):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            import uuid
            event_id = event.id or f"EVT-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}-{uuid.uuid4().hex[:6].upper()}"
            cursor.execute("""
                INSERT INTO security_events (
                    event_id, run_id, timestamp, severity, category, event,
                    source, message, details, action
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                event.run_id,
                event.timestamp,
                event.severity,
                event.category,
                event.event,
                event.source,
                event.message,
                json.dumps(event.details),
                event.action
            ))
            conn.commit()

    def list_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, timestamp, target_directory, commit_hash, commit_status,
                       dependency_status, runner_status, final_decision, exit_code,
                       score, execution_time_ms
                FROM validation_runs
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM validation_runs WHERE id = ?", (run_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            # Parse JSON sub-objects
            for field in ['commit_data', 'dependency_data', 'runner_data', 'policy_data']:
                if data.get(field):
                    try:
                        data[field] = json.loads(data[field])
                    except Exception:
                        pass
            return data

    def list_events(self, limit: int = 100, severity: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM security_events"
            params = []
            conditions = []
            if severity:
                conditions.append("severity = ?")
                params.append(severity)
            if category:
                conditions.append("category = ?")
                params.append(category)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY id DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                if item.get("details"):
                    try:
                        item["details"] = json.loads(item["details"])
                    except Exception:
                        pass
                results.append(item)
            return results

    def save_baseline_record(self, data: Dict[str, Any]):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO runner_baselines (generated_at, generator, total_files, data)
                VALUES (?, ?, ?, ?)
            """, (
                data.get("generated_at", datetime.utcnow().isoformat()),
                data.get("generator", "zt-validator"),
                len(data.get("files", {})),
                json.dumps(data)
            ))
            conn.commit()


# Singleton database instance
db = DatabaseManager()

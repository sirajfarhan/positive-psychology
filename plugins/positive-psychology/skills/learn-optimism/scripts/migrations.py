#!/usr/bin/env python3
"""Schema migrations for the optimism store.

The problem this solves: someone installs a version, uses it for weeks, then
upgrades. Their data has to survive a schema that moved underneath it, without
anyone remembering which version they were on.

How it works. SQLite carries an integer in `PRAGMA user_version`, and that is
the schema version. Every change to the schema appends one entry to MIGRATIONS
and never edits an earlier one. On open, `migrate()` applies every entry above
the store's current version, in order, each inside its own transaction, and
records what it did. A store three versions behind catches up in one call; a
current store does nothing.

Three rules keep this safe:

  Migrations are append-only. Editing a shipped migration means two stores
  claiming the same version with different shapes.

  Migrations are idempotent where they can be. Adding a column checks first,
  so a half-applied upgrade can be re-run.

  The file is copied before anything runs. A failed migration rolls back its
  transaction, and the backup covers the case where SQLite itself is unhappy.
"""

from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _cols(con: sqlite3.Connection, table: str) -> set[str]:
    return {r[1] for r in con.execute(f"PRAGMA table_info({table})")}


def _add_column(con: sqlite3.Connection, table: str, col: str, decl: str) -> None:
    """Idempotent ALTER, because a rerun must not fail on an existing column."""
    if col not in _cols(con, table):
        con.execute(f"ALTER TABLE {table} ADD COLUMN {col} {decl}")


# --------------------------------------------------------------------------
# The migrations, append-only: never edit one that has shipped.
# --------------------------------------------------------------------------

def _m1_baseline(con: sqlite3.Connection) -> None:
    """The four tables as they stand, created only if absent.

    Stores that predate versioning already have these, so every statement is
    IF NOT EXISTS and this migration is a no-op for them. It exists so a fresh
    store and an upgraded store converge on the same shape.
    """
    con.executescript("""
    CREATE TABLE IF NOT EXISTS explanation (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        captured_at     TEXT    NOT NULL,
        event           TEXT    NOT NULL,
        valence         TEXT    NOT NULL CHECK (valence IN ('good','bad')),
        quote           TEXT    NOT NULL,
        note            TEXT
    );
    CREATE TABLE IF NOT EXISTS concept (
        id            TEXT PRIMARY KEY,
        name          TEXT NOT NULL,
        performance   TEXT NOT NULL,
        mastery       TEXT NOT NULL DEFAULT 'new',
        seen          INTEGER NOT NULL DEFAULT 0,
        correct       INTEGER NOT NULL DEFAULT 0,
        last_seen     TEXT,
        next_due      TEXT,
        interval_days REAL NOT NULL DEFAULT 0,
        ease          REAL NOT NULL DEFAULT 2.3
    );
    CREATE TABLE IF NOT EXISTS attempt (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        concept_id     TEXT NOT NULL REFERENCES concept(id),
        at             TEXT NOT NULL,
        stage          TEXT NOT NULL,
        result         TEXT NOT NULL CHECK (result IN ('correct','partial','incorrect')),
        evidence       TEXT
    );
    """)
    for dim in ("permanence", "pervasiveness", "personalization", "builds"):
        _add_column(con, "explanation", dim, "REAL")


def _m2_scoring_and_ledger(con: sqlite3.Connection) -> None:
    """Domain tags, concept provenance, drill novelty, and the open drill."""
    _add_column(con, "explanation", "domain", "TEXT")
    _add_column(con, "concept", "source", "TEXT NOT NULL DEFAULT 'seligman'")
    _add_column(con, "concept", "kind", "TEXT NOT NULL DEFAULT 'principle'")
    _add_column(con, "attempt", "prompt", "TEXT")
    _add_column(con, "attempt", "explanation_id", "INTEGER")
    con.execute("""
        CREATE TABLE IF NOT EXISTS pending (
            id             INTEGER PRIMARY KEY CHECK (id = 1),
            concept_id     TEXT NOT NULL REFERENCES concept(id),
            prompt         TEXT NOT NULL,
            explanation_id INTEGER REFERENCES explanation(id),
            asked_at       TEXT NOT NULL
        )""")


def _m3_practice_statements(con: sqlite3.Connection) -> None:
    """Separate real events from re-explanations produced during drills.

    Practice lines are drill material forever and never enter the reading, so
    coached sentences cannot contaminate the instrument. Existing rows are all
    real events, which is what the default gives them.
    """
    _add_column(con, "explanation", "kind", "TEXT NOT NULL DEFAULT 'event'")


def _m4_indexes(con: sqlite3.Connection) -> None:
    """Indexes last, so every column they name is guaranteed to exist."""
    con.executescript("""
    CREATE INDEX IF NOT EXISTS idx_expl_valence   ON explanation(valence);
    CREATE INDEX IF NOT EXISTS idx_expl_captured  ON explanation(captured_at);
    CREATE INDEX IF NOT EXISTS idx_expl_kind      ON explanation(kind);
    CREATE INDEX IF NOT EXISTS idx_attempt_concept ON attempt(concept_id);
    CREATE INDEX IF NOT EXISTS idx_attempt_expl    ON attempt(explanation_id);
    """)


MIGRATIONS: list[tuple[int, str, callable]] = [
    (1, "baseline tables and dimension scores", _m1_baseline),
    (2, "domains, concept provenance, drill novelty, pending drill", _m2_scoring_and_ledger),
    (3, "practice statements kept out of the reading", _m3_practice_statements),
    (4, "indexes", _m4_indexes),
]

LATEST = max(v for v, _, _ in MIGRATIONS)


# --------------------------------------------------------------------------

def current_version(con: sqlite3.Connection) -> int:
    return con.execute("PRAGMA user_version").fetchone()[0]


def backup(path: Path) -> Path | None:
    """Copy the store beside itself before a migration touches it."""
    if not path.exists() or path.stat().st_size == 0:
        return None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = path.with_name(f"{path.stem}.pre-v{current_version_of(path)}.{stamp}.bak")
    shutil.copy2(path, dest)
    return dest


def current_version_of(path: Path) -> int:
    con = sqlite3.connect(path)
    try:
        return con.execute("PRAGMA user_version").fetchone()[0]
    finally:
        con.close()


def migrate(con: sqlite3.Connection, path: Path | None = None,
            verbose: bool = False) -> dict:
    """Bring the store to LATEST. Safe to call on every open."""
    at = current_version(con)
    pending = [m for m in MIGRATIONS if m[0] > at]
    result = {"from": at, "to": at, "applied": [], "backup": None}
    if not pending:
        return result

    if path is not None:
        b = backup(path)
        result["backup"] = str(b) if b else None

    con.execute("""CREATE TABLE IF NOT EXISTS migration_log (
        version INTEGER PRIMARY KEY, description TEXT NOT NULL, applied_at TEXT NOT NULL)""")

    for version, description, fn in pending:
        try:
            con.execute("BEGIN")
            fn(con)
            con.execute(
                "INSERT OR REPLACE INTO migration_log (version, description, applied_at) "
                "VALUES (?,?,?)",
                (version, description,
                 datetime.now(timezone.utc).replace(microsecond=0).isoformat()))
            # PRAGMA cannot be parameterised, and version is ours, not input
            con.execute(f"PRAGMA user_version = {int(version)}")
            con.execute("COMMIT")
        except Exception:
            con.execute("ROLLBACK")
            raise
        result["applied"].append({"version": version, "description": description})
        result["to"] = version
        if verbose:
            print(f"  migrated to v{version}: {description}")
    return result

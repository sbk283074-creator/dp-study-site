"""Ordered, one-way schema migrations.

Each entry takes the schema from version N-1 to N. Never edit a released
migration; add a new one.
"""

from __future__ import annotations

from collections.abc import Callable

from sqlalchemy import Engine, Connection, text


def _v1_initial(conn: Connection) -> None:
    from taskforge.models import Base

    Base.metadata.create_all(conn)


MIGRATIONS: list[Callable[[Connection], None]] = [_v1_initial]


def ensure_schema(engine: Engine) -> None:
    """Bring the database up to the newest migration, then stop."""
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)"))
        current = conn.execute(text("SELECT version FROM schema_version")).scalar()
        if current is None:
            conn.execute(text("INSERT INTO schema_version (version) VALUES (0)"))
            current = 0
        for version, step in enumerate(MIGRATIONS, start=1):
            if version > current:
                step(conn)
                conn.execute(text("UPDATE schema_version SET version = :v"), {"v": version})

"""Settings read from the environment, with sane defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_HOME = Path.home() / ".taskforge"


@dataclass(frozen=True, slots=True)
class Settings:
    database_url: str
    log_path: Path

    @classmethod
    def from_env(cls, env: dict[str, str] | None = None) -> Settings:
        env = dict(os.environ if env is None else env)
        url = env.get("TASKFORGE_DB") or f"sqlite:///{DEFAULT_HOME / 'taskforge.db'}"
        log_path = Path(env.get("TASKFORGE_LOG") or DEFAULT_HOME / "taskforge.log").expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if url.startswith("sqlite"):
            db_file = Path(url.split("///")[-1]).expanduser()
            db_file.parent.mkdir(parents=True, exist_ok=True)
        return cls(database_url=url, log_path=log_path)

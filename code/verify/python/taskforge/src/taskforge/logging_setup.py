"""Logging configuration: quiet by default, chatty with --verbose."""

from __future__ import annotations

import logging
from pathlib import Path

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"


def configure_logging(log_path: Path, *, verbose: bool = False) -> None:
    logger = logging.getLogger("taskforge")
    logger.setLevel(logging.DEBUG if verbose else logging.WARNING)
    logger.propagate = False
    logger.handlers.clear()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(_FORMAT))
    logger.addHandler(file_handler)

    if verbose:
        stream = logging.StreamHandler()
        stream.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
        logger.addHandler(stream)

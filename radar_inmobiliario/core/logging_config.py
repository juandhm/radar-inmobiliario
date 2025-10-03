"""Logging configuration helper.

Provides a simple function to configure logging to stdout with a consistent
format. Individual scripts can call this at startup.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logging with stream handler to stdout."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )



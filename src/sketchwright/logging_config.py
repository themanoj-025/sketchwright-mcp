"""Logging configuration for Sketchwright, strictly isolating MCP stdio transport."""

from __future__ import annotations

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    is_mcp: bool = False,
    logger_name: Optional[str] = "sketchwright",
) -> logging.Logger:
    """Configure structured logging for Sketchwright.

    When `is_mcp` is True, logging is explicitly configured to write ONLY to sys.stderr,
    preserving sys.stdout exclusively for MCP JSON-RPC protocol frames.
    """
    logger = logging.getLogger(logger_name)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Clear existing handlers to prevent duplicate lines
    if logger.handlers:
        logger.handlers.clear()

    # Destination stream: stderr is mandatory for MCP, and standard for CLI diagnostic logs
    stream = sys.stderr if is_mcp else sys.stderr

    handler = logging.StreamHandler(stream)
    handler.setLevel(numeric_level)

    # Format
    if is_mcp:
        formatter = logging.Formatter(
            fmt="[Sketchwright-MCP] %(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False

    return logger

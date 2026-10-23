"""Configuration management and system limits for Sketchwright."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from sketchwright.errors import ConfigurationError


@dataclass(frozen=True)
class Limits:
    """Security and resource limits to defend against resource exhaustion."""

    max_input_bytes: int = 1_048_576  # 1 MB
    max_nodes: int = 500
    max_edges: int = 1000
    max_label_length: int = 256
    max_nesting_depth: int = 10
    max_title_length: int = 128
    max_dimension: float = 100_000.0


@dataclass(frozen=True)
class Settings:
    """Runtime settings and default layout parameters."""

    log_level: str = "INFO"
    default_algorithm: str = "layered"
    default_direction: str = "LR"
    default_node_spacing: float = 80.0
    default_rank_spacing: float = 120.0
    default_padding: float = 40.0
    deterministic: bool = True
    limits: Limits = field(default_factory=Limits)

    @classmethod
    def from_env(cls) -> Settings:
        """Load settings from environment variables with SKETCHWRIGHT_ prefix."""
        log_level = os.getenv("SKETCHWRIGHT_LOG_LEVEL", "INFO").upper()
        if log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            log_level = "INFO"

        algorithm = os.getenv("SKETCHWRIGHT_DEFAULT_ALGORITHM", "layered").lower()
        if algorithm not in ("layered", "grid", "tree"):
            algorithm = "layered"

        direction = os.getenv("SKETCHWRIGHT_DEFAULT_DIRECTION", "LR").upper()
        if direction not in ("LR", "RL", "TB", "BT"):
            direction = "LR"

        def _get_float(key: str, default: float) -> float:
            val = os.getenv(key)
            if val is None:
                return default
            try:
                parsed = float(val)
                if parsed <= 0:
                    raise ValueError("Must be positive")
                return parsed
            except Exception as e:
                raise ConfigurationError(
                    f"Invalid float value for {key}: {val}",
                    details={"key": key, "value": val, "error": str(e)},
                ) from e

        def _get_int(key: str, default: int) -> int:
            val = os.getenv(key)
            if val is None:
                return default
            try:
                parsed = int(val)
                if parsed <= 0:
                    raise ValueError("Must be positive integer")
                return parsed
            except Exception as e:
                raise ConfigurationError(
                    f"Invalid int value for {key}: {val}",
                    details={"key": key, "value": val, "error": str(e)},
                ) from e

        node_spacing = _get_float("SKETCHWRIGHT_NODE_SPACING", 80.0)
        rank_spacing = _get_float("SKETCHWRIGHT_RANK_SPACING", 120.0)
        padding = _get_float("SKETCHWRIGHT_PADDING", 40.0)

        limits = Limits(
            max_input_bytes=_get_int("SKETCHWRIGHT_MAX_INPUT_BYTES", 1_048_576),
            max_nodes=_get_int("SKETCHWRIGHT_MAX_NODES", 500),
            max_edges=_get_int("SKETCHWRIGHT_MAX_EDGES", 1000),
            max_label_length=_get_int("SKETCHWRIGHT_MAX_LABEL_LENGTH", 256),
        )

        return cls(
            log_level=log_level,
            default_algorithm=algorithm,
            default_direction=direction,
            default_node_spacing=node_spacing,
            default_rank_spacing=rank_spacing,
            default_padding=padding,
            limits=limits,
        )


# Global default settings instance
default_settings = Settings()

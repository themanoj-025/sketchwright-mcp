"""Unit tests for configuration and environment variable loading."""

import pytest

from sketchwright.config import Settings
from sketchwright.errors import ConfigurationError


def test_settings_default_values() -> None:
    s = Settings()
    assert s.log_level == "INFO"
    assert s.default_algorithm == "layered"
    assert s.default_direction == "LR"
    assert s.default_node_spacing == 80.0
    assert s.default_rank_spacing == 120.0
    assert s.limits.max_nodes == 500


def test_settings_from_env_custom_values(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKETCHWRIGHT_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("SKETCHWRIGHT_DEFAULT_ALGORITHM", "grid")
    monkeypatch.setenv("SKETCHWRIGHT_DEFAULT_DIRECTION", "TB")
    monkeypatch.setenv("SKETCHWRIGHT_NODE_SPACING", "150.5")
    monkeypatch.setenv("SKETCHWRIGHT_MAX_NODES", "250")

    s = Settings.from_env()
    assert s.log_level == "DEBUG"
    assert s.default_algorithm == "grid"
    assert s.default_direction == "TB"
    assert s.default_node_spacing == 150.5
    assert s.limits.max_nodes == 250


def test_settings_from_env_invalid_float(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKETCHWRIGHT_NODE_SPACING", "not-a-number")
    with pytest.raises(ConfigurationError) as exc:
        Settings.from_env()
    assert "Invalid float value for SKETCHWRIGHT_NODE_SPACING" in str(exc.value)


def test_settings_from_env_invalid_int(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SKETCHWRIGHT_MAX_NODES", "-5")
    with pytest.raises(ConfigurationError) as exc:
        Settings.from_env()
    assert "Invalid int value for SKETCHWRIGHT_MAX_NODES" in str(exc.value)


def test_setup_logging_mcp_and_cli() -> None:
    from sketchwright.logging_config import setup_logging

    logger_mcp = setup_logging(level="DEBUG", is_mcp=True, logger_name="test_mcp")
    assert logger_mcp.level == 10  # DEBUG
    assert len(logger_mcp.handlers) == 1

    logger_cli = setup_logging(level="WARNING", is_mcp=False, logger_name="test_cli")
    assert logger_cli.level == 30  # WARNING
    assert len(logger_cli.handlers) == 1

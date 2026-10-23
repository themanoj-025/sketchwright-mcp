"""Error taxonomy and custom exceptions for Sketchwright."""

from typing import Any, Optional

from mcp.server.mcpserver.exceptions import ToolError


class SketchwrightError(Exception):
    """Base exception for all Sketchwright errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert error to a structured dictionary for diagnostics and MCP responses."""
        payload: dict[str, Any] = {
            "error_type": self.__class__.__name__,
            "message": self.message,
        }
        if self.details:
            payload["details"] = self.details
        return payload


class ValidationError(SketchwrightError):
    """Raised when diagram specification or schema validation fails."""


class LayoutError(SketchwrightError):
    """Raised when graph layout or geometry calculation fails."""


class SerializationError(SketchwrightError):
    """Raised when Excalidraw scene generation or serialization fails."""


class FileSystemError(SketchwrightError):
    """Raised when safe filesystem operations, path validation, or file writes fail."""


class ConfigurationError(SketchwrightError):
    """Raised when configuration validation or limits fail."""


class MCPToolError(SketchwrightError, ToolError):
    """Raised when an MCP tool invocation encounters an unrecoverable error."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None) -> None:
        super().__init__(message, details=details)

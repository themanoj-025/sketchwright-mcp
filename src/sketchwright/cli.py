"""Command-line interface for Sketchwright."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, NoReturn, Optional

from sketchwright import __version__
from sketchwright.engine.generator import DiagramGenerator
from sketchwright.errors import FileSystemError, SketchwrightError, ValidationError
from sketchwright.excalidraw.export import write_excalidraw_file, write_svg_file
from sketchwright.excalidraw.validator import validate_excalidraw_scene
from sketchwright.layout.engine import LayoutEngine
from sketchwright.mcp.server import run_server
from sketchwright.mcp.tools import handle_get_capabilities
from sketchwright.models.diagram import DiagramSpec
from sketchwright.models.validation import validate_raw_input
from sketchwright.parser.structured import parse_json_file
from sketchwright.parser.text import parse_text_dsl


class CustomArgumentParser(argparse.ArgumentParser):
    """ArgumentParser returning exit code 2 on argument parsing errors."""

    def error(self, message: str) -> NoReturn:
        sys.stderr.write(f"Error: {message}\n\n")
        self.print_help(sys.stderr)
        sys.exit(2)


def create_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser with subcommands."""
    parser = CustomArgumentParser(
        prog="sketchwright",
        description="Sketchwright: Deterministic Excalidraw MCP diagram agent and layout engine.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"sketchwright {__version__}",
    )

    subparsers = parser.add_subparsers(dest="subcommand", title="Commands", metavar="<command>")

    # validate
    val_parser = subparsers.add_parser("validate", help="Validate a diagram specification or scene JSON.")
    val_parser.add_argument("input_file", help="Path to JSON specification or .excalidraw file.")
    val_parser.add_argument("--json", action="store_true", help="Output machine-readable JSON result.")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate an Excalidraw scene from specification.")
    gen_parser.add_argument("input_file", help="Path to input JSON or text DSL file.")
    gen_parser.add_argument("-o", "--output", help="Output file path (e.g. diagram.excalidraw or diagram.svg).")
    gen_parser.add_argument(
        "--format",
        choices=["excalidraw", "svg"],
        default="excalidraw",
        help="Target output format.",
    )
    gen_parser.add_argument("--algorithm", choices=["layered", "grid", "tree"], help="Override layout algorithm.")
    gen_parser.add_argument("--direction", choices=["LR", "RL", "TB", "BT"], help="Override layout direction.")
    gen_parser.add_argument("--overwrite", action="store_true", help="Allow overwriting destination file.")
    gen_parser.add_argument("--json", action="store_true", help="Print generated scene JSON to stdout.")

    # layout
    lay_parser = subparsers.add_parser("layout", help="Compute deterministic coordinates and edge routes.")
    lay_parser.add_argument("input_file", help="Path to input specification file.")
    lay_parser.add_argument("--algorithm", choices=["layered", "grid", "tree"], help="Override layout algorithm.")
    lay_parser.add_argument("--direction", choices=["LR", "RL", "TB", "BT"], help="Override layout direction.")

    # capabilities
    cap_parser = subparsers.add_parser("capabilities", help="Print runtime capabilities manifest.")
    cap_parser.add_argument("--json", action="store_true", default=True, help="Output as JSON.")

    # mcp
    mcp_parser = subparsers.add_parser("mcp", help="Launch Model Context Protocol server over stdio.")
    mcp_parser.add_argument("--transport", choices=["stdio"], default="stdio", help="MCP transport mode.")

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    """Main CLI entry point with documented exit codes:

    0: Success
    2: User / Validation / Syntax error
    1: Internal runtime / Filesystem error
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    try:
        if args.subcommand == "validate":
            _cmd_validate(args)
        elif args.subcommand == "generate":
            _cmd_generate(args)
        elif args.subcommand == "layout":
            _cmd_layout(args)
        elif args.subcommand == "capabilities":
            _cmd_capabilities(args)
        elif args.subcommand == "mcp":
            _cmd_mcp(args)
    except (ValidationError, ValueError) as e:
        sys.stderr.write(f"Validation Error: {e}\n")
        sys.exit(2)
    except FileSystemError as e:
        sys.stderr.write(f"File System Error: {e}\n")
        sys.exit(2)
    except SketchwrightError as e:
        sys.stderr.write(f"Sketchwright Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Internal Error: {e}\n")
        sys.exit(1)


def _load_spec_from_path(file_path: str) -> DiagramSpec:
    p = Path(file_path)
    if not p.is_file():
        raise FileSystemError(f"Input file does not exist: {p}")

    content = p.read_text(encoding="utf-8")
    content_stripped = content.strip()

    if content_stripped.startswith("{"):
        return parse_json_file(p)
    else:
        return parse_text_dsl(content)


def _cmd_validate(args: argparse.Namespace) -> None:
    p = Path(args.input_file)
    if not p.is_file():
        raise FileSystemError(f"Input file not found: {p}")

    content = p.read_text(encoding="utf-8")
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in {p}: {e}") from e

    out: dict[str, Any]
    if isinstance(data, dict) and data.get("type") == "excalidraw":
        res = validate_excalidraw_scene(data)
        out = {
            "type": "excalidraw_scene",
            "is_valid": res.is_valid,
            "errors": res.errors,
            "warnings": res.warnings,
            "stats": res.stats,
        }
    else:
        v_res, _ = validate_raw_input(data)
        out = {
            "type": "diagram_spec",
            "is_valid": v_res.is_valid,
            "errors": v_res.errors,
            "warnings": v_res.warnings,
            "stats": v_res.stats,
        }

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        status = "VALID" if out["is_valid"] else "INVALID"
        print(f"Validation result for {p.name}: {status}")
        errors_list: list[str] = list(out.get("errors", []))
        if errors_list:
            print("Errors:")
            for err in errors_list:
                print(f"  - {err}")
        warnings_list: list[str] = list(out.get("warnings", []))
        if warnings_list:
            print("Warnings:")
            for w in warnings_list:
                print(f"  - {w}")

    if not out["is_valid"]:
        sys.exit(2)


def _cmd_generate(args: argparse.Namespace) -> None:
    spec = _load_spec_from_path(args.input_file)

    if args.algorithm:
        spec.layout.algorithm = args.algorithm
    if args.direction:
        spec.layout.direction = args.direction

    generator = DiagramGenerator(spec)
    result = generator.generate()

    if args.output:
        out_p = Path(args.output)
        fmt = "svg" if out_p.suffix.lower() == ".svg" or args.format == "svg" else "excalidraw"
        if fmt == "svg":
            written = write_svg_file(result.scene, out_p, overwrite=args.overwrite)
        else:
            written = write_excalidraw_file(result.scene, out_p, overwrite=args.overwrite)
        print(f"Generated diagram written to: {written}")

    if args.json or not args.output:
        print(json.dumps(result.scene, indent=2))


def _cmd_layout(args: argparse.Namespace) -> None:
    spec = _load_spec_from_path(args.input_file)
    if args.algorithm:
        spec.layout.algorithm = args.algorithm
    if args.direction:
        spec.layout.direction = args.direction

    engine = LayoutEngine(spec)
    laid_out = engine.layout()

    out = {
        "nodes": {
            nid: {
                "x": n.rect.x,
                "y": n.rect.y,
                "width": n.rect.width,
                "height": n.rect.height,
            }
            for nid, n in laid_out.nodes.items()
        },
        "canvas": {
            "width": laid_out.canvas_rect.width,
            "height": laid_out.canvas_rect.height,
        },
        "stats": laid_out.stats,
    }
    print(json.dumps(out, indent=2))


def _cmd_capabilities(args: argparse.Namespace) -> None:
    caps = handle_get_capabilities()
    print(json.dumps(caps, indent=2))


def _cmd_mcp(args: argparse.Namespace) -> None:
    run_server(transport=args.transport)


if __name__ == "__main__":
    main()

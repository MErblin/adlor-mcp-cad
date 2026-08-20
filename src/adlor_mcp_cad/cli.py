"""CLI launcher and batch compliance auditor for adlor-mcp-cad."""

import sys
import json
import argparse

# Ensure safe output on Windows cp1252 terminal
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from adlor_mcp_cad.server import mcp
from adlor_mcp_cad.batch_audit import audit_piping_schedule


def main():
    parser = argparse.ArgumentParser(
        prog="adlor-mcp-cad",
        description="FastMCP Server & Engineering Standards Compliance Auditor for Autodesk Revit / IFC.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # serve command
    serve_parser = subparsers.add_parser("serve", help="Run the FastMCP server over stdio.")

    # audit command
    audit_parser = subparsers.add_parser("audit", help="Run a batch engineering compliance audit on a JSON schedule.")
    audit_parser.add_argument("schedule_file", help="Path to JSON file containing element definitions.")

    args = parser.parse_args()

    if args.command == "audit":
        with open(args.schedule_file, "r", encoding="utf-8") as f:
            elements = json.load(f)
        report = audit_piping_schedule(elements)
        print(json.dumps(report.model_dump(), indent=2))
        sys.exit(0 if report.non_compliant_elements == 0 else 1)
    else:
        # Default: run the FastMCP server
        mcp.run()


if __name__ == "__main__":
    main()

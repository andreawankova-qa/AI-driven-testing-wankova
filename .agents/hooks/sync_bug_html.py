#!/usr/bin/env python3
"""PostToolUse hook pro automatickou synchronizaci docs/bug_reports.html.

Po jakékoliv úpravě souboru docs/JIRA_BUG_REPORTS.md automaticky přegeneruje
HTML přehled docs/bug_reports.html pomocí generate_bug_reports_html.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def _get_workspace_roots(payload: dict[str, Any]) -> list[Path]:
    """Vrátí normalizované kořenové cesty workspace z payloadu."""
    roots: list[Path] = []
    for raw in payload.get("workspacePaths") or []:
        if raw:
            roots.append(Path(os.path.realpath(raw)))
    if not roots and payload.get("cwd"):
        roots.append(Path(os.path.realpath(payload["cwd"])))
    if not roots:
        roots.append(Path(__file__).resolve().parents[2])
    return roots


def _extract_target_path(payload: dict[str, Any]) -> str:
    """Extrahuje cestu upravovaného souboru z argumentů toolCall."""
    tool_call = payload.get("toolCall") or {}
    args = tool_call.get("args") or {}
    if not isinstance(args, dict):
        return ""
    for key in ("Path", "TargetFile", "path", "file_path"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _resolve_target_register(target_path: str, roots: list[Path], cwd: str | None) -> Path | None:
    """Vrátí cestu k docs/JIRA_BUG_REPORTS.md, pokud jde o upravovaný soubor."""
    if not target_path:
        return None

    p = Path(target_path)
    if not p.is_absolute() and cwd:
        p = Path(cwd) / p
    resolved = Path(os.path.realpath(str(p)))

    for root in roots:
        register_path = root / "docs" / "JIRA_BUG_REPORTS.md"
        if resolved == register_path:
            return register_path

    normalized = target_path.replace("\\", "/")
    if normalized == "docs/JIRA_BUG_REPORTS.md" or normalized.endswith("/docs/JIRA_BUG_REPORTS.md"):
        return Path(__file__).resolve().parents[2] / "docs" / "JIRA_BUG_REPORTS.md"
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        print(f"[sync_bug_html] Chyba čtení stdin JSON: {exc}", file=sys.stderr)
        print("{}")
        return 0

    if not isinstance(payload, dict):
        print("[sync_bug_html] Očekáván JSON objekt na stdin.", file=sys.stderr)
        print("{}")
        return 0

    target_path = _extract_target_path(payload)
    roots = _get_workspace_roots(payload)
    cwd = payload.get("cwd")
    register_path = _resolve_target_register(target_path, roots, cwd)

    if register_path is not None and register_path.exists():
        try:
            scripts_dir = Path(__file__).resolve().parents[1] / "skills" / "bug_reporting" / "scripts"
            sys.path.insert(0, str(scripts_dir))
            from generate_bug_reports import generate_bug_reports_html

            output_path = register_path.parent / "bug_reports.html"
            generate_bug_reports_html(register_path, output_path)
            print(f"[sync_bug_html] Aktualizován {output_path}", file=sys.stderr)
        except Exception as exc:
            print(f"[sync_bug_html] Chyba generování HTML: {exc}", file=sys.stderr)

    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

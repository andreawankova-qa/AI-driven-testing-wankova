#!/usr/bin/env python3
"""PreToolUse hook chránící skilly (.agents/skills/) a hooky (.agents/hooks/, .agents/hooks.json).

Zabraňuje vytváření, úpravám a mazání skillů i hooků přes souborové nástroje.
V `run_command` blokuje veškeré operace nad chráněnými cestami s jedinou výjimkou:
přímé spuštění skriptu ze složky `.agents/skills/<skill>/scripts/` bez shellového řetězení.
"""

import json
import os
import re
import shlex
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_FILE_TOOLS = frozenset({
    "write_file",
    "edit_file",
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "delete_file",
})

_PROTECTED_RE = re.compile(r"(^|[\s'\"=/])\.agents(?:/(?:skills|hooks|hooks\.json))?(?:/|[\s'\"&|;]|$)")
_SHELL_META_RE = re.compile(r"&&|\|\||[;|><`\n]|\$\(")
_SKILL_SCRIPT_RE = re.compile(r"(?:^|/)\.agents/skills/[^/]+/scripts/[^/]+\.(?:py|sh)$")


def _get_roots(payload: Dict[str, Any]) -> List[Path]:
    roots = [Path(os.path.realpath(p)) for p in (payload.get("workspacePaths") or []) if p]
    if not roots and payload.get("cwd"):
        roots.append(Path(os.path.realpath(payload["cwd"])))
    return roots


def _resolve(path_str: str, cwd: Optional[str]) -> Path:
    p = Path(path_str)
    if not p.is_absolute() and cwd:
        p = Path(cwd) / p
    return Path(os.path.realpath(str(p)))


def _is_protected_path(target: str, roots: List[Path], cwd: Optional[str]) -> bool:
    if not target:
        return False
    resolved = _resolve(target, cwd)
    for root in roots:
        agents = root / ".agents"
        skills, hooks, hooks_json = agents / "skills", agents / "hooks", agents / "hooks.json"
        if resolved in (skills, hooks, hooks_json) or skills in resolved.parents or hooks in resolved.parents:
            return True
    norm = target.replace("\\", "/")
    return bool(re.search(r"(^|/)\.agents/(?:skills|hooks)(/|$)|(^|/)\.agents/hooks\.json$", norm))


def _references_protected(text: str, roots: List[Path], cwd: Optional[str]) -> bool:
    if _PROTECTED_RE.search(text):
        return True
    for root in roots:
        agents = root / ".agents"
        if any(str(t) in text for t in (agents / "skills", agents / "hooks", agents / "hooks.json")):
            return True
    if cwd:
        resolved_cwd = Path(os.path.realpath(cwd))
        for root in roots:
            agents = root / ".agents"
            if resolved_cwd in (agents, agents / "skills", agents / "hooks") or (agents / "skills") in resolved_cwd.parents or (agents / "hooks") in resolved_cwd.parents:
                return True
    return False


def _is_allowed_skill_script(cmd: str, roots: List[Path], cwd: Optional[str]) -> bool:
    if _SHELL_META_RE.search(cmd):
        return False
    try:
        tokens = shlex.split(cmd)
    except ValueError:
        return False
    if len(tokens) < 2 or Path(tokens[0]).name not in ("python", "python3"):
        return False
    script_norm = str(_resolve(tokens[1], cwd)).replace("\\", "/")
    if not _SKILL_SCRIPT_RE.search(script_norm):
        return False
    return not any(_references_protected(arg, roots, None) for arg in tokens[2:])


def _respond(decision: str, reason: Optional[str] = None) -> int:
    out: Dict[str, str] = {"decision": decision}
    if reason is not None:
        out["reason"] = reason
    print(json.dumps(out, ensure_ascii=False))
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception as exc:
        return _respond("deny", f"Chyba při čtení vstupu hooku protect_skills_and_hooks: {exc}")

    tool_call = payload.get("toolCall") or {}
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args") or {}
    cwd, roots = payload.get("cwd"), _get_roots(payload)

    if tool_name in _FILE_TOOLS:
        target = args.get("Path") or args.get("TargetFile") or args.get("path") or args.get("file_path") or ""
        if _is_protected_path(target, roots, cwd):
            return _respond("deny", f"Soubor '{target}' patří mezi chráněné skilly nebo hooky (.agents/skills/, .agents/hooks/, .agents/hooks.json).")
    elif tool_name == "run_command":
        cmd = args.get("CommandLine") or args.get("command") or ""
        if _references_protected(cmd, roots, cwd) and not _is_allowed_skill_script(cmd, roots, cwd):
            return _respond("deny", "Shellové operace nad .agents/skills/, .agents/hooks/ nebo .agents/hooks.json jsou zakázány (povoleno je jen přímé spuštění skriptů ze složky skills/*/scripts/).")

    return _respond("allow")


if __name__ == "__main__":
    sys.exit(main())

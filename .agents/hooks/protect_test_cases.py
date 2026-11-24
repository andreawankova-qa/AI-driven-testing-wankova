#!/usr/bin/env python3
"""PreToolUse hook chránící automatizované testy (tests/) a katalog (docs/TEST_CASES.md).

Zabraňuje vytváření, úpravám nebo mazání test casů tvrdým zablokováním
(decision: "deny"). Čtení a spouštění testů (např. pytest) zůstává povoleno.
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

_REDIR_RE = re.compile(
    r"""(?:^|[^0-9&])(?:[0-9]+|&)?>{1,2}\s*(?:"([^"]+)"|'([^']+)'|((?:\\.|[^\s;&|])+))"""
)
_MUTATION_RULES = (
    (
        re.compile(r"\b(?:rm|rmdir|unlink|mv|cp|touch|mkdir|truncate|dd|install|ln|chmod|chown|trash)\b"),
        "Příkaz pro vytvoření, přesun, kopírování nebo smazání chráněných souborů",
    ),
    (
        re.compile(r"\b(?:sed|perl|ruby)\b[^\n]*\s-[a-zA-Z]*i"),
        "In-place úprava chráněného souboru",
    ),
    (
        re.compile(r"\bgit\s+(?:rm|mv|restore|clean|reset)\b|\bgit\s+checkout\s+--(?:\s|$)"),
        "Git operace měnící nebo mažící chráněné soubory",
    ),
    (
        re.compile(
            r"\b(?:python3?|node)\b[^\n]*\s-[ce]\s[^\n]*"
            r"(?:open\s*\(|write(?:_text|_bytes)?\s*\(|unlink\s*\(|remove\s*\(|rmdir\s*\(|rename\s*\(|replace\s*\(|shutil\.|fs\.(?:write|unlink|rm|mkdir))"
        ),
        "Inline skript zapisující nebo mažící chráněné soubory",
    ),
)


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
        tests_dir = root / "tests"
        if resolved == tests_dir or tests_dir in resolved.parents or resolved == root / "docs" / "TEST_CASES.md":
            return True
    norm = target.replace("\\", "/")
    return bool(re.search(r"(^|/)tests(/|$)", norm) or norm.endswith("docs/TEST_CASES.md"))


def _references_protected(text: str, cwd: Optional[str], roots: List[Path]) -> bool:
    if re.search(r"(^|[\s'\"=/])tests(/|[\s'\"&|;]|$)", text) or "TEST_CASES.md" in text:
        return True
    for root in roots:
        if str(root / "tests") in text or str(root / "docs" / "TEST_CASES.md") in text:
            return True
    if cwd:
        rcwd = Path(os.path.realpath(cwd))
        if rcwd.name == "tests" or any(rcwd == r / "tests" or (r / "tests") in rcwd.parents for r in roots):
            return True
    return False


def _is_mutating_segment(segment: str, cwd: Optional[str], roots: List[Path]) -> Optional[str]:
    stripped = segment.strip()
    if not stripped:
        return None

    for match in _REDIR_RE.finditer(stripped):
        target = (match.group(1) or match.group(2) or match.group(3) or "").replace("\\ ", " ").strip("'\"")
        if target and target != "/dev/null" and not target.startswith("&"):
            if _is_protected_path(target, roots, cwd) or _references_protected(target, cwd, roots):
                return f"Přesměrování zápisu do chráněné cesty ({target})"

    if not _references_protected(stripped, cwd, roots):
        return None

    if re.search(r"\btee\b", stripped):
        tee_part = re.split(r"\btee\b", stripped, maxsplit=1)[1]
        if _references_protected(tee_part, cwd, roots):
            return "Zápis pomocí příkazu tee do chráněné cesty"

    for pattern, reason in _MUTATION_RULES:
        if pattern.search(stripped):
            return reason
    return None


def _split_segments(cmd: str) -> List[str]:
    segs, buf, quote, esc = [], [], "", False
    i, n = 0, len(cmd)
    while i < n:
        ch = cmd[i]
        if esc:
            buf.append(ch)
            esc = False
        elif ch == "\\" and quote != "'":
            buf.append(ch)
            esc = True
        elif ch in ("'", '"') and quote in ("", ch):
            quote = "" if quote else ch
            buf.append(ch)
        elif not quote and (cmd[i : i + 2] in ("&&", "||") or ch in ";|\n"):
            if s := "".join(buf).strip():
                segs.append(s)
            buf.clear()
            i += 2 if cmd[i : i + 2] in ("&&", "||") else 1
            continue
        else:
            buf.append(ch)
        i += 1
    if s := "".join(buf).strip():
        segs.append(s)
    return segs


def _update_cwd(segment: str, cwd: Optional[str]) -> Optional[str]:
    cleaned = segment.strip().strip("()").strip()
    try:
        tokens = shlex.split(cleaned)
    except ValueError:
        tokens = cleaned.split()
    if not tokens or tokens[0] not in ("cd", "pushd"):
        return cwd
    target = next((t for t in tokens[1:] if t not in ("-L", "-P", "-e", "-@")), "~")
    return cwd if target == "-" else str(_resolve(os.path.expanduser(target), cwd))


def _check_run_command(cmd: str, cwd: Optional[str], roots: List[Path]) -> Optional[str]:
    current_cwd = cwd
    for seg in _split_segments(cmd):
        if reason := _is_mutating_segment(seg, current_cwd, roots):
            return reason
        current_cwd = _update_cwd(seg, current_cwd)
    return None


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
        return _respond("deny", f"Chyba při čtení vstupu hooku protect_test_cases: {exc}")

    tool_call = payload.get("toolCall") or {}
    tool_name = tool_call.get("name", "")
    args = tool_call.get("args") or {}
    cwd, roots = payload.get("cwd"), _get_roots(payload)

    if tool_name in _FILE_TOOLS:
        target = args.get("Path") or args.get("TargetFile") or args.get("path") or args.get("file_path") or ""
        if _is_protected_path(target, roots, cwd):
            return _respond(
                "deny",
                f"Soubor '{target}' patří mezi chráněné test casy (tests/ nebo docs/TEST_CASES.md). Vytváření, úpravy a mazání jsou zakázány.",
            )
    elif tool_name == "run_command":
        cmd = args.get("CommandLine") or args.get("command") or ""
        if reason := _check_run_command(cmd, cwd, roots):
            return _respond("deny", f"{reason}. Zásahy do tests/ nebo docs/TEST_CASES.md jsou zakázány.")

    return _respond("allow")


if __name__ == "__main__":
    sys.exit(main())

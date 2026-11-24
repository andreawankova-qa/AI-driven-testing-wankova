#!/usr/bin/env python3
"""Stop hook pro vynucení Definice hotovo (DoD) u reportování chyb.

Ověřuje, že:
1. Existuje aktuální HTML přehled docs/bug_reports.html a obsahuje reporty z registru.
2. Každý report v docs/JIRA_BUG_REPORTS.md má povinná pole ze zadání
   (kroky k reprodukci, očekávaný a skutečný výsledek, prostředí, důkaz).
3. Každý aktuální padající test v .pytest_cache/v/cache/lastfailed má report.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

REQUIRED_SECTIONS: list[tuple[str, str]] = [
    ("Kroky k reprodukci", r"^#{2,6}[^\n]*Kroky k reprodukci[^\n]*\n(.*?)(?=\n---|\n#{2,6}|\Z)"),
    ("Očekávané chování", r"^#{2,6}[^\n]*Očekávané chování[^\n]*\n(.*?)(?=\n---|\n#{2,6}|\Z)"),
    ("Skutečné chování", r"^#{2,6}[^\n]*Skutečné chování[^\n]*\n(.*?)(?=\n---|\n#{2,6}|\Z)"),
    ("Technický důkaz", r"^#{2,6}[^\n]*Technický důkaz[^\n]*\n(.*?)(?=\n---|\n#{2,6}|\Z)"),
]

TEMPLATE_PLACEHOLDERS = (
    "<nazev_screenshotu>",
    "<nazev_trace>",
    "<přesná_URL>",
    "<Popis správného chování",
    "<Přesný popis toho",
    "<Reprodukováno / Nereprodukováno>",
    "<DD. MM. RRRR>",
)

# Max stáří .pytest_cache/v/cache/lastfailed (10 min), aby starý pád neblokoval jiné úkoly
LASTFAILED_MAX_AGE_SECONDS = 600
# Okno pro pojistku proti zacyklení stejné blokace v jedné konverzaci (2 min)
LOOP_GUARD_TTL_SECONDS = 120


def _get_workspace_root(payload: dict[str, Any]) -> Path:
    """Vrátí kořenovou cestu projektu z payloadu nebo z umístění skriptu."""
    for raw in payload.get("workspacePaths") or []:
        if raw:
            return Path(os.path.realpath(raw))
    if payload.get("cwd"):
        return Path(os.path.realpath(payload["cwd"]))
    return Path(__file__).resolve().parents[2]


def _extract_test_identifiers(nodeid: str) -> tuple[str, str]:
    """Z pytest nodeid vytáhne cestu k souboru a název testovací funkce bez parametrů."""
    parts = nodeid.split("::")
    file_path = parts[0].strip()
    func_name = parts[-1].split("[")[0].strip() if len(parts) > 1 else ""
    return file_path, func_name


def _split_bug_reports(register_content: str) -> list[tuple[str, str]]:
    """Rozdělí registr na dvojice (BR-XX, text_reportu)."""
    chunks = re.split(r"(?=^###\s+🐞\s+BR-\d+)", register_content, flags=re.MULTILINE)
    reports: list[tuple[str, str]] = []
    for chunk in chunks:
        match = re.match(r"^###\s+🐞\s+(BR-\d+)", chunk.strip())
        if match:
            reports.append((match.group(1), chunk))
    return reports


def _check_html(html_path: Path) -> tuple[str, list[str]]:
    if not html_path.exists() or html_path.stat().st_size == 0:
        return "", ["Chybí nebo je prázdný HTML přehled `docs/bug_reports.html`."]
    return html_path.read_text(encoding="utf-8", errors="replace"), []


def _check_register(register_path: Path, html_path: Path, html_content: str) -> tuple[str, list[str]]:
    if not register_path.exists():
        return "", ["Chybí centrální registr chyb `docs/JIRA_BUG_REPORTS.md`."]

    content = register_path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []

    if html_content and (html_path.stat().st_mtime + 1) < register_path.stat().st_mtime:
        errors.append(
            "`docs/bug_reports.html` je starší než `docs/JIRA_BUG_REPORTS.md` — "
            "přegeneruj jej pomocí `python3 .agents/skills/bug_reporting/scripts/manage_bug_reports.py html`."
        )

    for bug_id, report_text in _split_bug_reports(content):
        missing: list[str] = []
        if not re.search(r"\*\s*\*\*Prostředí:\*\*\s*\S+", report_text):
            missing.append("Prostředí")

        for label, pattern in REQUIRED_SECTIONS:
            match = re.search(pattern, report_text, flags=re.MULTILINE | re.DOTALL)
            body = match.group(1).strip() if match else ""
            if not body:
                missing.append(label)
            elif label == "Technický důkaz" and not re.search(
                r"(\.png|\.zip|report\.html|```)", body, flags=re.IGNORECASE
            ):
                errors.append(
                    f"Report `{bug_id}` v sekci `Technický důkaz` postrádá odkaz na screenshot (`.png`), "
                    "trace (`.zip`), `report.html` nebo výpis chyby (```)."
                )

        if missing:
            errors.append(f"Report `{bug_id}` postrádá nebo má prázdná pole: {', '.join(missing)}.")

        if any(ph in report_text for ph in TEMPLATE_PLACEHOLDERS):
            errors.append(f"Report `{bug_id}` obsahuje nevyplněný placeholder ze šablony.")

        if html_content and bug_id not in html_content:
            errors.append(f"Report `{bug_id}` chybí v `docs/bug_reports.html`.")
    return content, errors


def _check_lastfailed(lastfailed_path: Path, register_content: str) -> list[str]:
    if not lastfailed_path.exists():
        return []
    if (time.time() - lastfailed_path.stat().st_mtime) > LASTFAILED_MAX_AGE_SECONDS:
        return []

    try:
        lastfailed = json.loads(lastfailed_path.read_text(encoding="utf-8"))
    except Exception:
        return []

    if not isinstance(lastfailed, dict) or not lastfailed:
        return []

    register_lower = register_content.lower()
    errors: list[str] = []
    for nodeid, failed in lastfailed.items():
        if not failed:
            continue
        file_path, func_name = _extract_test_identifiers(nodeid)
        # Primárně ověřujeme konkrétní název testu; na soubor padáme jen u import/module chyb
        is_reported = (
            (func_name.lower() in register_lower)
            if func_name
            else bool(file_path and file_path.lower() in register_lower)
        )
        if not is_reported:
            errors.append(
                f"Padající test `{nodeid}` nemá report v `docs/JIRA_BUG_REPORTS.md` "
                "(pokud šlo o Test Bug, oprav test a spusť jej znovu)."
            )
    return errors


def _is_repeated_block(conversation_id: str, reason: str) -> bool:
    """Pojistka proti zacyklení: nepustí stejnou blokaci dvakrát za sebou v jedné konverzaci."""
    conv_key = hashlib.sha256((conversation_id or "default").encode("utf-8")).hexdigest()[:12]
    reason_hash = hashlib.sha256(reason.encode("utf-8")).hexdigest()[:16]
    state_file = Path(tempfile.gettempdir()) / f"check_bug_dod_{conv_key}.json"

    now = time.time()
    try:
        if state_file.exists():
            prev = json.loads(state_file.read_text(encoding="utf-8"))
            if (
                prev.get("reason_hash") == reason_hash
                and (now - float(prev.get("ts", 0))) < LOOP_GUARD_TTL_SECONDS
            ):
                state_file.unlink(missing_ok=True)
                return True
        state_file.write_text(json.dumps({"reason_hash": reason_hash, "ts": now}), encoding="utf-8")
    except Exception:
        return False
    return False


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return 0

    if not isinstance(payload, dict):
        print(json.dumps({"decision": "allow"}))
        return 0

    if (
        payload.get("continuationActive")
        or payload.get("stopHookActive")
        or payload.get("stop_hook_active")
        or payload.get("terminationReason") in ("USER_CANCELED", "ERROR")
    ):
        print(json.dumps({"decision": "allow"}))
        return 0

    root = _get_workspace_root(payload)
    html_path = root / "docs" / "bug_reports.html"
    html_content, html_errors = _check_html(html_path)
    register_content, reg_errors = _check_register(root / "docs" / "JIRA_BUG_REPORTS.md", html_path, html_content)
    test_errors = _check_lastfailed(root / ".pytest_cache" / "v" / "cache" / "lastfailed", register_content)

    errors = html_errors + reg_errors + test_errors
    if errors:
        reason = "Definice hotovo (Stop hook) není splněna:\n- " + "\n- ".join(errors[:5])
        if _is_repeated_block(str(payload.get("conversationId", "")), reason):
            print(json.dumps({"decision": "allow"}))
            return 0
        print(json.dumps({"decision": "continue", "reason": reason}, ensure_ascii=False))
        return 0

    print(json.dumps({"decision": "allow"}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

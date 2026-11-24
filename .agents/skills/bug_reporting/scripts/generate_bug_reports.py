#!/usr/bin/env python3
"""
Bug Reports HTML Generator for E2E Test Suite
=============================================
Parsuje centrální registr defektů v docs/JIRA_BUG_REPORTS.md a generuje
interaktivní HTML dashboard docs/bug_reports.html ve stejném vizuálním stylu
jako docs/story_coverage.html.

Použití:
  python3 generate_bug_reports.py
  python3 generate_bug_reports.py --output docs/bug_reports.html
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_DOCS_PATH = PROJECT_ROOT / "docs" / "JIRA_BUG_REPORTS.md"
DEFAULT_OUTPUT_PATH = PROJECT_ROOT / "docs" / "bug_reports.html"

MODULE_CSS_CLASSES = {
    "AUTH": "mod-auth",
    "CRS": "mod-crs",
    "ENR": "mod-enr",
    "LEC": "mod-lec",
    "PRF": "mod-prf",
    "SEC": "mod-sec",
    "RBAC": "mod-sec",
}


def normalize_severity(raw: str) -> str:
    """Normalizuje závažnost na jednu z kategorií: Critical, High, Medium, Low."""
    low = raw.lower()
    if "critical" in low or "blocker" in low:
        return "Critical"
    if "high" in low:
        return "High"
    if "medium" in low:
        return "Medium"
    if "low" in low:
        return "Low"
    return raw.strip() or "Medium"


def normalize_priority(raw: str) -> str:
    """Normalizuje prioritu na High, Medium nebo Low."""
    low = raw.lower()
    if "high" in low:
        return "High"
    if "medium" in low:
        return "Medium"
    if "low" in low:
        return "Low"
    return raw.strip() or "Medium"


def normalize_status(raw: str) -> tuple[str, str]:
    """Vrátí (klíč_stavu, zobrazovaný_text) pro stav incidentu."""
    low = raw.lower()
    if "vyřešeno" in low or "closed" in low or "verified" in low or "🟢" in raw:
        return ("closed", raw.strip())
    if "řešení" in low or "progress" in low or "🟡" in raw:
        return ("in_progress", raw.strip())
    return ("open", raw.strip() or "🔴 Otevřeno")


def resolve_module_code(raw_module: str) -> str:
    """Určí primární kód modulu pro CSS třídu a filtrování."""
    upper = raw_module.upper()
    for code in ("SEC", "AUTH", "CRS", "ENR", "LEC", "PRF"):
        if code in upper:
            return code
    if "RBAC" in upper:
        return "SEC"
    return raw_module.strip().split("/")[0].strip().upper() or "OTHER"


def severity_badge_class(severity: str) -> str:
    """Vrátí CSS třídu pro badge závažnosti."""
    return {
        "Critical": "badge-danger",
        "High": "badge-amber",
        "Medium": "badge-warning",
        "Low": "badge-muted",
    }.get(severity, "badge-warning")


def status_badge_class(status_key: str) -> str:
    """Vrátí CSS třídu pro badge stavu."""
    return {
        "open": "badge-danger",
        "in_progress": "badge-warning",
        "closed": "badge-success",
    }.get(status_key, "badge-danger")


def render_inline_markdown(text: str) -> str:
    """Bezpečně převede inline Markdown (odkazy, kód, tučný text, kurzíva) na HTML."""
    # Nejprve rozdělíme podle inline kódu `...`, abychom neupravovali obsah uvnitř backticků
    parts = re.split(r"(`[^`]+`)", text)
    rendered_parts: list[str] = []

    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) >= 2:
            code_inner = html.escape(part[1:-1])
            rendered_parts.append(f"<code>{code_inner}</code>")
            continue

        # Escapujeme HTML znaky v běžném textu
        escaped = html.escape(part)

        # Markdown obrázky ![alt](url) -> náhled obrázku s odkazem
        def _replace_image(match: re.Match[str]) -> str:
            alt = match.group(1) or "Screenshot"
            src = match.group(2)
            return f'<a href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="{alt}" class="inline-thumb" loading="lazy"></a>'

        escaped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", _replace_image, escaped)

        # Markdown odkazy [text](url) -> klikací odkaz (nebo zvýrazněný odkaz)
        def _replace_link(match: re.Match[str]) -> str:
            label = match.group(1)
            href = match.group(2)
            # Odstraníme případné `...` uvnitř labelu
            label_clean = re.sub(r"`([^`]+)`", r"<code>\1</code>", label)
            if href.startswith("#"):
                return f'<a href="{href}">{label_clean}</a>'
            return f'<a href="{href}" target="_blank" rel="noopener">{label_clean}</a>'

        escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", _replace_link, escaped)
        # Tučný text **...**
        escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
        # Kurzíva *...*
        escaped = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", escaped)
        rendered_parts.append(escaped)

    return "".join(rendered_parts)


def render_markdown_block(md_text: str) -> str:
    """Převede blok Markdownu (odstavce, seznamy, code blocky) na čisté HTML."""
    lines = md_text.strip().splitlines()
    html_out: list[str] = []
    in_code = False
    code_lines: list[str] = []
    list_type: str | None = None  # "ul" nebo "ol"

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            html_out.append(f"</{list_type}>")
            list_type = None

    for line in lines:
        stripped = line.strip()

        # Kódové bloky ```...```
        if stripped.startswith("```"):
            if in_code:
                code_html = html.escape("\n".join(code_lines))
                html_out.append(f'<pre class="code-block"><code>{code_html}</code></pre>')
                code_lines = []
                in_code = False
            else:
                close_list()
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not stripped or stripped == "---":
            close_list()
            continue

        # Nečíslovaný seznam (- nebo *)
        ul_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if ul_match:
            if list_type != "ul":
                close_list()
                html_out.append('<ul class="md-list">')
                list_type = "ul"
            html_out.append(f"<li>{render_inline_markdown(ul_match.group(1))}</li>")
            continue

        # Číslovaný seznam (1. ...)
        ol_match = re.match(r"^\d+\.\s+(.+)$", stripped)
        if ol_match:
            if list_type != "ol":
                close_list()
                html_out.append('<ol class="md-list">')
                list_type = "ol"
            html_out.append(f"<li>{render_inline_markdown(ol_match.group(1))}</li>")
            continue

        # Podpoložka seznamu odsazená mezerami (např. "  - ...")
        sub_ul_match = re.match(r"^\s{2,}[-*]\s+(.+)$", line)
        if sub_ul_match and list_type:
            html_out.append(f'<li class="sub-item">{render_inline_markdown(sub_ul_match.group(1))}</li>')
            continue

        close_list()
        html_out.append(f"<p>{render_inline_markdown(stripped)}</p>")

    if in_code and code_lines:
        code_html = html.escape("\n".join(code_lines))
        html_out.append(f'<pre class="code-block"><code>{code_html}</code></pre>')
    close_list()

    return "\n".join(html_out)


def parse_summary_table(content: str) -> dict[str, dict[str, str]]:
    """Načte přehledovou tabulku defektů z horní části JIRA_BUG_REPORTS.md."""
    summary_map: dict[str, dict[str, str]] = {}
    row_pattern = re.compile(
        r"\|\s*\[\*\*(BR-\d+)\*\*\]\([^)]+\)\s*\|\s*`?([^`|]+)`?\s*\|\s*([^|]+)\s*\|\s*"
        r"\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
    )
    for match in row_pattern.finditer(content):
        bug_id = match.group(1).strip().upper()
        summary_map[bug_id] = {
            "module_display": match.group(2).strip(),
            "title": match.group(3).strip(),
            "severity": normalize_severity(match.group(4)),
            "priority": normalize_priority(match.group(5)),
            "linked_us": match.group(6).strip(),
            "status_raw": match.group(7).strip(),
        }
    return summary_map


def parse_bug_reports(docs_path: Path) -> list[dict[str, Any]]:
    """Parsuje všechny bug reporty z docs/JIRA_BUG_REPORTS.md."""
    if not docs_path.exists():
        raise FileNotFoundError(f"Registr chyb nebyl nalezen: {docs_path}")

    content = docs_path.read_text(encoding="utf-8")
    summary_map = parse_summary_table(content)

    # Rozdělení detailních sekcí podle ### 🐞 BR-XX
    detail_pattern = re.compile(r"^###\s+🐞\s+(BR-\d+)\s*(?:\[([^\]]+)\])?:\s*(.+)$", re.MULTILINE)
    matches = list(detail_pattern.finditer(content))
    bugs: list[dict[str, Any]] = []

    for idx, match in enumerate(matches):
        bug_id = match.group(1).strip().upper()
        heading_module = (match.group(2) or "").strip()
        heading_title = match.group(3).strip()

        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(content)
        body = content[start:end].strip()

        # Rozdělení na podsekce #### ...
        sec_pattern = re.compile(r"^####\s+(.+)$", re.MULTILINE)
        sec_matches = list(sec_pattern.finditer(body))

        metadata_items: list[tuple[str, str]] = []
        sections: list[tuple[str, str]] = []

        for s_idx, s_match in enumerate(sec_matches):
            sec_title = s_match.group(1).strip()
            s_start = s_match.end()
            s_end = sec_matches[s_idx + 1].start() if s_idx + 1 < len(sec_matches) else len(body)
            sec_body = body[s_start:s_end].strip()
            # Odstranění koncového oddělovače ---
            sec_body = re.sub(r"\n---\s*$", "", sec_body).strip()

            if "metadata" in sec_title.lower():
                metadata_items = parse_metadata_list(sec_body)
            else:
                sections.append((sec_title, sec_body))

        table_info = summary_map.get(bug_id, {})
        module_display = table_info.get("module_display") or heading_module or "OTHER"
        module_code = resolve_module_code(module_display)

        # Záložní extrakce závažnosti/priority z metadat, pokud chybí v tabulce
        sev_raw = table_info.get("severity") or _find_meta(metadata_items, "Závažnost") or "Medium"
        prio_raw = table_info.get("priority") or _find_meta(metadata_items, "Priorita") or "Medium"
        severity = normalize_severity(sev_raw)
        priority = normalize_priority(prio_raw)

        status_key, status_display = normalize_status(table_info.get("status_raw", "🔴 Otevřeno"))
        linked_us = table_info.get("linked_us") or ", ".join(dict.fromkeys(re.findall(r"US-\d+", body))) or "—"
        us_list = list(dict.fromkeys(re.findall(r"US-\d+", linked_us + " " + body)))
        browser_verify = _find_meta(metadata_items, "Ověření v prohlížeči")

        bugs.append(
            {
                "bug_id": bug_id,
                "module_display": module_display,
                "module_code": module_code,
                "title": table_info.get("title") or heading_title,
                "severity": severity,
                "priority": priority,
                "status_key": status_key,
                "status_display": status_display,
                "browser_verify": browser_verify,
                "linked_us": linked_us,
                "us_list": us_list,
                "metadata": metadata_items,
                "sections": sections,
                "raw_markdown": f"### 🐞 {bug_id} [{heading_module or module_display}]: {heading_title}\n\n{body}".strip(),
            }
        )

    return bugs


def parse_metadata_list(sec_body: str) -> list[tuple[str, str]]:
    """Parsuje odrážkový seznam metadat JIRA ticketu včetně vnořených odrážek."""
    items: list[tuple[str, str]] = []
    current_key: str | None = None
    current_val_lines: list[str] = []

    for line in sec_body.splitlines():
        top_match = re.match(r"^\*\s+\*\*([^*:]+):\*\*\s*(.*)$", line)
        if top_match:
            if current_key is not None:
                items.append((current_key, "\n".join(current_val_lines).strip()))
            current_key = top_match.group(1).strip()
            val = top_match.group(2).strip()
            current_val_lines = [val] if val else []
        elif current_key is not None and line.strip():
            current_val_lines.append(line.strip())

    if current_key is not None:
        items.append((current_key, "\n".join(current_val_lines).strip()))

    return items


def _find_meta(metadata: list[tuple[str, str]], prefix: str) -> str:
    for k, v in metadata:
        if k.lower().startswith(prefix.lower()):
            return v
    return ""


def _resolve_screenshot_href(raw_path: str, output_dir: Path) -> str:
    """Převede cestu ke screenshotu na relativní odkaz vůči umístění HTML souboru."""
    cleaned = raw_path.strip().strip("`\"'")
    if cleaned.startswith(("http://", "https://", "data:")):
        return cleaned

    candidate = Path(cleaned)
    if not candidate.is_absolute():
        from_project = (PROJECT_ROOT / cleaned).resolve()
        from_output = (output_dir / cleaned).resolve()
        resolved = from_project if from_project.exists() or not from_output.exists() else from_output
    else:
        resolved = candidate

    try:
        return Path(
            *([".."] * len(output_dir.resolve().relative_to(PROJECT_ROOT.resolve()).parts)),
            resolved.relative_to(PROJECT_ROOT.resolve()),
        ).as_posix()
    except ValueError:
        return cleaned


def render_screenshot_gallery(sec_body: str, output_dir: Path) -> str:
    """Vyhledá odkazy na obrázky screenshotů v textu a vykreslí jejich HTML náhledy."""
    img_matches = re.findall(
        r"(?:!\[[^\]]*\]\(([^)]+\.(?:png|jpe?g|webp|gif))\)|[`\"']?((?:\.\./)?reports/screenshots/[^\s`\"')>]+?\.(?:png|jpe?g|webp|gif))[`\"']?)",
        sec_body,
        flags=re.IGNORECASE,
    )
    paths: list[str] = []
    for m_alt, m_raw in img_matches:
        raw = m_alt or m_raw
        if raw and raw not in paths:
            paths.append(raw)

    if not paths:
        return ""

    cards: list[str] = []
    for raw in paths:
        href = html.escape(_resolve_screenshot_href(raw, output_dir))
        filename = html.escape(Path(raw).name)
        cards.append(
            f'<a class="evidence-card" href="{href}" target="_blank" rel="noopener" title="Otevřít {filename} v novém okně">'
            f'<img src="{href}" alt="{filename}" class="evidence-thumb" loading="lazy">'
            f'<span class="evidence-caption">🖼️ {filename}</span>'
            f"</a>"
        )
    return f'<div class="evidence-gallery">{"".join(cards)}</div>'


def _render_verify_badge(raw_verify: str) -> str:
    """Vrátí HTML badge pro stav ověření v prohlížeči."""
    if not raw_verify:
        return ""
    low = raw_verify.lower()
    if "nereprodukováno" in low:
        cls = "badge-warning"
        icon = "⚠️"
    elif "reprodukováno" in low:
        cls = "badge-danger"
        icon = "🌐"
    else:
        cls = "badge-muted"
        icon = "ℹ️"
    return f'<span class="badge {cls}" title="Ověření v prohlížeči">{icon} {html.escape(raw_verify)}</span>'


def build_html(bugs: list[dict[str, Any]], output_dir: Path = DEFAULT_OUTPUT_PATH.parent) -> str:
    """Sestaví kompletní interaktivní HTML report ve stylu story_coverage.html."""
    total_bugs = len(bugs)
    open_count = sum(1 for b in bugs if b["status_key"] == "open")
    in_progress_count = sum(1 for b in bugs if b["status_key"] == "in_progress")
    closed_count = sum(1 for b in bugs if b["status_key"] == "closed")

    critical_count = sum(1 for b in bugs if b["severity"] == "Critical")
    high_count = sum(1 for b in bugs if b["severity"] == "High")
    medium_count = sum(1 for b in bugs if b["severity"] == "Medium")
    low_count = sum(1 for b in bugs if b["severity"] == "Low")

    active_modules = sorted({b["module_code"] for b in bugs})
    unique_us = sorted({us for b in bugs for us in b["us_list"]})
    generated_at = datetime.now().strftime("%d. %m. %Y %H:%M")

    # Sestavení řádků tabulky a detailních akordeonů
    rows_html: list[str] = []
    for idx, bug in enumerate(bugs):
        bug_id = bug["bug_id"]
        mod_code = bug["module_code"]
        mod_cls = MODULE_CSS_CLASSES.get(mod_code, "")
        sev_cls = severity_badge_class(bug["severity"])
        prio_cls = severity_badge_class(bug["priority"])
        stat_cls = status_badge_class(bug["status_key"])

        search_blob = html.escape(
            f"{bug_id} {bug['module_display']} {bug['title']} {bug['severity']} "
            f"{bug['priority']} {bug['linked_us']} {bug['raw_markdown'][:600]}".lower()
        )

        # Metadata tabulka uvnitř detailu
        meta_rows = []
        for k, v in bug["metadata"]:
            # Zkrácený výpis víceřádkové hodnoty (např. US / TC)
            if "\n" in v:
                val_html = render_markdown_block(v)
            else:
                val_html = render_inline_markdown(v)
            meta_rows.append(
                f"<tr><td class='meta-key'>{html.escape(k)}</td><td class='meta-val'>{val_html}</td></tr>"
            )
        meta_table_html = f"<table class='meta-table'>{''.join(meta_rows)}</table>"

        # Sekce detailu
        sections_html: list[str] = []
        for sec_title, sec_body in bug["sections"]:
            sec_content_html = render_markdown_block(sec_body)
            gallery_html = ""
            # Zvýraznění karet Očekávané vs. Skutečné chování a náhledy screenshotů
            extra_cls = ""
            if "očekávané" in sec_title.lower():
                extra_cls = " sec-expected"
            elif "skutečné" in sec_title.lower():
                extra_cls = " sec-actual"
            elif "dopad" in sec_title.lower():
                extra_cls = " sec-impact"
            elif "důkaz" in sec_title.lower() or "screenshot" in sec_title.lower():
                gallery_html = render_screenshot_gallery(sec_body, output_dir)

            sections_html.append(
                f"""
                <div class="detail-section{extra_cls}">
                    <h4>{html.escape(sec_title)}</h4>
                    <div class="sec-body">{sec_content_html}{gallery_html}</div>
                </div>
                """
            )

        verify_badge_html = _render_verify_badge(bug.get("browser_verify", ""))
        raw_escaped = html.escape(bug["raw_markdown"])
        row_id = f"detail-{idx}"

        rows_html.append(
            f"""
            <tr class="story-row"
                data-status="{bug['status_key']}"
                data-severity="{bug['severity'].lower()}"
                data-module="{mod_code}"
                data-search="{search_blob}"
                onclick="toggleDetail('{row_id}', this)">
                <td><strong>{html.escape(bug_id)}</strong></td>
                <td><span class="module-tag {mod_cls}">{html.escape(bug['module_display'])}</span></td>
                <td class="col-title">{html.escape(bug['title'])}</td>
                <td class="text-center"><span class="badge {sev_cls}">{html.escape(bug['severity'])}</span></td>
                <td class="text-center"><span class="badge {prio_cls}">{html.escape(bug['priority'])}</span></td>
                <td>{html.escape(bug['linked_us'])}</td>
                <td class="text-center"><span class="badge {stat_cls}">{html.escape(bug['status_display'])}</span></td>
                <td class="text-center"><button class="btn-toggle" aria-label="Zobrazit detail">▼</button></td>
            </tr>
            <tr id="{row_id}" class="accordion-content">
                <td colspan="8">
                    <div class="accordion-inner">
                        <div class="detail-actions">
                            <div class="detail-title-group">
                                <span class="detail-id-label">📌 Detail hlášení {html.escape(bug_id)}</span>
                                {verify_badge_html}
                            </div>
                            <button type="button" class="btn-copy" onclick="copyJiraMarkdown(event, 'raw-{idx}', this)">
                                📋 Kopírovat pro JIRA
                            </button>
                            <textarea id="raw-{idx}" class="hidden-raw" readonly>{raw_escaped}</textarea>
                        </div>
                        <div class="detail-section">
                            <h4>📋 JIRA Ticket Metadata</h4>
                            {meta_table_html}
                        </div>
                        <div class="sections-grid">
                            {''.join(sections_html)}
                        </div>
                    </div>
                </td>
            </tr>
            """
        )

    module_buttons = "".join(
        f'<button class="filter-btn" data-filter-type="module" data-value="{m}">{m}</button>'
        for m in active_modules
    )

    return f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Centrální registr chyb (JIRA Bug Reports)</title>
    <style>
        :root {{
            --bg-page: #f8fafc;
            --bg-card: #ffffff;
            --border-color: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --success: #16a34a;
            --success-bg: #dcfce7;
            --warning: #d97706;
            --warning-bg: #fef3c7;
            --danger: #dc2626;
            --danger-bg: #fee2e2;
            --amber: #ea580c;
            --amber-bg: #ffedd5;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg-page);
            color: var(--text-main);
            padding: 30px 20px;
            line-height: 1.5;
        }}
        .container {{ max-width: 1300px; margin: 0 auto; }}
        header {{ margin-bottom: 28px; }}
        h1 {{ font-size: 26px; font-weight: 700; color: #0f172a; margin-bottom: 6px; }}
        .subtitle {{ color: var(--text-muted); font-size: 14px; }}

        /* KPI Cards */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .kpi-title {{ font-size: 12px; font-weight: 600; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 28px; font-weight: 700; color: var(--text-main); margin-top: 4px; }}
        .kpi-sub {{ font-size: 13px; color: var(--text-muted); margin-top: 2px; }}

        /* Filter Toolbar */
        .toolbar {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 14px 18px;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }}
        .toolbar-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            justify-content: space-between;
        }}
        .filter-group {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }}
        .filter-label {{ font-size: 12px; font-weight: 600; color: var(--text-muted); margin-right: 4px; text-transform: uppercase; }}
        .filter-btn {{
            background: #f1f5f9;
            border: 1px solid transparent;
            color: #475569;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.15s ease;
        }}
        .filter-btn:hover {{ background: #e2e8f0; }}
        .filter-btn.active {{
            background: var(--primary);
            color: #ffffff;
            font-weight: 600;
        }}
        .search-box {{
            padding: 7px 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 13px;
            width: 280px;
            outline: none;
        }}
        .search-box:focus {{ border-color: var(--primary); }}

        /* Table */
        .table-wrap {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        table {{ width: 100%; border-collapse: collapse; text-align: left; font-size: 14px; }}
        th {{
            background: #f8fafc;
            color: #475569;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
        }}
        td {{ padding: 12px 16px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }}
        tr.story-row {{ cursor: pointer; transition: background 0.1s ease; }}
        tr.story-row:hover {{ background: #f1f5f9; }}
        .text-center {{ text-align: center; }}
        .col-title {{ font-weight: 500; max-width: 400px; }}

        /* Badges & Tags */
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            white-space: nowrap;
        }}
        .badge-success {{ background: var(--success-bg); color: var(--success); }}
        .badge-warning {{ background: var(--warning-bg); color: var(--warning); }}
        .badge-danger {{ background: var(--danger-bg); color: var(--danger); }}
        .badge-amber {{ background: var(--amber-bg); color: var(--amber); }}
        .badge-muted {{ background: #f1f5f9; color: var(--text-muted); }}

        .module-tag {{
            display: inline-block;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            background: #e2e8f0;
            color: #334155;
            white-space: nowrap;
        }}
        .mod-auth {{ background: #e0e7ff; color: #3730a3; }}
        .mod-crs {{ background: #dbeafe; color: #1e40af; }}
        .mod-enr {{ background: #ccfbf1; color: #115e59; }}
        .mod-lec {{ background: #fef3c7; color: #92400e; }}
        .mod-prf {{ background: #f3e8ff; color: #6b21a8; }}
        .mod-sec {{ background: #fee2e2; color: #991b1b; }}

        .btn-toggle {{
            background: none;
            border: none;
            font-size: 12px;
            cursor: pointer;
            color: var(--text-muted);
            transition: transform 0.2s ease;
        }}
        .btn-toggle.open {{ transform: rotate(180deg); color: var(--primary); }}

        /* Accordion Detail */
        tr.accordion-content {{ display: none; background: #fafafa; }}
        tr.accordion-content.show {{ display: table-row; }}
        .accordion-inner {{ padding: 20px 24px; }}
        .detail-actions {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }}
        .detail-id-label {{ font-size: 15px; font-weight: 700; color: var(--text-main); }}
        .detail-title-group {{ display: flex; flex-wrap: wrap; align-items: center; gap: 10px; }}
        .evidence-gallery {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-top: 12px;
        }}
        .evidence-card {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            max-width: 340px;
            padding: 8px;
            background: #f8fafc;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            text-decoration: none;
            transition: border-color 0.15s ease, box-shadow 0.15s ease;
        }}
        .evidence-card:hover {{
            border-color: var(--primary);
            box-shadow: 0 2px 8px rgba(37, 99, 235, 0.12);
            text-decoration: none !important;
        }}
        .evidence-thumb {{
            width: 100%;
            max-height: 210px;
            object-fit: cover;
            border-radius: 4px;
            border: 1px solid var(--border-color);
            display: block;
        }}
        .inline-thumb {{
            max-width: 340px;
            max-height: 210px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            margin-top: 6px;
            display: block;
        }}
        .evidence-caption {{
            font-size: 12px;
            font-weight: 500;
            color: var(--text-muted);
            word-break: break-all;
        }}
        .btn-copy {{
            background: var(--primary);
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 7px 14px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.15s ease;
        }}
        .btn-copy:hover {{ opacity: 0.9; }}
        .btn-copy.copied {{ background: var(--success); }}
        .hidden-raw {{ position: absolute; left: -9999px; opacity: 0; }}

        .detail-section {{
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px 18px;
            margin-bottom: 14px;
        }}
        .detail-section h4 {{
            font-size: 13px;
            text-transform: uppercase;
            color: #475569;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 6px;
        }}
        .sec-expected {{ border-left: 4px solid var(--success); }}
        .sec-actual {{ border-left: 4px solid var(--danger); }}
        .sec-impact {{ border-left: 4px solid var(--warning); }}

        .sections-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 14px;
        }}
        .sec-body p {{ margin-bottom: 8px; font-size: 13.5px; color: #334155; }}
        .sec-body p:last-child {{ margin-bottom: 0; }}
        .md-list {{ padding-left: 20px; margin-bottom: 8px; font-size: 13.5px; color: #334155; }}
        .md-list li {{ margin-bottom: 4px; }}
        .md-list li.sub-item {{ margin-left: 18px; list-style-type: circle; }}
        .sec-body code, .meta-val code {{
            background: #f1f5f9;
            color: #0f172a;
            padding: 1px 5px;
            border-radius: 4px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
        }}
        .sec-body a, .meta-val a {{ color: var(--primary); text-decoration: none; }}
        .sec-body a:hover, .meta-val a:hover {{ text-decoration: underline; }}

        .code-block {{
            background: #0f172a;
            color: #f8fafc;
            padding: 12px 14px;
            border-radius: 6px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
            overflow-x: auto;
            margin-top: 6px;
            line-height: 1.45;
        }}
        .code-block code {{ background: none; color: inherit; padding: 0; font-size: inherit; }}

        .meta-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
        .meta-table td {{ padding: 6px 10px; border-bottom: 1px solid #f1f5f9; vertical-align: top; }}
        .meta-table tr:last-child td {{ border-bottom: none; }}
        .meta-key {{ width: 210px; font-weight: 600; color: #475569; }}
        .meta-val {{ color: #1e293b; }}

        .empty-state {{
            display: none;
            text-align: center;
            padding: 32px;
            color: var(--text-muted);
            font-size: 14px;
        }}

        footer {{
            margin-top: 24px;
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐞 Centrální registr chyb (JIRA Bug Reports)</h1>
            <p class="subtitle">Přehled evidovaných defektů aplikace testovani.kitner.cz | Zdroj: <code>docs/JIRA_BUG_REPORTS.md</code> | Vygenerováno: {generated_at}</p>
        </header>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Celkem defektů</div>
                <div class="kpi-value">{total_bugs}</div>
                <div class="kpi-sub">Otevřeno: {open_count} | V řešení: {in_progress_count} | Vyřešeno: {closed_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Critical &amp; High</div>
                <div class="kpi-value" style="color: var(--danger);">{critical_count + high_count}</div>
                <div class="kpi-sub">Critical: {critical_count} | High: {high_count} | Medium: {medium_count} | Low: {low_count}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Zasažené moduly</div>
                <div class="kpi-value" style="color: var(--primary);">{len(active_modules)}</div>
                <div class="kpi-sub">{", ".join(active_modules) if active_modules else "—"}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Dotčené User Stories</div>
                <div class="kpi-value" style="color: var(--warning);">{len(unique_us)}</div>
                <div class="kpi-sub">{", ".join(unique_us) if unique_us else "—"}</div>
            </div>
        </div>

        <div class="toolbar">
            <div class="toolbar-row">
                <div class="filter-group">
                    <span class="filter-label">Stav:</span>
                    <button class="filter-btn active" data-filter-type="status" data-value="all">Vše</button>
                    <button class="filter-btn" data-filter-type="status" data-value="open">🔴 Otevřeno</button>
                    <button class="filter-btn" data-filter-type="status" data-value="in_progress">🟡 V řešení</button>
                    <button class="filter-btn" data-filter-type="status" data-value="closed">🟢 Vyřešeno</button>
                </div>
                <input type="text" id="searchInput" class="search-box" placeholder="Hledat BR-XX, název, US-XX, text..." oninput="applyFilters()">
            </div>
            <div class="toolbar-row">
                <div class="filter-group">
                    <span class="filter-label">Závažnost:</span>
                    <button class="filter-btn active" data-filter-type="severity" data-value="all">Vše</button>
                    <button class="filter-btn" data-filter-type="severity" data-value="critical">Critical</button>
                    <button class="filter-btn" data-filter-type="severity" data-value="high">High</button>
                    <button class="filter-btn" data-filter-type="severity" data-value="medium">Medium</button>
                    <button class="filter-btn" data-filter-type="severity" data-value="low">Low</button>
                </div>
                <div class="filter-group">
                    <span class="filter-label">Modul:</span>
                    <button class="filter-btn active" data-filter-type="module" data-value="all">Vše</button>
                    {module_buttons}
                </div>
            </div>
        </div>

        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th style="width: 90px;">ID</th>
                        <th style="width: 120px;">Modul</th>
                        <th>Název incidentu</th>
                        <th class="text-center" style="width: 110px;">Závažnost</th>
                        <th class="text-center" style="width: 100px;">Priorita</th>
                        <th style="width: 130px;">Vázaná US</th>
                        <th class="text-center" style="width: 130px;">Stav</th>
                        <th class="text-center" style="width: 60px;">Detail</th>
                    </tr>
                </thead>
                <tbody id="bugsTableBody">
                    {''.join(rows_html)}
                </tbody>
            </table>
            <div id="emptyState" class="empty-state">Žádný bug report neodpovídá zvoleným filtrům.</div>
        </div>

        <footer>
            Automaticky generováno z <code>docs/JIRA_BUG_REPORTS.md</code> pomocí <code>generate_bug_reports.py</code>
        </footer>
    </div>

    <script>
        const activeFilters = {{
            status: 'all',
            severity: 'all',
            module: 'all'
        }};

        document.querySelectorAll('.filter-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                const type = btn.dataset.filterType;
                const val = btn.dataset.value;
                activeFilters[type] = val;

                document.querySelectorAll(`.filter-btn[data-filter-type="${{type}}"]`).forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                applyFilters();
            }});
        }});

        function applyFilters() {{
            const query = document.getElementById('searchInput').value.trim().toLowerCase();
            const rows = document.querySelectorAll('tr.story-row');
            let visibleCount = 0;

            rows.forEach((row, idx) => {{
                const matchStatus = activeFilters.status === 'all' || row.dataset.status === activeFilters.status;
                const matchSev = activeFilters.severity === 'all' || row.dataset.severity === activeFilters.severity;
                const matchMod = activeFilters.module === 'all' || row.dataset.module === activeFilters.module;
                const matchSearch = !query || row.dataset.search.includes(query);

                const detailRow = document.getElementById(`detail-${{idx}}`);
                if (matchStatus && matchSev && matchMod && matchSearch) {{
                    row.style.display = '';
                    visibleCount++;
                }} else {{
                    row.style.display = 'none';
                    if (detailRow) detailRow.classList.remove('show');
                    const toggle = row.querySelector('.btn-toggle');
                    if (toggle) toggle.classList.remove('open');
                }}
            }});

            document.getElementById('emptyState').style.display = visibleCount === 0 ? 'block' : 'none';
        }}

        function toggleDetail(detailId, rowEl) {{
            const detailRow = document.getElementById(detailId);
            const btn = rowEl.querySelector('.btn-toggle');
            if (!detailRow) return;
            const isOpen = detailRow.classList.toggle('show');
            if (btn) btn.classList.toggle('open', isOpen);
        }}

        function copyJiraMarkdown(event, textareaId, btnEl) {{
            event.stopPropagation();
            const textarea = document.getElementById(textareaId);
            if (!textarea) return;
            navigator.clipboard.writeText(textarea.value).then(() => {{
                const original = btnEl.textContent;
                btnEl.textContent = '✅ Zkopírováno!';
                btnEl.classList.add('copied');
                setTimeout(() => {{
                    btnEl.textContent = original;
                    btnEl.classList.remove('copied');
                }}, 1800);
            }});
        }}
    </script>
</body>
</html>
"""


def generate_bug_reports_html(
    docs_path: Path = DEFAULT_DOCS_PATH,
    output_path: Path = DEFAULT_OUTPUT_PATH,
) -> Path:
    """Vygeneruje HTML report z docs/JIRA_BUG_REPORTS.md a uloží ho do output_path."""
    bugs = parse_bug_reports(docs_path)
    html_content = build_html(bugs, output_dir=output_path.parent)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generátor HTML přehledu bug reportů z docs/JIRA_BUG_REPORTS.md")
    parser.add_argument("--docs-path", type=Path, default=DEFAULT_DOCS_PATH, help="Cesta k JIRA_BUG_REPORTS.md")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Výstupní cesta HTML souboru")
    parser.add_argument("--quiet", action="store_true", help="Tichý režim bez výpisu")
    args = parser.parse_args()

    try:
        out = generate_bug_reports_html(args.docs_path, args.output)
        if not args.quiet:
            print(f"✅ HTML report bugů byl úspěšně vygenerován: {out}")
    except Exception as exc:
        print(f"❌ Chyba při generování HTML reportu: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

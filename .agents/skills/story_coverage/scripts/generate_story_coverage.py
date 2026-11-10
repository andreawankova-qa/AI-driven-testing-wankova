#!/usr/bin/env python3
"""
Story Coverage Generator for E2E Test Suite
============================================
Analyzuje pokrytí byznysových User Stories automatizovanými testy
a generuje interaktivní HTML dashboard s akordeonem pro akceptační kritéria.

Zdroje dat:
1. docs/požadavky_ust_podle_src.md (User Stories a akceptační kritéria)
2. docs/TEST_CASES.md (Katalog testovacích případů a mapování na AK)
3. tests/**/*.py (Kód testů, markery a stav @pytest.mark.xfail)
4. docs/JIRA_BUG_REPORTS.md (Evidované defekty aplikace)

Použití:
  python3 generate_story_coverage.py
  python3 generate_story_coverage.py --output reports/story_coverage.html
"""

import os
import re
import sys
import ast
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Set

MODULE_NAMES = {
    "AUTH": "Autentizace a správa sezení",
    "CRS": "Katalog kurzů a detail",
    "ENR": "Zápis na kurz a Moje kurzy",
    "LEC": "Lektorská správa kurzů",
    "PRF": "Uživatelský profil a nástěnka",
    "SEC": "Bezpečnost a autorizace (RBAC)",
}


class AcceptanceCriterion:
    def __init__(self, index: int, text: str):
        self.index = index
        self.code = f"AK-{index}"
        self.text = text


class UserStory:
    def __init__(self, us_id: str, title: str, module_code: str, actor: str = "", goal: str = "", benefit: str = ""):
        self.us_id = us_id.upper()
        self.title = title
        self.module_code = module_code.upper()
        self.module_name = MODULE_NAMES.get(self.module_code, self.module_code)
        self.actor = actor
        self.goal = goal
        self.benefit = benefit
        self.criteria: List[AcceptanceCriterion] = []
        self.test_cases: List[Dict[str, Any]] = []


class TestCase:
    def __init__(self, tc_id: str, us_id: str, title: str, priority_type: str, covered_aks: List[str]):
        self.tc_id = tc_id.upper()
        self.us_id = us_id.upper()
        self.title = title
        self.priority_type = priority_type
        self.covered_aks = covered_aks
        self.automated_test: Optional[Dict[str, Any]] = None


def parse_user_stories(file_path: Path) -> Dict[str, UserStory]:
    """Parsuje docs/požadavky_ust_podle_src.md a vrací slovník User Stories s jejich AK."""
    stories: Dict[str, UserStory] = {}
    if not file_path.exists():
        return stories

    content = file_path.read_text(encoding="utf-8")
    header_pattern = re.compile(r'####\s*(?P<us_id>US-\d+):\s*(?P<title>[^\n]+)')
    splits = header_pattern.split(content)

    i = 1
    while i < len(splits):
        us_id = splits[i].strip().upper()
        title = splits[i + 1].strip()
        body = splits[i + 2] if i + 2 < len(splits) else ""
        i += 3

        # Odvození modulu podle čísla US nebo kontextu
        us_num = int(re.search(r'\d+', us_id).group(0))
        if us_num <= 7:
            mod_code = "AUTH"
        elif us_num <= 10:
            mod_code = "CRS"
        elif us_num <= 12:
            mod_code = "ENR"
        elif us_num <= 15:
            mod_code = "LEC"
        elif us_num <= 17:
            mod_code = "PRF"
        else:
            mod_code = "SEC"

        actor = ""
        goal = ""
        benefit = ""
        m_actor = re.search(r'-\s*\*\*Jako:\*\*\s*(.+)', body)
        m_goal = re.search(r'-\s*\*\*Chci:\*\*\s*(.+)', body)
        m_benefit = re.search(r'-\s*\*\*Abych:\*\*\s*(.+)', body)
        if m_actor:
            actor = m_actor.group(1).strip()
        if m_goal:
            goal = m_goal.group(1).strip()
        if m_benefit:
            benefit = m_benefit.group(1).strip()

        story = UserStory(us_id, title, mod_code, actor, goal, benefit)

        crit_match = re.search(r'-\s*\*\*Akceptační kritéria:\*\*(.*?)(?=\n####|\n#{2,3}|\n\s*---\s*(?:\n|\Z)|\Z)', body, re.DOTALL)
        if crit_match:
            raw_lines = crit_match.group(1).strip().splitlines()
            crit_idx = 1
            for line in raw_lines:
                clean = re.sub(r'^\s*[-*]\s*', '', line).strip()
                if clean and not re.match(r'^-{2,}$', clean):
                    story.criteria.append(AcceptanceCriterion(crit_idx, clean))
                    crit_idx += 1

        stories[us_id] = story

    return stories


def parse_test_cases(file_path: Path) -> Dict[str, TestCase]:
    """Parsuje tabulku v docs/TEST_CASES.md a extrahuje Test Casy, mapování na US a pokrytá AK."""
    test_cases: Dict[str, TestCase] = {}
    if not file_path.exists():
        return test_cases

    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    in_table = False
    current_us_id = ""

    for line in lines:
        line_clean = line.strip()
        if not line_clean.startswith("|"):
            if in_table and line_clean.startswith("##"):
                in_table = False
            continue

        parts = [p.strip() for p in line_clean.split("|")[1:-1]]
        if len(parts) < 6:
            continue

        if "Kód testovacího případu" in parts[2] or "---" in parts[2]:
            in_table = True
            continue

        if not in_table:
            continue

        # parts: [Modul, User Story, Kód TC, Pokrytá AK, Název, Typ/Priorita]
        col_us = parts[1]
        col_tc = parts[2]
        col_aks = parts[3]
        col_title = parts[4]
        col_type = parts[5]

        # Extrakce US ID (pokud je prázdné, dědí se z předchozího řádku)
        us_match = re.search(r'US-\d+', col_us, re.IGNORECASE)
        if us_match:
            current_us_id = us_match.group(0).upper()

        tc_match = re.search(r'TC-\d{2}-[A-Z]{3,4}', col_tc, re.IGNORECASE)
        if not tc_match:
            continue

        tc_id = tc_match.group(0).upper()

        # Parsování pokrytých AK (např. "AK-1, AK-7", "AK-1 až AK-8", "Všechna AK")
        covered_aks = []
        range_match = re.search(r'AK-(\d+)\s*(?:až|-)\s*AK-(\d+)', col_aks, re.IGNORECASE)
        if range_match:
            start_k = int(range_match.group(1))
            end_k = int(range_match.group(2))
            for k in range(start_k, end_k + 1):
                covered_aks.append(f"AK-{k}")
        else:
            ak_singles = re.findall(r'AK-\d+', col_aks, re.IGNORECASE)
            covered_aks = [a.upper() for a in ak_singles]

        test_cases[tc_id] = TestCase(
            tc_id=tc_id,
            us_id=current_us_id,
            title=col_title,
            priority_type=col_type,
            covered_aks=covered_aks,
        )

    return test_cases


def parse_automated_tests(tests_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Analyzuje kód testů v tests/ pomocí AST a páruje je na kanonická ID TC-xx-MODUL."""
    automated: Dict[str, Dict[str, Any]] = {}
    if not tests_dir.exists():
        return automated

    for py_file in tests_dir.rglob("test_*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except Exception:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef) or not node.name.startswith("test_"):
                continue

            doc = ast.get_docstring(node) or ""
            tc_match = re.search(r'TC-(?P<num>\d{2})-(?P<mod>[A-Z]{3,4})', doc, re.IGNORECASE)
            is_legacy = False

            if not tc_match:
                fn_match = re.search(r'test_tc(?P<num>\d{2})_(?P<mod>[a-z]{3,4})_', node.name, re.IGNORECASE)
                if fn_match:
                    tc_id = f"TC-{fn_match.group('num')}-{fn_match.group('mod').upper()}"
                else:
                    leg_match = re.search(r'TC0?(?P<num>\d{1,2})', doc, re.IGNORECASE)
                    if leg_match:
                        num = int(leg_match.group('num'))
                        tc_id = f"TC-{num:02d}"
                        is_legacy = True
                    else:
                        continue
            else:
                tc_id = f"TC-{tc_match.group('num')}-{tc_match.group('mod').upper()}"

            # Extrakce markerů a xfail
            markers = []
            is_xfail = False
            xfail_reason = ""
            linked_bug = ""

            for dec in node.decorator_list:
                if isinstance(dec, ast.Attribute) and dec.attr:
                    markers.append(dec.attr)
                    if dec.attr == "xfail":
                        is_xfail = True
                elif isinstance(dec, ast.Call):
                    func_name = ""
                    if isinstance(dec.func, ast.Attribute):
                        func_name = dec.func.attr
                    elif isinstance(dec.func, ast.Name):
                        func_name = dec.func.id
                    if func_name:
                        markers.append(func_name)
                    if func_name == "xfail":
                        is_xfail = True
                        for kw in dec.keywords:
                            if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                                xfail_reason = str(kw.value.value)
                                bug_m = re.search(r'BR-\d+', xfail_reason, re.IGNORECASE)
                                if bug_m:
                                    linked_bug = bug_m.group(0).upper()

            automated[tc_id] = {
                "tc_id": tc_id,
                "function_name": node.name,
                "file_path": str(py_file),
                "line_no": node.lineno,
                "markers": markers,
                "is_xfail": is_xfail,
                "xfail_reason": xfail_reason,
                "linked_bug": linked_bug,
                "is_legacy": is_legacy,
            }

    return automated


def parse_bug_reports(file_path: Path) -> Dict[str, Dict[str, Any]]:
    """Parsuje evidované chyby v docs/JIRA_BUG_REPORTS.md."""
    bugs: Dict[str, Dict[str, Any]] = {}
    if not file_path.exists():
        return bugs

    content = file_path.read_text(encoding="utf-8")
    sections = re.split(r'###\s*(BR-\d+):\s*([^\n]+)', content)

    i = 1
    while i < len(sections):
        b_id = sections[i].strip().upper()
        b_title = sections[i + 1].strip()
        body = sections[i + 2] if i + 2 < len(sections) else ""
        i += 3

        sev = re.search(r'-\s*\*\*Závažnost:\*\*\s*(.+)', body)
        prio = re.search(r'-\s*\*\*Priorita:\*\*\s*(.+)', body)
        status = re.search(r'-\s*\*\*Stav:\*\*\s*(.+)', body)

        bugs[b_id] = {
            "bug_id": b_id,
            "title": b_title,
            "severity": sev.group(1).strip() if sev else "Normal",
            "priority": prio.group(1).strip() if prio else "Medium",
            "status": status.group(1).strip() if status else "Otevřený",
        }

    return bugs


def aggregate_story_data(
    stories: Dict[str, UserStory],
    test_cases: Dict[str, TestCase],
    automated_tests: Dict[str, Dict[str, Any]],
    bugs: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Propojí všechny datové zdroje a sestaví finální strukturu pro HTML report."""
    results = []

    # Mapování test casů k User Stories
    for tc in test_cases.values():
        if tc.tc_id in automated_tests:
            tc.automated_test = automated_tests[tc.tc_id]
        else:
            # Zkusit matching podle čísla pro legacy testy
            num_match = re.search(r'\d{2}', tc.tc_id)
            if num_match:
                leg_key = f"TC-{num_match.group(0)}"
                if leg_key in automated_tests:
                    tc.automated_test = automated_tests[leg_key]

        if tc.us_id in stories:
            stories[tc.us_id].test_cases.append(tc)

    for us_id in sorted(stories.keys(), key=lambda x: int(re.search(r'\d+', x).group(0))):
        story = stories[us_id]
        total_tc = len(story.test_cases)
        implemented_tc = [tc for tc in story.test_cases if tc.automated_test is not None]
        total_at = len(implemented_tc)
        xfail_tc = [tc for tc in implemented_tc if tc.automated_test.get("is_xfail")]

        # Analýza pokrytí jednotlivých akceptačních kritérií
        criteria_analysis = []
        covered_crit_count = 0

        for crit in story.criteria:
            matching_tcs = [tc for tc in story.test_cases if crit.code in tc.covered_aks]
            matching_ats = [tc for tc in matching_tcs if tc.automated_test is not None]
            has_at = len(matching_ats) > 0
            has_xfail = any(tc.automated_test.get("is_xfail") for tc in matching_ats)

            if has_at:
                covered_crit_count += 1

            criteria_analysis.append({
                "code": crit.code,
                "text": crit.text,
                "is_covered": has_at,
                "is_xfail": has_xfail,
                "matching_tcs": matching_tcs,
            })

        total_crit = len(story.criteria)
        crit_pct = (covered_crit_count / total_crit * 100) if total_crit > 0 else 100.0

        # Určení celkového stavu User Story
        if total_tc == 0:
            status_code = "uncovered"
            status_label = "Nepokryto"
            badge_class = "badge-danger"
        elif total_at == 0:
            status_code = "uncovered"
            status_label = "0 % AT"
            badge_class = "badge-danger"
        elif total_at == total_tc:
            if len(xfail_tc) > 0:
                status_code = "xfail"
                status_label = f"Pokryto ({len(xfail_tc)} defekt)"
                badge_class = "badge-warning"
            else:
                status_code = "full"
                status_label = "Plně pokryto"
                badge_class = "badge-success"
        else:
            status_code = "partial"
            status_label = f"Částečně ({total_at}/{total_tc} AT)"
            badge_class = "badge-amber"

        # Připojení informací o defektech
        active_bugs = []
        for tc in xfail_tc:
            b_id = tc.automated_test.get("linked_bug")
            if b_id and b_id in bugs:
                active_bugs.append(bugs[b_id])
            elif b_id:
                active_bugs.append({"bug_id": b_id, "title": tc.automated_test.get("xfail_reason") or "Defekt"})

        results.append({
            "us_id": story.us_id,
            "title": story.title,
            "module_code": story.module_code,
            "module_name": story.module_name,
            "actor": story.actor,
            "goal": story.goal,
            "benefit": story.benefit,
            "total_tc": total_tc,
            "total_at": total_at,
            "total_crit": total_crit,
            "covered_crit": covered_crit_count,
            "crit_pct": crit_pct,
            "status_code": status_code,
            "status_label": status_label,
            "badge_class": badge_class,
            "criteria": criteria_analysis,
            "test_cases": story.test_cases,
            "xfail_count": len(xfail_tc),
            "active_bugs": active_bugs,
        })

    return results


def render_html_report(data: List[Dict[str, Any]], output_path: Path) -> None:
    """Generuje samostatný interaktivní HTML soubor bez nutnosti externích knihoven."""
    total_us = len(data)
    fully_covered_us = sum(1 for d in data if d["status_code"] in ("full", "xfail"))
    partially_covered_us = sum(1 for d in data if d["status_code"] == "partial")
    uncovered_us = sum(1 for d in data if d["status_code"] == "uncovered")

    total_tcs = sum(d["total_tc"] for d in data)
    total_ats = sum(d["total_at"] for d in data)
    total_bugs = sum(d["xfail_count"] for d in data)

    overall_pct = (fully_covered_us / total_us * 100) if total_us > 0 else 0.0
    tc_at_pct = (total_ats / total_tcs * 100) if total_tcs > 0 else 0.0

    now_str = datetime.now().strftime("%d. %m. %Y v %H:%M")

    # Sestavení řádků tabulky
    table_rows = []
    for d in data:
        us_id = d["us_id"]
        mod = d["module_code"]
        title = d["title"]
        total_tc = d["total_tc"]
        total_at = d["total_at"]
        badge_class = d["badge_class"]
        status_label = d["status_label"]
        crit_text = f"{d['covered_crit']}/{d['total_crit']}"
        crit_pct = d["crit_pct"]

        # Detail akceptačních kritérií
        crit_items = []
        for c in d["criteria"]:
            if c["is_xfail"]:
                c_badge = '<span class="pill pill-warning">⚠️ XFAIL</span>'
            elif c["is_covered"]:
                c_badge = '<span class="pill pill-success">🟢 Pokryto AT</span>'
            else:
                c_badge = '<span class="pill pill-muted">🔴 Nepokryto v kódu</span>'

            tc_refs = ", ".join([f"<code>{tc.tc_id}</code>" for tc in c["matching_tcs"]]) or "—"
            crit_items.append(f"""
                <li class="crit-item">
                    <div class="crit-header">
                        <strong>{c['code']}</strong> {c_badge}
                        <span class="crit-tcs">Navázané TC: {tc_refs}</span>
                    </div>
                    <div class="crit-text">{c['text']}</div>
                </li>
            """)
        crit_html = "".join(crit_items) or "<p class='text-muted'>Žádná akceptační kritéria nebyla specifikována.</p>"

        # Detail testovacích případů a automatů
        tc_items = []
        for tc in d["test_cases"]:
            if tc.automated_test:
                fn = tc.automated_test
                rel_path = Path(fn["file_path"]).name
                if fn["is_xfail"]:
                    tc_badge = f'<span class="pill pill-warning">⚠️ XFAIL ({fn.get("linked_bug") or "Defekt"})</span>'
                else:
                    tc_badge = '<span class="pill pill-success">🟢 AT Implementován</span>'
                code_info = f"<code class='code-loc'>{rel_path}:{fn['line_no']}</code> &rarr; <code>{fn['function_name']}</code>"
            else:
                tc_badge = '<span class="pill pill-danger">🔴 Chybí v kódu</span>'
                code_info = "<span class='text-muted'>Zatím nezautomatizováno</span>"

            tc_items.append(f"""
                <div class="tc-card">
                    <div class="tc-top">
                        <span class="tc-id"><code>{tc.tc_id}</code></span>
                        <span class="tc-title"><strong>{tc.title}</strong></span>
                        <span class="tc-type">({tc.priority_type})</span>
                        {tc_badge}
                    </div>
                    <div class="tc-bottom">
                        <span class="tc-impl">Implementace: {code_info}</span>
                        <span class="tc-aks">Pokrývá: {', '.join(tc.covered_aks) or '—'}</span>
                    </div>
                </div>
            """)
        tc_html = "".join(tc_items) or "<p class='text-muted'>Žádné testovací případy v katalogu.</p>"

        # Sekce defektů
        bug_html = ""
        if d["active_bugs"]:
            bug_items = "".join([
                f"<li><strong>{b['bug_id']}:</strong> {b['title']} <span class='badge badge-warning'>{b.get('severity', 'Defekt')}</span></li>"
                for b in d["active_bugs"]
            ])
            bug_html = f"""
                <div class="story-bugs">
                    <h5>🐛 Evidované defekty aplikace (JIRA):</h5>
                    <ul>{bug_items}</ul>
                </div>
            """

        user_story_spec = ""
        if d["actor"] or d["goal"]:
            user_story_spec = f"""
                <div class="story-desc">
                    <p><strong>Jako:</strong> {d['actor']} | <strong>Chci:</strong> {d['goal']} | <strong>Abych:</strong> {d['benefit']}</p>
                </div>
            """

        row_html = f"""
            <tr class="story-row" data-module="{mod}" data-status="{d['status_code']}" onclick="toggleAccordion('{us_id}')">
                <td><span class="module-tag mod-{mod.lower()}">{mod}</span></td>
                <td><strong>{us_id}</strong></td>
                <td class="col-title">{title}</td>
                <td class="text-center"><code>{total_tc}</code></td>
                <td class="text-center"><code>{total_at}</code></td>
                <td>
                    <div class="progress-wrap">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {crit_pct}%;"></div>
                        </div>
                        <span class="crit-label">{crit_text} ({crit_pct:.0f} %)</span>
                    </div>
                </td>
                <td><span class="badge {badge_class}">{status_label}</span></td>
                <td class="text-center"><button class="btn-toggle" id="btn-{us_id}" title="Zobrazit detail">&#9660;</button></td>
            </tr>
            <tr class="accordion-content" id="detail-{us_id}">
                <td colspan="8">
                    <div class="accordion-inner">
                        {user_story_spec}
                        {bug_html}
                        <div class="detail-grid">
                            <div class="detail-col">
                                <h4>🎯 Akceptační kritéria ({d['covered_crit']}/{d['total_crit']} pokryto):</h4>
                                <ul class="crit-list">
                                    {crit_html}
                                </ul>
                            </div>
                            <div class="detail-col">
                                <h4>🧪 Test Casy & Automatizace ({d['total_at']}/{d['total_tc']}):</h4>
                                <div class="tc-list">
                                    {tc_html}
                                </div>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        """
        table_rows.append(row_html)

    tbody_content = "\n".join(table_rows)

    html_content = f"""<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Přehled pokrytí User Stories automatizovanými testy</title>
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
            flex-wrap: wrap;
            gap: 12px;
            align-items: center;
            justify-content: space-between;
        }}
        .filter-group {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
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
            width: 260px;
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
        .col-title {{ font-weight: 500; max-width: 380px; }}

        /* Badges & Tags */
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-success {{ background: var(--success-bg); color: var(--success); }}
        .badge-warning {{ background: var(--warning-bg); color: var(--warning); }}
        .badge-danger {{ background: var(--danger-bg); color: var(--danger); }}
        .badge-amber {{ background: var(--amber-bg); color: var(--amber); }}

        .module-tag {{
            display: inline-block;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
            background: #e2e8f0;
            color: #334155;
        }}
        .mod-auth {{ background: #e0e7ff; color: #3730a3; }}
        .mod-crs {{ background: #dbeafe; color: #1e40af; }}
        .mod-enr {{ background: #ccfbf1; color: #115e59; }}
        .mod-lec {{ background: #fef3c7; color: #92400e; }}
        .mod-prf {{ background: #f3e8ff; color: #6b21a8; }}
        .mod-sec {{ background: #fee2e2; color: #991b1b; }}

        .pill {{
            display: inline-block;
            padding: 2px 7px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }}
        .pill-success {{ background: var(--success-bg); color: var(--success); }}
        .pill-warning {{ background: var(--warning-bg); color: var(--warning); }}
        .pill-danger {{ background: var(--danger-bg); color: var(--danger); }}
        .pill-muted {{ background: #f1f5f9; color: var(--text-muted); }}

        .btn-toggle {{
            background: none;
            border: none;
            font-size: 12px;
            cursor: pointer;
            color: var(--text-muted);
            transition: transform 0.2s ease;
        }}
        .btn-toggle.open {{ transform: rotate(180deg); color: var(--primary); }}

        /* Progress Bar */
        .progress-wrap {{ width: 140px; }}
        .progress-bar {{
            height: 6px;
            background: #e2e8f0;
            border-radius: 3px;
            overflow: hidden;
            margin-bottom: 3px;
        }}
        .progress-fill {{
            height: 100%;
            background: var(--success);
            border-radius: 3px;
        }}
        .crit-label {{ font-size: 11px; color: var(--text-muted); }}

        /* Accordion Detail */
        tr.accordion-content {{ display: none; background: #fafafa; }}
        tr.accordion-content.show {{ display: table-row; }}
        .accordion-inner {{ padding: 18px 24px; }}
        .story-desc {{
            background: #ffffff;
            border-left: 3px solid var(--primary);
            padding: 10px 14px;
            margin-bottom: 16px;
            font-size: 13px;
            color: #334155;
            border-radius: 0 6px 6px 0;
        }}
        .story-bugs {{
            background: var(--warning-bg);
            border: 1px solid #fde68a;
            border-radius: 6px;
            padding: 10px 14px;
            margin-bottom: 16px;
            font-size: 13px;
        }}
        .story-bugs h5 {{ margin-bottom: 4px; color: #92400e; }}
        .story-bugs ul {{ padding-left: 18px; }}

        .detail-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}
        @media (max-width: 900px) {{
            .detail-grid {{ grid-template-columns: 1fr; }}
        }}
        .detail-col h4 {{
            font-size: 13px;
            text-transform: uppercase;
            color: #475569;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 6px;
        }}
        .crit-list {{ list-style: none; display: flex; flex-direction: column; gap: 8px; }}
        .crit-item {{
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }}
        .crit-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }}
        .crit-tcs {{ font-size: 11px; color: var(--text-muted); }}
        .crit-text {{ color: #334155; }}

        .tc-list {{ display: flex; flex-direction: column; gap: 8px; }}
        .tc-card {{
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
        }}
        .tc-top {{ display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }}
        .tc-id {{ font-size: 12px; }}
        .tc-title {{ font-size: 13px; color: #1e293b; flex-grow: 1; }}
        .tc-type {{ font-size: 11px; color: var(--text-muted); }}
        .tc-bottom {{ display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); margin-top: 4px; }}
        .code-loc {{ color: #0284c7; }}

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
            <h1>📊 Přehled pokrytí User Stories automatizovanými testy</h1>
            <p class="subtitle">E2E Testovací sada Kitner.cz | Vygenerováno: {now_str}</p>
        </header>

        <!-- KPI Summary Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">Míra pokrytí požadavků</div>
                <div class="kpi-value">{overall_pct:.1f} %</div>
                <div class="kpi-sub">{fully_covered_us} z {total_us} User Stories pokryto</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">User Stories</div>
                <div class="kpi-value">{total_us}</div>
                <div class="kpi-sub">🟢 {fully_covered_us} plně | 🟡 {partially_covered_us} část. | 🔴 {uncovered_us} ne</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Test Casy vs. Kód AT</div>
                <div class="kpi-value">{total_ats} / {total_tcs}</div>
                <div class="kpi-sub">{tc_at_pct:.1f} % testovacích případů v kódu</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Evidované defekty aplikace</div>
                <div class="kpi-value">{total_bugs}</div>
                <div class="kpi-sub">Označené testy jako @pytest.mark.xfail</div>
            </div>
        </div>

        <!-- Toolbar & Filters -->
        <div class="toolbar">
            <div class="filter-group">
                <span style="font-size: 13px; font-weight: 600; color: #475569; margin-right: 4px;">Stav:</span>
                <button class="filter-btn active" onclick="setStatusFilter('all', this)">Vše ({total_us})</button>
                <button class="filter-btn" onclick="setStatusFilter('full', this)">🟢 Plně pokryto ({fully_covered_us - total_bugs})</button>
                <button class="filter-btn" onclick="setStatusFilter('xfail', this)">⚠️ S defektem ({total_bugs})</button>
                <button class="filter-btn" onclick="setStatusFilter('partial', this)">🟡 Částečně ({partially_covered_us})</button>
                <button class="filter-btn" onclick="setStatusFilter('uncovered', this)">🔴 Nepokryto ({uncovered_us})</button>
            </div>
            <input type="text" id="searchInput" class="search-box" placeholder="Hledat US, název, TC, modul..." oninput="applyFilters()">
        </div>

        <!-- Main Coverage Table -->
        <div class="table-wrap">
            <table id="coverageTable">
                <thead>
                    <tr>
                        <th style="width: 70px;">Modul</th>
                        <th style="width: 80px;">US ID</th>
                        <th>Název User Story</th>
                        <th style="width: 60px;" class="text-center">TC</th>
                        <th style="width: 60px;" class="text-center">AT</th>
                        <th style="width: 170px;">Pokrytí AK</th>
                        <th style="width: 150px;">Stav</th>
                        <th style="width: 50px;" class="text-center">Detail</th>
                    </tr>
                </thead>
                <tbody>
                    {tbody_content}
                </tbody>
            </table>
        </div>

        <footer>
            Zdroj: <code>docs/požadavky_ust_podle_src.md</code> &bull; <code>docs/TEST_CASES.md</code> &bull; <code>tests/</code> &bull; <code>docs/JIRA_BUG_REPORTS.md</code>
        </footer>
    </div>

    <script>
        let currentStatusFilter = 'all';

        function toggleAccordion(usId) {{
            const detailRow = document.getElementById('detail-' + usId);
            const btn = document.getElementById('btn-' + usId);
            if (!detailRow) return;

            const isOpen = detailRow.classList.contains('show');
            if (isOpen) {{
                detailRow.classList.remove('show');
                if (btn) btn.classList.remove('open');
            }} else {{
                detailRow.classList.add('show');
                if (btn) btn.classList.add('open');
            }}
        }}

        function setStatusFilter(status, btnElement) {{
            currentStatusFilter = status;
            document.querySelectorAll('.filter-group .filter-btn').forEach(btn => btn.classList.remove('active'));
            if (btnElement) btnElement.classList.add('active');
            applyFilters();
        }}

        function applyFilters() {{
            const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
            const rows = document.querySelectorAll('.story-row');

            rows.forEach(row => {{
                const status = row.getAttribute('data-status');
                const usId = row.querySelector('td:nth-child(2)').innerText.toLowerCase();
                const title = row.querySelector('.col-title').innerText.toLowerCase();
                const module = row.getAttribute('data-module').toLowerCase();
                const detailRow = document.getElementById('detail-' + usId.toUpperCase());

                let matchesStatus = (currentStatusFilter === 'all') || 
                                    (currentStatusFilter === 'full' && status === 'full') ||
                                    (currentStatusFilter === 'xfail' && status === 'xfail') ||
                                    (currentStatusFilter === 'partial' && status === 'partial') ||
                                    (currentStatusFilter === 'uncovered' && status === 'uncovered');

                let matchesQuery = !query || usId.includes(query) || title.includes(query) || module.includes(query);

                if (matchesStatus && matchesQuery) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                    if (detailRow) detailRow.classList.remove('show');
                }}
            }});
        }}
    </script>
</body>
</html>
"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Generátor přehledu pokrytí User Stories automatizovanými testy (HTML Dashboard)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="reports/story_coverage.html",
        help="Výstupní cesta pro HTML report (výchozí: reports/story_coverage.html)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Tichý režim (nevypisuje detailní zprávy do konzole)",
    )

    args = parser.parse_args()
    project_root = Path.cwd()

    us_file = project_root / "docs" / "požadavky_ust_podle_src.md"
    tc_file = project_root / "docs" / "TEST_CASES.md"
    tests_dir = project_root / "tests"
    bugs_file = project_root / "docs" / "JIRA_BUG_REPORTS.md"
    output_path = project_root / args.output

    if not args.quiet:
        print("🔍 Analyzuji pokrytí User Stories...")

    stories = parse_user_stories(us_file)
    test_cases = parse_test_cases(tc_file)
    automated = parse_automated_tests(tests_dir)
    bugs = parse_bug_reports(bugs_file)

    data = aggregate_story_data(stories, test_cases, automated, bugs)
    render_html_report(data, output_path)

    if not args.quiet:
        total_us = len(data)
        fully_covered = sum(1 for d in data if d["status_code"] in ("full", "xfail"))
        total_ats = sum(d["total_at"] for d in data)
        total_tcs = sum(d["total_tc"] for d in data)
        pct = (fully_covered / total_us * 100) if total_us > 0 else 0
        print(f"✅ HTML přehled byl úspěšně vygenerován: {output_path}")
        print(f"📊 Pokrytí požadavků: {fully_covered}/{total_us} US ({pct:.1f} %) | {total_ats}/{total_tcs} AT implementováno.")


if __name__ == "__main__":
    main()

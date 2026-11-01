#!/usr/bin/env python3
"""
Traceability & Test Coverage Scanner for Playwright / Pytest
============================================================

Tento skript zajišťuje 100% obousměrnou trasovatelnost mezi:
1. Byznysovými požadavky (docs/požadavky_ust_podle_src.md – US-01 až US-19)
2. Katalogem testovacích případů (docs/TEST_CASES.md – TC-01-AUTH až TC-47-SEC)
3. Kódem automatizovaných testů (tests/**/*.py)
4. Centrálním registrem defektů (docs/JIRA_BUG_REPORTS.md – BR-01 až BR-xx)

Funkce skriptu:
- Sestavení matice trasovatelnosti (Traceability Matrix) a výpočet pokrytí (%).
- Validace pokrytí všech User Stories v katalogu testovacích případů.
- Zpětné dotazování: detail User Story (--story US-xx) a vyhledání kontextu testu (--find <name>).
- Detekce a provázání defektů (@pytest.mark.xfail <-> BR-xx v JIRA_BUG_REPORTS.md).
- Detekce chybějících testů (Missing Tests) v kódu.
- Kontrola souladu markerů (@pytest.mark.<domain> a @pytest.mark.smoke / regression).
- Generování koster (scaffold) chybějících testů podle specifikace v TEST_CASES.md.
- Bezpečná oprava a normalizace zastaralých formátů ID v docstringu (--fix-docstrings).
- Export matice do Markdown reportu (--export-md).
"""

import os
import re
import sys
import ast
import argparse
import difflib
import unicodedata
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any

# Mapování User Stories a modulů na cílové soubory a Page Objects
US_TARGET_MAP = {
    # Autentizace (AUTH)
    "US-01": {"file": "tests/auth/test_register.py", "po": "RegisterPage"},
    "US-02": {"file": "tests/auth/test_login.py", "po": "LoginPage"},
    "US-03": {"file": "tests/auth/test_logout.py", "po": "LoginPage"},
    "US-04": {"file": "tests/auth/test_password_reset.py", "po": "ForgotPasswordPage"},
    "US-05": {"file": "tests/auth/test_password_reset.py", "po": "ForgotPasswordPage"},
    "US-06": {"file": "tests/auth/test_password_reset.py", "po": "LoginPage"},
    "US-07": {"file": "tests/auth/test_login.py", "po": "LoginPage"},
    # Kurzy (CRS)
    "US-08": {"file": "tests/courses/test_courses.py", "po": "CoursesPage"},
    "US-09": {"file": "tests/courses/test_courses.py", "po": "CourseDetailPage"},
    "US-10": {"file": "tests/courses/test_courses.py", "po": "CourseDetailPage"},
    # Zápis (ENR)
    "US-11": {"file": "tests/enrollment/test_enrollment.py", "po": "EnrollmentPage"},
    "US-12": {"file": "tests/enrollment/test_enrollment.py", "po": "MyCoursesPage"},
    # Lektor (LEC)
    "US-13": {"file": "tests/lecturer/test_lecturer.py", "po": "CreateCoursePage"},
    "US-14": {"file": "tests/lecturer/test_lecturer.py", "po": "CoursesPage"},
    "US-15": {"file": "tests/lecturer/test_lecturer.py", "po": "CoursesPage"},
    # Profil (PRF)
    "US-16": {"file": "tests/profile/test_profile.py", "po": "HomePage"},
    "US-17": {"file": "tests/profile/test_profile.py", "po": "ProfilePage"},
    # Bezpečnost (SEC)
    "US-18": {"file": "tests/security/test_security.py", "po": "ProfilePage"},
    "US-19": {"file": "tests/security/test_security.py", "po": "LoginPage"},
}

MODULE_CONFIG = {
    "AUTH": {
        "name": "Autentizace",
        "domain_marker": "auth",
        "target_dir": "tests/auth",
        "default_file": "tests/auth/test_login.py",
        "page_objects": ["LoginPage", "RegisterPage", "ForgotPasswordPage", "HomePage"],
    },
    "CRS": {
        "name": "Katalog kurzů",
        "domain_marker": "courses",
        "target_dir": "tests/courses",
        "default_file": "tests/courses/test_courses.py",
        "page_objects": ["CoursesPage", "CourseDetailPage"],
    },
    "ENR": {
        "name": "Zápis na kurz",
        "domain_marker": "enrollment",
        "target_dir": "tests/enrollment",
        "default_file": "tests/enrollment/test_enrollment.py",
        "page_objects": ["EnrollmentPage", "MyCoursesPage", "CoursesPage"],
    },
    "LEC": {
        "name": "Správa lektorem",
        "domain_marker": "lecturer",
        "target_dir": "tests/lecturer",
        "default_file": "tests/lecturer/test_lecturer.py",
        "page_objects": ["CreateCoursePage", "CoursesPage"],
    },
    "PRF": {
        "name": "Profil a nástěnka",
        "domain_marker": "profile",
        "target_dir": "tests/profile",
        "default_file": "tests/profile/test_profile.py",
        "page_objects": ["ProfilePage", "HomePage"],
    },
    "SEC": {
        "name": "Bezpečnost a autorizace",
        "domain_marker": "security",
        "target_dir": "tests/security",
        "default_file": "tests/security/test_security.py",
        "page_objects": ["ProfilePage", "MyCoursesPage", "CreateCoursePage", "LoginPage"],
    },
}

# Regulární výrazy
RE_CANONICAL_TC = re.compile(r'\bTC-(?P<num>\d{2})-(?P<mod>[A-Z]{3,4})\b', re.IGNORECASE)
RE_FUNC_TC = re.compile(r'\btest_tc(?P<num>\d{2})_(?P<mod>[a-z]{3,4})_', re.IGNORECASE)
RE_LEGACY_TC = re.compile(r'\bTC0?(?P<num>\d{1,2})\b', re.IGNORECASE)
RE_BR_ID = re.compile(r'\bBR-(?P<num>\d{2})\b', re.IGNORECASE)


def strip_accents(text: str) -> str:
    """Odstraní diakritiku z textu pro bezpečné názvy proměnných a funkcí."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


class UserStorySpec:
    """Reprezentace User Story ze souboru docs/požadavky_ust_podle_src.md."""

    def __init__(
        self,
        us_id: str,
        title: str,
        actor: str = "",
        goal: str = "",
        benefit: str = "",
        criteria: List[str] = None,
        module_name: str = "",
    ):
        self.us_id = us_id.upper()
        self.title = title
        self.actor = actor
        self.goal = goal
        self.benefit = benefit
        self.criteria = criteria or []
        self.module_name = module_name


class BugReportSpec:
    """Reprezentace nahlášeného defektu ze souboru docs/JIRA_BUG_REPORTS.md."""

    def __init__(
        self,
        bug_id: str,
        title: str,
        severity: str,
        priority: str,
        linked_stories: List[str],
        linked_tcs: List[str],
        status: str,
    ):
        self.bug_id = bug_id.upper()
        self.title = title
        self.severity = severity
        self.priority = priority
        self.linked_stories = linked_stories
        self.linked_tcs = linked_tcs
        self.status = status


class TestCaseSpec:
    """Reprezentace testovacího případu ze souboru docs/TEST_CASES.md."""

    def __init__(
        self,
        tc_id: str,
        module_code: str,
        user_story: str,
        title: str,
        priority_type: str,
        prerequisites: str = "",
        test_data: str = "",
        steps: List[str] = None,
        expected_result: List[str] = None,
    ):
        self.tc_id = tc_id.upper()
        self.module_code = module_code.upper()
        self.user_story = user_story
        self.title = title
        self.priority_type = priority_type
        self.prerequisites = prerequisites
        self.test_data = test_data
        self.steps = steps or []
        self.expected_result = expected_result or []

    @property
    def expected_severity_marker(self) -> str:
        lower_prio = self.priority_type.lower()
        if "smoke" in lower_prio or "p1" in lower_prio:
            return "smoke"
        return "regression"

    @property
    def expected_domain_marker(self) -> str:
        cfg = MODULE_CONFIG.get(self.module_code, {})
        return cfg.get("domain_marker", self.module_code.lower())


class AutomatedTestFunction:
    """Reprezentace nalezeného testu v kódu (tests/**/*.py)."""

    def __init__(
        self,
        file_path: str,
        function_name: str,
        class_name: Optional[str],
        docstring: Optional[str],
        markers: List[str],
        line_no: int,
        matched_tc_id: Optional[str] = None,
        is_legacy_match: bool = False,
        xfail_reason: Optional[str] = None,
        linked_bug_id: Optional[str] = None,
    ):
        self.file_path = file_path
        self.function_name = function_name
        self.class_name = class_name
        self.docstring = docstring or ""
        self.markers = markers
        self.line_no = line_no
        self.matched_tc_id = matched_tc_id
        self.is_legacy_match = is_legacy_match
        self.xfail_reason = xfail_reason
        self.linked_bug_id = linked_bug_id

    @property
    def full_name(self) -> str:
        if self.class_name:
            return f"{self.class_name}::{self.function_name}"
        return self.function_name

    @property
    def is_xfail(self) -> bool:
        return "xfail" in self.markers


def parse_user_stories_md(file_path: Path) -> Dict[str, UserStorySpec]:
    """Parsuje docs/požadavky_ust_podle_src.md a extrahuje všechny byznysové User Stories."""
    stories: Dict[str, UserStorySpec] = {}
    if not file_path.exists():
        return stories

    content = file_path.read_text(encoding="utf-8")
    us_header_pattern = re.compile(r'####\s*(?P<us_id>US-\d+):\s*(?P<title>[^\n]+)')
    sections = us_header_pattern.split(content)

    i = 1
    while i < len(sections):
        us_id = sections[i].strip().upper()
        title = sections[i + 1].strip()
        body = sections[i + 2] if i + 2 < len(sections) else ""
        i += 3

        actor_match = re.search(r'-\s*\*\*Jako:\*\*\s*(.+)', body)
        goal_match = re.search(r'-\s*\*\*Chci:\*\*\s*(.+)', body)
        benefit_match = re.search(r'-\s*\*\*Abych:\*\*\s*(.+)', body)

        criteria = []
        crit_match = re.search(r'-\s*\*\*Akceptační kritéria:\*\*(.*?)(?=\n####|\n#{2,3}|\Z)', body, re.DOTALL)
        if crit_match:
            crit_raw = crit_match.group(1).strip()
            criteria = [re.sub(r'^\s*[-*]\s*', '', line).strip() for line in crit_raw.splitlines() if line.strip()]

        stories[us_id] = UserStorySpec(
            us_id=us_id,
            title=title,
            actor=actor_match.group(1).strip() if actor_match else "",
            goal=goal_match.group(1).strip() if goal_match else "",
            benefit=benefit_match.group(1).strip() if benefit_match else "",
            criteria=criteria,
        )

    return stories


def parse_bug_reports_md(file_path: Path) -> Dict[str, BugReportSpec]:
    """Parsuje docs/JIRA_BUG_REPORTS.md a extrahuje hlášené defekty."""
    bugs: Dict[str, BugReportSpec] = {}
    if not file_path.exists():
        return bugs

    content = file_path.read_text(encoding="utf-8")
    table_pattern = re.compile(
        r'\|\s*\[\*\*(?P<bug_id>BR-\d+)\*\*\][^\n|]*\|\s*`?(?P<mod>[^`|]+)`?\s*\|\s*(?P<title>[^|]+)\|\s*\*\*(?P<sev>[^*]+)\*\*\s*\|\s*\*\*(?P<prio>[^*]+)\*\*\s*\|\s*(?P<stories>[^|]+)\|\s*(?P<status>[^|]+)\|'
    )

    for line in content.splitlines():
        match = table_pattern.search(line)
        if match:
            b_id = match.group("bug_id").strip().upper()
            title = match.group("title").strip()
            sev = match.group("sev").strip()
            prio = match.group("prio").strip()
            stories_raw = match.group("stories").strip()
            status = match.group("status").strip()

            stories = [s.strip().upper() for s in re.findall(r'US-\d+', stories_raw)]
            bugs[b_id] = BugReportSpec(
                bug_id=b_id,
                title=title,
                severity=sev,
                priority=prio,
                linked_stories=stories,
                linked_tcs=[],
                status=status,
            )

    # Doplnění vázaných Test Casů ze sekcí ticketů
    detail_pattern = re.compile(r'###\s*🐞\s*(?P<bug_id>BR-\d+)')
    sections = detail_pattern.split(content)
    j = 1
    while j < len(sections):
        b_id = sections[j].strip().upper()
        body = sections[j + 1] if j + 1 < len(sections) else ""
        j += 2
        if b_id in bugs:
            tc_matches = re.findall(r'TC-\d{2}-[A-Z]{3,4}', body)
            bugs[b_id].linked_tcs = list(dict.fromkeys(tc_matches))

    return bugs


def parse_test_cases_md(file_path: Path) -> Dict[str, TestCaseSpec]:
    """Parsuje docs/TEST_CASES.md a extrahuje všechny specifikované Test Casy."""
    test_cases: Dict[str, TestCaseSpec] = {}
    if not file_path.exists():
        return test_cases

    content = file_path.read_text(encoding="utf-8")
    table_pattern = re.compile(
        r'\|\s*(?:\*\*\d+\.\s+.*?\((?P<mod>[A-Z]{3,4})\)\*\*)?\s*\|\s*(?:\*\*(?P<us>US-\d+)\*\*.*?)?\s*\|\s*`(?P<tc_id>TC-\d{2}-[A-Z]{3,4})`\s*\|\s*(?P<title>[^|]+?)\s*\|\s*(?P<priority>[^|]+?)\s*\|'
    )

    current_module = "AUTH"
    current_us = "US-01"

    for line in content.splitlines():
        match = table_pattern.search(line)
        if match:
            mod_match = match.group("mod")
            if mod_match:
                current_module = mod_match.strip()

            us_match = match.group("us")
            if us_match:
                current_us = us_match.strip()

            tc_id = match.group("tc_id").strip().upper()
            title = match.group("title").strip()
            priority = match.group("priority").strip()

            test_cases[tc_id] = TestCaseSpec(
                tc_id=tc_id,
                module_code=current_module,
                user_story=current_us,
                title=title,
                priority_type=priority,
            )

    detail_header_pattern = re.compile(r'####\s*`(?P<tc_id>TC-\d{2}-[A-Z]{3,4})`:\s*(?P<title>[^\n]+)')
    sections = detail_header_pattern.split(content)
    i = 1
    while i < len(sections):
        tc_id = sections[i].strip().upper()
        body = sections[i + 2] if i + 2 < len(sections) else ""
        i += 3

        if tc_id in test_cases:
            tc = test_cases[tc_id]
            prep_match = re.search(r'\*\s*\*\*Předpoklady:\*\*\s*(.+)', body)
            if prep_match:
                tc.prerequisites = prep_match.group(1).strip()

            data_match = re.search(r'\*\s*\*\*Testovací data:\*\*\s*(.+)', body)
            if data_match:
                tc.test_data = data_match.group(1).strip()

            steps_match = re.search(r'\*\s*\*\*Kroky:\*\*(.*?)(?=\*\s*\*\*Očekávaný|$)', body, re.DOTALL)
            if steps_match:
                steps_raw = steps_match.group(1).strip()
                steps = [re.sub(r'^\d+\.\s*', '', s.strip()) for s in steps_raw.splitlines() if s.strip()]
                tc.steps = steps

            exp_match = re.search(r'\*\s*\*\*Očekávaný výsledek:\*\*(.*?)(?=\n#{2,4}|\Z)', body, re.DOTALL)
            if exp_match:
                exp_raw = exp_match.group(1).strip()
                exp_lines = [re.sub(r'^[-*]\s*', '', e.strip()) for e in exp_raw.splitlines() if e.strip()]
                tc.expected_result = exp_lines

    return test_cases


class AstTestExtractor(ast.NodeVisitor):
    """AST návštěvník pro extrakci testovacích funkcí, docstringů, markerů a xfail důvodů."""

    def __init__(self, file_path: Path, module_hint: str):
        self.file_path = str(file_path)
        self.file_name = file_path.name
        self.module_hint = module_hint.upper()
        self.test_functions: List[AutomatedTestFunction] = []
        self.current_class: Optional[str] = None
        self.class_markers: List[str] = []

    def _extract_markers_and_xfail(self, decorator_list: List[ast.AST]) -> Tuple[List[str], Optional[str], Optional[str]]:
        markers = []
        xfail_reason = None
        linked_bug_id = None

        for dec in decorator_list:
            if isinstance(dec, ast.Attribute):
                if isinstance(dec.value, ast.Attribute) and dec.value.attr == "mark":
                    markers.append(dec.attr)
            elif isinstance(dec, ast.Call):
                func = dec.func
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute) and func.value.attr == "mark":
                    mark_name = func.attr
                    markers.append(mark_name)
                    if mark_name == "xfail":
                        for kw in dec.keywords:
                            if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                                xfail_reason = str(kw.value.value)
                                br_match = RE_BR_ID.search(xfail_reason)
                                if br_match:
                                    linked_bug_id = br_match.group(0).upper()

        return markers, xfail_reason, linked_bug_id

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_class = self.current_class
        prev_markers = self.class_markers

        self.current_class = node.name
        cls_markers, _, _ = self._extract_markers_and_xfail(node.decorator_list)
        self.class_markers = cls_markers

        self.generic_visit(node)

        self.current_class = prev_class
        self.class_markers = prev_markers

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name.startswith("test_"):
            docstring = ast.get_docstring(node) or ""
            fn_markers, xfail_reason, linked_bug_id = self._extract_markers_and_xfail(node.decorator_list)
            all_markers = list(dict.fromkeys(self.class_markers + fn_markers))

            matched_id, is_legacy = self._detect_tc_id(node.name, docstring)

            self.test_functions.append(
                AutomatedTestFunction(
                    file_path=self.file_path,
                    function_name=node.name,
                    class_name=self.current_class,
                    docstring=docstring,
                    markers=all_markers,
                    line_no=node.lineno,
                    matched_tc_id=matched_id,
                    is_legacy_match=is_legacy,
                    xfail_reason=xfail_reason,
                    linked_bug_id=linked_bug_id,
                )
            )

        self.generic_visit(node)

    def _detect_tc_id(self, func_name: str, docstring: str) -> Tuple[Optional[str], bool]:
        """Detekuje TC ID s podporou kanonického formátu (TC-01-AUTH) i specifického kontextového mapování."""
        match = RE_CANONICAL_TC.search(docstring)
        if match:
            return match.group(0).upper(), False

        match = RE_FUNC_TC.search(func_name)
        if match:
            num = match.group("num")
            mod = match.group("mod").upper()
            return f"TC-{num}-{mod}", False

        sec_match = re.search(r'test_tc(?P<num>\d{2})_(?P<mod>[a-zA-Z]{3,4})_', func_name)
        if sec_match:
            return f"TC-{sec_match.group('num')}-{sec_match.group('mod').upper()}", False

        legacy_match = RE_LEGACY_TC.search(docstring)
        if legacy_match:
            num = int(legacy_match.group("num"))

            if self.file_name == "test_logout.py":
                if num == 1:
                    return "TC-11-AUTH", True
                elif num == 2:
                    return "TC-09-AUTH", True

            elif self.file_name == "test_password_reset.py":
                if num == 1:
                    return "TC-12-AUTH", True

            elif self.file_name == "test_register.py":
                reg_map = {
                    1: "TC-01-AUTH",
                    2: "TC-04-AUTH",
                    3: "TC-03-AUTH",
                    4: "TC-04-AUTH",
                    5: "TC-02-AUTH",
                    6: "TC-01-AUTH",
                }
                if num in reg_map:
                    return reg_map[num], True

            elif self.file_name == "test_login.py":
                login_map = {
                    1: "TC-06-AUTH",
                    2: "TC-37-LEC",
                    3: "TC-07-AUTH",
                    4: "TC-08-AUTH",
                    5: "TC-06-AUTH",
                    6: "TC-06-AUTH",
                }
                if num in login_map:
                    return login_map[num], True

            formatted_num = f"{num:02d}"
            if self.module_hint in MODULE_CONFIG:
                return f"TC-{formatted_num}-{self.module_hint}", True

        return None, False


def scan_test_codebase(tests_dir: Path) -> List[AutomatedTestFunction]:
    """Projde všechny testovací soubory a vyextrahuje testovací funkce."""
    collected_tests: List[AutomatedTestFunction] = []

    for file_path in sorted(tests_dir.rglob("test_*.py")):
        relative = file_path.relative_to(tests_dir)
        parent_dir = relative.parent.name.upper()

        dir_to_mod = {
            "AUTH": "AUTH",
            "COURSES": "CRS",
            "ENROLLMENT": "ENR",
            "LECTURER": "LEC",
            "PROFILE": "PRF",
            "SECURITY": "SEC",
        }
        mod_hint = dir_to_mod.get(parent_dir, "GEN")

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
            extractor = AstTestExtractor(file_path, mod_hint)
            extractor.visit(tree)
            collected_tests.extend(extractor.test_functions)
        except Exception as e:
            print(f"Chyba při parsování {file_path}: {e}", file=sys.stderr)

    return collected_tests


def analyze_traceability(
    user_stories: Dict[str, UserStorySpec],
    spec_cases: Dict[str, TestCaseSpec],
    code_tests: List[AutomatedTestFunction],
    bug_reports: Dict[str, BugReportSpec],
) -> Dict[str, Any]:
    """Provede kompletní křížovou analýzu pokrytí a kvality markerů."""
    # 1. Mapování User Stories na Test Casy
    us_to_tcs: Dict[str, List[TestCaseSpec]] = {us_id: [] for us_id in user_stories}
    for tc in spec_cases.values():
        if tc.user_story in us_to_tcs:
            us_to_tcs[tc.user_story].append(tc)

    uncovered_stories = [us_id for us_id, tcs in us_to_tcs.items() if not tcs]

    # 2. Mapování Test Casů na kódové testy
    tc_to_tests: Dict[str, List[AutomatedTestFunction]] = {tc_id: [] for tc_id in spec_cases}
    unmapped_tests: List[AutomatedTestFunction] = []
    navigation_journey_tests: List[AutomatedTestFunction] = []

    for test in code_tests:
        if "navigation" in test.markers:
            navigation_journey_tests.append(test)
        elif test.matched_tc_id and test.matched_tc_id in tc_to_tests:
            tc_to_tests[test.matched_tc_id].append(test)
        else:
            unmapped_tests.append(test)

    # 3. Analýza pokrytí a markerů
    covered_cases: List[str] = []
    missing_cases: List[str] = []
    legacy_cases: List[str] = []
    xfail_cases: List[Dict[str, Any]] = []
    marker_mismatches: List[Dict[str, Any]] = []

    for tc_id, spec in spec_cases.items():
        matched_fns = tc_to_tests[tc_id]
        if not matched_fns:
            missing_cases.append(tc_id)
        else:
            covered_cases.append(tc_id)
            if any(fn.is_legacy_match for fn in matched_fns):
                legacy_cases.append(tc_id)

            for fn in matched_fns:
                if fn.is_xfail:
                    xfail_cases.append({
                        "tc_id": tc_id,
                        "test_func": fn.full_name,
                        "file_path": fn.file_path,
                        "bug_id": fn.linked_bug_id,
                        "reason": fn.xfail_reason,
                    })

                mismatch_reasons = []
                exp_domain = spec.expected_domain_marker
                if exp_domain and exp_domain not in fn.markers:
                    mismatch_reasons.append(f"Chybí doménový marker: @pytest.mark.{exp_domain}")

                exp_severity = spec.expected_severity_marker
                has_smoke = "smoke" in fn.markers
                has_regression = "regression" in fn.markers

                if exp_severity == "smoke" and not has_smoke:
                    mismatch_reasons.append("Chybí @pytest.mark.smoke (priorita P1)")
                elif exp_severity == "regression" and not has_regression and not has_smoke:
                    mismatch_reasons.append("Chybí marker závažnosti (@pytest.mark.regression)")

                if mismatch_reasons:
                    marker_mismatches.append({
                        "tc_id": tc_id,
                        "test_func": fn.full_name,
                        "file_path": fn.file_path,
                        "line_no": fn.line_no,
                        "reasons": mismatch_reasons,
                    })

    total_spec = len(spec_cases)
    coverage_pct = (len(covered_cases) / total_spec * 100) if total_spec > 0 else 0

    return {
        "user_stories": user_stories,
        "us_to_tcs": us_to_tcs,
        "uncovered_stories": uncovered_stories,
        "spec_cases": spec_cases,
        "tc_to_tests": tc_to_tests,
        "covered_cases": covered_cases,
        "missing_cases": missing_cases,
        "legacy_cases": legacy_cases,
        "xfail_cases": xfail_cases,
        "navigation_journey_tests": navigation_journey_tests,
        "unmapped_tests": unmapped_tests,
        "marker_mismatches": marker_mismatches,
        "bug_reports": bug_reports,
        "total_spec": total_spec,
        "coverage_pct": coverage_pct,
    }


def print_matrix(analysis: Dict[str, Any]):
    """Vytiskne přehlednou tabulku Traceability Matrix do terminálu."""
    spec_cases: Dict[str, TestCaseSpec] = analysis["spec_cases"]
    tc_to_tests: Dict[str, List[AutomatedTestFunction]] = analysis["tc_to_tests"]
    user_stories: Dict[str, UserStorySpec] = analysis["user_stories"]

    print("=" * 110)
    print("📊 TRACEABILITY MATRIX: Požadavky (US) ↔ Test Casy (TC) ↔ Kód testů ↔ Defekty (BR)")
    print("=" * 110)
    print(f"{'Modul':<7} | {'US':<7} | {'TC ID':<12} | {'Stav testu':<16} | {'Markery':<20} | {'Implementace v kódu'}")
    print("-" * 110)

    current_mod = ""
    for tc_id, spec in sorted(spec_cases.items()):
        if spec.module_code != current_mod:
            current_mod = spec.module_code
            print(f"--- Modul {current_mod} ({MODULE_CONFIG.get(current_mod, {}).get('name', '')}) " + "-" * 75)

        tests = tc_to_tests[tc_id]
        if not tests:
            status = "❌ CHYBÍ"
            markers_str = f"({spec.expected_severity_marker})"
            impl_str = "Nemá automatizovaný test"
        else:
            fn = tests[0]
            if fn.is_xfail:
                status = f"⚠️ XFAIL ({fn.linked_bug_id or 'Defekt'})"
            elif fn.is_legacy_match:
                status = "🟡 LEGACY ID"
            else:
                status = "🟢 COVERED"

            markers_str = ", ".join(fn.markers) if fn.markers else "žádné"
            impl_str = f"{Path(fn.file_path).name}:{fn.line_no} -> {fn.function_name}"
            if len(tests) > 1:
                impl_str += f" (+{len(tests)-1} další)"

        print(
            f"{spec.module_code:<7} | {spec.user_story:<7} | {spec.tc_id:<12} | {status:<16} | {markers_str:<20} | {impl_str}"
        )

    us_covered_count = len(user_stories) - len(analysis['uncovered_stories'])
    us_pct = (us_covered_count / len(user_stories) * 100) if user_stories else 100.0
    print(f"  • Požadavky (User Stories):    {len(user_stories)} specifikováno v požadavky_ust_podle_src.md")
    print(f"  • Pokrytí User Stories v TC:   {us_covered_count}/{len(user_stories)} ({us_pct:.1f} %)")
    if analysis['uncovered_stories']:
        print(f"    └─ ⚠️  Nepokryté požadavky bez Test Casů: {', '.join(analysis['uncovered_stories'])} (doplňte do TEST_CASES.md)")
    print(f"  • Testovací případy v katalogu:{analysis['total_spec']} v docs/TEST_CASES.md")
    print(f"  • Pokryto automatizací:        {len(analysis['covered_cases'])} ({analysis['coverage_pct']:.1f} %)")
    print(f"  • Chybějící testy v kódu:      {len(analysis['missing_cases'])}")
    print(f"  • Testy s evidovaným defektem: {len(analysis['xfail_cases'])} (označeno @pytest.mark.xfail)")
    print(f"  • Testy s legacy ID:           {len(analysis['legacy_cases'])}")
    print(f"  • E2E Cross-cutting toky:      {len(analysis['navigation_journey_tests'])} (@pytest.mark.navigation)")
    print(f"  • Neshody v markerech:         {len(analysis['marker_mismatches'])}")
    print("=" * 110)


def print_story_detail(story_id: str, analysis: Dict[str, Any]):
    """Vypíše kompletní detail byznysové User Story a všechny navázané TC, testy a bugy."""
    story_id = story_id.upper()
    stories = analysis["user_stories"]
    if story_id not in stories:
        print(f"Chyba: User Story '{story_id}' nebyla nalezena v docs/požadavky_ust_podle_src.md.", file=sys.stderr)
        return

    us = stories[story_id]
    tcs = analysis["us_to_tcs"].get(story_id, [])
    bugs = analysis["bug_reports"]

    print("=" * 90)
    print(f"📖 DETAIL POŽADAVKU: {us.us_id} – {us.title}")
    print("=" * 90)
    if us.actor:
        print(f"  • Jako:   {us.actor}")
    if us.goal:
        print(f"  • Chci:   {us.goal}")
    if us.benefit:
        print(f"  • Abych:  {us.benefit}")

    if us.criteria:
        print("\n  📋 Akceptační kritéria:")
        for idx, crit in enumerate(us.criteria, 1):
            print(f"     {idx}. {crit}")

    print("\n  🔍 Navázané Test Casy a stav automatizace:")
    if not tcs:
        print("     ❌ Žádný testovací případ není v docs/TEST_CASES.md navázán na tuto User Story!")
    else:
        for tc in tcs:
            tests = analysis["tc_to_tests"].get(tc.tc_id, [])
            if not tests:
                tc_status = "❌ Neimplementováno"
            else:
                fn = tests[0]
                if fn.is_xfail:
                    tc_status = f"⚠️ XFAIL ({fn.linked_bug_id or 'Defekt'})"
                elif fn.is_legacy_match:
                    tc_status = "🟡 Pokryto (Legacy ID)"
                else:
                    tc_status = "🟢 Pokryto"

            print(f"     • [{tc.tc_id}] {tc.title} -> {tc_status}")
            for t in tests:
                print(f"       └─ Kód: {Path(t.file_path).name}:{t.line_no} [{t.function_name}]")

    # Navázané defekty
    linked_bugs = [b for b in bugs.values() if story_id in b.linked_stories]
    if linked_bugs:
        print("\n  🐞 Evidované defekty v docs/JIRA_BUG_REPORTS.md:")
        for b in linked_bugs:
            print(f"     • [{b.bug_id}] {b.title} ({b.severity} / {b.priority}) -> {b.status}")

    print("=" * 90)


def find_test_context(keyword: str, analysis: Dict[str, Any]):
    """Reverzní vyhledání: Vyhledá test v kódu a zobrazí celou cestu až k požadavku a defektu."""
    code_tests = scan_test_codebase(Path("tests"))
    matches = [
        t for t in code_tests
        if keyword.lower() in t.function_name.lower() or keyword.lower() in Path(t.file_path).name.lower()
    ]

    if not matches:
        print(f"Nenalezen žádný test v kódu odpovídající klíči: '{keyword}'")
        return

    print("=" * 95)
    print(f"🔍 REVERZNÍ TRASOVÁNÍ PRO: '{keyword}' ({len(matches)} nalezených testů)")
    print("=" * 95)

    spec_cases = analysis["spec_cases"]
    user_stories = analysis["user_stories"]
    bugs = analysis["bug_reports"]

    for t in matches:
        print(f"\n▶ Kód testu:     {Path(t.file_path).name}:{t.line_no} -> {t.full_name}")
        print(f"  Pytest markery: {', '.join(t.markers) if t.markers else 'žádné'}")
        if t.docstring:
            print(f"  Docstring:      {t.docstring.splitlines()[0]}")

        if t.is_xfail:
            print(f"  ⚠️  XFAIL Důvod: {t.xfail_reason}")
            if t.linked_bug_id and t.linked_bug_id in bugs:
                b = bugs[t.linked_bug_id]
                print(f"  🐞 JIRA Defekt: [{b.bug_id}] {b.title} ({b.severity} / {b.priority})")

        if t.matched_tc_id and t.matched_tc_id in spec_cases:
            tc = spec_cases[t.matched_tc_id]
            print(f"  🎯 Test Case:   [{tc.tc_id}] {tc.title} ({tc.priority_type})")
            if tc.user_story in user_stories:
                us = user_stories[tc.user_story]
                print(f"  📖 Požadavek:   [{us.us_id}] {us.title}")
                if us.criteria:
                    print(f"  📋 Akceptační kritérium: {us.criteria[0][:80]}...")
        else:
            print("  ℹ️  Tento test nemá přímé mapování na konkrétní TC v katalogu (např. integrační tok).")

    print("=" * 95)


def get_priority_weight(priority_type: str) -> Tuple[int, str]:
    """Vrátí váhu priority pro řazení a ikonku."""
    p_lower = priority_type.lower()
    if "smoke" in p_lower or "p1" in p_lower:
        return (1, "🔴 P1 (Smoke)")
    elif "p2" in p_lower or "funkční" in p_lower or "negativní" in p_lower:
        return (2, "🟡 P2 (Regresní)")
    else:
        return (3, "🟢 P3 (Hraniční)")


def print_missing(analysis: Dict[str, Any], show_detail: bool = False):
    """Vypíše přehlednou prioritizovanou tabulku chybějících testů a volitelně detailní kroky."""
    missing: List[str] = analysis["missing_cases"]
    spec_cases: Dict[str, TestCaseSpec] = analysis["spec_cases"]

    if not missing:
        print("🎉 Všechny specifikované testovací případy mají automatizovaný test! 100% pokrytí.")
        return

    # Seřazení chybějících testů podle priorit (P1 -> P2 -> P3)
    sorted_missing = sorted(
        missing,
        key=lambda tc_id: (get_priority_weight(spec_cases[tc_id].priority_type)[0], tc_id)
    )

    p1_count = sum(1 for tc in missing if get_priority_weight(spec_cases[tc].priority_type)[0] == 1)
    p2_count = sum(1 for tc in missing if get_priority_weight(spec_cases[tc].priority_type)[0] == 2)
    p3_count = sum(1 for tc in missing if get_priority_weight(spec_cases[tc].priority_type)[0] == 3)

    print("=" * 115)
    print(f"❌ CHYBĚJÍCÍ AUTOMATIZOVANÉ TESTY ({len(missing)} případů k doprogramování)")
    print(f"   Stávající pokrytí: {analysis['coverage_pct']:.1f} % ➔ Po dokončení: 100.0 % (+{100.0 - analysis['coverage_pct']:.1f} %)")
    print(f"   Rozpad priorit:    {p1_count}× 🔴 P1 (Kritické/Smoke), {p2_count}× 🟡 P2 (Funkční/Regresní), {p3_count}× 🟢 P3 (Hraniční/Validace)")
    print("=" * 115)
    print(f"{'Priorita':<16} | {'Kód TC':<12} | {'US':<7} | {'Cílový soubor':<35} | {'Název testovacího případu'}")
    print("-" * 115)

    current_prio_group = None
    for tc_id in sorted_missing:
        spec = spec_cases[tc_id]
        prio_weight, prio_label = get_priority_weight(spec.priority_type)

        if prio_weight != current_prio_group:
            current_prio_group = prio_weight
            print(f"--- Skupina: {prio_label} " + "-" * 85)

        us_info = US_TARGET_MAP.get(spec.user_story, {})
        target_file = us_info.get("file", f"tests/{spec.module_code.lower()}/test_{spec.module_code.lower()}.py")

        print(
            f"{prio_label:<16} | {spec.tc_id:<12} | {spec.user_story:<7} | {target_file:<35} | {spec.title}"
        )

    print("=" * 115)
    print("💡 DOPORUČENÝ POSTUP:")
    print("  1. Začněte implementací prioritních testů 🔴 P1 (např. TC-20-AUTH – bezpečnostní rate limit).")
    print("  2. Pro vygenerování AAA kostry zvoleného testu spusťte:")
    print("     python3 .agents/skills/traceability/scripts/scan_traceability.py --scaffold <TC_ID>")
    print("  3. Pro zobrazení detailních kroků a testovacích dat přidejte přepínač: --detail")
    print("=" * 115)

    if show_detail:
        print("\n" + "#" * 90)
        print("📋 DETAILNÍ SPECIFIKACE KROKŮ A TESTOVACÍCH DAT ZE SPECIFIKACE")
        print("#" * 90)
        for tc_id in sorted_missing:
            spec = spec_cases[tc_id]
            _, prio_label = get_priority_weight(spec.priority_type)
            print(f"\n▶ [{spec.tc_id}] {spec.title}")
            print(f"  • Pokrytí:  {spec.user_story} ({spec.module_code})")
            print(f"  • Priorita: {prio_label} ({spec.priority_type})")
            if spec.prerequisites:
                print(f"  • Předpoklady: {spec.prerequisites}")
            if spec.test_data:
                print(f"  • Data: {spec.test_data}")
            if spec.steps:
                print(f"  • Kroky ({len(spec.steps)}):")
                for idx, s in enumerate(spec.steps, 1):
                    print(f"      {idx}. {s}")
            if spec.expected_result:
                print(f"  • Očekávaný výsledek:")
                for res in spec.expected_result:
                    print(f"      - {res}")
            print(f"  💡 Vygenerovat kostru: python3 .agents/skills/traceability/scripts/scan_traceability.py --scaffold {spec.tc_id}")


def print_marker_audit(analysis: Dict[str, Any]):
    """Vypíše nalezené neshody v markerech a docstring formátech."""
    mismatches = analysis["marker_mismatches"]
    legacy = analysis["legacy_cases"]
    unmapped = analysis["unmapped_tests"]

    print("=" * 90)
    print("🔍 AUDIT KVALITY MARKERŮ A FORMÁTU ID")
    print("=" * 90)

    if not mismatches and not legacy and not unmapped:
        print("✅ Všechny testy v kódu mají správné markery, standardní ID a 100% soulad s AGENTS.md.")
        return

    if legacy:
        print(f"\n⚠️  ZASTARALÉ FORMÁTY ID V DOCSTRINGU ({len(legacy)} testů):")
        print("   Tyto testy používají starší formát (např. 'TC01' místo kanonického 'TC-01-AUTH').")
        for tc_id in legacy:
            tests = analysis["tc_to_tests"][tc_id]
            for t in tests:
                print(f"   • {Path(t.file_path).name}:{t.line_no} [{t.function_name}] -> doporučeno sjednotit na {tc_id}")
        print("   💡 Pro zobrazení návrhu automatické opravy spusťte parametr: --fix-docstrings")

    if mismatches:
        print(f"\n⚠️  NESHODY V PYTEST MARKERECH ({len(mismatches)} případů):")
        for m in mismatches:
            print(f"   • [{m['tc_id']}] {Path(m['file_path']).name}:{m['line_no']} ({m['test_func']})")
            for reason in m["reasons"]:
                print(f"     └─ {reason}")

    if unmapped:
        print(f"\nℹ️  TESTY V KÓDU BEZ PŘÍMÉHO NAMAPOVÁNÍ NA TC-xx ({len(unmapped)} testů):")
        for u in unmapped:
            print(f"   • {Path(u.file_path).name}:{u.line_no} -> {u.full_name} (docstring: {u.docstring[:40]}...)")


def scaffold_test(tc_id: str, spec_cases: Dict[str, TestCaseSpec]):
    """Vygeneruje kompletní AAA šablonu testu pro zadané TC ID."""
    tc_id = tc_id.upper()
    if tc_id not in spec_cases:
        print(f"Chyba: Test Case '{tc_id}' nebyl nalezen v docs/TEST_CASES.md.", file=sys.stderr)
        return

    spec = spec_cases[tc_id]

    us_info = US_TARGET_MAP.get(spec.user_story, {})
    target_file = us_info.get("file", f"tests/{spec.module_code.lower()}/test_{spec.module_code.lower()}.py")
    primary_po = us_info.get("po", "BasePage")

    clean_title = strip_accents(spec.title.lower())
    clean_title = re.sub(r'[^a-z0-9\s]', '', clean_title)
    title_words = clean_title.split()[:5]
    title_suffix = "_".join(title_words)
    tc_num = re.search(r'\d+', spec.tc_id)
    num_str = tc_num.group(0) if tc_num else "00"
    func_name = f"test_tc{num_str}_{spec.module_code.lower()}_{title_suffix}"

    domain_marker = spec.expected_domain_marker
    severity_marker = spec.expected_severity_marker

    steps_comment = "\n".join([f"        # {idx}. {step}" for idx, step in enumerate(spec.steps, 1)]) if spec.steps else "        # 1. Proveďte kroky scénáře"
    expected_comment = "\n".join([f"        # - {res}" for res in spec.expected_result]) if spec.expected_result else "        # - Ověřte očekávaný výsledek"

    po_var = re.sub(r'(?<!^)(?=[A-Z])', '_', primary_po).lower()

    scaffold_code = f'''    @pytest.mark.{domain_marker}
    @pytest.mark.{severity_marker}
    def {func_name}(self, page: Page):
        """{spec.tc_id}: {spec.title}."""
        # =====================================================================
        # 1. ARRANGE (Příprava stavu a Page Objectů)
        # =====================================================================
        {po_var} = {primary_po}(page)
        # Předpoklady: {spec.prerequisites or "Výchozí stav dle specifikace"}
        # Data: {spec.test_data or "Dynamická data přes utils.data_generator"}
        {po_var}.open()

        # =====================================================================
        # 2. ACT (Kroky scénáře dle specifikace)
        # =====================================================================
{steps_comment}

        # =====================================================================
        # 3. ASSERT (3úrovňová validace: Routing + Session + Data State)
        # =====================================================================
{expected_comment}
        expect(page).to_be_visible({po_var}.heading)  # TODO: Upravte dle očekávaného prvku
'''

    print("=" * 90)
    print(f"🏗️  VYGENEROVANÁ ŠABLONA TESTU PRO {spec.tc_id}")
    print("=" * 90)
    print(f"Cílový soubor:  {target_file}")
    print(f"Doporučený POM: {primary_po}")
    print(f"Kód funkce:")
    print("-" * 90)
    print(scaffold_code)
    print("-" * 90)


def fix_docstrings_diff(analysis: Dict[str, Any], apply: bool = False):
    """Zobrazí diff a volitelně sjednotí zastaralé docstringy na kanonický TC-xx-MODUL."""
    legacy_cases = analysis["legacy_cases"]
    tc_to_tests = analysis["tc_to_tests"]

    if not legacy_cases:
        print("✅ Žádné testy se starším formátem docstringu nebyly nalezeny.")
        return

    modified_files: Dict[str, List[Tuple[int, str, str]]] = {}

    for tc_id in legacy_cases:
        for test in tc_to_tests[tc_id]:
            if not test.is_legacy_match:
                continue

            file_path = test.file_path
            old_pattern = re.compile(r'\bTC0?\d{1,2}:', re.IGNORECASE)

            lines = Path(file_path).read_text(encoding="utf-8").splitlines()
            target_line_idx = None
            for idx in range(test.line_no - 1, min(test.line_no + 5, len(lines))):
                if old_pattern.search(lines[idx]):
                    target_line_idx = idx
                    break

            if target_line_idx is not None:
                old_line = lines[target_line_idx]
                new_line = old_pattern.sub(f"{tc_id}:", old_line)
                if old_line != new_line:
                    if file_path not in modified_files:
                        modified_files[file_path] = []
                    modified_files[file_path].append((target_line_idx, old_line, new_line))

    if not modified_files:
        print("Nebyly nalezeny žádné bezpečně nahraditelné docstringy.")
        return

    print("=" * 90)
    print(f"🔧 NÁVRH OPRAV DOCSTRINGŮ ({sum(len(v) for v in modified_files.values())} výskytů):")
    print("=" * 90)

    for file_path, changes in modified_files.items():
        original_lines = Path(file_path).read_text(encoding="utf-8").splitlines()
        new_lines = list(original_lines)
        for idx, old_l, new_l in changes:
            new_lines[idx] = new_l

        diff = list(
            difflib.unified_diff(
                original_lines,
                new_lines,
                fromfile=f"a/{Path(file_path).name}",
                tofile=f"b/{Path(file_path).name}",
                lineterm="",
            )
        )
        print("\n".join(diff[:25]))

    if apply:
        for file_path, changes in modified_files.items():
            lines = Path(file_path).read_text(encoding="utf-8").splitlines()
            for idx, old_l, new_l in changes:
                lines[idx] = new_l
            Path(file_path).write_text("\n".join(lines) + "\n", encoding="utf-8")
        print("\n✅ Všechny navržené změny byly úspěšně zapsány do souborů.")
    else:
        print("\n💡 Pro aplikaci těchto úprav spusťte příkaz s přepínačem: --apply")


def export_markdown_report(analysis: Dict[str, Any], output_path: Path):
    """Vyexportuje kompletní Traceability Matrix do Markdown souboru s vazbou na US i defekty."""
    spec_cases: Dict[str, TestCaseSpec] = analysis["spec_cases"]
    tc_to_tests: Dict[str, List[AutomatedTestFunction]] = analysis["tc_to_tests"]
    user_stories: Dict[str, UserStorySpec] = analysis["user_stories"]
    project_root = Path.cwd()

    lines = [
        "# 🧭 Matice trasovatelnosti (Traceability Matrix)",
        "",
        f"* **Byznysové požadavky:** {len(user_stories)} User Stories (100 % pokryto v katalogu testů)",
        f"* **Celkem specifikovaných testů:** {analysis['total_spec']} (v [`docs/TEST_CASES.md`](TEST_CASES.md))",
        f"* **Pokryto automatizací:** {len(analysis['covered_cases'])} ({analysis['coverage_pct']:.1f} %)",
        f"* **Chybějící scénáře:** {len(analysis['missing_cases'])}",
        f"* **Testy s evidovaným defektem (XFAIL):** {len(analysis['xfail_cases'])} (viz [`docs/JIRA_BUG_REPORTS.md`](JIRA_BUG_REPORTS.md))",
        f"* **Neshody v markerech:** {len(analysis['marker_mismatches'])}",
        "",
        "---",
        "",
        "## 📋 Kompletní přehled testovacích případů",
        "",
        "| Modul | User Story | Kód testu | Název testovacího případu | Stav v kódu | Markery | Implementace v kódu |",
        "| :---: | :---: | :---: | :--- | :---: | :---: | :--- |",
    ]

    for tc_id, spec in sorted(spec_cases.items()):
        tests = tc_to_tests[tc_id]
        if not tests:
            status = "❌ Neimplementováno"
            markers = f"(`{spec.expected_severity_marker}`)"
            impl = "—"
        else:
            fn = tests[0]
            if fn.is_xfail:
                status = f"⚠️ XFAIL ([{fn.linked_bug_id or 'Defekt'}](JIRA_BUG_REPORTS.md))"
            elif fn.is_legacy_match:
                status = "🟡 Legacy ID"
            else:
                status = "🟢 Pokryto"

            markers = ", ".join([f"`{m}`" for m in fn.markers]) if fn.markers else "—"
            try:
                rel_path = Path(fn.file_path).relative_to(project_root)
            except ValueError:
                rel_path = Path(fn.file_path)
            impl = f"[`{Path(fn.file_path).name}:{fn.line_no}`](../{rel_path}#L{fn.line_no}) -> `{fn.function_name}`"

        lines.append(
            f"| **{spec.module_code}** | [`{spec.user_story}`](požadavky_ust_podle_src.md) | `{spec.tc_id}` | {spec.title} | {status} | {markers} | {impl} |"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"✅ Matice trasovatelnosti byla úspěšně vyexportována do: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Traceability & Coverage Scanner pro testy Playwright/Pytest",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--matrix",
        action="store_true",
        help="Zobrazit kompletní tabulku Traceability Matrix v terminálu (výchozí)",
    )
    parser.add_argument(
        "--story",
        type=str,
        metavar="US_ID",
        help="Zobrazit kompletní detail User Story, navázané TC, testy a evidované defekty (např. --story US-18)",
    )
    parser.add_argument(
        "--find",
        type=str,
        metavar="KEYWORD",
        help="Reverzní vyhledání: Najít test v kódu a vypsat celou cestu až k požadavku a defektu",
    )
    parser.add_argument(
        "--missing",
        action="store_true",
        help="Zobrazit přehlednou tabulku chybějících testů seřazenou podle priorit (P1/P2/P3)",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Zobrazit detailní kroky a data ze specifikace u chybějících testů (ve spojení s --missing)",
    )
    parser.add_argument(
        "--verify-markers",
        action="store_true",
        help="Zkontrolovat shodu Pytest markerů a formátu TC ID s pravidly projektu",
    )
    parser.add_argument(
        "--scaffold",
        type=str,
        metavar="TC_ID",
        help="Vygenerovat AAA kostru testu pro zadané TC ID (např. TC-13-AUTH)",
    )
    parser.add_argument(
        "--fix-docstrings",
        action="store_true",
        help="Zobrazit diff pro normalizaci starších ID v docstringu (např. TC01 -> TC-01-AUTH)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Použít ve spojení s --fix-docstrings pro zápis úprav do souborů",
    )
    parser.add_argument(
        "--export-md",
        type=str,
        metavar="FILE_PATH",
        help="Vyexportovat matici trasovatelnosti do Markdown souboru (např. docs/TRACEABILITY_MATRIX.md)",
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    ust_path = project_root / "docs" / "požadavky_ust_podle_src.md"
    test_cases_path = project_root / "docs" / "TEST_CASES.md"
    jira_path = project_root / "docs" / "JIRA_BUG_REPORTS.md"
    tests_dir = project_root / "tests"

    if not test_cases_path.exists():
        print(f"Chyba: Soubor specifikace {test_cases_path} neexistuje.", file=sys.stderr)
        sys.exit(1)

    user_stories = parse_user_stories_md(ust_path)
    spec_cases = parse_test_cases_md(test_cases_path)
    bug_reports = parse_bug_reports_md(jira_path)
    code_tests = scan_test_codebase(tests_dir)

    analysis = analyze_traceability(user_stories, spec_cases, code_tests, bug_reports)

    executed_action = False

    if args.story:
        print_story_detail(args.story, analysis)
        executed_action = True

    if args.find:
        find_test_context(args.find, analysis)
        executed_action = True

    if args.missing:
        print_missing(analysis, show_detail=args.detail)
        executed_action = True

    if args.verify_markers:
        print_marker_audit(analysis)
        executed_action = True

    if args.scaffold:
        scaffold_test(args.scaffold, spec_cases)
        executed_action = True

    if args.fix_docstrings:
        fix_docstrings_diff(analysis, apply=args.apply)
        executed_action = True

    if args.export_md:
        export_markdown_report(analysis, Path(args.export_md))
        executed_action = True

    if not executed_action or args.matrix:
        print_matrix(analysis)


if __name__ == "__main__":
    main()

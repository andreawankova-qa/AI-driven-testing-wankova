#!/usr/bin/env python3
"""
Generátor přehledu automatizovaných testů (Test Steps & Checks Overview)
========================================================================

Tento skript analyzuje všechny automatizované testy (Playwright / Pytest)
v zadaném adresáři (výchozí: tests/) a generuje přehledný Markdown soubor.
Pro každý test extrahuje:
- Kanonické ID (TC-xx-MODUL) a název testu
- Cíl a popis testu (z docstringu)
- Pytest markery (smoke, regression, doménový marker, xfail)
- Testovací vstupy, varianty a parametrizaci
- Předpoklady a setup fixtures
- Všechny sekvenční kroky (akce, navigace, formuláře)
- Všechny validace a kontroly (Playwright expect web-first assertions, python asserts)
- Kontextové komentáře z kódu testu

Použití:
  python3 generate_test_overview.py
  python3 generate_test_overview.py --output docs/TEST_STEPS_OVERVIEW.md
  python3 generate_test_overview.py --module auth
  python3 generate_test_overview.py --marker smoke
"""

import os
import re
import sys
import ast
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Regulární výrazy pro detekci TC ID
RE_CANONICAL_TC = re.compile(r'\bTC-(?P<num>\d{2})-(?P<mod>[A-Z]{3,4})\b', re.IGNORECASE)
RE_FUNC_TC = re.compile(r'\btest_tc(?P<num>\d{2})_(?P<mod>[a-z]{3,4})_', re.IGNORECASE)
RE_LEGACY_TC = re.compile(r'\bTC0?(?P<num>\d{1,2})\b', re.IGNORECASE)

# Názvy a ikony modulů
MODULE_META = {
    "AUTH": {"title": "Autentizace a správa sezení", "icon": "🔐", "dir": "auth"},
    "CRS": {"title": "Katalog kurzů a detail běhů", "icon": "📚", "dir": "courses"},
    "ENR": {"title": "Zápis na kurz a Moje kurzy", "icon": "📝", "dir": "enrollment"},
    "LEC": {"title": "Lektorská správa kurzů", "icon": "🎓", "dir": "lecturer"},
    "NAV": {"title": "Navigace a integrace stránek", "icon": "🧭", "dir": "navigation"},
    "PRF": {"title": "Uživatelský profil a nástěnka", "icon": "👤", "dir": "profile"},
    "SEC": {"title": "Bezpečnost, RBAC a architektura", "icon": "🛡️", "dir": "security"},
    "OTHER": {"title": "Ostatní testy", "icon": "🧪", "dir": ""},
}


def format_ast_expr(node: Optional[ast.AST]) -> str:
    """Převede AST výraz na stručnou čitelnou textovou reprezentaci."""
    if node is None:
        return ""
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{format_ast_expr(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        func_name = format_ast_expr(node.func)
        args_str = ", ".join(format_ast_expr(a) for a in node.args[:2])
        if len(node.args) > 2:
            args_str += ", ..."
        return f"{func_name}({args_str})"
    if isinstance(node, ast.Subscript):
        return f"{format_ast_expr(node.value)}[{format_ast_expr(node.slice)}]"
    if isinstance(node, ast.List):
        return "[" + ", ".join(format_ast_expr(e) for e in node.elts[:3]) + (", ...]" if len(node.elts) > 3 else "]")
    if isinstance(node, ast.Dict):
        return "{...}"
    if isinstance(node, ast.UnaryOp):
        return f"not {format_ast_expr(node.operand)}"
    if isinstance(node, ast.Compare):
        left = format_ast_expr(node.left)
        return f"{left} ..."
    return "..."


class StepInterpreter:
    """Interpretuje AST uzly v těle testovací funkce do lidsky čitelných kroků a kontrol."""

    def __init__(self, source_lines: List[str]):
        self.source_lines = source_lines

    def _get_raw_code(self, node: ast.AST) -> str:
        line_start = getattr(node, "lineno", 1)
        line_end = getattr(node, "end_lineno", line_start)
        lines = [self.source_lines[i - 1].strip() for i in range(line_start, min(line_end + 1, len(self.source_lines) + 1))]
        return " ".join(lines)

    def _get_preceding_comments(self, node: ast.AST, last_end_line: int) -> List[str]:
        comments = []
        start_line = getattr(node, "lineno", 1)
        # Hledáme komentáře v řádcích mezi předchozím příkazem a aktuálním příkazem
        for l_num in range(last_end_line + 1, start_line):
            if l_num <= len(self.source_lines):
                line = self.source_lines[l_num - 1].strip()
                if line.startswith("#"):
                    comment_text = line.lstrip("#").strip()
                    if comment_text:
                        comments.append(comment_text)
        # Také zkontrolujeme inline komentář na stejném řádku
        if start_line <= len(self.source_lines):
            curr_line = self.source_lines[start_line - 1]
            if "#" in curr_line and not curr_line.strip().startswith("#"):
                inline_comment = curr_line.split("#", 1)[1].strip()
                if inline_comment and inline_comment not in comments:
                    comments.append(inline_comment)
        return comments

    def interpret_statement(self, stmt: ast.AST, last_end_line: int = 0) -> Optional[Dict[str, Any]]:
        # Přeskočit osamocený řetězec (např. docstring)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
            return None

        comments = self._get_preceding_comments(stmt, last_end_line)
        comment_summary = " | ".join(comments) if comments else None
        raw_code = self._get_raw_code(stmt)

        # 1. ASERCE / KONTROLY (Playwright expect)
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            # expect(target).assertion_method(args)
            if isinstance(call.func, ast.Attribute) and isinstance(call.func.value, ast.Call):
                inner_call = call.func.value
                if isinstance(inner_call.func, ast.Name) and inner_call.func.id == "expect":
                    method = call.func.attr
                    target = format_ast_expr(inner_call.args[0]) if inner_call.args else "prvek"
                    args_list = [format_ast_expr(a) for a in call.args]
                    args_desc = ", ".join(args_list)

                    desc, check_category = self._interpret_expect(method, target, args_list, args_desc)
                    return {
                        "category": "CHECK",
                        "badge": "🔍 Kontrola",
                        "subcategory": check_category,
                        "description": desc,
                        "code": raw_code,
                        "comment": comment_summary,
                        "lineno": stmt.lineno,
                    }

        # 2. PYTHON ASSERT
        if isinstance(stmt, ast.Assert):
            msg = format_ast_expr(stmt.msg) if stmt.msg else None
            desc = f"Ověření podmínky datového stavu: `{raw_code}`"
            if msg:
                desc += f" (Očekáváno: {msg})"
            return {
                "category": "CHECK",
                "badge": "🔍 Kontrola",
                "subcategory": "Datový stav",
                "description": desc,
                "code": raw_code,
                "comment": comment_summary,
                "lineno": stmt.lineno,
            }

        # 3. VOLÁNÍ METOD A AKCÍ
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value
            func_name = format_ast_expr(call.func)
            args_desc = ", ".join(format_ast_expr(a) for a in call.args)

            badge, action_desc, subcat = self._interpret_action(func_name, args_desc, call)
            return {
                "category": "ACTION",
                "badge": badge,
                "subcategory": subcat,
                "description": action_desc,
                "code": raw_code,
                "comment": comment_summary,
                "lineno": stmt.lineno,
            }

        # 4. PŘIŘAZENÍ (Inicializace Page Objectů, helpers, generování dat)
        if isinstance(stmt, ast.Assign):
            targets = ", ".join(format_ast_expr(t) for t in stmt.targets)
            val = format_ast_expr(stmt.value)

            badge, assign_desc, cat, subcat = self._interpret_assignment(targets, val, stmt)
            return {
                "category": cat,
                "badge": badge,
                "subcategory": subcat,
                "description": assign_desc,
                "code": raw_code,
                "comment": comment_summary,
                "lineno": stmt.lineno,
            }

        # 5. PODMÍNKY (if / else)
        if isinstance(stmt, ast.If):
            test_desc = format_ast_expr(stmt.test)
            substeps_body = []
            cur_line = stmt.lineno
            for s in stmt.body:
                step = self.interpret_statement(s, cur_line)
                if step:
                    substeps_body.append(step)
                cur_line = getattr(s, "end_lineno", s.lineno)

            substeps_else = []
            if stmt.orelse:
                for s in stmt.orelse:
                    step = self.interpret_statement(s, cur_line)
                    if step:
                        substeps_else.append(step)
                    cur_line = getattr(s, "end_lineno", s.lineno)

            return {
                "category": "BRANCH",
                "badge": "🔀 Větvení",
                "subcategory": "Podmíněný scénář",
                "description": f"Podmíněná větev: pokud platí `{test_desc}`",
                "code": f"if {test_desc}:",
                "comment": comment_summary,
                "lineno": stmt.lineno,
                "substeps": substeps_body,
                "substeps_else": substeps_else,
            }

        # 6. CYKLY (for / while)
        if isinstance(stmt, ast.For):
            target = format_ast_expr(stmt.target)
            iter_desc = format_ast_expr(stmt.iter)
            substeps = []
            cur_line = stmt.lineno
            for s in stmt.body:
                step = self.interpret_statement(s, cur_line)
                if step:
                    substeps.append(step)
                cur_line = getattr(s, "end_lineno", s.lineno)

            return {
                "category": "LOOP",
                "badge": "🔁 Cyklus",
                "subcategory": "Opakování kroků",
                "description": f"Iterace kroků (`pro {target} v {iter_desc}`)",
                "code": f"for {target} in {iter_desc}:",
                "comment": comment_summary,
                "lineno": stmt.lineno,
                "substeps": substeps,
            }

        # Ostatní příkazy
        return {
            "category": "ACTION",
            "badge": "▶️ Krok",
            "subcategory": "Operace",
            "description": f"Příkaz: `{raw_code}`",
            "code": raw_code,
            "comment": comment_summary,
            "lineno": stmt.lineno,
        }

    def _interpret_expect(self, method: str, target: str, args_list: List[str], args_desc: str) -> Tuple[str, str]:
        """Převede Playwright expect metodu na srozumitelný český popis a kategorii."""
        if method == "to_be_visible":
            return f"Ověření viditelnosti prvku `{target}` na stránce", "UI Viditelnost"
        if method == "not_to_be_visible":
            return f"Ověření nepřítomnosti / skrytí prvku `{target}`", "UI Negativní"
        if method == "to_have_text":
            return f"Ověření přesného textu prvku `{target}` (očekáváno: {args_desc})", "Text / Obsah"
        if method == "to_contain_text":
            return f"Ověření, že text prvku `{target}` obsahuje {args_desc}", "Text / Obsah"
        if method == "not_to_contain_text":
            return f"Ověření, že text prvku `{target}` neobsahuje {args_desc}", "Text / Obsah"
        if method == "to_have_url":
            return f"Ověření přesměrování a URL adresy (očekáváno: {args_desc})", "Routing"
        if method == "to_have_title":
            return f"Ověření titulku webové stránky `<title>` (očekáváno: {args_desc})", "Metadata"
        if method == "to_have_value":
            return f"Ověření hodnoty ve formulářovém poli `{target}` (očekáváno: {args_desc})", "Formulář"
        if method == "to_have_attribute":
            return f"Ověření HTML atributu prvku `{target}` ({args_desc})", "Atributy"
        if method == "to_be_enabled":
            return f"Ověření, že prvek `{target}` je aktivní a povolený (enabled)", "Stav prvku"
        if method == "to_be_disabled":
            return f"Ověření, že prvek `{target}` je deaktivovaný (disabled)", "Stav prvku"
        if method == "to_be_focused":
            return f"Ověření fokusu na poli / prvku `{target}`", "Přístupnost"
        if method == "to_have_count":
            return f"Ověření přesného počtu prvků `{target}`: {args_desc}", "Počet prvků"
        if method == "not_to_have_count":
            return f"Ověření, že počet prvků `{target}` není {args_desc}", "Počet prvků"
        return f"Kontrola `{method}` pro prvek `{target}` ({args_desc})", "Validace"

    def _interpret_action(self, func_name: str, args_desc: str, call: ast.Call) -> Tuple[str, str, str]:
        """Převede volání metody na srozumitelnou uživatelskou či systémovou akci."""
        if func_name.endswith(".open"):
            po = func_name[:-5]
            return "🌐 Navigace", f"Otevření stránky `{po}`", "Navigace"
        if "page.goto" in func_name:
            return "🌐 Navigace", f"Přímá navigace na URL {args_desc}", "Navigace"
        if "page.reload" in func_name:
            return "🔄 Obnovení", "Obnovení aktuální stránky v prohlížeči (Reload / F5)", "Navigace"
        if "page.wait_for_load_state" in func_name:
            return "⏳ Čekání", f"Čekání na ustálení síťového a vykreslovacího stavu ({args_desc})", "Synchronizace"

        if func_name in ("login_user", "login_lecturer") or func_name.endswith(".login"):
            return "🔑 Autentizace", f"Provedení přihlášení uživatele ({args_desc})", "Autentizace"
        if func_name in ("logout_user",) or func_name.endswith(".logout"):
            return "🚪 Odhlášení", "Odhlášení uživatele z portálu", "Autentizace"

        if ".fill" in func_name:
            field_name = func_name.split(".")[-1].replace("fill_", "").replace("fill", "pole")
            return "✍️ Vstup", f"Vyplnění pole `{field_name}` hodnotou {args_desc}", "Formulář"
        if "page.keyboard.type" in func_name:
            return "✍️ Vstup", f"Simulace psaní na klávesnici: {args_desc}", "Formulář"
        if ".press" in func_name or "page.keyboard.press" in func_name:
            target = func_name.replace(".press", "")
            return "⌨️ Klávesa", f"Stisk klávesy {args_desc} v rámci `{target}`", "Interakce"

        if ".click" in func_name:
            target = func_name.replace(".click", "")
            return "🖱️ Kliknutí", f"Kliknutí na prvek / tlačítko `{target}`", "Interakce"
        if ".select_option" in func_name:
            target = func_name.replace(".select_option", "")
            return "📋 Výběr", f"Výběr hodnoty v rozbalovací nabídce `{target}` ({args_desc})", "Formulář"

        return "▶️ Krok", f"Vyvolání akce `{func_name}({args_desc})`", "Akce"

    def _interpret_assignment(self, targets: str, val: str, stmt: ast.Assign) -> Tuple[str, str, str, str]:
        """Převede přiřazení proměnné na popis (Page Object, data generator, helper)."""
        if "Page(" in val or "Page" in val and "(" in val:
            return "⚙️ Příprava", f"Inicializace Page Objectu `{val}` do proměnné `{targets}`", "SETUP", "Page Object"
        if "generate_" in val:
            return "🎲 Test Data", f"Dynamické generování testovacích dat `{val}` -> `{targets}`", "SETUP", "Testovací data"
        if "load_json_data" in val:
            return "📂 Test Data", f"Načtení externích testovacích dat: `{val}`", "SETUP", "Data-Driven"
        if "login_user" in val or "login_lecturer" in val:
            return "🔑 Autentizace", f"Přihlášení uživatele přes pomocný helper: `{val}` -> `{targets}`", "ACTION", "Autentizace"
        return "⚙️ Příprava", f"Nastavení lokální proměnné `{targets}` = `{val}`", "SETUP", "Lokální stav"


class TestCaseExtractor(ast.NodeVisitor):
    """AST návštěvník pro extrakci testovacích funkcí, tříd a jejich kroků."""

    def __init__(self, file_path: Path, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.interpreter = StepInterpreter(self.source_lines)

        self.current_class: Optional[str] = None
        self.current_class_doc: Optional[str] = None
        self.class_markers: List[str] = []
        self.class_fixtures: List[Dict[str, Any]] = []

        self.extracted_tests: List[Dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_class = self.current_class
        prev_doc = self.current_class_doc
        prev_markers = list(self.class_markers)
        prev_fixtures = list(self.class_fixtures)

        self.current_class = node.name
        self.current_class_doc = ast.get_docstring(node)
        self.class_markers = self._extract_markers(node.decorator_list)
        self.class_fixtures = []

        # Kontrola autouse fixtures ve třídě
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                for dec in item.decorator_list:
                    if self._is_autouse_fixture(dec):
                        self.class_fixtures.append({
                            "name": item.name,
                            "docstring": ast.get_docstring(item) or "",
                            "lineno": item.lineno,
                        })

        self.generic_visit(node)

        self.current_class = prev_class
        self.current_class_doc = prev_doc
        self.class_markers = prev_markers
        self.class_fixtures = prev_fixtures

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if node.name.startswith("test_"):
            docstring = ast.get_docstring(node) or ""
            fn_markers = self._extract_markers(node.decorator_list)
            all_markers = list(dict.fromkeys(self.class_markers + fn_markers))

            # Detekce xfail a linked bug
            xfail_reason, linked_bug = self._extract_xfail(node.decorator_list)

            # Detekce parametrizace
            parametrize_info = self._extract_parametrize(node.decorator_list)

            # Detekce kanonického TC ID a názvu
            tc_id, title = self._resolve_tc_id_and_title(node.name, docstring)

            # Detekce modulu
            module_code = self._detect_module(self.file_path, tc_id, all_markers)

            # Extrakce kroků a kontrol
            steps = []
            cur_line = node.lineno
            for stmt in node.body:
                step_data = self.interpreter.interpret_statement(stmt, cur_line)
                if step_data:
                    steps.append(step_data)
                cur_line = getattr(stmt, "end_lineno", stmt.lineno)

            # Agregace statistik kroků
            action_count = sum(1 for s in steps if s["category"] in ("ACTION", "SETUP", "BRANCH", "LOOP"))
            check_count = sum(1 for s in steps if s["category"] == "CHECK")
            # Přičíst kontroly z vnořených větví
            for s in steps:
                if "substeps" in s:
                    check_count += sum(1 for sub in s["substeps"] if sub["category"] == "CHECK")
                    action_count += sum(1 for sub in s["substeps"] if sub["category"] != "CHECK")
                if "substeps_else" in s:
                    check_count += sum(1 for sub in s["substeps_else"] if sub["category"] == "CHECK")
                    action_count += sum(1 for sub in s["substeps_else"] if sub["category"] != "CHECK")

            test_data = {
                "id": tc_id,
                "title": title,
                "function_name": node.name,
                "class_name": self.current_class,
                "file_path": str(self.file_path),
                "line_no": node.lineno,
                "module": module_code,
                "docstring": docstring,
                "markers": all_markers,
                "is_smoke": "smoke" in all_markers,
                "is_regression": "regression" in all_markers,
                "xfail_reason": xfail_reason,
                "linked_bug": linked_bug,
                "parametrize": parametrize_info,
                "class_fixtures": list(self.class_fixtures),
                "steps": steps,
                "action_count": action_count,
                "check_count": check_count,
            }
            self.extracted_tests.append(test_data)

        self.generic_visit(node)

    def _extract_markers(self, decorator_list: List[ast.AST]) -> List[str]:
        markers = []
        for dec in decorator_list:
            if isinstance(dec, ast.Attribute):
                if isinstance(dec.value, ast.Attribute) and dec.value.attr == "mark":
                    markers.append(dec.attr)
            elif isinstance(dec, ast.Call):
                func = dec.func
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Attribute) and func.value.attr == "mark":
                    markers.append(func.attr)
        return markers

    def _extract_xfail(self, decorator_list: List[ast.AST]) -> Tuple[Optional[str], Optional[str]]:
        for dec in decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                if isinstance(func, ast.Attribute) and getattr(func.value, "attr", "") == "mark" and func.attr == "xfail":
                    reason = ""
                    for kw in dec.keywords:
                        if kw.arg == "reason" and isinstance(kw.value, ast.Constant):
                            reason = str(kw.value.value)
                    bug_match = re.search(r'\bBR-(?P<num>\d{2})\b', reason, re.IGNORECASE)
                    linked_bug = f"BR-{bug_match.group('num')}" if bug_match else None
                    return reason, linked_bug
        return None, None

    def _extract_parametrize(self, decorator_list: List[ast.AST]) -> Optional[Dict[str, Any]]:
        for dec in decorator_list:
            if isinstance(dec, ast.Call):
                func = dec.func
                if isinstance(func, ast.Attribute) and getattr(func.value, "attr", "") == "mark" and func.attr == "parametrize":
                    arg_names = format_ast_expr(dec.args[0]) if len(dec.args) > 0 else ""
                    ids_val = None
                    for kw in dec.keywords:
                        if kw.arg == "ids":
                            ids_val = format_ast_expr(kw.value)
                    return {"args": arg_names, "ids": ids_val}
        return None

    def _is_autouse_fixture(self, dec: ast.AST) -> bool:
        if isinstance(dec, ast.Call):
            func = dec.func
            if (isinstance(func, ast.Attribute) and func.attr == "fixture") or (isinstance(func, ast.Name) and func.id == "fixture"):
                for kw in dec.keywords:
                    if kw.arg == "autouse" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                        return True
        return False

    def _resolve_tc_id_and_title(self, func_name: str, docstring: str) -> Tuple[str, str]:
        first_line = docstring.strip().splitlines()[0] if docstring.strip() else ""

        # 1. Hledání v docstringu: TC-01-AUTH: Popis
        m = RE_CANONICAL_TC.search(first_line)
        if m:
            tc_id = m.group(0).upper()
            title = first_line.replace(m.group(0), "").lstrip(":").strip()
            return tc_id, title or first_line

        # 2. Hledání v názvu funkce: test_tc06_auth_...
        mf = RE_FUNC_TC.search(func_name)
        if mf:
            tc_id = f"TC-{mf.group('num')}-{mf.group('mod').upper()}"
            title = first_line or func_name.replace(f"test_tc{mf.group('num')}_{mf.group('mod')}_", "").replace("_", " ").capitalize()
            return tc_id, title

        # 3. Záložní TC
        sec_m = re.search(r'test_tc(?P<num>\d{2})_(?P<mod>[a-zA-Z]{3,4})', func_name)
        if sec_m:
            tc_id = f"TC-{sec_m.group('num')}-{sec_m.group('mod').upper()}"
            return tc_id, first_line or func_name

        # 4. Generické pojmenování
        readable_title = first_line or func_name.replace("test_", "").replace("_", " ").capitalize()
        return func_name, readable_title

    def _detect_module(self, file_path: Path, tc_id: str, markers: List[str]) -> str:
        # Podle TC ID (např. TC-06-AUTH -> AUTH)
        parts = tc_id.split("-")
        if len(parts) == 3 and parts[2].upper() in MODULE_META:
            return parts[2].upper()

        # Podle markeru
        marker_map = {
            "auth": "AUTH",
            "courses": "CRS",
            "enrollment": "ENR",
            "lecturer": "LEC",
            "navigation": "NAV",
            "profile": "PRF",
            "security": "SEC",
        }
        for m in markers:
            if m.lower() in marker_map:
                return marker_map[m.lower()]

        # Podle cesty k souboru
        path_str = str(file_path).lower()
        for mod, meta in MODULE_META.items():
            if meta["dir"] and f"/{meta['dir']}/" in path_str:
                return mod

        return "OTHER"


class MarkdownOverviewGenerator:
    """Sestaví a vyexportuje strukturovaný Markdown přehled testů."""

    def __init__(self, tests: List[Dict[str, Any]], format_mode: str = "both"):
        self.tests = tests
        self.format_mode = format_mode

    def generate(self) -> str:
        now_str = datetime.now().strftime("%d. %m. %Y, %H:%M:%S")
        total_tests = len(self.tests)
        total_actions = sum(t["action_count"] for t in self.tests)
        total_checks = sum(t["check_count"] for t in self.tests)
        smoke_count = sum(1 for t in self.tests if t["is_smoke"])
        regression_count = sum(1 for t in self.tests if t["is_regression"])
        xfail_count = sum(1 for t in self.tests if t["xfail_reason"])

        # Seskupení podle modulů
        modules: Dict[str, List[Dict[str, Any]]] = {}
        for t in self.tests:
            mod = t["module"]
            modules.setdefault(mod, []).append(t)

        lines = []

        # Hlavička dokumentu
        lines.append("# 📋 Přehled automatizovaných testů (Test Steps & Checks Overview)")
        lines.append("")
        lines.append("> **Automaticky vygenerovaná živá dokumentace testovací sady Playwright & Pytest.**  ")
        lines.append(f"> *Tento dokument mapuje všech **{total_tests}** automatizovaných testů v projektu, jejich hierarchii, konkrétní uživatelské kroky, formulářové vstupy a veškeré prováděné kontroly (Web-First assertions).*")
        lines.append("")
        lines.append(f"*Poslední aktualizace: **{now_str}** | Zdrojové testy: `tests/**/*.py`*")
        lines.append("")

        # Manažerský souhrn a metriky
        lines.append("---")
        lines.append("")
        lines.append("## 📊 Manažerský souhrn a metriky testovací sady")
        lines.append("")
        lines.append("| Metrika | Hodnota | Poznámka |")
        lines.append("| :--- | :---: | :--- |")
        lines.append(f"| **Celkem automatizovaných testů (AT)** | **{total_tests}** | Unikátní implementované testovací metody |")
        lines.append(f"| **Pokrytých doménových modulů** | **{len(modules)}** | AUTH, CRS, ENR, LEC, NAV, PRF, SEC |")
        lines.append(f"| **Kritické scénáře (Smoke / P1)** | **{smoke_count}** | `@pytest.mark.smoke` – rychlá regrese jádra |")
        lines.append(f"| **Regresní a validační testy** | **{regression_count}** | `@pytest.mark.regression` – edge cases, chyby, limity |")
        lines.append(f"| **Evidované defekty (`xfail`)** | **{xfail_count}** | Očekávaně selhávající testy navázané na JIRA tickety |")
        lines.append(f"| **Celkový počet akčních kroků** | **{total_actions}** | Navigace, kliknutí, formuláře, příprava |")
        lines.append(f"| **Celkový počet ověření a kontrol** | **{total_checks}** | Playwright `expect()` web-first aserce |")
        lines.append("")

        # Rychlá navigace podle modulů
        lines.append("### 🧭 Rychlá navigace po modulech")
        lines.append("")
        for mod_code, mod_tests in sorted(modules.items()):
            meta = MODULE_META.get(mod_code, {"title": mod_code, "icon": "📁"})
            anchor = f"modul-{mod_code.lower()}"
            lines.append(f"- [{meta['icon']} **{meta['title']} ({mod_code})**](#{anchor}) – `{len(mod_tests)} testů` (kroků: {sum(t['action_count'] for t in mod_tests)}, kontrol: {sum(t['check_count'] for t in mod_tests)})")
        lines.append("")

        # Přehledová tabulka (pokud mode je 'both' nebo 'summary')
        if self.format_mode in ("both", "summary"):
            lines.append("---")
            lines.append("")
            lines.append("## 📑 Souhrnná tabulka všech testů")
            lines.append("")
            lines.append("| ID testu | Název a cíl testu | Modul | Typ / Marker | Kroky | Kontroly | Soubor |")
            lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :--- |")
            for t in self.tests:
                marker_badge = "🔥 Smoke" if t["is_smoke"] else ("🛡️ Regression" if t["is_regression"] else "🧪 Test")
                if t["xfail_reason"]:
                    marker_badge += f" (⚠️ {t['linked_bug'] or 'xfail'})"
                file_rel = t["file_path"].replace(os.getcwd() + "/", "")
                anchor = self._slugify(f"{t['id']}-{t['title']}")
                lines.append(
                    f"| [`{t['id']}`](#{anchor}) | {t['title']} | `{t['module']}` | {marker_badge} | {t['action_count']} | {t['check_count']} | `{file_rel}` |"
                )
            lines.append("")

        # Pokud byl požadován pouze souhrn, skončíme zde
        if self.format_mode == "summary":
            return "\n".join(lines)

        # Detailní rozpad podle modulů a testů
        lines.append("---")
        lines.append("")
        lines.append("## 🔍 Detailní rozpad kroků a kontrol jednotlivých testů")
        lines.append("")

        for mod_code, mod_tests in sorted(modules.items()):
            meta = MODULE_META.get(mod_code, {"title": mod_code, "icon": "📁"})
            anchor_mod = f"modul-{mod_code.lower()}"
            lines.append(f"<a id=\"{anchor_mod}\"></a>")
            lines.append(f"### {meta['icon']} Modul: {meta['title']} ({mod_code})")
            lines.append("")
            lines.append(f"*Počet testů v modulu: **{len(mod_tests)}** | Celkem akcí: **{sum(t['action_count'] for t in mod_tests)}** | Celkem kontrol: **{sum(t['check_count'] for t in mod_tests)}***")
            lines.append("")

            for t in mod_tests:
                anchor_test = self._slugify(f"{t['id']}-{t['title']}")
                lines.append(f"<a id=\"{anchor_test}\"></a>")
                lines.append(f"#### `{t['id']}`: {t['title']}")
                lines.append("")

                # Metadata box
                lines.append("| Vlastnost | Hodnota |")
                lines.append("| :--- | :--- |")
                lines.append(f"| **Kód funkce** | `{t['function_name']}()` |")
                if t["class_name"]:
                    lines.append(f"| **Testovací třída** | `{t['class_name']}` |")
                lines.append(f"| **Zdrojový soubor** | [`{t['file_path']}:{t['line_no']}`]({t['file_path']}#L{t['line_no']}) |")
                lines.append(f"| **Pytest Markery** | {', '.join(f'`@{m}`' for m in t['markers']) or 'žádné'} |")

                if t["xfail_reason"]:
                    lines.append(f"| **⚠️ Evidovaný defekt (xfail)** | **{t['xfail_reason']}** |")

                if t["parametrize"]:
                    p_info = f"Parametry: `{t['parametrize']['args']}`"
                    if t['parametrize']['ids']:
                        p_info += f", Scénáře: `{t['parametrize']['ids']}`"
                    lines.append(f"| **Data-driven varianty** | {p_info} |")

                if t["class_fixtures"]:
                    fix_names = ", ".join(f"`{f['name']}`" for f in t["class_fixtures"])
                    lines.append(f"| **Automatické předpoklady (Fixtures)** | {fix_names} |")

                lines.append("")

                if t["docstring"]:
                    doc_lines = [dl.strip() for dl in t["docstring"].splitlines() if dl.strip()]
                    if len(doc_lines) > 1:
                        lines.append(f"> **Účel testu:** {' '.join(doc_lines[1:])}")
                        lines.append("")

                # Detailní postup kroků a kontrol
                lines.append("##### 👣 Postup testu (Kroky & Kontroly):")
                lines.append("")

                if not t["steps"]:
                    lines.append("_Test neobsahuje žádné explicitní kroky nebo kontroly v těle funkce._")
                    lines.append("")
                    continue

                step_num = 1
                for step in t["steps"]:
                    self._render_step(lines, step, step_num, indent=0)
                    step_num += 1

                lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("*(Konec vygenerovaného přehledu testů)*")
        return "\n".join(lines)

    def _render_step(self, lines: List[str], step: Dict[str, Any], number: int, indent: int = 0):
        pad = "  " * indent
        prefix = f"{pad}{number}. " if number > 0 else f"{pad}- "

        badge = step["badge"]
        desc = step["description"]
        comment = step.get("comment")

        comment_part = f" — *({comment})*" if comment else ""
        lines.append(f"{prefix}**{badge}:** {desc}{comment_part}")
        lines.append(f"{pad}   `{step['code']}`")

        # Vnořené větve pro podmínky
        if "substeps" in step and step["substeps"]:
            sub_num = 1
            for sub in step["substeps"]:
                self._render_step(lines, sub, sub_num, indent + 1)
                sub_num += 1

        if "substeps_else" in step and step["substeps_else"]:
            lines.append(f"{pad}   *Jinak:*")
            sub_num = 1
            for sub in step["substeps_else"]:
                self._render_step(lines, sub, sub_num, indent + 1)
                sub_num += 1

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-z0-9]+', '-', text)
        return text.strip('-')


def scan_tests_directory(tests_dir: Path) -> List[Dict[str, Any]]:
    """Projmenuje testovací složku a extrahuje všechny testy."""
    test_files = sorted(tests_dir.glob("**/test_*.py"))
    all_tests = []

    for file_path in test_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content, filename=str(file_path))
            extractor = TestCaseExtractor(file_path, content)
            extractor.visit(tree)
            all_tests.extend(extractor.extracted_tests)
        except Exception as e:
            print(f"⚠️ Chyba při analýze {file_path}: {e}", file=sys.stderr)

    # Seřadit testy podle modulu a ID
    def sort_key(t):
        tc_id = t["id"]
        m = RE_CANONICAL_TC.search(tc_id)
        if m:
            return (t["module"], int(m.group("num")), tc_id)
        return (t["module"], 999, tc_id)

    all_tests.sort(key=sort_key)
    return all_tests


def main():
    parser = argparse.ArgumentParser(
        description="Generátor přehledu automatizovaných testů (Test Steps & Checks Overview)"
    )
    parser.add_argument(
        "-o", "--output",
        default="docs/TEST_STEPS_OVERVIEW.md",
        help="Cesta k výstupnímu Markdown souboru (výchozí: docs/TEST_STEPS_OVERVIEW.md)"
    )
    parser.add_argument(
        "-d", "--tests-dir",
        default="tests",
        help="Cesta ke složce s testy (výchozí: tests)"
    )
    parser.add_argument(
        "-m", "--module",
        choices=["auth", "courses", "enrollment", "lecturer", "navigation", "profile", "security"],
        help="Filtrovat pouze určitý modul"
    )
    parser.add_argument(
        "--marker",
        help="Filtrovat pouze testy s daným markerem (např. smoke, regression, xfail)"
    )
    parser.add_argument(
        "--format",
        choices=["both", "summary", "full"],
        default="both",
        help="Formát výstupu: both (tabulka + detaily), summary (jen tabulka), full (jen detaily)"
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Vypsat Markdown přímo do standardního výstupu (stdout)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Ověřit, zda existující výstupní soubor odpovídá aktuálnímu stavu kódu"
    )

    args = parser.parse_args()

    tests_dir = Path(args.tests_dir)
    if not tests_dir.exists():
        print(f"❌ Složka {tests_dir} neexistuje!", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 Prohledávám automatizované testy v `{tests_dir}`...")
    all_tests = scan_tests_directory(tests_dir)

    # Filtrování
    if args.module:
        mod_upper = args.module.upper()
        if mod_upper == "COURSES":
            mod_upper = "CRS"
        all_tests = [t for t in all_tests if t["module"].lower() == args.module.lower() or t["module"].upper() == mod_upper]

    if args.marker:
        marker_target = args.marker.lower()
        if marker_target == "xfail":
            all_tests = [t for t in all_tests if t["xfail_reason"] is not None]
        else:
            all_tests = [t for t in all_tests if marker_target in [m.lower() for m in t["markers"]]]

    print(f"✅ Nalezeno a analyzováno {len(all_tests)} testů.")

    generator = MarkdownOverviewGenerator(all_tests, format_mode=args.format)
    md_content = generator.generate()

    if args.stdout:
        print(md_content)
        return

    output_path = Path(args.output)
    if args.check:
        if not output_path.exists():
            print(f"❌ Výstupní soubor `{output_path}` neexistuje! Spusťte bez --check pro vygenerování.", file=sys.stderr)
            sys.exit(1)
        existing_content = output_path.read_text(encoding="utf-8")
        # Porovnání bez času vygenerování (první 10 řádků)
        norm_existing = "\n".join(existing_content.splitlines()[6:])
        norm_new = "\n".join(md_content.splitlines()[6:])
        if norm_existing == norm_new:
            print(f"✅ Soubor `{output_path}` je 100% aktuální vůči testům.")
            sys.exit(0)
        else:
            print(f"⚠️ Soubor `{output_path}` NENÍ aktuální vůči testům! Aktualizujte jej spuštěním skriptu.", file=sys.stderr)
            sys.exit(2)

    # Uložení do souboru
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(md_content, encoding="utf-8")
    print(f"🎉 Přehled testů byl úspěšně vygenerován do: `{output_path}` ({len(md_content)} bajtů)")


if __name__ == "__main__":
    main()

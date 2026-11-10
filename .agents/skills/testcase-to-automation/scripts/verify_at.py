#!/usr/bin/env python3
"""
verify_at.py – Validační skript Definice hotovo (Definition of Done) pro převod TC na AT.
Používá se v rámci skillu 'testcase-to-automation' (dříve 'tc-to-at').

Skript deterministicky ověřuje 4 pilíře kvality dle zadání:
1. Každý test case má svůj implementovaný test v tests/.
2. Žádná pevná čekání v kódu (žádný time.sleep ani page.wait_for_timeout).
3. Pre-flight & Lint kontrola kvality projde bez chyb (žádné přímé lokátory v testech,
   žádný python assert na UI, povinné pytest markery).
4. Testy projdou 3x po sobě bez pádu (--retries=0, ochrana proti flaky testům).

Návratový kód (Exit Code):
- 0: Všechna kritéria DoD jsou splněna (PASS).
- 1: Nalezeny chyby nebo nestabilita testu (FAIL).
"""

import argparse
import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

# Cesty k projektu
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[4]
TESTS_DIR = PROJECT_ROOT / "tests"
PAGES_DIR = PROJECT_ROOT / "pages"
TEST_CASES_FILE = PROJECT_ROOT / "docs" / "TEST_CASES.md"

RE_CANONICAL_TC = re.compile(r'\bTC-(?P<num>\d{1,2})-(?P<mod>[A-Z]{3,4})\b', re.IGNORECASE)
RE_SIMPLE_TC = re.compile(r'\bTC-?(?P<num>\d{1,2})\b', re.IGNORECASE)

KNOWN_DOMAINS = {"auth", "courses", "enrollment", "lecturer", "profile", "security", "navigation"}
KNOWN_SEVERITIES = {"smoke", "regression"}


def find_pytest_executable() -> List[str]:
    """Najde dostupný spustitelný soubor pytest v projektu (např. ve .venv)."""
    venv_pytest = PROJECT_ROOT / ".venv" / "bin" / "pytest"
    if venv_pytest.exists():
        return [str(venv_pytest)]
    return [sys.executable, "-m", "pytest"]


class TestCodeVisitor(ast.NodeVisitor):
    """AST návštěvník pro statickou analýzu testů, čekání a kvality kódu."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: List[Dict[str, Any]] = []
        self.test_functions: List[Dict[str, Any]] = []
        self.current_class_markers: List[str] = []
        self.in_test_function = False

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_markers = list(self.current_class_markers)
        class_markers = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Attribute):
                class_markers.append(dec.attr)
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                class_markers.append(dec.func.attr)
        self.current_class_markers = class_markers
        self.generic_visit(node)
        self.current_class_markers = prev_markers

    def visit_FunctionDef(self, node: ast.FunctionDef):
        is_test = node.name.startswith("test_")
        if is_test:
            self.in_test_function = True
            doc = ast.get_docstring(node) or ""

            # Hledání ID test casu v docstringu a v názvu
            tc_ids = set()
            for m in RE_CANONICAL_TC.finditer(doc):
                tc_ids.add(f"TC-{int(m.group('num')):02d}-{m.group('mod').upper()}")
            for m in RE_CANONICAL_TC.finditer(node.name):
                tc_ids.add(f"TC-{int(m.group('num')):02d}-{m.group('mod').upper()}")

            # Podpora pro zkrácený formát např. TC01 v názvu
            simple_matches = re.findall(r'test_tc(\d{1,2})_', node.name, re.IGNORECASE)
            for sm in simple_matches:
                tc_ids.add(f"TC-{int(sm):02d}")

            # Extrakce markerů
            marker_names = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Attribute):
                    marker_names.append(dec.attr)
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    marker_names.append(dec.func.attr)

            all_markers = set(marker_names + self.current_class_markers)

            self.test_functions.append({
                "name": node.name,
                "line": node.lineno,
                "doc": doc,
                "tc_ids": tc_ids,
                "markers": all_markers,
            })

            # Kontrola přítomnosti markerů
            has_domain = any(m in KNOWN_DOMAINS for m in all_markers)
            has_severity = any(m in KNOWN_SEVERITIES for m in all_markers)

            if not has_domain:
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_DOMAIN_MARKER",
                    "severity": "CRITICAL",
                    "message": f"Testovací funkce '{node.name}' postrádá doménový marker (např. @pytest.mark.auth).",
                })
            if not has_severity:
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_SEVERITY_MARKER",
                    "severity": "CRITICAL",
                    "message": f"Testovací funkce '{node.name}' postrádá marker závažnosti (@pytest.mark.smoke nebo @pytest.mark.regression).",
                })

            if not doc:
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_DOCSTRING",
                    "severity": "CRITICAL",
                    "message": f"Testovací funkce '{node.name}' nemá docstring s popisem a ID testu.",
                })
            elif not RE_CANONICAL_TC.search(doc) and not RE_SIMPLE_TC.search(doc):
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_TC_ID_IN_DOCSTRING",
                    "severity": "CRITICAL",
                    "message": f"Docstring funkce '{node.name}' neobsahuje ID test casu (např. 'TC-01-AUTH: ...').",
                })

        self.generic_visit(node)
        if is_test:
            self.in_test_function = False

    def visit_Call(self, node: ast.Call):
        # 1. Kontrola zakázaných pevných čekání: time.sleep() / sleep()
        if isinstance(node.func, ast.Attribute) and node.func.attr == "sleep":
            self.violations.append({
                "line": node.lineno,
                "type": "FORBIDDEN_SLEEP",
                "severity": "CRITICAL",
                "message": "Zákaz pevného čekání 'time.sleep()'. Použijte web-first aserce Playwrightu s auto-waitingem.",
            })
        elif isinstance(node.func, ast.Name) and node.func.id == "sleep":
            self.violations.append({
                "line": node.lineno,
                "type": "FORBIDDEN_SLEEP",
                "severity": "CRITICAL",
                "message": "Zákaz pevného čekání 'sleep()'. Použijte web-first aserce Playwrightu s auto-waitingem.",
            })

        # 2. Kontrola zakázaných pevných čekání: page.wait_for_timeout(...)
        elif isinstance(node.func, ast.Attribute) and node.func.attr == "wait_for_timeout":
            self.violations.append({
                "line": node.lineno,
                "type": "FORBIDDEN_WAIT_FOR_TIMEOUT",
                "severity": "CRITICAL",
                "message": "Zákaz pevného čekání 'wait_for_timeout()'. Nahraďte web-first asercemi expect(...).",
            })

        # 3. Kontrola přímých lokátorů v testu (POM-First pravidlo z AGENTS.md)
        elif self.in_test_function and isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            is_on_page = isinstance(node.func.value, ast.Name) and node.func.value.id == "page"
            if is_on_page and attr_name == "locator":
                self.violations.append({
                    "line": node.lineno,
                    "type": "DIRECT_PAGE_LOCATOR",
                    "severity": "CRITICAL",
                    "message": "Zakázáno přímé volání 'page.locator()' v testu. Lokátory patří výhradně do Page Objects v pages/.",
                })
            elif is_on_page and attr_name.startswith("get_by_"):
                self.violations.append({
                    "line": node.lineno,
                    "type": "DIRECT_PAGE_GET_BY",
                    "severity": "CRITICAL",
                    "message": f"Zakázáno přímé volání 'page.{attr_name}()' v testu. Lokátory patří výhradně do Page Objects v pages/.",
                })

        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        # 4. Kontrola Python assert na UI metodách Playwrightu namísto expect()
        is_ui_check = False
        method_name = ""
        if isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Attribute):
            attr = node.test.func.attr
            if attr in (
                "is_visible", "is_enabled", "is_checked", "is_editable", "is_hidden",
                "inner_text", "text_content", "input_value", "get_attribute"
            ):
                is_ui_check = True
                method_name = attr

        if is_ui_check:
            self.violations.append({
                "line": node.lineno,
                "type": "PYTHON_ASSERT_ON_UI",
                "severity": "CRITICAL",
                "message": f"Nativní Python assert na UI metodě (.{method_name}()). Použijte web-first 'expect(loc)...'.",
            })
        self.generic_visit(node)


class AutomatedTestDoDValidator:
    """Hlavní validátor Definice hotovo (DoD) pro převod TC na kód automatizovaného testu."""

    def __init__(self, tc_id: Optional[str] = None, test_file: Optional[str] = None, runs: int = 3, skip_run: bool = False):
        self.tc_id = tc_id.strip() if tc_id else None
        self.test_file = Path(test_file) if test_file else None
        self.runs = runs
        self.skip_run = skip_run

        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.discovered_tests: List[Dict[str, Any]] = []
        self.target_test_file: Optional[Path] = None
        self.target_test_func: Optional[str] = None

    def normalize_tc_id(self, tc_str: str) -> str:
        """Normalizuje ID test casu pro jednotné porovnání (např. 'tc-01-auth' -> 'TC-01-AUTH')."""
        m = RE_CANONICAL_TC.search(tc_str)
        if m:
            return f"TC-{int(m.group('num')):02d}-{m.group('mod').upper()}"
        m_simple = RE_SIMPLE_TC.search(tc_str)
        if m_simple:
            return f"TC-{int(m_simple.group('num')):02d}"
        return tc_str.strip().upper()

    def discover_tests_in_workspace(self):
        """Projde všechny soubory v tests/ a extrahuje testovací funkce a jejich mapování na TC."""
        search_files = [self.test_file] if self.test_file and self.test_file.is_file() else list(TESTS_DIR.glob("**/test_*.py"))

        for file_path in search_files:
            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(file_path))
                visitor = TestCodeVisitor(file_path)
                visitor.visit(tree)

                for tf in visitor.test_functions:
                    tf["file"] = file_path
                    self.discovered_tests.append(tf)

            except SyntaxError as e:
                self.errors.append(f"Chyba syntaxe v souboru {file_path}:{e.lineno} – {e.msg}")
            except Exception as e:
                self.errors.append(f"Chyba při čtení souboru {file_path}: {e}")

    def validate_pillar_1_tc_mapping(self):
        """Pilíř 1: Každý test case má svůj implementovaný test v tests/."""
        if not self.tc_id:
            if not self.test_file:
                self.errors.append("Musíte zadat buď ID test casu (--tc) nebo soubor testu (--file).")
            return

        norm_target_id = self.normalize_tc_id(self.tc_id)
        # Hledáme číslo a modul
        target_num_match = re.search(r'TC-?0*(\d+)', norm_target_id, re.IGNORECASE)
        target_num = int(target_num_match.group(1)) if target_num_match else None

        found_test = None
        for test in self.discovered_tests:
            # Přesná shoda kanonického ID
            for tid in test["tc_ids"]:
                if self.normalize_tc_id(tid) == norm_target_id:
                    found_test = test
                    break
                # Nebo shoda čísla
                t_num_match = re.search(r'TC-?0*(\d+)', tid, re.IGNORECASE)
                if target_num and t_num_match and int(t_num_match.group(1)) == target_num:
                    found_test = test
                    break
            if found_test:
                break

        if not found_test:
            self.errors.append(
                f"[PILÍŘ 1 - Mapování TC] Pro test case '{self.tc_id}' nebyl v tests/ nalezen žádný test "
                f"s odpovídajícím ID v docstringu ani v názvu metody."
            )
        else:
            self.target_test_file = found_test["file"]
            self.target_test_func = found_test["name"]

    def validate_pillar_2_and_3_static_checks(self):
        """Pilíř 2 (Zákaz pevných čekání) a Pilíř 3 (Pre-flight & Lint kvalita)."""
        # Pokud máme cílový soubor, analyzujeme ten, jinak všechny testovací soubory
        files_to_check = [self.target_test_file] if self.target_test_file else (
            [self.test_file] if self.test_file and self.test_file.is_file() else list(TESTS_DIR.glob("**/test_*.py"))
        )

        for file_path in files_to_check:
            if not file_path or not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(file_path))
                visitor = TestCodeVisitor(file_path)
                visitor.visit(tree)

                rel_path = file_path.relative_to(PROJECT_ROOT)

                for violation in visitor.violations:
                    v_type = violation["type"]
                    line = violation["line"]
                    msg = violation["message"]

                    if v_type in ("FORBIDDEN_SLEEP", "FORBIDDEN_WAIT_FOR_TIMEOUT"):
                        self.errors.append(f"[PILÍŘ 2 - Zákaz čekání] [{rel_path}:{line}] {msg}")
                    else:
                        self.errors.append(f"[PILÍŘ 3 - Lint & Quality] [{rel_path}:{line}] {msg}")

            except SyntaxError as e:
                self.errors.append(f"[Syntax Error] [{file_path}:{e.lineno}] {e.msg}")

    def validate_pillar_4_repeat_runs(self) -> bool:
        """Pilíř 4: Testy projdou 3x po sobě bez pádu (--retries=0, ochrana proti flaky testům)."""
        if self.skip_run:
            self.warnings.append("[PILÍŘ 4 - Dynamický běh] Běh testů byl přeskočen parametrem --skip-run.")
            return True

        if self.errors:
            # Pokud už máme statické chyby, nepouštíme dynamický běh
            return False

        pytest_cmd = find_pytest_executable()
        target_args = []

        if self.target_test_file and self.target_test_func:
            rel_file = str(self.target_test_file.relative_to(PROJECT_ROOT))
            target_args = [rel_file, "-k", self.target_test_func]
        elif self.test_file:
            rel_file = str(self.test_file.relative_to(PROJECT_ROOT))
            target_args = [rel_file]
        else:
            self.errors.append("[PILÍŘ 4 - Dynamický běh] Není určen konkrétní test ani soubor pro spuštění.")
            return False

        print("\n" + "=" * 70)
        print(f"🛡️  PILÍŘ 4: OCHRANA PROTI FLAKY TESTŮM ({self.runs}x běh bez pádu, retries=0)")
        print(f"🎯 Cíl: {' '.join(target_args)}")
        print("=" * 70)

        for iteration in range(1, self.runs + 1):
            print(f"\n▶️  Spouštím běh {iteration}/{self.runs}...")
            # Sestavení příkazu (pytest s -v, bez rerunů)
            cmd = pytest_cmd + target_args + ["-v"]

            result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)

            if result.returncode != 0:
                self.errors.append(
                    f"[PILÍŘ 4 - Flaky test] Běh {iteration}/{self.runs} selhal s kódem {result.returncode}!\n"
                    f"Test není stabilní nebo selhává. Výstup chyb:\n"
                    f"{result.stdout[-800:] if result.stdout else ''}\n{result.stderr[-400:] if result.stderr else ''}"
                )
                print(f"❌ Běh {iteration}/{self.runs} SELHAL (FAIL)!")
                return False
            else:
                print(f"✅ Běh {iteration}/{self.runs} PROŠEL ÚSPĚŠNĚ (PASS).")

        return True

    def run_all_checks(self) -> int:
        """Spustí kompletní kontrolu všech 4 pilířů DoD."""
        self.discover_tests_in_workspace()
        self.validate_pillar_1_tc_mapping()
        self.validate_pillar_2_and_3_static_checks()
        self.validate_pillar_4_repeat_runs()

        return self.print_report()

    def print_report(self) -> int:
        print("\n" + "=" * 70)
        print("🔍 VÝSLEDEK DEFINICE HOTOVO (DoD) – TESTCASE-TO-AUTOMATION")
        print("=" * 70)
        if self.tc_id:
            print(f"📋 Test Case ID: {self.tc_id}")
        if self.target_test_file:
            print(f"📄 Nalezený soubor testu: {self.target_test_file.relative_to(PROJECT_ROOT)}")
        if self.target_test_func:
            print(f"🧪 Testovací funkce: {self.target_test_func}")

        print("-" * 70)

        if self.warnings:
            print("⚠️  VAROVÁNÍ:")
            for w in self.warnings:
                print(f"  [!] {w}")
            print("-" * 70)

        if self.errors:
            print("❌ NALEZENÉ CHYBY DEFINICE HOTOVO (DoD):")
            for idx, err in enumerate(self.errors, 1):
                print(f"\n  [{idx}] {err}")
            print("\n" + "=" * 70)
            print("🛑 VÝSLEDEK: FAIL – Úkol NENÍ hotový! Opravte výše uvedené chyby.")
            print("   Agent nesmí ohlásit hotovo ani předat test ke schválení před exit code 0.")
            print("=" * 70)
            return 1
        else:
            print("✅ VŠECHNA 4 KRITÉRIA DEFINICE HOTOVO (DoD) JSOU SPLNĚNA!")
            print("   1. Test case má odpovídající test v tests/ (mapování ověřeno).")
            print("   2. V kódu nejsou žádná pevná čekání (sleep ani wait_for_timeout).")
            print("   3. Pre-flight lint proběhl bez chyb (žádné přímé lokátory v testu, markery v pořádku).")
            print(f"   4. Test prošel {self.runs}x po sobě bez pádu (ochrana proti flaky testům aktivní).")
            print("=" * 70)
            print("🎉 VÝSLEDEK: PASS – Test je plně připraven k lidskému schválení (Krok 5).")
            print("=" * 70)
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="Validační skript Definice hotovo (DoD) pro převod Test Case na kód automatizovaného testu."
    )
    parser.add_argument("--tc", help="Identifikátor test casu (např. 'TC-01-AUTH' nebo 'TC-01').")
    parser.add_argument("--file", help="Cesta k souboru s testem (např. 'tests/auth/test_login.py').")
    parser.add_argument("--runs", type=int, default=3, help="Počet opakovaných běhů pro ověření stability (default: 3).")
    parser.add_argument("--skip-run", action="store_true", help="Přeskočí dynamické spouštění (pouze statická analýza).")

    args = parser.parse_args()

    validator = AutomatedTestDoDValidator(
        tc_id=args.tc,
        test_file=args.file,
        runs=args.runs,
        skip_run=args.skip_run,
    )

    exit_code = validator.run_all_checks()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

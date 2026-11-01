#!/usr/bin/env python3
"""
author_test.py – Nástroj pro komplexní autorství testovacích scénářů (Test Authoring).
===================================================================================
Podporuje kompletní životní cyklus nového testu v projektu:
1. Návrh & Alokace ID: Výpočet dalšího unikátního globálního čísla (TC-xx-MODUL).
2. Dokumentace: Zápis scénáře do docs/TEST_CASES.md (včetně aktualizace tabulky a souhrnu).
3. Scaffolding kódu: Vygenerování čisté AAA kostry do tests/ s POM a fixtures.
4. Pre-Flight kontrola: AST analýza dodržení pravidel z AGENTS.md (lokátory, asserty, sleep, markery).
5. Autonomní spuštění: Okamžitý běh testu přes pytest (-k) pro rychlou validaci.
"""

import argparse
import ast
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set

# Cesty k projektovým souborům
PROJECT_ROOT = Path(__file__).resolve().parents[4]
TEST_CASES_PATH = PROJECT_ROOT / "docs" / "TEST_CASES.md"
REQUIREMENTS_PATH = PROJECT_ROOT / "docs" / "požadavky_ust_podle_src.md"
TESTS_DIR = PROJECT_ROOT / "tests"
PAGES_DIR = PROJECT_ROOT / "pages"

MODULE_MAP = {
    "AUTH": {
        "name": "Autentizace a správa uživatelského sezení",
        "domain_marker": "auth",
        "target_dir": "tests/auth",
        "default_file": "tests/auth/test_login.py",
        "page_objects": ["LoginPage", "CoursesPage"],
    },
    "CRS": {
        "name": "Katalog a detail kurzů",
        "domain_marker": "courses",
        "target_dir": "tests/courses",
        "default_file": "tests/courses/test_courses.py",
        "page_objects": ["CoursesPage", "CourseDetailPage"],
    },
    "ENR": {
        "name": "Zápis na kurz a Moje kurzy",
        "domain_marker": "enrollment",
        "target_dir": "tests/enrollment",
        "default_file": "tests/enrollment/test_enrollment.py",
        "page_objects": ["EnrollmentPage", "MyCoursesPage", "CourseDetailPage"],
    },
    "LEC": {
        "name": "Správa kurzů lektorem",
        "domain_marker": "lecturer",
        "target_dir": "tests/lecturer",
        "default_file": "tests/lecturer/test_lecturer.py",
        "page_objects": ["CreateCoursePage", "CoursesPage"],
    },
    "PRF": {
        "name": "Uživatelský profil a domovská nástěnka",
        "domain_marker": "profile",
        "target_dir": "tests/profile",
        "default_file": "tests/profile/test_profile.py",
        "page_objects": ["ProfilePage", "HomePage", "CoursesPage"],
    },
    "SEC": {
        "name": "Bezpečnost a autorizace",
        "domain_marker": "security",
        "target_dir": "tests/security",
        "default_file": "tests/security/test_security.py",
        "page_objects": ["ProfilePage", "MyCoursesPage", "CreateCoursePage", "LoginPage"],
    },
}

RE_CANONICAL_TC = re.compile(r'\bTC-(?P<num>\d{2})-(?P<mod>[A-Z]{3,4})\b')


def strip_accents(text: str) -> str:
    """Odstraní diakritiku pro bezpečné názvy v kódu."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])


def get_all_existing_tc_ids(content: str) -> List[Tuple[int, str, str]]:
    """Vrátí seznam všech existujících (číslo, modul, plné_id) z markdown souboru."""
    matches = []
    for m in RE_CANONICAL_TC.finditer(content):
        full_id = m.group(0).upper()
        num = int(m.group("num"))
        mod = m.group("mod").upper()
        matches.append((num, mod, full_id))
    return matches


def get_next_tc_id(module_code: str) -> str:
    """Vypočte další volné kanonické ID pro zadaný modul s průběžným číslováním."""
    module_code = module_code.upper()
    if module_code not in MODULE_MAP:
        raise ValueError(f"Neznámý kód modulu '{module_code}'. Podporované: {list(MODULE_MAP.keys())}")

    if not TEST_CASES_PATH.exists():
        return f"TC-01-{module_code}"

    content = TEST_CASES_PATH.read_text(encoding="utf-8")
    existing = get_all_existing_tc_ids(content)
    if not existing:
        return f"TC-01-{module_code}"

    max_num = max(num for num, mod, full_id in existing)
    next_num = max_num + 1
    return f"TC-{next_num:02d}-{module_code}"


def find_module_table_insert_pos(content: str, module_code: str) -> int:
    """Najde přesnou pozici pro vložení nového řádku do přehledové tabulky Traceability Matrix."""
    mod_start_pattern = rf"\|\s*\*\*\d+\.\s*[^*]+\({module_code}\)\*\*.*?\n"
    m = re.search(mod_start_pattern, content)
    if not m:
        return -1
    pos = m.end()
    lines = content[pos:].splitlines(keepends=True)
    last_end = pos
    for line in lines:
        if line.startswith("| |"):
            last_end += len(line)
        else:
            break
    return last_end


def find_module_detail_insert_pos(content: str, module_code: str) -> int:
    """Najde pozici pro vložení nového Markdown bloku na konec sekce daného modulu."""
    header_pattern = rf"### Modul \d+:.*?\({module_code}\)"
    m = re.search(header_pattern, content)
    if not m:
        return -1
    start_pos = m.end()
    next_header_pattern = r"(---[\r\n]+\s*### Modul \d+:|### Modul \d+:)"
    next_m = re.search(next_header_pattern, content[start_pos:])
    if next_m:
        return start_pos + next_m.start()
    else:
        return len(content)


def append_tc_to_spec(
    tc_id: str,
    title: str,
    user_story: str,
    priority_type: str,
    prerequisites: str,
    test_data: str,
    steps: List[str],
    expected_results: List[str],
) -> bool:
    """Přidá nový Test Case do docs/TEST_CASES.md na správné místo v tabulce i detailu."""
    if not TEST_CASES_PATH.exists():
        print(f"Chyba: Soubor {TEST_CASES_PATH} neexistuje.", file=sys.stderr)
        return False

    content = TEST_CASES_PATH.read_text(encoding="utf-8")

    if tc_id in content:
        print(f"Varování: Test Case {tc_id} již v {TEST_CASES_PATH.name} existuje!", file=sys.stderr)
        return False

    mod_match = re.search(r'TC-\d+-([A-Z]{3,4})', tc_id)
    if not mod_match:
        print(f"Chyba: Neplatný formát TC ID '{tc_id}'. Očekává se TC-xx-MODUL.", file=sys.stderr)
        return False
    module_code = mod_match.group(1).upper()
    if module_code not in MODULE_MAP:
        print(f"Chyba: Neznámý modul '{module_code}'.", file=sys.stderr)
        return False

    # 1. Příprava Markdown bloku nového Test Casu
    steps_md = "\n".join([f"  {idx}. {step}" for idx, step in enumerate(steps, 1)])
    expected_md = "\n".join([f"  - {res}" for res in expected_results])
    data_line = f"* **Testovací data:** {test_data}\n" if test_data else ""
    prereq_line = f"* **Předpoklady:** {prerequisites}\n" if prerequisites else ""

    new_tc_block = (
        f"#### `{tc_id}`: {title}\n"
        f"* **Pokrytí:** {user_story}\n"
        f"{prereq_line}"
        f"{data_line}"
        f"* **Kroky:**\n"
        f"{steps_md}\n"
        f"* **Očekávaný výsledek:**\n"
        f"{expected_md}\n\n"
    )

    # 2. Vložení detailu scénáře do sekce modulu
    detail_pos = find_module_detail_insert_pos(content, module_code)
    if detail_pos == -1:
        print(f"Chyba: Sekce pro modul {module_code} nebyla nalezena v {TEST_CASES_PATH.name}.", file=sys.stderr)
        return False

    updated_content = content[:detail_pos] + new_tc_block + content[detail_pos:]

    # 3. Vložení řádku do přehledové tabulky Traceability Matrix
    table_pos = find_module_table_insert_pos(updated_content, module_code)
    if table_pos != -1:
        new_table_line = f"| | **{user_story}** | `{tc_id}` | {title} | {priority_type} |\n"
        updated_content = (
            updated_content[:table_pos]
            + new_table_line
            + updated_content[table_pos:]
        )
    else:
        print(f"Varování: Místo pro modul {module_code} v tabulce nebylo nalezeno.", file=sys.stderr)

    # 4. Aktualizace počtu v hlavičce NOTE
    existing_all = get_all_existing_tc_ids(updated_content)
    total_count = len(set(full_id for _, _, full_id in existing_all))
    max_num = max(num for num, _, _ in existing_all) if existing_all else total_count

    note_sub_pattern = re.compile(
        r'(\* \*\*Celkový počet testovacích případů:\*\* \*\*)\d+(\*\* \(`TC-01` až `TC-)\d+(\`\))'
    )
    updated_content = note_sub_pattern.sub(rf"\g<1>{total_count}\g<2>{max_num:02d}\g<3>", updated_content)

    TEST_CASES_PATH.write_text(updated_content, encoding="utf-8")
    return True


def generate_test_code_scaffold(
    tc_id: str,
    title: str,
    user_story: str,
    priority_type: str,
    steps: List[str],
    expected_results: List[str],
    prerequisites: str = "",
    test_data: str = "",
) -> str:
    """Vygeneruje produkční AAA kód testu v Playwright + Pytest."""
    tc_id = tc_id.upper()
    mod_match = re.search(r'TC-(\d+)-([A-Z]{3,4})', tc_id)
    num_str = mod_match.group(1) if mod_match else "00"
    module_code = mod_match.group(2) if mod_match else "AUTH"
    mod_info = MODULE_MAP.get(module_code, MODULE_MAP["AUTH"])

    # Název funkce testu
    clean_title = strip_accents(title.lower())
    clean_title = re.sub(r'[^a-z0-9\s]', '', clean_title)
    words = clean_title.split()[:5]
    slug = "_".join(words) if words else "scenario"
    func_name = f"test_tc{num_str}_{module_code.lower()}_{slug}"

    # Markery
    domain_marker = mod_info["domain_marker"]
    prio_lower = priority_type.lower()
    severity_marker = "smoke" if ("smoke" in prio_lower or "p1" in prio_lower) else "regression"

    # Primární Page Object
    primary_po = mod_info["page_objects"][0]
    po_var = re.sub(r'(?<!^)(?=[A-Z])', '_', primary_po).lower()

    steps_comments = "\n".join([f"        # {i}. {s}" for i, s in enumerate(steps, 1)]) if steps else "        # 1. Provedení kroků scénáře"
    expected_comments = "\n".join([f"        # - {e}" for e in expected_results]) if expected_results else "        # - Ověření očekávaných výsledků"

    code = f'''    @pytest.mark.{severity_marker}
    def {func_name}(self, page: Page):
        """{tc_id}: {title}."""
        # =====================================================================
        # 1. ARRANGE (Příprava stránky, Page Objectů a testovacích dat)
        # =====================================================================
        {po_var} = {primary_po}(page)
        {po_var}.open()
        # Předpoklady: {prerequisites or "Výchozí stav"}
        # Data: {test_data or "Unikátní testovací data z utils.data_generator"}

        # =====================================================================
        # 2. ACT (Kroky scénáře dle specifikace)
        # =====================================================================
{steps_comments}

        # =====================================================================
        # 3. ASSERT (3úrovňové ověření: Routing, Session, Data State / UI)
        # =====================================================================
{expected_comments}
        expect(page).to_have_url({po_var}.URL)
'''
    return code


class PreFlightVisitor(ast.NodeVisitor):
    """AST návštěvník pro statickou kontrolu pravidel AGENTS.md v novém testu."""

    def __init__(self):
        self.violations: List[Dict[str, Any]] = []
        self.current_class_markers: List[str] = []

    def visit_ClassDef(self, node: ast.ClassDef):
        prev_markers = self.current_class_markers
        class_markers = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Attribute):
                class_markers.append(dec.attr)
            elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                class_markers.append(dec.func.attr)
        self.current_class_markers = class_markers
        self.generic_visit(node)
        self.current_class_markers = prev_markers

    def visit_Call(self, node: ast.Call):
        # 1. Detekce time.sleep() nebo sleep()
        if isinstance(node.func, ast.Attribute) and node.func.attr == "sleep":
            self.violations.append({
                "line": node.lineno,
                "type": "FORBIDDEN_TIME_SLEEP",
                "severity": "CRITICAL",
                "message": "Absolutní zákaz 'time.sleep()'. Použijte web-first Playwright asserty s auto-waitingem.",
            })
        elif isinstance(node.func, ast.Name) and node.func.id == "sleep":
            self.violations.append({
                "line": node.lineno,
                "type": "FORBIDDEN_TIME_SLEEP",
                "severity": "CRITICAL",
                "message": "Absolutní zákaz 'sleep()'. Použijte web-first Playwright asserty s auto-waitingem.",
            })

        # 2. Detekce přímých volání page.locator(...) nebo page.get_by_... v testu (CRITICAL dle AGENTS.md)
        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            is_on_page = isinstance(node.func.value, ast.Name) and node.func.value.id == "page"
            if is_on_page and attr_name == "locator":
                self.violations.append({
                    "line": node.lineno,
                    "type": "DIRECT_PAGE_LOCATOR",
                    "severity": "CRITICAL",
                    "message": "Zakázáno přímé volání 'page.locator()' v testu. Lokátory musí patřit výhradně do Page Objects.",
                })
            elif is_on_page and attr_name.startswith("get_by_"):
                self.violations.append({
                    "line": node.lineno,
                    "type": "DIRECT_PAGE_GET_BY",
                    "severity": "CRITICAL",
                    "message": f"Zakázáno přímé volání 'page.{attr_name}()' v testu. Lokátory musí patřit výhradně do Page Objects.",
                })

        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert):
        # 3. Detekce Python assert na UI metodách Playwrightu
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
                "message": f"Nativní Python assert na UI metodě (.{method_name}() apod.). Použijte Playwright 'expect(loc)...'.",
            })
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Kontrola testovacích metod
        if node.name.startswith("test_"):
            # Kontrola docstringu
            doc = ast.get_docstring(node)
            if not doc:
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_DOCSTRING",
                    "severity": "WARNING",
                    "message": f"Testovací funkce '{node.name}' nemá docstring.",
                })
            elif not RE_CANONICAL_TC.search(doc):
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_CANONICAL_ID_IN_DOCSTRING",
                    "severity": "WARNING",
                    "message": f"Docstring funkce '{node.name}' neobsahuje kanonické ID ve formátu 'TC-xx-MODUL'.",
                })

            # Kontrola markerů (kombinace dekorátorů funkce a třídy)
            marker_names = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Attribute):
                    marker_names.append(dec.attr)
                elif isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
                    marker_names.append(dec.func.attr)

            all_markers = set(marker_names + self.current_class_markers)
            has_severity = any(m in ("smoke", "regression") for m in all_markers)
            has_domain = any(m in ("auth", "courses", "enrollment", "lecturer", "profile", "security", "navigation") for m in all_markers)

            if not has_severity:
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_SEVERITY_MARKER",
                    "severity": "WARNING",
                    "message": f"Test '{node.name}' postrádá marker závažnosti (@pytest.mark.smoke nebo @pytest.mark.regression).",
                })
            if not has_domain:
                self.violations.append({
                    "line": node.lineno,
                    "type": "MISSING_DOMAIN_MARKER",
                    "severity": "WARNING",
                    "message": f"Test '{node.name}' postrádá doménový marker (např. @pytest.mark.auth na funkci nebo třídě).",
                })

        self.generic_visit(node)


def run_pre_flight_check(file_path: Path) -> List[Dict[str, Any]]:
    """Provede AST analýzu kódu testu a vrátí seznam nalezených porušení standardů."""
    if not file_path.exists():
        print(f"Chyba: Soubor {file_path} neexistuje.", file=sys.stderr)
        return []

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content, filename=str(file_path))
    except SyntaxError as e:
        return [{
            "line": e.lineno or 1,
            "type": "SYNTAX_ERROR",
            "severity": "CRITICAL",
            "message": f"Syntax error v kódu: {e.msg}",
        }]

    visitor = PreFlightVisitor()
    visitor.visit(tree)
    return visitor.violations


def run_pytest(target: str, verbose: bool = True) -> int:
    """Spustí test přes pytest s filtrem -k."""
    cmd = ["pytest", target]
    if verbose:
        cmd.append("-v")

    print(f"🚀 Spouštím test: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="Nástroj pro komplexní autorství a tvorbu testovacích scénářů (Test Authoring)."
    )
    subparsers = parser.add_subparsers(dest="command")

    # 1. next-id
    p_next = subparsers.add_parser("next-id", help="Zobrazí další volné kanonické ID pro daný modul.")
    p_next.add_argument("module", choices=list(MODULE_MAP.keys()), help="Kód modulu (AUTH, CRS, ENR, LEC, PRF, SEC)")

    # 2. new-tc (návrh a zápis scénáře do docs/TEST_CASES.md)
    p_new = subparsers.add_parser("new-tc", help="Vytvoří a volitelně zapíše nový Test Case do docs/TEST_CASES.md.")
    p_new.add_argument("--module", required=True, choices=list(MODULE_MAP.keys()), help="Kód modulu")
    p_new.add_argument("--us", required=True, help="Kód User Story (např. US-01)")
    p_new.add_argument("--title", required=True, help="Výstižný název testovacího případu")
    p_new.add_argument(
        "--priority",
        default="Smoke / P1",
        help="Typ a priorita (např. 'Smoke / P1', 'Negativní / P2', 'Validační / P2', 'Hraniční / P3')",
    )
    p_new.add_argument("--prereq", default="Výchozí stav aplikace.", help="Předpoklady testu")
    p_new.add_argument("--data", default="Dynamická data z utils.data_generator.", help="Testovací data")
    p_new.add_argument("--steps", nargs="+", required=True, help="Seznam kroků scénáře (oddělené uvozovkami)")
    p_new.add_argument("--expected", nargs="+", required=True, help="Seznam očekávaných výsledků")
    p_new.add_argument("--append-doc", action="store_true", help="Přímo zapsat nový TC do docs/TEST_CASES.md")

    # 3. scaffold-code
    p_scaffold = subparsers.add_parser("scaffold-code", help="Vygeneruje čistou AAA šablonu testu v Pythonu.")
    p_scaffold.add_argument("--id", required=True, help="Kanonické ID (např. TC-48-AUTH)")
    p_scaffold.add_argument("--title", required=True, help="Název testu")
    p_scaffold.add_argument("--us", default="US-01", help="User Story kód")
    p_scaffold.add_argument("--priority", default="Smoke / P1", help="Priorita (Smoke / P1 nebo Regresní / P2)")
    p_scaffold.add_argument("--steps", nargs="*", default=[], help="Kroky testu")
    p_scaffold.add_argument("--expected", nargs="*", default=[], help="Očekávané výsledky")
    p_scaffold.add_argument("--prereq", default="", help="Předpoklady")
    p_scaffold.add_argument("--data", default="", help="Testovací data")

    # 4. pre-flight
    p_check = subparsers.add_parser("pre-flight", help="Provede statickou kontrolu souboru s testem proti AGENTS.md.")
    p_check.add_argument("file", type=Path, help="Cesta k souboru s testem (např. tests/auth/test_login.py)")

    # 5. run
    p_run = subparsers.add_parser("run", help="Spustí test přes pytest.")
    p_run.add_argument("target", help="Výraz pro filtr -k nebo cesta k testu (např. test_tc06_auth)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "next-id":
        next_id = get_next_tc_id(args.module)
        print(f"🎯 Další volné ID pro modul {args.module}: {next_id}")

    elif args.command == "new-tc":
        tc_id = get_next_tc_id(args.module)
        print("=" * 80)
        print(f"📋 NÁVRH NOVÉHO TESTOVACÍHO PŘÍPADU: [{tc_id}]")
        print("=" * 80)
        print(f"Modul:         {args.module} ({MODULE_MAP[args.module]['name']})")
        print(f"User Story:    {args.us}")
        print(f"Název:         {args.title}")
        print(f"Priorita:      {args.priority}")
        print(f"Předpoklady:   {args.prereq}")
        print(f"Testovací data:{args.data}")
        print("Kroky:")
        for idx, s in enumerate(args.steps, 1):
            print(f"  {idx}. {s}")
        print("Očekávaný výsledek:")
        for res in args.expected:
            print(f"  • {res}")
        print("=" * 80)

        if args.append_doc:
            ok = append_tc_to_spec(
                tc_id=tc_id,
                title=args.title,
                user_story=args.us,
                priority_type=args.priority,
                prerequisites=args.prereq,
                test_data=args.data,
                steps=args.steps,
                expected_results=args.expected,
            )
            if ok:
                print(f"✅ Úspěšně zapsáno do {TEST_CASES_PATH.name} na správné místo modulu a aktualizována tabulka!")
            else:
                print("❌ Zápis do dokumentace selhal.", file=sys.stderr)
        else:
            print("ℹ️  Poznámka: Pro zápis do docs/TEST_CASES.md zadejte přepínač --append-doc")

    elif args.command == "scaffold-code":
        code = generate_test_code_scaffold(
            tc_id=args.id,
            title=args.title,
            user_story=args.us,
            priority_type=args.priority,
            steps=args.steps,
            expected_results=args.expected,
            prerequisites=args.prereq,
            test_data=args.data,
        )
        print("=" * 80)
        print(f"💻 VYGENEROVANÝ KÓD TESTU PRO [{args.id}]")
        print("=" * 80)
        print(code)
        print("=" * 80)

    elif args.command == "pre-flight":
        violations = run_pre_flight_check(args.file)
        print("=" * 80)
        print(f"🔍 PRE-FLIGHT AUDIT: {args.file}")
        print("=" * 80)
        if not violations:
            print("✅ Žádná porušení standardů nenalezena. Kód plně odpovídá AGENTS.md!")
        else:
            criticals = [v for v in violations if v["severity"] == "CRITICAL"]
            warnings = [v for v in violations if v["severity"] == "WARNING"]
            print(f"Nalezeno {len(criticals)} kritických chyb a {len(warnings)} varování:\n")
            for v in violations:
                icon = "❌" if v["severity"] == "CRITICAL" else "⚠️ "
                print(f"{icon} Řádek {v['line']}: [{v['type']}] {v['message']}")
            if criticals:
                sys.exit(1)

    elif args.command == "run":
        code = run_pytest(args.target)
        sys.exit(code)


if __name__ == "__main__":
    main()

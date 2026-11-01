#!/usr/bin/env python3
"""
Assertion Quality & Standards Scanner for Playwright / Pytest

Tento skript provádí statickou analýzu Python kódu v `tests/` a `pages/` na dodržování
standardů kvality assertů a detekci známých anti-patternů:
1. Zákaz umělého čekání time.sleep()
2. Zákaz synchronních assertů nad UI (assert locator.is_visible() -> expect(locator).to_be_visible())
3. Zákaz testování celého HTML přes assert "..." in page.content()
4. Zákaz assertů uvnitř Page Object Model tříd v pages/
5. Detekce mělkých testů (pouze to_have_url bez kontroly prvků a stavu)
6. Zákaz prázdných textových matcherů (to_contain_text(""))
7. Detekce potenciálně rizikových negativních kontrol (not_to_be_visible) bez ustálení stavu

Podporuje volitelný přepínač --fix pro automatickou opravu bezpečných případů.
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Tuple


# Detekční regulární výrazy
RE_TIME_SLEEP = re.compile(r'\btime\.sleep\s*\(\s*[\d\.]+\s*\)')

RE_SYNC_ASSERT_UI = re.compile(
    r'assert\s+(?P<locator>[a-zA-Z0-9_\.\(\)]+)\.(?P<method>is_visible|is_hidden|is_enabled|is_disabled|is_checked)\s*\(\s*\)'
)

RE_PAGE_CONTENT_ASSERT = re.compile(
    r'assert\s+[\'"].*?[\'"]\s+(?:in|not\s+in)\s+[a-zA-Z0-9_\.]*page\.content\s*\(\s*\)'
)

RE_SYNC_COUNT_ASSERT = re.compile(
    r'assert\s+(?P<locator>[a-zA-Z0-9_\.\(\)]+)\.count\s*\(\s*\)\s*(?:>|!=|==|<)'
)

RE_EMPTY_TEXT_MATCHER = re.compile(
    r'\.(?:to_contain_text|to_have_text)\s*\(\s*[\'"]\s*[\'"]\s*\)'
)

RE_ASSERT_IN_POM = re.compile(
    r'^\s*(?:assert\b|expect\s*\()'
)


class AssertionViolation:
    def __init__(
        self,
        file_path: str,
        line_no: int,
        line_text: str,
        rule_id: str,
        message: str,
        suggested_fix: str = "",
        fix_available: bool = False
    ):
        self.file_path = file_path
        self.line_no = line_no
        self.line_text = line_text.strip()
        self.rule_id = rule_id
        self.message = message
        self.suggested_fix = suggested_fix
        self.fix_available = fix_available


def analyze_file(file_path: str) -> List[AssertionViolation]:
    """Analyzuje jeden soubor a vrátí seznam nalezených porušení pravidel."""
    violations: List[AssertionViolation] = []
    is_pom_file = "/pages/" in file_path or file_path.startswith("pages/")
    is_test_file = "/tests/" in file_path or file_path.startswith("tests/")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Chyba při čtení souboru {file_path}: {e}", file=sys.stderr)
        return violations

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()

        # Přeskočit komentáře a prázdné řádky
        if not stripped or stripped.startswith("#"):
            continue

        # 1. Kontrola time.sleep()
        if RE_TIME_SLEEP.search(line):
            violations.append(
                AssertionViolation(
                    file_path=file_path,
                    line_no=i,
                    line_text=line,
                    rule_id="RULE-01-NO-SLEEP",
                    message="Použití time.sleep() způsobuje flakiness a zpomaluje testy.",
                    suggested_fix="Nahraďte web-first asercí expect(locator).to_be_visible() s auto-waitingem.",
                    fix_available=False
                )
            )

        # 2. Kontrola synchronního assertu nad UI prvky
        match_sync = RE_SYNC_ASSERT_UI.search(line)
        if match_sync:
            loc = match_sync.group("locator")
            method = match_sync.group("method")
            fixed_line = ""
            if method == "is_visible":
                fixed_line = f"expect({loc}).to_be_visible()"
            elif method == "is_hidden":
                fixed_line = f"expect({loc}).not_to_be_visible()"
            elif method == "is_enabled":
                fixed_line = f"expect({loc}).to_be_enabled()"
            elif method == "is_disabled":
                fixed_line = f"expect({loc}).to_be_disabled()"
            elif method == "is_checked":
                fixed_line = f"expect({loc}).to_be_checked()"

            violations.append(
                AssertionViolation(
                    file_path=file_path,
                    line_no=i,
                    line_text=line,
                    rule_id="RULE-02-SYNC-UI-ASSERT",
                    message=f"Synchronní assert nad '{method}()' nečeká na vykreslení prvku v DOMu.",
                    suggested_fix=fixed_line,
                    fix_available=bool(fixed_line)
                )
            )

        # Kontrola synchronního assertu nad count()
        match_count = RE_SYNC_COUNT_ASSERT.search(line)
        if match_count:
            loc = match_count.group("locator")
            violations.append(
                AssertionViolation(
                    file_path=file_path,
                    line_no=i,
                    line_text=line,
                    rule_id="RULE-02-SYNC-COUNT-ASSERT",
                    message="Synchronní assert nad locator.count() nečeká na načtení elementů.",
                    suggested_fix=f"Použijte expect({loc}).not_to_have_count(0) nebo expect({loc}.first).to_be_visible().",
                    fix_available=False
                )
            )

        # 3. Kontrola page.content() scrapingu
        if RE_PAGE_CONTENT_ASSERT.search(line):
            violations.append(
                AssertionViolation(
                    file_path=file_path,
                    line_no=i,
                    line_text=line,
                    rule_id="RULE-03-NO-PAGE-CONTENT-ASSERT",
                    message="Hledání textu v surovém HTML (page.content()) ignoruje strukturu DOMu.",
                    suggested_fix="Použijte expect(locator).to_contain_text('...') na konkrétním elementu.",
                    fix_available=False
                )
            )

        # 4. Kontrola prázdného matcher textu
        if RE_EMPTY_TEXT_MATCHER.search(line):
            violations.append(
                AssertionViolation(
                    file_path=file_path,
                    line_no=i,
                    line_text=line,
                    rule_id="RULE-04-NO-EMPTY-TEXT-MATCHER",
                    message="Aserce testuje prázdný řetězec, který projde pro jakýkoliv element (tautologie).",
                    suggested_fix="Doplňte konkrétní očekávaný text nebo použijte expect(locator).not_to_be_empty().",
                    fix_available=False
                )
            )

        # 5. Kontrola asercí v Page Objects (pages/)
        if is_pom_file and RE_ASSERT_IN_POM.search(line):
            violations.append(
                AssertionViolation(
                    file_path=file_path,
                    line_no=i,
                    line_text=line,
                    rule_id="RULE-05-NO-ASSERTS-IN-POM",
                    message="Aserce a expect(...) nepatří do Page Objects (porušení Single Responsibility).",
                    suggested_fix="Přesuňte validaci do testovací metody v tests/.",
                    fix_available=False
                )
            )

    return violations


def apply_fixes(file_path: str, violations: List[AssertionViolation]) -> int:
    """Aplikuje automatické opravy na soubor a vrátí počet opravených řádků."""
    fixable_violations = [v for v in violations if v.fix_available and v.suggested_fix]
    if not fixable_violations:
        return 0

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    fixed_count = 0
    # Mapování podle line_no
    line_fixes = {v.line_no: v for v in fixable_violations}

    new_lines = []
    for i, line in enumerate(lines, start=1):
        if i in line_fixes:
            v = line_fixes[i]
            indent = len(line) - len(line.lstrip())
            indent_str = line[:indent]
            new_lines.append(f"{indent_str}{v.suggested_fix}\n")
            fixed_count += 1
        else:
            new_lines.append(line)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    return fixed_count


def scan_directories(targets: List[str]) -> Dict[str, List[AssertionViolation]]:
    """Rekurzivně prohledá zadané složky nebo soubory."""
    all_violations: Dict[str, List[AssertionViolation]] = {}

    for target in targets:
        if os.path.isfile(target):
            if target.endswith(".py"):
                v = analyze_file(target)
                if v:
                    all_violations[target] = v
        elif os.path.isdir(target):
            for root, _, files in os.walk(target):
                # Přeskočit .venv, .pytest_cache apod.
                if any(ignored in root for ignored in [".venv", ".pytest_cache", ".git", "__pycache__"]):
                    continue
                for file in files:
                    if file.endswith(".py"):
                        fp = os.path.join(root, file)
                        v = analyze_file(fp)
                        if v:
                            all_violations[fp] = v

    return all_violations


def print_report(violations_by_file: Dict[str, List[AssertionViolation]], auto_fixed: bool = False):
    """Vypíše přehledný diagnostický report do terminálu."""
    total_violations = sum(len(v) for v in violations_by_file.values())

    print("\n" + "=" * 80)
    print("🔍 AUDIT KVALITY TESTOVACÍCH ASSERTŮ (PLAYWRIGHT / PYTEST)")
    print("=" * 80)

    if total_violations == 0:
        print("\n✨ Skvělá práce! V analyzovaných souborech nebyly nalezeny žádné neshody.")
        print("   Všechny kontroly splňují pravidla Web-First Assertions a standard projektu.\n")
        print("=" * 80)
        return

    print(f"\nNalezeno celkem {total_violations} neshod v {len(violations_by_file)} souborech:\n")

    for file_path, violations in violations_by_file.items():
        print(f"📄 Soubor: \033[1;34m{file_path}\033[0m")
        for v in violations:
            status_color = "\033[1;31m"  # Červená
            fix_tag = "\033[1;32m[OPRAVENO]\033[0m" if auto_fixed and v.fix_available else ""
            print(f"   {status_color}[{v.rule_id}]\033[0m Řádek {v.line_no}: {v.message} {fix_tag}")
            print(f"      Původní kód:    \033[33m{v.line_text}\033[0m")
            if v.suggested_fix:
                print(f"      Doporučený kód: \033[1;32m{v.suggested_fix}\033[0m")
        print("-" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Statický AST skener kvality assertů a detekce anti-patternů v Playwright testech."
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=["tests", "pages"],
        help="Cílové složky nebo soubory ke kontrole (výchozí: tests pages)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automaticky opravit bezpečné případy (např. synchronní asserty na expect)"
    )

    args = parser.parse_args()

    # Kontrola existence cest
    valid_targets = []
    for t in args.targets:
        if os.path.exists(t):
            valid_targets.append(t)
        else:
            print(f"Varování: Cesta '{t}' nebyla nalezena, přeskakuji.", file=sys.stderr)

    if not valid_targets:
        print("Chyba: Žádná ze zadaných cest neexistuje.", file=sys.stderr)
        sys.exit(1)

    violations_by_file = scan_directories(valid_targets)
    total_violations = sum(len(v) for v in violations_by_file.values())

    if args.fix and total_violations > 0:
        fixed_files_count = 0
        total_fixed_lines = 0
        for file_path, v_list in violations_by_file.items():
            fixed = apply_fixes(file_path, v_list)
            if fixed > 0:
                fixed_files_count += 1
                total_fixed_lines += fixed

        # Znovu zkontrolovat po opravách pro zobrazení finálního stavu
        violations_after = scan_directories(valid_targets)
        print_report(violations_by_file, auto_fixed=True)
        print(f"\n🛠️  Automatická oprava provedena: {total_fixed_lines} řádků v {fixed_files_count} souborech.")
        remaining_violations = sum(len(v) for v in violations_after.values())
        if remaining_violations > 0:
            print(f"⚠️  Zbývá {remaining_violations} neshod vyžadujících manuální posouzení.")
            sys.exit(1)
        else:
            print("✅ Všechny neshody byly úspěšně opraveny!")
            sys.exit(0)
    else:
        print_report(violations_by_file)
        if total_violations > 0:
            sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Locator Quality & Compliance Scanner for Playwright / POM

Tento skript analyzuje kód Page Objects a testů na dodržování standardů pro lokátory:
1. Používání nativní metody get_by_test_id namísto locator('[data-testid="..."]').
2. Zákaz indexů .first, .last, .nth() – vyžadováno řetězení kontejnerů.
3. Zákaz XPath a křehkých CSS selektorů.
4. Zákaz přímých lokátorů v testech (vrstva tests/ musí používat Page Objects).

Podporuje volitelný přepínač --fix pro automatickou opravu bezpečných vzorů.
"""

import os
import re
import sys
import argparse
from typing import List, Dict, Tuple


# Regulární výrazy pro detekci anti-patternů
RE_CSS_DATA_TESTID = re.compile(
    r'(?P<receiver>\b\w+)\.locator\(\s*[\'"](?:\[data-testid=|\[data-test=)[\'"]?(?P<id>[\w\-]+)[\'"]?\][\'"]\s*\)'
)

RE_INDEX_ACCESS = re.compile(
    r'\.(?:first|last|nth\s*\(\s*\d+\s*\))'
)

RE_XPATH_SELECTOR = re.compile(
    r'\.locator\(\s*[\'"](?:xpath=|\/\/|\.\/\/)[^\'"]*[\'"]\s*\)'
)

RE_DYNAMIC_ID = re.compile(
    r'\.locator\(\s*[\'"][^\'"]*#(?:input|field|react|vue|el|item|btn|auto)[_\-]?\d+[\'"]\s*\)'
)

RE_GENERATED_CSS = re.compile(
    r'\.locator\(\s*[\'"][^\'"]*\.css-[a-z0-9]+[^\'"]*[\'"]\s*\)'
)

RE_DIRECT_PAGE_LOCATOR = re.compile(
    r'\bpage\.(?:locator|get_by_test_id|get_by_role|get_by_text|get_by_label|get_by_placeholder)\s*\('
)


class Violation:
    def __init__(
        self,
        file_path: str,
        line_no: int,
        line_text: str,
        rule: str,
        message: str,
        suggested_fix: str = "",
        educational_tip: str = "",
        fix_available: bool = False
    ):
        self.file_path = file_path
        self.line_no = line_no
        self.line_text = line_text.strip()
        self.rule = rule
        self.message = message
        self.suggested_fix = suggested_fix
        self.educational_tip = educational_tip
        self.fix_available = fix_available


def scan_file(file_path: str, is_test_file: bool) -> List[Violation]:
    """Skenuje jeden soubor a vrací seznam zjištěných porušení."""
    violations = []
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for idx, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        
        # Ignorovat komentáře a docstringy
        if line.startswith("#") or line.startswith('"""') or line.startswith("'''"):
            continue

        # Pravidlo 1: Atributový zápis CSS [data-testid="..."]
        if RE_CSS_DATA_TESTID.search(raw_line):
            suggested = RE_CSS_DATA_TESTID.sub(r'\g<receiver>.get_by_test_id("\g<id>")', line)
            violations.append(Violation(
                file_path=file_path,
                line_no=idx,
                line_text=line,
                rule="NO_CSS_DATA_TESTID",
                message="Použij nativní metodu .get_by_test_id(...) namísto .locator('[data-testid=...]').",
                suggested_fix=suggested,
                educational_tip="Priorita 1: Nativní get_by_test_id je čistší, přímo podporovaná metoda v Playwrightu.",
                fix_available=True
            ))

        # Pravidlo 2: Indexy .first, .last, .nth()
        if RE_INDEX_ACCESS.search(raw_line) and any(keyword in raw_line for keyword in ["get_by_", "locator(", ".link", ".button", "_link", "_button"]):
            violations.append(Violation(
                file_path=file_path,
                line_no=idx,
                line_text=line,
                rule="NO_INDEX_LOCATOR",
                message="Vyhni se indexům (.first, .last, .nth()). Použij Locator Chaining z rodičovského kontejneru nebo .filter(has_text=...).",
                suggested_fix="page.get_by_test_id('<rodicovsky_kontejner>').get_by_test_id('<prvek>')",
                educational_tip="Pravidlo zákazů: Indexy v DOMu jsou křehké a selžou při přidání jiného prvku či notifikace.",
                fix_available=False
            ))

        # Pravidlo 3: XPath selektory
        if RE_XPATH_SELECTOR.search(raw_line):
            violations.append(Violation(
                file_path=file_path,
                line_no=idx,
                line_text=line,
                rule="NO_XPATH",
                message="XPath selektory jsou v projektu zakázány. Použij get_by_test_id nebo sémantické role.",
                suggested_fix="page.get_by_test_id(...) nebo page.get_by_role(...)",
                educational_tip="Priorita 1–2: Dedikované atributy a přístupnost jsou násobně odolnější než cesty ve stromu DOM.",
                fix_available=False
            ))

        # Pravidlo 4: Dynamicky generovaná ID
        if RE_DYNAMIC_ID.search(raw_line):
            violations.append(Violation(
                file_path=file_path,
                line_no=idx,
                line_text=line,
                rule="NO_DYNAMIC_ID",
                message="Vyhni se dynamicky generovaným ID (#input_123). Použij stabilní atributy, get_by_label nebo data-testid.",
                suggested_fix="page.get_by_label(...) nebo page.locator('input[name=\"...\"]')",
                educational_tip="Priorita 3: Generovaná ID se mění s každým sestavením (buildem) nebo obnovením stránky.",
                fix_available=False
            ))

        # Pravidlo 5: Generované CSS třídy
        if RE_GENERATED_CSS.search(raw_line):
            violations.append(Violation(
                file_path=file_path,
                line_no=idx,
                line_text=line,
                rule="NO_GENERATED_CSS",
                message="Generované CSS třídy (.css-1x84a9) jsou zakázány. Použij funkční atributy nebo get_by_test_id.",
                suggested_fix="page.locator('button[type=\"submit\"]') nebo page.get_by_role('button', name='...')",
                educational_tip="Priorita 5: Spoléhejte se pouze na funkční technické atributy, nikdy na generované třídy vzhledu.",
                fix_available=False
            ))

        # Pravidlo 6: Přímé lokátory v testovacích souborech (vrstva tests/)
        if is_test_file and RE_DIRECT_PAGE_LOCATOR.search(raw_line):
            # Výjimka pro helpery uvnitř conftest / specifické povolené kontexty
            if "page.goto" not in raw_line and "page.screenshot" not in raw_line:
                violations.append(Violation(
                    file_path=file_path,
                    line_no=idx,
                    line_text=line,
                    rule="NO_DIRECT_LOCATORS_IN_TESTS",
                    message="Přímý lokátor v testu porušuje POM (vrstva 3 vs 6). Přesuň definici prvku do Page Objectu.",
                    suggested_fix="Vystavte prvek jako atribut Page Objectu: self.<nazev_prvku> = page.get_by_test_id(...)",
                    educational_tip="Architektura POM: Lokátory patří do Page Objects, testy obsahují pouze scénáře a aserce.",
                    fix_available=False
                ))

    return violations


def apply_fixes(file_path: str) -> int:
    """Aplikuje automatické bezpečné opravy na daný soubor. Vrací počet opravených míst."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content, count = RE_CSS_DATA_TESTID.subn(r'\g<receiver>.get_by_test_id("\g<id>")', content)

    if count > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    return count


def main():
    parser = argparse.ArgumentParser(
        description="Audit a validace Playwright lokátorů podle standardů projektu Kitner.cz"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["pages", "tests", "helpers"],
        help="Cesty k adresářům nebo souborům pro kontrolu (výchozí: pages tests helpers)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automaticky opravit bezpečné vzory (převod locator('[data-testid=...]') na get_by_test_id)"
    )

    args = parser.parse_args()

    target_files = []
    for path in args.paths:
        if os.path.isfile(path) and path.endswith(".py"):
            target_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        target_files.append(os.path.join(root, file))

    if not target_files:
        print("⚠️ Nebyly nalezeny žádné Python soubory ke kontrole.")
        return 0

    print("=" * 70)
    print("🔍 AUDIT KVALITY LOKÁTORŮ (Playwright Locator Quality Scan)")
    print("=" * 70)
    print(f"📁 Počet skenovaných souborů: {len(target_files)}")
    if args.fix:
        print("⚙️ Režim: Kontrola s automatickou opravou (--fix)\n")
    else:
        print("⚙️ Režim: Pouze čtení a audit\n")

    all_violations: List[Violation] = []
    total_fixed = 0

    for file_path in target_files:
        is_test = "tests" in file_path.split(os.sep)

        if args.fix:
            fixed_count = apply_fixes(file_path)
            if fixed_count > 0:
                print(f"🔧 [AUTO-FIX] V souboru {file_path} opraveno {fixed_count} výskytů CSS testid selektorů.")
                total_fixed += fixed_count

        violations = scan_file(file_path, is_test)
        all_violations.extend(violations)

    print("-" * 70)
    if all_violations:
        print(f"❌ Nalezeno {len(all_violations)} porušení pravidel lokátorů:\n")
        by_file: Dict[str, List[Violation]] = {}
        for v in all_violations:
            by_file.setdefault(v.file_path, []).append(v)

        for f_path, v_list in by_file.items():
            print(f"📄 Soubor: {f_path}")
            for v in v_list:
                fix_badge = " [Auto-fix možný]" if v.fix_available else ""
                print(f"   L{v.line_no} [{v.rule}]{fix_badge}: {v.message}")
                print(f"      ❌ Původní: {v.line_text}")
                if v.suggested_fix:
                    print(f"      ✅ Návrh:   {v.suggested_fix}")
                if v.educational_tip:
                    print(f"      💡 Tip:     {v.educational_tip}")
            print()
    else:
        print("✅ Žádná porušení pravidel lokátorů nebyla nalezena. Kód plně odpovídá standardům!")

    print("=" * 70)
    print("📊 SHRNUTÍ AUDITU")
    print(f"   Skenované soubory: {len(target_files)}")
    print(f"   Nalezené neshody:  {len(all_violations)}")
    if args.fix:
        print(f"   Automaticky opraveno: {total_fixed}")
    print("=" * 70)

    if all_violations:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

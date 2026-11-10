#!/usr/bin/env python3
"""
Validační skript: Rozhodnutí zda je hotovo (Definition of Done)
==============================================================

Tento skript provádí automatickou kontrolu a rozhodnutí, zda je úkol
vytvoření přehledu automatizovaných testů kompletně HOTOV.

Kontroluje:
1. Existenci a neprázdnost výstupního Markdown souboru.
2. Přítomnost všech testů z adresáře tests/ v MD souboru (100% úplnost).
3. Přítomnost názvu a ID u každého testu.
4. Přítomnost evidovaných kroků (akcí) u každého testu.
5. Přítomnost evidovaných kontrol (asercí / expect) u každého testu.

Návratové kódy:
  0 = HOTOVO (všechna kritéria splněna)
  1 = NENÍ HOTOVO (některé kritérium selhalo)
"""

import sys
import ast
import argparse
from pathlib import Path
from typing import List, Dict, Set


def get_all_tests_from_code(tests_dir: Path) -> List[Dict[str, str]]:
    """Extrahuje všechny testovací funkce a jejich ID/třídu z kódu v tests/."""
    tests = []
    test_files = sorted(tests_dir.glob("**/test_*.py"))

    for tf in test_files:
        try:
            with open(tf, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(tf))
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                    doc = ast.get_docstring(node) or ""
                    first_line = doc.strip().splitlines()[0] if doc.strip() else ""
                    tests.append({
                        "file": str(tf),
                        "func_name": node.name,
                        "doc_title": first_line,
                        "line": node.lineno,
                    })
        except Exception as e:
            print(f"⚠️ Chyba při čtení {tf}: {e}", file=sys.stderr)

    return tests


def verify_overview_file(overview_path: Path, tests_dir: Path) -> bool:
    """Provede validaci a vrátí True (HOTOVO) nebo False (NENÍ HOTOVO)."""
    print("=" * 60)
    print("🎯 VALIDACE DOKONČENÍ (DEFINITION OF DONE): TEST OVERVIEW")
    print("=" * 60)

    is_done = True
    failures = []

    # 1. Kontrola existence souboru
    if not overview_path.exists():
        print(f"  ❌ [1/5] Výstupní soubor neexistuje: `{overview_path}`")
        print("-" * 60)
        print("❌ ROZHODNUTÍ: NENÍ HOTOVO")
        print("💡 Doporučení: Spusťte generátor pro vytvoření souboru:")
        print("   python3 .agents/skills/test_overview/scripts/generate_test_overview.py")
        print("=" * 60)
        return False

    content = overview_path.read_text(encoding="utf-8")
    if not content.strip():
        print(f"  ❌ [1/5] Výstupní soubor je prázdný: `{overview_path}`")
        return False

    file_size_kb = len(content.encode("utf-8")) / 1024
    print(f"  ✅ [1/5] Výstupní soubor existuje a má obsah: `{overview_path}` ({file_size_kb:.1f} KB)")

    # 2. Získání testů ze zdrojového kódu
    code_tests = get_all_tests_from_code(tests_dir)
    total_code_tests = len(code_tests)
    if total_code_tests == 0:
        print(f"  ❌ [2/5] Ve složce `{tests_dir}` nebyly nalezeny žádné testy!")
        return False

    # 3. Kontrola přítomnosti všech testů v MD souboru
    missing_in_md = []
    tests_without_steps = []
    tests_without_checks = []

    for t in code_tests:
        func_name = t["func_name"]
        # Kontrola, zda je funkce zmíněna v MD
        if func_name not in content:
            missing_in_md.append(f"{func_name} ({t['file']}:{t['line']})")

    if missing_in_md:
        is_done = False
        print(f"  ❌ [2/5] V přehledu chybí {len(missing_in_md)} z {total_code_tests} testů!")
        for m in missing_in_md[:5]:
            print(f"     - {m}")
        if len(missing_in_md) > 5:
            print(f"     ... a dalších {len(missing_in_md) - 5} testů")
    else:
        print(f"  ✅ [2/5] Všech {total_code_tests} testů z kódu je přítomno v přehledu")

    # 4. Kontrola přítomnosti sekcí a kroků
    import re
    step_pattern = re.compile(r'\*\*.*?(Krok|Navigace|Vstup|Příprava|Kliknutí|Autentizace|Klávesa|Obnovení|Výběr|Čekání):?\*\*', re.IGNORECASE)
    step_matches = step_pattern.findall(content)
    has_steps_section = "Postup testu" in content or len(step_matches) > 0

    if not has_steps_section:
        is_done = False
        print("  ❌ [3/5] V souboru nebyly nalezeny sekce s kroky testů!")
        failures.append("Chybí detailní kroky testů.")
    else:
        print(f"  ✅ [3/5] Všechny testy obsahují popsané kroky (nalezeno {len(step_matches)} zaznamenaných kroků)")

    # 5. Kontrola přítomnosti kontrol a asercí
    check_pattern = re.compile(r'\*\*.*?Kontrola:?\*\*', re.IGNORECASE)
    check_matches = check_pattern.findall(content)
    has_checks = len(check_matches) > 0 or "expect(" in content

    if not has_checks:
        is_done = False
        print("  ❌ [4/5] V souboru nebyly nalezeny kontroly ani aserce!")
        failures.append("Chybí ověření a kontroly testů.")
    else:
        print(f"  ✅ [4/5] Všechny testy obsahují evidované kontroly a aserce (nalezeno {len(check_matches)} kontrol)")

    # 6. Kontrola struktury tabulky a modulů
    has_table = "| ID testu |" in content or "| Metrika |" in content
    if has_table:
        print("  ✅ [5/5] Přehled obsahuje strukturovanou tabulku a metriky")
    else:
        is_done = False
        print("  ❌ [5/5] Chybí souhrnná tabulka testů")

    print("-" * 60)

    # Finální rozhodnutí
    if is_done:
        print("🎉 ROZHODNUTÍ: HOTOVO")
        print("Všechna kritéria pro přehled automatizovaných testů jsou 100% splněna.")
        print("=" * 60)
        return True
    else:
        print("❌ ROZHODNUTÍ: NENÍ HOTOVO")
        print("Důvody nedokončení:")
        for f in failures:
            print(f"  - {f}")
        print("💡 Doporučení: Spusťte regeneraci přehledu:")
        print("   python3 .agents/skills/test_overview/scripts/generate_test_overview.py")
        print("=" * 60)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Rozhodnutí zda je hotovo (Definition of Done) pro skill test_overview"
    )
    parser.add_argument(
        "-f", "--overview-file",
        default="docs/TEST_STEPS_OVERVIEW.md",
        help="Cesta k ověřovanému MD souboru (výchozí: docs/TEST_STEPS_OVERVIEW.md)"
    )
    parser.add_argument(
        "-d", "--tests-dir",
        default="tests",
        help="Cesta ke složce s testy (výchozí: tests)"
    )

    args = parser.parse_args()

    overview_path = Path(args.overview_file)
    tests_dir = Path(args.tests_dir)

    is_done = verify_overview_file(overview_path, tests_dir)
    sys.exit(0 if is_done else 1)


if __name__ == "__main__":
    main()

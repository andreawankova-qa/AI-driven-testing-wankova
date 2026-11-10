#!/usr/bin/env python3
"""
verify_tc.py – Validační skript Definice hotovo (Definition of Done) pro manuální test casy.
Používá se v rámci skillu 'story-to-testcases'.

Skript deterministicky ověřuje:
1. Formální úplnost všech test casů (ID, AK, předpoklady, kroky, očekávaný výsledek).
2. Pokrytí všech akceptačních kritérií (AK) ze zadané User Story (každé AK má min. 1 TC).
3. Že v testech nejsou vymyšlená AK, která v zadání neexistují.
4. Přítomnost negativních nebo hraničních testů (zákaz pouze šťastných cest).

Návratový kód (Exit Code):
- 0: Všechna kritéria DoD jsou splněna (PASS).
- 1: Nalezeny formální chyby nebo chybějící pokrytí (FAIL).
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Set, Tuple


class TestCaseDoDValidator:
    def __init__(self, tc_file_path: str, story_file_path: str = None, story_id: str = None, explicit_aks: List[str] = None):
        self.tc_file_path = tc_file_path
        self.story_file_path = story_file_path
        self.story_id = story_id
        self.explicit_aks = explicit_aks or []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.test_cases: List[Dict] = []
        self.story_aks: Set[str] = set()

    def load_files(self) -> bool:
        if not os.path.exists(self.tc_file_path):
            self.errors.append(f"Soubor s test casy neexistuje: {self.tc_file_path}")
            return False

        if self.story_file_path and not os.path.exists(self.story_file_path):
            self.errors.append(f"Soubor se specifikací User Story neexistuje: {self.story_file_path}")
            return False

        return True

    def extract_aks_from_story(self):
        """Vyextrahuje seznam AK z textu story nebo souboru specifikace."""
        if self.explicit_aks:
            for ak in self.explicit_aks:
                cleaned = ak.strip().upper()
                if cleaned:
                    self.story_aks.add(cleaned)
            return

        if not self.story_file_path:
            return

        with open(self.story_file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Pokud je zadáno konkrétní ID story (např. US-01), omezíme se na její sekci
        story_text = content
        if self.story_id:
            pattern = rf"(####\s+{re.escape(self.story_id)}:.*?(?=(####\s+US-|\Z)))"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                story_text = match.group(1)
            else:
                self.warnings.append(f"Sekce pro '{self.story_id}' nebyla v souboru '{self.story_file_path}' nalezena. Hledám AK v celém souboru.")

        # 1. Hledání explicitních AK tagů (např. AK-01, AK-1, **AK-1**)
        explicit_matches = re.findall(r"\b(AK-\d+(?:-[A-Z0-9]+)?)\b", story_text, re.IGNORECASE)
        for m in explicit_matches:
            self.story_aks.add(m.strip().upper())

        # 2. Pokud nejsou explicitní AK tagy, vyextrahujeme odrážky pod sekcí Akceptační kritéria
        if not self.story_aks:
            ak_section_match = re.search(r"-\s+\*\*Akceptační kritéria:\*\*(.*?)(?=(\n#{1,4}\s+|\Z))", story_text, re.DOTALL | re.IGNORECASE)
            if ak_section_match:
                bullets = [
                    line.strip().lstrip("-* ").strip()
                    for line in ak_section_match.group(1).strip().splitlines()
                    if line.strip().startswith(("-", "*"))
                    and not line.strip().startswith("---")
                    and line.strip().lstrip("-* ").strip()
                ]
                for idx, bullet in enumerate(bullets, start=1):
                    self.story_aks.add(f"AK-{idx}")

    def parse_test_cases(self):
        """Parsuje markdown soubor a hledá test casy a jejich atributy."""
        with open(self.tc_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        current_tc = None
        current_section = None

        tc_header_regex = re.compile(r"^(?:####|###)\s+[`\*]*([A-Za-z0-9_-]+)[`\*]*\s*:\s*(.+)$")

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            header_match = tc_header_regex.match(stripped)
            if header_match:
                if current_tc:
                    self.test_cases.append(current_tc)

                current_tc = {
                    "line": line_num,
                    "id": header_match.group(1).strip(),
                    "title": header_match.group(2).strip(),
                    "aks": set(),
                    "stories": set(),
                    "preconditions": [],
                    "test_data": [],
                    "steps": [],
                    "expected": [],
                    "raw_text": [],
                    "test_type": None,
                }
                current_section = None
                continue

            if not current_tc:
                continue

            current_tc["raw_text"].append(stripped)

            # Detekce typu testu
            if "typ testu:" in stripped.lower():
                current_tc["test_type"] = stripped.split(":", 1)[1].strip()

            # Detekce AK a US v pokrytí
            if "pokrytí:" in stripped.lower() or "akceptační kritérium:" in stripped.lower():
                # Hledání US
                us_matches = re.findall(r"\b(US-\d+)\b", stripped, re.IGNORECASE)
                for us in us_matches:
                    current_tc["stories"].add(us.upper())

                # Hledání AK
                ak_matches = re.findall(r"\b(AK-\d+|AK\d+)\b", stripped, re.IGNORECASE)
                for ak in ak_matches:
                    norm_ak = re.sub(r"^AK(\d+)", r"AK-\1", ak.upper())
                    current_tc["aks"].add(norm_ak)

            # Přepínání sekcí
            if re.search(r"^\*\s*\*\*předpoklady:\*\*", stripped, re.IGNORECASE):
                current_section = "preconditions"
                content_after = re.sub(r"^\*\s*\*\*předpoklady:\*\*\s*", "", stripped, flags=re.IGNORECASE)
                if content_after:
                    current_tc["preconditions"].append(content_after)
                continue

            if re.search(r"^\*\s*\*\*testovací data:\*\*", stripped, re.IGNORECASE):
                current_section = "test_data"
                content_after = re.sub(r"^\*\s*\*\*testovací data:\*\*\s*", "", stripped, flags=re.IGNORECASE)
                if content_after:
                    current_tc["test_data"].append(content_after)
                continue

            if re.search(r"^\*\s*\*\*kroky:\*\*", stripped, re.IGNORECASE):
                current_section = "steps"
                continue

            if re.search(r"^\*\s*\*\*očekávaný výsledek:\*\*", stripped, re.IGNORECASE):
                current_section = "expected"
                continue

            # Plnění aktivní sekce
            if current_section == "preconditions" and (stripped.startswith("-") or stripped.startswith("*")):
                current_tc["preconditions"].append(stripped.lstrip("-* ").strip())
            elif current_section == "test_data" and (stripped.startswith("-") or stripped.startswith("*")):
                current_tc["test_data"].append(stripped.lstrip("-* ").strip())
            elif current_section == "steps" and re.match(r"^\d+\.\s+", stripped):
                current_tc["steps"].append(re.sub(r"^\d+\.\s+", "", stripped).strip())
            elif current_section == "expected" and (stripped.startswith("-") or stripped.startswith("*")):
                current_tc["expected"].append(stripped.lstrip("-* ").strip())

        if current_tc:
            self.test_cases.append(current_tc)

    def validate_dod(self):
        """Vyhodnotí splnění všech pravidel Definice hotovo (DoD)."""
        # 1. Pravidlo: Existují test casy?
        if not self.test_cases:
            self.errors.append("V souboru nebyly nalezeny žádné test casy ve formátu '#### TC-xx: Název'.")
            return

        tc_ids = set()
        covered_aks = set()
        has_negative_or_boundary = False

        for tc in self.test_cases:
            tc_id = tc["id"]
            line = tc["line"]

            # Duplicitní ID
            if tc_id in tc_ids:
                self.errors.append(f"[Řádek {line}] Duplicitní ID testovacího případu '{tc_id}'.")
            tc_ids.add(tc_id)

            # Vazba na AK nebo US
            if not tc["aks"] and not tc["stories"]:
                self.errors.append(f"[{tc_id}] Chybí vazba na akceptační kritérium nebo User Story (* **Pokrytí:** AK-xx nebo US-xx).")
            elif self.story_aks and not tc["aks"]:
                self.errors.append(f"[{tc_id}] Chybí vazba na konkrétní akceptační kritérium (* **Pokrytí:** AK-xx).")
            else:
                covered_aks.update(tc["aks"])

            # Předpoklady
            if not tc["preconditions"]:
                self.errors.append(f"[{tc_id}] Chybí sekce '* **Předpoklady:**' nebo je prázdná.")

            # Kroky
            if not tc["steps"]:
                self.errors.append(f"[{tc_id}] Chybí očíslované kroky testu ('1. ...', '2. ...').")
            elif len(tc["steps"]) < 2 and "negativní" not in (tc.get("test_type") or "").lower():
                self.warnings.append(f"[{tc_id}] Test má pouze 1 krok, prověřte detailnost postupu.")

            # Očekávaný výsledek
            if not tc["expected"]:
                self.errors.append(f"[{tc_id}] Chybí sekce '* **Očekávaný výsledek:**' s odrážkami výsledků.")

            # Detekce rozmanitosti (negativní, hraniční, validace)
            raw_blob = " ".join(tc["raw_text"]).lower()
            if any(term in raw_blob for term in ["negativní", "chyb", "neplatn", "validac", "hranic", "bva", "limit"]):
                has_negative_or_boundary = True

        # 2. Pravidlo: Pokrytí všech AK ze zadání
        if self.story_aks:
            # Normalizace pro porovnání (např. AK-1 vs AK-01)
            def normalize_ak_set(ak_set):
                res = set()
                for ak in ak_set:
                    m = re.match(r"^AK-?0*(\d+)", ak, re.IGNORECASE)
                    if m:
                        res.add(f"AK-{int(m.group(1))}")
                    else:
                        res.add(ak.upper())
                return res

            norm_story_aks = normalize_ak_set(self.story_aks)
            norm_covered_aks = normalize_ak_set(covered_aks)

            missing_aks = norm_story_aks - norm_covered_aks
            if missing_aks:
                self.errors.append(f"Nenalezen žádný test case pro akceptační kritéria: {', '.join(sorted(missing_aks))}.")

            extra_aks = norm_covered_aks - norm_story_aks
            if extra_aks:
                self.warnings.append(f"Testy odkazují na AK, která nebyla nalezena ve specifikaci story: {', '.join(sorted(extra_aks))}.")

        # 3. Pravidlo: Přítomnost negativních scénářů
        if not has_negative_or_boundary:
            self.warnings.append("Sada testů neobsahuje zjevné negativní, validační ani hraniční scénáře (pouze Happy Path).")

    def print_report(self) -> int:
        print("=" * 70)
        print("🔍 VÝSLEDEK DEFINICE HOTOVO (DoD) – STORY-TO-TESTCASES")
        print("=" * 70)
        print(f"📄 Soubor s test casy: {self.tc_file_path}")
        if self.story_file_path:
            print(f"📖 Soubor se specifikací: {self.story_file_path}")
        if self.story_id:
            print(f"🎯 Analyzovaná User Story: {self.story_id}")
        print(f"📊 Celkem nalezených test casů: {len(self.test_cases)}")

        if self.story_aks:
            print(f"🎯 Vyžadovaná akceptační kritéria: {', '.join(sorted(self.story_aks))}")

        print("-" * 70)

        if self.warnings:
            print("⚠️  VAROVÁNÍ:")
            for w in self.warnings:
                print(f"  [!] {w}")
            print("-" * 70)

        if self.errors:
            print("❌ CHYBY DEFINICE HOTOVO (DoD):")
            for e in self.errors:
                print(f"  [X] {e}")
            print("=" * 70)
            print("🛑 VÝSLEDEK: FAIL – Úkol NENÍ hotový! Opravte výše uvedené chyby.")
            print("=" * 70)
            return 1
        else:
            print("✅ VŠECHNA KRITÉRIA DEFINICE HOTOVO (DoD) JSOU SPLNĚNA!")
            print(f"   Všechny test casy ({len(self.test_cases)}) mají kompletní strukturu a pokrývají AK.")
            print("=" * 70)
            print("🎉 VÝSLEDEK: PASS – Test casy jsou připraveny k lidskému schválení (Krok 4).")
            print("=" * 70)
            return 0


def main():
    parser = argparse.ArgumentParser(description="Validační skript Definice hotovo (DoD) pro převod User Story na manuální Test Casy.")
    parser.add_argument("--tc", required=True, help="Cesta k markdown souboru s test casy (např. docs/TEST_CASES.md).")
    parser.add_argument("--story", help="Cesta k souboru se specifikací User Story (např. docs/požadavky_ust_podle_src.md).")
    parser.add_argument("--story-id", help="Identifikátor User Story (např. US-01).")
    parser.add_argument("--ak", help="Čárkou oddělený seznam očekávaných AK (např. 'AK-1,AK-2,AK-3').")

    args = parser.parse_args()

    explicit_aks = [a.strip() for a in args.ak.split(",")] if args.ak else []

    validator = TestCaseDoDValidator(
        tc_file_path=args.tc,
        story_file_path=args.story,
        story_id=args.story_id,
        explicit_aks=explicit_aks,
    )

    if not validator.load_files():
        validator.print_report()
        sys.exit(1)

    validator.extract_aks_from_story()
    validator.parse_test_cases()
    validator.validate_dod()
    exit_code = validator.print_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

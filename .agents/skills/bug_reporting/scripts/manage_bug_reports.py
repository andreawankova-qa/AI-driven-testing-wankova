#!/usr/bin/env python3
"""Pomocný skript pro správu centrálního registru chyb v docs/JIRA_BUG_REPORTS.md.

Poskytuje funkce pro:
- Zjištění dalšího volného ID (BR-XX)
- Validaci struktury a povinných polí JIRA hlášení
- Bezpečné zapsání reportu do přehledové tabulky a na konec dokumentu
- Výpis existujících chyb v registru
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

# Cesta k centrálnímu registru chyb
DEFAULT_DOCS_PATH = Path(__file__).resolve().parents[4] / "docs" / "JIRA_BUG_REPORTS.md"


def get_anchor_slug(heading_text: str) -> str:
    """Vytvoří standardní GitHub markdown kotvu (anchor) z nadpisu."""
    # Odstranění emoji a speciálních znaků, převod na malá písmena
    text = heading_text.lower()
    # Nahrazení mezer a nepovolených znaků pomlčkami
    text = re.sub(r"[^\w\s\-/–—]", "", text)
    text = re.sub(r"[\s/–—]+", "-", text).strip("-")
    return text


def read_register(docs_path: Path) -> str:
    """Načte obsah registru chyb."""
    if not docs_path.exists():
        raise FileNotFoundError(f"Registr chyb nebyl nalezen na cestě: {docs_path}")
    return docs_path.read_text(encoding="utf-8")


def find_all_bug_ids(content: str) -> list[int]:
    """Najde všechna existující čísla BR-XX z nadpisů a řádků přehledové tabulky."""
    # Hledáme pouze řádky tabulky | [**BR-XX**] nebo nadpisy ### 🐞 BR-XX
    table_ids = [int(m) for m in re.findall(r"\|\s*\[\*\*BR-(\d+)\*\*\]", content)]
    heading_ids = [int(m) for m in re.findall(r"###\s+🐞\s+BR-(\d+)", content)]
    all_ids = set(table_ids + heading_ids)
    return sorted(list(all_ids))


def get_next_bug_id(docs_path: Path) -> str:
    """Vrátí následující volné ID ve formátu BR-XX."""
    content = read_register(docs_path)
    ids = find_all_bug_ids(content)
    next_num = (max(ids) + 1) if ids else 1
    return f"BR-{next_num:02d}"


def validate_report_content(report_text: str) -> tuple[bool, list[str]]:
    """Ověří, zda text reportu obsahuje všechny povinné sekce a metadata."""
    errors = []

    # Kontrola hlavního nadpisu
    if not re.search(r"###\s+🐞\s+BR-\d+", report_text):
        errors.append("Chybí hlavní nadpis ve formátu: '### 🐞 BR-XX [MODUL]: ...'")

    # Povinná metadata
    mandatory_metadata = [
        ("Project:", r"\*\s*\*\*Project:\*\*"),
        ("Issue Type:", r"\*\s*\*\*Issue Type:\*\*"),
        ("Summary:", r"\*\s*\*\*Summary.*:\*\*"),
        ("Komponenta:", r"\*\s*\*\*Komponenta:\*\*"),
        ("Závažnost (Severity):", r"\*\s*\*\*Závažnost.*:\*\*"),
        ("Priorita (Priority):", r"\*\s*\*\*Priorita.*:\*\*"),
        ("Reprodukovatelnost:", r"\*\s*\*\*Reprodukovatelnost.*:\*\*"),
        ("Vázané User Stories:", r"\*\s*\*\*Vázané User Stories:\*\*"),
        ("Související Test Casy:", r"\*\s*\*\*Související Test Casy:\*\*"),
        ("Prostředí:", r"\*\s*\*\*Prostředí:\*\*"),
        ("Nahlásil:", r"\*\s*\*\*Nahlásil:\*\*"),
        ("Datum nálezu:", r"\*\s*\*\*Datum nálezu:\*\*"),
    ]

    for label, pattern in mandatory_metadata:
        if not re.search(pattern, report_text):
            errors.append(f"Chybí povinné metadatové pole: {label}")

    # Povinné obsahové sekce (H4)
    mandatory_sections = [
        ("Popis problému", r"####\s+📝\s+Popis problému"),
        ("Předpoklady", r"####\s+⚙️\s+Předpoklady"),
        ("Kroky k reprodukci", r"####\s+👣\s+Kroky k reprodukci"),
        ("Očekávané chování", r"####\s+✅\s+Očekávané chování"),
        ("Skutečné chování", r"####\s+❌\s+Skutečné chování"),
        ("Bezpečnostní a byznysový dopad", r"####\s+⚠️\s+Bezpečnostní a byznysový dopad"),
        ("Technický důkaz (Log)", r"####\s+💻\s+Technický důkaz"),
        ("Doporučené řešení", r"####\s+💡\s+Doporučené řešení"),
        ("Záznam o verifikaci", r"####\s+🔄\s+Záznam o verifikaci"),
    ]

    for label, pattern in mandatory_sections:
        if not re.search(pattern, report_text):
            errors.append(f"Chybí povinná sekce: {label}")

    return (len(errors) == 0, errors)


def extract_table_fields(report_text: str) -> dict[str, str]:
    """Extrahuje klíčové hodnoty pro vložení do souhrnné tabulky."""
    fields = {
        "bug_id": "",
        "heading": "",
        "module": "N/A",
        "title": "Incident",
        "severity": "Medium",
        "priority": "Medium",
        "linked_us": "N/A",
        "status": "🔴 Otevřeno",
    }

    # ID a Nadpis
    heading_match = re.search(r"###\s+🐞\s+(BR-\d+)\s*(\[.*?\])?:\s*(.+)", report_text)
    if heading_match:
        fields["bug_id"] = heading_match.group(1).strip()
        mod_tag = heading_match.group(2)
        if mod_tag:
            fields["module"] = mod_tag.strip("[] ")
        fields["title"] = heading_match.group(3).strip()
        fields["heading"] = f"{fields['bug_id']} {mod_tag or ''}: {fields['title']}".strip()
    else:
        # Fallback na prosté BR-XX
        id_match = re.search(r"(BR-\d+)", report_text)
        if id_match:
            fields["bug_id"] = id_match.group(1)

    # Závažnost
    sev_match = re.search(r"\*\s*\*\*Závažnost.*:\*\*\s*([^\n\r(]+)", report_text)
    if sev_match:
        fields["severity"] = sev_match.group(1).strip()

    # Priorita
    prio_match = re.search(r"\*\s*\*\*Priorita.*:\*\*\s*([^\n\r(]+)", report_text)
    if prio_match:
        fields["priority"] = prio_match.group(1).strip()

    # User Stories
    us_matches = re.findall(r"US-\d+", report_text)
    if us_matches:
        # Odstranit duplicity a zachovat pořadí
        unique_us = list(dict.fromkeys(us_matches))
        fields["linked_us"] = ", ".join(unique_us)

    # Komponenta / Modul z metadat, pokud nebyl v nadpisu
    if fields["module"] == "N/A":
        comp_match = re.search(r"\*\s*\*\*Komponenta:\*\*\s*([^\n\r]+)", report_text)
        if comp_match:
            fields["module"] = comp_match.group(1).strip()

    return fields


def append_bug_report(docs_path: Path, report_text: str, dry_run: bool = False) -> str:
    """Připojí hlášení do přehledové tabulky a na konec registru."""
    is_valid, errors = validate_report_content(report_text)
    if not is_valid:
        error_msg = "Chyba validace reportu:\n" + "\n".join(f" - {err}" for err in errors)
        raise ValueError(error_msg)

    content = read_register(docs_path)
    fields = extract_table_fields(report_text)
    bug_id = fields["bug_id"]

    # Ověřit, zda ID již neexistuje v přehledu
    if f"| [**{bug_id}**]" in content:
        raise ValueError(f"Chyba s ID '{bug_id}' již v přehledové tabulce existuje!")

    # Vytvoření kotvy a řádku tabulky
    # Najít přesný text nadpisu v report_text pro kotvu
    heading_line_match = re.search(r"###\s+🐞\s+(.+)", report_text)
    heading_for_slug = heading_line_match.group(1) if heading_line_match else f"{bug_id} incident"
    # Odstranit lomítka a formátovat slug
    slug = heading_for_slug.lower()
    slug = re.sub(r"[^\w\s\-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug).strip("-")

    # Formát řádku: | [**BR-02**](#kotva) | `MODUL` | Název incidentu | **Severity** | **Priority** | US-XX | 🔴 Otevřeno |
    table_row = (
        f"| [**{bug_id}**](#{slug}) | `{fields['module']}` | {fields['title']} | "
        f"**{fields['severity']}** | **{fields['priority']}** | {fields['linked_us']} | {fields['status']} |"
    )

    # Najít konec tabulky: řádek začínající "| [**BR-" a následovaný prázdným řádkem
    table_pattern = re.compile(r"(\| \[\*\*BR-\d+\*\*\][^\n]*\n)(\n)", re.MULTILINE)
    match = list(table_pattern.finditer(content))
    if not match:
        raise RuntimeError("V dokumentu se nepodařilo nalézt existující řádky souhrnné tabulky defektů.")

    last_row_match = match[-1]
    insert_pos = last_row_match.end(1)

    # Vložení nového řádku do tabulky
    new_content = content[:insert_pos] + table_row + "\n" + content[insert_pos:]

    # Připojení detailního ticketu na konec dokumentu s oddělovačem
    clean_report = report_text.strip()
    new_content = new_content.rstrip() + "\n\n---\n\n" + clean_report + "\n"

    if dry_run:
        print("=== DRY RUN (NÁHLED ŘÁDKU TABULKY) ===")
        print(table_row)
        print("\n=== DRY RUN (NÁHLED ZÁVĚRU TICKETU) ===")
        print(clean_report[:400] + "\n...")
        return new_content

    docs_path.write_text(new_content, encoding="utf-8")
    return new_content


def list_existing_bugs(docs_path: Path) -> None:
    """Vypíše přehled dosud nahlášených chyb v registru."""
    content = read_register(docs_path)
    pattern = re.compile(
        r"\|\s*\[\*\*(BR-\d+)\*\*\]\([^)]+\)\s*\|\s*`?([^`|]+)`?\s*\|\s*([^|]+)\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|"
    )
    rows = pattern.findall(content)

    print(f"\n📋 Přehled chyb v registru: {docs_path.name}")
    print("-" * 80)
    print(f"{'ID':<8} {'Modul':<15} {'Závažnost':<15} {'Priorita':<10} {'Stav':<12} Název")
    print("-" * 80)
    for r in rows:
        bid, mod, title, sev, prio, us, status = [x.strip() for x in r]
        print(f"{bid:<8} {mod:<15} {sev:<15} {prio:<10} {status:<12} {title[:40]}")
    print("-" * 80)


def main():
    parser = argparse.ArgumentParser(description="Správce registru chyb v docs/JIRA_BUG_REPORTS.md")
    parser.add_argument(
        "--docs-path",
        type=Path,
        default=DEFAULT_DOCS_PATH,
        help=f"Cesta k souboru registru chyb (výchozí: {DEFAULT_DOCS_PATH})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # next-id
    subparsers.add_parser("next-id", help="Vrátí následující volné ID chyby (např. BR-02)")

    # list
    subparsers.add_parser("list", help="Vypíše seznam všech nahlášených chyb v přehledu")

    # validate
    val_parser = subparsers.add_parser("validate", help="Ověří formální správnost JIRA hlášení")
    val_parser.add_argument("file", nargs="?", type=Path, help="Soubor s hlášením (nebo stdin)")

    # append
    app_parser = subparsers.add_parser("append", help="Zapíše schválené hlášení do JIRA_BUG_REPORTS.md")
    app_parser.add_argument("file", nargs="?", type=Path, help="Soubor s hlášením (nebo stdin)")
    app_parser.add_argument("--dry-run", action="store_true", help="Pouze zobrazí náhled změn bez zápisu do souboru")

    args = parser.parse_args()

    try:
        if args.command == "next-id":
            print(get_next_bug_id(args.docs_path))

        elif args.command == "list":
            list_existing_bugs(args.docs_path)

        elif args.command == "validate":
            text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
            is_valid, errors = validate_report_content(text)
            if is_valid:
                print("✅ Hlášení je platné a splňuje všechny požadované sekce.")
            else:
                print("❌ Hlášení nesplňuje požadovanou strukturu:")
                for err in errors:
                    print(f"  - {err}")
                sys.exit(1)

        elif args.command == "append":
            text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
            append_bug_report(args.docs_path, text, dry_run=args.dry_run)
            if not args.dry_run:
                print(f"✅ Hlášení bylo úspěšně připojeno do {args.docs_path}")

    except Exception as e:
        print(f"❌ Chyba: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

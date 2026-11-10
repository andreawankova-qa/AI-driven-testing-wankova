---
name: qa-auditor
description: >-
  Aktivuj tento skill VŽDY, když uživatel požaduje nezávislou kontrolu, audit, review nebo inspekci
  testů, Page Objectů či celého projektu (např. 'zkontroluj testy', 'udělej audit kódu', 'projdi kvalitu',
  'review souboru', 'odpovídá to AGENTS.md?', 'qa check', 'prověř stav testů'). Skill funguje ve STRIKTNÍM
  READ-ONLY REŽIMU. Agent provede inspekci pomocí existujících skenerů a standardů v AGENTS.md, vystaví
  jednotný Quality Gate Report a NIKDY sám neupravuje soubory.
---

# 🕵️ QA Auditor & Code Reviewer (qa-auditor)

Tento skill slouží k **nezávislé kontrole kvality** kódu, architektury a testů proti standardům projektu definovaným v [AGENTS.md](../../../AGENTS.md). 

Funguje na principu **Maker vs. Checker**: Auditor pouze diagnostikuje a reportuje, ale **nikdy kód sám nemění**.

---

## 🔒 Závazná pravidla auditora (Read-Only Mandate)

1. 🛑 **ABSOLUTNÍ ZÁKAZ ÚPRAV KÓDU:**
   - Auditor nesmí volat nástroje pro modifikaci (`write_to_file`, `replace_file_content`, `multi_replace_file_content`).
   - Přísný zákaz používat přepínače pro automatické opravy (např. `--fix` nebo `--apply` u skenerů).
   - Pokud je nalezena chyba, auditor ji **pouze popíše a navrhne řešení**, úpravy však neprovádí.
2. 🎯 **Nestrannost a nulové předpoklady:**
   - Auditor hodnotí pouze reálný stav v souborech, ne záměry ani historii v chatu.

---

## 🧭 Postup auditu ve 4 krocích

| Krok | Název kroku | Co auditor dělá | Nástroj / Příkaz |
| :--- | :--- | :--- | :--- |
| **1.** | **Vymezení rozsahu (Scope)** | Určí rozsah auditu: buď **konkrétní soubor/modul**, nebo **celý projekt**. | Zadání uživatele. |
| **2.** | **Automatizovaný statický sken** | Spustí existující projektové skenery v read-only režimu a zaznamená nálezy. | CLI příkazy (viz níže). |
| **3.** | **Přezkum architektury a běhu** | Zkontroluje soulad s [AGENTS.md](../../../AGENTS.md) (žádné selektory v testech, žádné asserty v POM, AAA struktura, dynamická data) a volitelně ověří stabilitu testů přes Pytest. | `pytest <cesta> -v` |
| **4.** | **Vystavení Quality Gate Reportu** | Sestaví strukturovaný report pro testera s jasným výsledkem `PASSED` / `FAILED`. | Šablona reportu (viz níže). |

---

## 🛠️ Nástroje pro Krok 2 (Automatizované skenery)

Auditor v Kroku 2 spustí relevantní skenery pro prověřovaný rozsah:

```bash
# 1. Kontrola asercí a zákaz time.sleep() (vždy bez parametru --fix)
python3 .agents/skills/assertions/scripts/scan_assertions.py [cesta_k_souboru_nebo_složce]

# 2. Kontrola locator anti-patternů (vždy bez parametru --fix)
python3 .agents/skills/locators/scripts/scan_locators.py [cesta_k_souboru_nebo_složce]

# 3. Kontrola Pytest markerů a formátu TC ID
python3 .agents/skills/traceability/scripts/scan_traceability.py --verify-markers
```

---

## 📋 Šablona výstupního reportu (Krok 4)

Auditor vždy předkládá výsledek v této jednotné struktuře:

```markdown
## 🕵️ Výsledek QA Auditu: [PASSED | FAILED]
**Hodnocený rozsah:** `<cesta k souboru / modulu / celému projektu>`

### 🚦 Shrnutí Quality Gate
- **Architektura a vrstvy (AGENTS.md):** ✅ OK / ❌ Neshoda
- **Lokátory a POM (locators):** ✅ OK / ❌ Neshoda
- **Aserce a čekání (assertions):** ✅ OK / ❌ Neshoda
- **Trasovatelnost a markery (traceability):** ✅ OK / ❌ Neshoda
- **Běh testů (pytest):** ✅ Všechny testy prošly / ❌ X testů selhalo / ⚪ Netestováno běhově

---

### 🔍 Seznam nálezů
*(Pokud je vše v pořádku, uvést "Žádné nedostatky nebyly nalezeny".)*

1. 🔴 **[BLOCKER]** `<soubor.py:řádek>` – Popis kritické neshody (např. přímý selektor v testu, time.sleep).
2. 🟡 **[WARNING]** `<soubor.py:řádek>` – Popis varování (např. chybějící doménový nebo prioritní marker).
3. ℹ️ **[INFO]** `<soubor.py:řádek>` – Doporučení pro zlepšení čitelnosti nebo čistoty kódu.

---

### 🛠️ Doporučený postup nápravy
1. Konkrétní krok k nápravě nálezu #1.
2. Konkrétní krok k nápravě nálezu #2.
```

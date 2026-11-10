---
name: story_coverage
description: >-
  Aktivuj tento skill VŽDY, když uživatel požaduje přehled, stav nebo analýzu pokrytí User Stories
  test casy či automatizovanými testy (např. dotazy na dostatečnost testů, zda jsou všechny US pokryté/otestované,
  nebo kde jsou mezery v pokrytí akceptačních kritérií). Generuje interaktivní HTML dashboard a stručné
  manažerské shrnutí stávajícího stavu projektu.
---

# 📊 Story Coverage (Přehled pokrytí User Stories)

Tento skill slouží k vygenerování opakovatelného a přehledného HTML reportu, který mapuje pokrytí jednotlivých User Stories automatizovanými testy.

---

## 🎯 Zdroje dat

Skript analyzuje 4 klíčové zdroje v projektu:
1. **Byznysové požadavky:** `docs/požadavky_ust_podle_src.md` (User Stories `US-01` až `US-19` a jejich akceptační kritéria).
2. **Katalog testovacích případů:** `docs/TEST_CASES.md` (Přiřazení Test Casů k User Stories a pokrytá AK).
3. **Kód automatizovaných testů:** `tests/**/*.py` (Reálně implementované testy, markery a `@pytest.mark.xfail`).
4. **Centrální registr defektů:** `docs/JIRA_BUG_REPORTS.md` (Evidované chyby `BR-xx` v aplikaci).

---

## 🚀 Pracovní postup (Workflow)

Kdykoliv uživatel požádá o přehled pokrytí požadavků nebo user stories, agent postupuje takto:

### Krok 1: Spuštění generování reportu
Spusťte skript pro vygenerování HTML reportu:
```bash
python3 .agents/skills/story_coverage/scripts/generate_story_coverage.py
```
*(Volitelně lze určit vlastní cestu výstupu parametrem `--output <cesta.html>`.)*

### Krok 2: Ověření existence reportu
Ověřte, že byl soubor `reports/story_coverage.html` úspěšně vytvořen a má nenulovou velikost.

### Krok 3: Prezentace výsledku uživateli
Do chatu nevypisujte celý obsah souboru. Předložte pouze **stručné exekutivní shrnutí** podle této šablony:

```markdown
### 📊 Souhrn pokrytí User Stories automatizovanými testy
- **Celkem User Stories:** X (Z toho plně pokryto: Y, částečně: Z, nepokryto: W)
- **Celková míra pokrytí požadavků:** XX.X %
- **Celkem Test Casů:** XX | **Zautomatizováno:** YY (ZZ.Z %)
- **Aktivní evidované defekty (XFAIL):** N

HTML report byl úspěšně vygenerován: [story_coverage.html](file:///cesta/k/reports/story_coverage.html)
```

---

## ⚙️ CLI parametry skriptu

```bash
# Výchozí běh (generuje reports/story_coverage.html)
python3 .agents/skills/story_coverage/scripts/generate_story_coverage.py

# Vlastní výstupní soubor
python3 .agents/skills/story_coverage/scripts/generate_story_coverage.py --output docs/story_coverage.html

# Tichý režim (pouze návratový kód 0 / 1)
python3 .agents/skills/story_coverage/scripts/generate_story_coverage.py --quiet
```

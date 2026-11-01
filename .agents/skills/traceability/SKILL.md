---
name: traceability
description: >-
  Použij tento skill, kdykoliv uživatel ověřuje pokrytí požadavků (Traceability Matrix), kontroluje soulad
  testů s TEST_CASES.md a User Stories, hledá nepokryté scénáře, vytváří nové testy podle specifikace nebo
  sjednocuje číslování a markery testů. Vynucuje 5 zlatých pravidel trasovatelnosti, kontrolu shody doménových
  a prioritních markerů (@pytest.mark.smoke/regression), formát docstringů TC-xx-MODUL a obsahuje skript
  scan_traceability.py pro audit, export matice a scaffolding testů.
---

# 🧭 Traceability – Matice pokrytí a obousměrná trasovatelnost (Playwright & Pytest)

Tento skill představuje ucelenou metodiku a automatizovaný nástroj pro zajištění 100% obousměrné trasovatelnosti mezi:
1. **Byznysovými požadavky** ([`docs/požadavky_ust_podle_src.md`](../../../docs/požadavky_ust_podle_src.md) – `US-01` až `US-19`)
2. **Katalogem testovacích případů** ([`docs/TEST_CASES.md`](../../../docs/TEST_CASES.md) – `TC-01-AUTH` až `TC-47-SEC`)
3. **Kódem automatizovaných testů** (`tests/**/*.py`)
4. **Centrálním registrem defektů** ([`docs/JIRA_BUG_REPORTS.md`](../../../docs/JIRA_BUG_REPORTS.md) – `BR-01` až `BR-xx`)

> **Základní princip trasovatelnosti:**  
> *Každý automatizovaný test musí mít jasného „rodiče“ ve specifikaci požadavků a každý byznysový požadavek musí mít prokazatelnou validaci v kódu. Test bez vazby na specifikaci je nekontrolovaný, požadavek bez testu je rizikem pro produkci.*

---

## 🏆 5 zlatých pravidel trasovatelnosti v projektu

1. **Jednoznačné kanonické ID (`TC-xx-MODUL`):**  
   Každý testovací případ má unikátní kód s dvoumístným číslem a kódem modulu (`TC-01-AUTH` až `TC-47-SEC`). Toto ID musí být uvedeno v prvním řádku docstringu testovací funkce a doporučeno i v jejím názvu.
2. **Konzistence Pytest markerů:**  
   Každý test musí nést doménový marker odpovídající modulu (`@pytest.mark.auth`, `courses`, `enrollment`, `lecturer`, `profile`, `security`) a marker závažnosti odpovídající prioritě v `TEST_CASES.md` (`smoke` pro P1/Smoke, `regression` pro P2/P3).
3. **Striktní AAA struktura (Arrange, Act, Assert):**  
   Implementace testu musí být členěna do 3 bloků. Příprava dat využívá výhradně dynamický generátor [`utils.data_generator`](../../../utils/data_generator.py) pro zaručení idempotence.
4. **Žádné osiřelé testy ani slepá místa:**  
   Všechny testovací metody v `tests/` musí mapovat na schválený Test Case. Nově objevené scénáře se nejprve zaevidují do [`docs/TEST_CASES.md`](../../../docs/TEST_CASES.md).
5. **Human-in-the-Loop při refaktoringu:**  
   Agent nesmí přejmenovávat testy ani hromadně měnit docstringy bez předložení diffu a výslovného souhlasu uživatele.

---

## 🛠️ Nástroj: `scan_traceability.py`

Skill obsahuje výkonný nástroj pro statickou analýzu a generování kódu umístěný v:
`scripts/scan_traceability.py`

### Rychlý přehled příkazů CLI:

```bash
# 1. Zobrazení kompletní matice pokrytí, statistik a vazeb na defekty
python3 .agents/skills/traceability/scripts/scan_traceability.py --matrix

# 2. Reverzní dotaz na byznysový požadavek (všechny navázané TC, kód testů a JIRA bugy)
python3 .agents/skills/traceability/scripts/scan_traceability.py --story US-18

# 3. Reverzní vyhledání z kódu nahoru (najde test a zobrazí celou cestu k TC, US a defektu)
python3 .agents/skills/traceability/scripts/scan_traceability.py --find test_tc44_sec

# 4. Zobrazení přehledné prioritizované tabulky chybějících testů (P1 / P2 / P3)
python3 .agents/skills/traceability/scripts/scan_traceability.py --missing

# 5. Zobrazení detailních kroků a testovacích dat u chybějících testů
python3 .agents/skills/traceability/scripts/scan_traceability.py --missing --detail

# 6. Audit kvality markerů a detekce zastaralých/nekonzistentních ID
python3 .agents/skills/traceability/scripts/scan_traceability.py --verify-markers

# 7. Vygenerování připravené AAA kostry pro chybějící Test Case (např. TC-13-AUTH)
python3 .agents/skills/traceability/scripts/scan_traceability.py --scaffold TC-13-AUTH

# 8. Zobrazení Before & After diffu pro sjednocení starších formátů docstringů
python3 .agents/skills/traceability/scripts/scan_traceability.py --fix-docstrings

# 9. Aplikace sjednocení docstringů (po schválení uživatelem)
python3 .agents/skills/traceability/scripts/scan_traceability.py --fix-docstrings --apply

# 10. Vyexportování aktuální matice trasovatelnosti do Markdown reportu
python3 .agents/skills/traceability/scripts/scan_traceability.py --export-md docs/TRACEABILITY_MATRIX.md
```

---

## 📋 Standard pro prezentaci chybějících testů uživateli

Kdykoliv uživatel položí dotaz na chybějící testy (*„Jaké testy nám chybí?“, „Co ještě není pokryto?“, „Vypiš mi chybějící testy“*), agent **nesmí** do chatu nekriticky vložit surový víceřádkový text z terminálu. Povinně dodrží tento **4krokový formát**:

### 1. Manažerské shrnutí (Executive Summary)
* Uvede přesný počet chybějících scénářů.
* Uvede stávající stav pokrytí a cílový stav po jejich implementaci (např. *„V projektu chybí 11 testů v modulu AUTH; po jejich dokončení stoupne pokrytí ze 76.6 % na 100 %“*).

### 2. Strukturovaná tabulka rozdělená podle priorit (P1 ➔ P2 ➔ P3)
Tabulka musí obsahovat přesné sloupce:
* **Priorita:**
  * 🔴 **P1 (Smoke):** Kritické a bezpečnostní scénáře (přímý dopad na integritu systému).
  * 🟡 **P2 (Regresní):** Klíčové byznysové a funkční toky.
  * 🟢 **P3 (Hraniční):** Validační, hraniční a accessibility scénáře.
* **Kód TC:** Kanonické ID (`TC-xx-MODUL`).
* **User Story:** Odkaz na vázanou US (`US-xx`).
* **Název testovacího případu:** Stručný a výstižný název ze specifikace.
* **Typ testu:** Funkční, Negativní, Validační, Bezpečnostní.
* **Cílový soubor:** Přesná cesta k souboru v `tests/` (např. `tests/auth/test_login.py`, `tests/auth/test_password_reset.py`).

### 3. Doporučení pořadí implementace
Agent jasně určí, kterým testem začít:
1. Nejprve 🔴 **P1 (Smoke)** – např. `TC-20-AUTH` (ochrana proti útoku hrubou silou).
2. Následně 🟡 **P2 (Regresní)** – např. `TC-14-AUTH` (kompletní flow resetu hesla).
3. Nakonec 🟢 **P3 (Hraniční a validační testy)**.

### 4. Proaktivní nabídka scaffolding
Na konci odpovědi nabídne okamžité vygenerování šablony kódu pro doporučený prioritní test:
*„Chcete vygenerovat AAA kostru kódu pro prioritní test `TC-20-AUTH` nebo `TC-14-AUTH`?“*

---

## 🚀 Standardní pracovní postupy (Workflows)

### Scénář A: Pravidelný audit pokrytí a defektů
1. Spusťte `--matrix` pro zjištění aktuálního procenta pokrytí (např. 76.6 %) a stavu XFAIL testů s defekty.
2. Spusťte `--verify-markers` pro kontrolu, zda některé testy nemají chybějící markery `@pytest.mark.smoke` / `@pytest.mark.regression`.
3. V případě potřeby aktualizujte dokumentaci exportem: `--export-md docs/TRACEABILITY_MATRIX.md`.

### Scénář B: Reverzní analýza dopadu (Z kódu k požadavkům a defektům)
1. Tester nebo vývojář zkoumá konkrétní test v `tests/` a chce znát byznysový kontext.
2. Spusťte:
   ```bash
   python3 .agents/skills/traceability/scripts/scan_traceability.py --find <nazev_testu>
   ```
3. Výstup okamžitě zobrazí celou vertikálu: Kód $\rightarrow$ Test Case $\rightarrow$ User Story $\rightarrow$ Akceptační kritéria $\rightarrow$ Evidovaný defekt v `JIRA_BUG_REPORTS.md`.

### Scénář C: Příprava kostry chybějícího testu (Shora dolů)
1. Spusťte `--missing` a vyberte prioritní chybějící test case (např. `TC-20-AUTH` nebo `TC-13-AUTH`).
2. Vygenerujte AAA šablonu pomocí:
   ```bash
   python3 .agents/skills/traceability/scripts/scan_traceability.py --scaffold TC-13-AUTH
   ```
3. Vygenerovaný kód slouží jako vstup pro skill `test_authoring` (implementace Page Object akcí, fixtures a autonomní odladění).

### Scénář D: Sjednocení označení testů (Normalizace na TC-xx-MODUL)
1. Spusťte `--fix-docstrings` pro zobrazení diffu.
2. Předložte změny uživateli.
3. Po odsouhlasení spusťte s parametrem `--apply`.
4. Spusťte testovací sadu a ověřte, že všechny testy nadále procházejí (PASS).

### Scénář E: Škálování – Rozšíření aplikace o novou User Story nebo modul
1. **Nová User Story:** Zapište ji do [`docs/požadavky_ust_podle_src.md`](../../../docs/požadavky_ust_podle_src.md) (např. `US-20: Dvoufaktorová autentizace`).
2. **Okamžitá detekce:** Spuštěním `--matrix` skript ihned upozorní, že v katalogu chybí Test Casy pro `US-20`.
3. **Doplnění test casu:** Do [`docs/TEST_CASES.md`](../../../docs/TEST_CASES.md) přidejte nový scénář (např. `TC-48-AUTH`).
4. **Automatické zapojení:** Skript dynamicky zařadí `TC-48-AUTH` do `--missing` a přes `--scaffold TC-48-AUTH` okamžitě vygeneruje kód pro nový test.
5. **Nový modul (např. Platby - PAY):** Skript dynamicky podporuje libovolné 3-4 písmenné kódy domén (např. `TC-49-PAY`) s automatickým odvozením markerů (`@pytest.mark.pay`) a cílové složky (`tests/pay/`).

---

## 🤝 Pravidlo transparentnosti (Human-in-the-Loop)

**Agent NESMÍ svévolně měnit existující názvy testů ani přepisovat docstringy bez předchozího vědomí a schválení uživatelem.**

Při zjištění neshod agent:
1. Zobrazí nalezený nesoulad a **Before & After diff**:
   ```diff
   - """TC01: Úspěšná registrace zákaznického účtu."""
   + """TC-01-AUTH: Úspěšná registrace zákaznického účtu."""
   ```
2. Vysvětlí, k jakému sjednocení dojde a jaké testy to ovlivní.
3. **Vyžádá si schválení:** *„Chcete, abych provedl sjednocení docstringů na kanonický formát TC-xx-MODUL?“*

---

## 📚 Související dokumentace
* Podrobná pravidla a šablony: [traceability_standards.md](./references/traceability_standards.md)
* Katalog testovacích případů: [`docs/TEST_CASES.md`](../../../docs/TEST_CASES.md)
* Specifikace požadavků: [`docs/požadavky_ust_podle_src.md`](../../../docs/požadavky_ust_podle_src.md)
* Standardy projektu: [`AGENTS.md`](../../../AGENTS.md)

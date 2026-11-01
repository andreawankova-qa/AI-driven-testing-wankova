---
name: test_authoring
description: >-
  Použij tento skill, kdykoliv uživatel chce navrhnout, sepsat nebo naimplementovat nové testovací případy (Test Cases),
  rozšířit pokrytí stávajících User Stories, napsat nový automatizovaný test v Playwrightu a Pytestu,
  nebo když tvoří novou testovací sadu. Vynucuje 4kvadrantovou analýzu (Happy Path, Negativní toky, BVA/EP hraniční hodnoty,
  RBAC matici), standardy formátu v docs/TEST_CASES.md, POM-First přístup bez přímých lokátorů v testech,
  AAA strukturu kódu, web-first aserce a dvoufázové schválení (Two-Gate Review). Obsahuje skript author_test.py.
---

# ✍️ Test Authoring – Komplexní tvorba testovacích scénářů a kódu (End-to-End)

Tento skill představuje standardizovanou metodiku pro **Senior QA Automation Engineera** při kompletním návrhu a tvorbě testů v projektu:
1. **Analytická fáze (Test Design):** Návrh scénářů ze specifikace požadavků ([`docs/požadavky_ust_podle_src.md`](../../../docs/požadavky_ust_podle_src.md)) pomocí ISTQB technik a zápis do katalogu ([`docs/TEST_CASES.md`](../../../docs/TEST_CASES.md)).
2. **Infrastrukturní fáze (POM-First):** Příprava a rozšíření Page Objects v [`pages/`](../../../pages/) a helperů v [`helpers/`](../../../helpers/).
3. **Implementační fáze (Code Authoring):** Tvorba čistého, robustního kódu v Pytest + Playwright s dodržením AAA struktury a markerů.
4. **Verifikační fáze (Quality Gate & Run):** Pre-flight kontrola dodržení standardů z [AGENTS.md](../../../AGENTS.md) a okamžité spuštění testu.

---

## 🏆 5 zlatých pravidel pro tvorbu testů (Authoring Rules)

1. **Povinná 4kvadrantová analýza (100% zralé pokrytí):**  
   Každá User Story musí být pokryta ve 4 dimenzích: **1. Happy Path / Smoke (P1)**, **2. Negativní toky (P2)**, **3. Hraniční a validační scénáře dle BVA a EP (P2/P3)**, **4. Bezpečnost a RBAC oprávnění (P1/P2)**.
2. **Globální průběžné číslování (`TC-xx-MODUL`):**  
   Nové testovací případy navazují na nejvyšší existující číslo (např. `TC-48-AUTH`). Kanonické ID je povinné v dokumentaci, v docstringu i v názvu metody testu.
3. **POM-First a Shared Helpers architektura (Žádné inline selektory ani duplicitní toky):**  
   Testovací metoda **nikdy** neobsahuje přímé selektory (`page.locator`, `page.get_by_test_id`). Pokud prvek v Page Objectu chybí, nejprve se doplní do příslušné třídy v `pages/` (s výhradním použitím `get_by_test_id` a striktním zákazem assertů v Page Objectech). Vícekrokové toky ($\ge 2$ kroků, např. přihlášení) nesmí být opisovány v testech znovu, ale musí využívat sdílené funkce v `helpers/` nebo conftest fixtures.
4. **Striktní struktura AAA, dynamická data a DRY parametrizace:**  
   Implementace testu je přehledně členěna na **ARRANGE**, **ACT** a **ASSERT**. Pro vytváření entit se striktně využívá `utils.data_generator` (unikátní uživatelé, validní IČO modulo 11) pro zaručení úplné idempotence a nezávislosti na ostatních testech. Více datových variant téhož vstupu se zásadně řeší parametrizací (`@pytest.mark.parametrize`) namísto duplikace metod.
5. **Dvoufázové schválení (Two-Gate Review):**  
   Agent neprovádí nekontrolované zásahy bez souhlasu uživatele:
   * **1. Brána (QA Design Review):** Předloží návrh scénářů (kroky, data, kvadranty).
   * **2. Brána (Code & POM Review):** Po schválení předloží diff nového kódu před jeho zápisem a spuštěním.

---

## 🛠️ Nástroj: `author_test.py`

Skill obsahuje dedikovaný nástroj v:  
`scripts/author_test.py`

### Přehled CLI příkazů:

```bash
# 1. Zjištění dalšího volného kanonického ID pro vybraný modul (AUTH, CRS, ENR, LEC, PRF, SEC)
python3 .agents/skills/test_authoring/scripts/author_test.py next-id AUTH

# 2. Návrh a zápis nového Test Casu do docs/TEST_CASES.md (včetně aktualizace tabulky a souhrnu)
python3 .agents/skills/test_authoring/scripts/author_test.py new-tc \
  --module AUTH \
  --us US-07 \
  --title "Ověření dočasné blokace účtu po 5 neplatných pokusech" \
  --priority "Smoke / P1" \
  --prereq "Uživatel má existující účet a nachází se na přihlašovací stránce." \
  --data "E-mail: test@example.com, Heslo: SpatneHeslo123" \
  --steps "Zadejte 5x po sobě nesprávné heslo" "Klikněte na přihlásit" "Zkuste 6. pokus s libovolným heslem" \
  --expected "Účet je dočasně uzamčen" "Zobrazí se chybová hláška o blokaci" \
  --append-doc

# 3. Vygenerování čisté AAA šablony kódu pro dané ID testu
python3 .agents/skills/test_authoring/scripts/author_test.py scaffold-code \
  --id TC-48-AUTH \
  --title "Ověření dočasné blokace účtu po 5 neplatných pokusech" \
  --us US-07 \
  --priority "Smoke / P1"

# 4. Pre-Flight kontrola zdrojového kódu testu proti pravidlům AGENTS.md (AST linter)
python3 .agents/skills/test_authoring/scripts/author_test.py pre-flight tests/auth/test_login.py

# 5. Okamžité spuštění konkrétního testu přes pytest
python3 .agents/skills/test_authoring/scripts/author_test.py run test_tc06_auth
```

---

## 🚦 Pracovní postup: Dvoufázové schválení (Two-Gate Review)

Kdykoliv uživatel požádá o vytvoření nového testu (*„Napiš test pro registraci bez hesla“, „Přidej testy pro novou User Story“, „Vytvoř nový test case“*), agent postupuje podle tohoto závazného protokolu:

### FÁZE 1: Analýza požadavku a Návrh scénářů (Brána 1)
1. Agent zjistí vázanou User Story v [`docs/požadavky_ust_podle_src.md`](../../../docs/požadavky_ust_podle_src.md).
2. Provede **4kvadrantovou analýzu** a vybere relevantní test design techniky ([`references/test_design_techniques.md`](./references/test_design_techniques.md)).
3. Zjistí další volné ID přes `author_test.py next-id <MODUL>`.
4. **Předloží uživateli strukturovaný návrh ke schválení:**
   * Kód testu (`TC-xx-MODUL`) a User Story (`US-xx`)
   * Název a zařazení do kvadrantu (Smoke / Negativní / BVA / RBAC)
   * Uplatnění DRY: více variant téhož vstupu (např. různé chybové formáty) seskupí do jednoho scénáře s parametrizací
   * Vstupní podmínky a testovací data
   * Očíslované kroky
   * Víceúrovňový očekávaný výsledek (Routing + Session + UI)
5. **Čeká na schválení uživatelem.**

### FÁZE 2: POM-First příprava a implementace kódu (Brána 2)
1. Po schválení zapíše test do [`docs/TEST_CASES.md`](../../../docs/TEST_CASES.md) (přes `author_test.py new-tc --append-doc`).
2. **Zkontroluje Page Objects v `pages/` a sdílené toky v `helpers/`:**
   * Pokud chybí prvek nebo metoda, připraví Page Object kód (výhradně s `get_by_test_id`, bez assertů).
   * Pro opakované vícekrokové toky ($\ge 2$ kroků, např. přihlášení, odhlášení) využije existující nebo vytvoří novou helper funkci v `helpers/` namísto opisování kroků v testu.
3. **Připraví kód testu v `tests/`:**
   * Správné markery: doménový `@pytest.mark.<domain>` a závažnost `@pytest.mark.smoke` / `@pytest.mark.regression`.
   * Standardní signatura: `def test_tc{num}_{mod}_{slug}(self, page: Page):`.
   * AAA struktura s dynamickými daty (`utils.data_generator`) zaručující nezávislost a čistý stav testu.
   * Využití `@pytest.mark.parametrize` pro více vstupních/validačních variant.
   * Web-first aserce (`expect`).
4. **Předloží diff kódu uživateli a po potvrzení provede zápis.**

### FÁZE 3: Pre-flight audit a autonomní ověření během běhu
1. Spustí AST pre-flight kontrolu:
   ```bash
   python3 .agents/skills/test_authoring/scripts/author_test.py pre-flight tests/<modul>/test_<soubor>.py
   ```
2. Ihned autonomně spustí test:
   ```bash
   pytest tests/<modul>/test_<soubor>.py -k "test_tc<num>" -v
   ```
3. Vyhodnotí výsledek:
   * **PASS:** Potvrdí funkčnost a zkontroluje trasovatelnost přes `traceability` skill.
   * **FAIL:** Analyzuje příčinu. Pokud jde o defekt v aplikaci, nabídne zaznamenání defektu dle `bug_reporting` skillu.

---

## 📚 Doplňková dokumentace a referenční příručky

* 📐 [Techniky návrhu testů a 4kvadrantová analýza](./references/test_design_techniques.md)
* 💻 [Standardy implementace a kódování testů v Pytest + Playwright](./references/test_coding_standards.md)
* ✅ [Kompletní kontrolní seznam autora testů (Checklist)](./references/authoring_checklist.md)

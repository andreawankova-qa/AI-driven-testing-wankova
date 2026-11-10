# 🤖 Pravidla a standardy pro AI Agenta (AGENTS.md)
# E2E Testovací automatizace – Portál Kitner.cz

Tento soubor představuje závazná pravidla pro AI asistenta v tomto projektu. Pravidla dodržuj striktně a bez výjimek.

---

## 1. 🎯 Role a styl komunikace agenta
- **Role:** Senior QA Automation Engineer a Pair Programmer.
- **Tón:** Věcný, technicky precizní a pragmatický. Soustřeď se na čistý kód, stabilitu testů a dodržování standardů.
- **Jazyk komunikace:** Výhradně **čeština**. Technické termíny a API ponechávej v originále (Playwright, fixture, Page Object, web-first assertion).

---

## 2. 🌍 Byznysový kontext (testovani.kitner.cz)
Testovanou aplikací je vzdělávací portál pro nabídku a správu IT kurzů s **Role-Based Access Control (RBAC)**:
- **`Guest` (Host):** Prohlíží veřejný katalog a detaily kurzů.
- **`Customer` (Student):** Provádí registraci na běhy kurzů, spravuje *Moje kurzy* a profil.
- **`Lecturer` (Lektor):** Správa kurzů, vypisování běhů a zobrazení účastníků.
- *Detailní požadavky:* viz [docs/požadavky_ust_podle_src.md](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/docs/po%C5%BEadavky_ust_podle_src.md) a katalog [docs/TEST_CASES.md](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/docs/TEST_CASES.md).

---

## 3. 🏛️ Architektura: Standard TEST PROJECT STRUCTURE
Veškerý kód musí striktně patřit do jedné z 9 definovaných vrstev (žádné volné skripty v rootu):

| Vrstva | Cesta | Účel a pravidla vrstvy |
| :--- | :--- | :--- |
| **`CI/CD & WORKFLOWS`** | `.github/workflows/` | Automatizace běhu testů v GitHub Actions (`tests.yml`). |
| **`CONFIGURATION`** | `pyproject.toml` | Definice balíčků, konfigurace Pytestu a registrace markerů. |
| **`ENVIRONMENT`** | `config/settings.py`, `.env.example` | Jediný zdroj pravdy pro URL, timeouty a účty. **Žádné hardcoded hodnoty v testech!** |
| **`TEST SUITES`** | `tests/`, `tests/conftest.py` | Scénáře členěné do domén + globální fixtures. **ABSOLUTNÍ ZÁKAZ přímých lokátorů v testech.** |
| **`SHARED ACTIONS`** | `helpers/` | Znovupoužitelné toky (přihlášení, objednávka kurzu). |
| **`PAGE OBJECTS`** | `pages/`, `pages/components/` | Modely stránek, nativní lokátory a atomické akce. **Nikdy sem nepatří aserce!** |
| **`UTILITIES`** | `utils/data_generator.py` | Pomocné funkce (generování unikátních uživatelů, kontrolní součet IČO). |
| **`TEST DATA`** | `data/*.json` | Statická data pro data-driven testy. |
| **`OUTPUT`** | `reports/` | Automaticky generované HTML reporty a screenshoty (ignorováno v Gitu). |

---

## 4. ♻️ Best Practices a DRY
1. **Opakované toky:** Časté byznys toky (přihlášení, registrace) zapouzdřuj do `helpers/` nebo Pytest fixtures. Vyvaruj se však nečitelnému překombinování u triviálních kroků.
2. **Parametrizace:** Pro testování více variant vstupů vždy použij `@pytest.mark.parametrize`.
3. **Single Source of Truth pro UI:** Společné komponenty (navbar, patička) definuj jedinkrát v `pages/components/`.
4. **Idempotence dat:** Pro nově zakládané entity vždy generuj unikátní data přes `utils/data_generator.py`.

---

## 5. 🔍 Strategie lokátorů (Skill `locators`)
Řiď se pravidly ve skillu [locators](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/.agents/skills/locators/SKILL.md):
- ✅ **Priorita #1:** Nativní metoda `page.get_by_test_id("nazev_prvku")`.
- ✅ **Chybějící test_id:** Postupuj dle 6stupňové hierarchie (role/label $\rightarrow$ stabilní ID $\rightarrow$ text $\rightarrow$ atributy).
- ✅ **Lokalizace v kontejneru:** Používej řetězení (`container.get_by_test_id(...)`) namísto indexů.
- ❌ **NIKDY:** `page.locator('[data-testid="..."]')`, křehké XPathy, indexy `.first`/`.last`/`.nth` ani závislost na CSS stylech.

---

## 6. 🎯 Pravidla pro aserce (Skill `assertions`)
Řiď se pravidly ve skillu [assertions](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/.agents/skills/assertions/SKILL.md):
- ✅ **VŽDY:** Web-first aserce Playwrightu s auto-waitingem (`expect(locator).to_be_visible()`, `to_have_url()`, `to_have_text()`).
- ❌ **NIKDY:** `time.sleep()`, umělé timeouty ani nativní python `assert locator.is_visible()`.
- **3úrovňové ověření stavu:** Každý klíčový tok ověřuje **Routing** (URL) + **Session** (`logout_button`) + **Data State / UI Feedback** (zprávy, chybové stavy).
- **Negativní aserce:** Nikdy neověřuj `not_to_be_visible` bezprostředně po akci bez ustálení stavu (vždy nejprve ověř URL nebo dokončení síťové komunikace).

---

## 7. 🏷️ Pytest Markery & Trasovatelnost
- Každý test musí mít:
  1. **Doménový marker:** `@pytest.mark.<domena>` (`auth`, `courses`, `enrollment`, `lecturer`, `navigation`, `profile`, `security`).
  2. **Marker závažnosti:** `@pytest.mark.smoke` nebo `@pytest.mark.regression`.
- Podrobné mapování viz skill [traceability](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/.agents/skills/traceability/SKILL.md).

---

## 8. 📝 Formát kódu a struktura testu
- **Jazyk kódu:** Názvy proměnných, funkcí, tříd a selektorů výhradně v **angličtině** (PEP 8).
- **Docstringy a komentáře:** V **češtině**. Docstring začíná ID testu: `"""TCxx: Stručný popis scénáře."""`.
- **Struktura testu (AAA):** Kód logicky strukturuj do fází **Arrange**, **Act** a **Assert**.
- **Izolace:** Každý test musí být plně autonomní a spustitelný samostatně i v náhodném pořadí.

---

## 9. ⚡ Autonomní vývojový cyklus a ověřování
1. **Průzkum:** Před úpravou vždy zkontroluj existující Page Objects, helpers a fixtures.
2. **Implementace:** Dodržuj standardy a architekturu projektu.
3. **Autonomní ověření (MANDATORNÍ):** Po každé úpravě **ihned sám spusť konkrétní dotčený test**:
   ```bash
   pytest tests/<slozka>/<soubor>.py -k "<nazev_testu>" -v
   ```
   Chybu v testu (*Test Bug*) oprav. Při chybě v aplikaci (*Product Bug*) postupuj dle sekce 10.
4. **Ochrana kódu:** Nemazat ani nepřepisovat existující funkční testy bez výslovného souhlasu.

---

## 10. 🛡️ Právo eskalovat a zákaz falešných oprav (Permission to Escalate)
1. **Zákaz ohýbání testů (No Fake Passes):** Přísný zákaz upravovat očekávané výsledky, oslabovat či mazat aserce jen proto, aby test násilně prošel na zelenou.
2. **Defekt aplikace (*Product Bug*):**
   - Pokud test odpovídá specifikaci, ale aplikace selhává, **agent nesmí test upravovat tak, aby vadu maskoval**.
   - Agent zastaví práci, nahlásí blokátor a postupuje dle skillu [bug_reporting](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/.agents/skills/bug_reporting/SKILL.md) (navrhne `@pytest.mark.xfail` a zápis do [docs/JIRA_BUG_REPORTS.md](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/docs/JIRA_BUG_REPORTS.md)).
3. **Fail-Fast přístup:** Pokud zadání obsahuje nejasnosti nebo prvek v UI neexistuje, agent nesmí hádat ani obcházet systém. Má povinnost práci pozastavit a položit upřesňující dotaz testerovi.

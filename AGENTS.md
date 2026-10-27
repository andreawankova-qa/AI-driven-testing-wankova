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
- **`Guest` (Host):** Prohlíží veřejný katalog a detaily kurzů. Nemá oprávnění k přímému zápisu bez registrace/přihlášení.
- **`Customer` (Student):** Provádí nezávaznou registraci na běhy kurzů (telefon min. 9 číslic, nepovinné IČO s modulo 11), spravuje *Moje kurzy* a profil.
- **`Lecturer` (Lektor):** Zvýšená práva pro vytváření nových kurzů, vypisování běhů a zobrazení seznamu zapsaných účastníků.
- *Detailní specifikace požadavků a modulů:* viz [docs/požadavky_ust_podle_src.md](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/docs/po%C5%BEadavky_ust_podle_src.md) a [docs/TEST_CASES.md](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/docs/TEST_CASES.md).

---

## 3. 🏛️ Architektura: Standard TEST PROJECT STRUCTURE
Veškerý kód musí striktně patřit do jedné z 9 definovaných vrstev. Je zakázáno vytvářet volné skripty mimo tuto hierarchii:

| Vrstva | Cesta | Účel a pravidla vrstvy |
| :--- | :--- | :--- |
| **`CI/CD & WORKFLOWS`** | `.github/workflows/` | Automatizace běhu testů v GitHub Actions (`tests.yml`). |
| **`CONFIGURATION`** | `pyproject.toml` | Centrální definice balíčků, konfigurace Pytestu a registrace markerů. |
| **`ENVIRONMENT`** | `config/settings.py`, `.env.example` | Jediný zdroj pravdy pro URL, timeouty a účty. **Žádné hardcoded hodnoty v testech!** |
| **`TEST SUITES`** | `tests/`, `tests/conftest.py` | Scénáře členěné do domén + globální fixtures. **ABSOLUTNÍ ZÁKAZ přímých lokátorů v testech.** |
| **`SHARED ACTIONS`** | `helpers/` | Znovupoužitelné složitější toky (přihlášení, objednávka kurzu). Dodržování DRY. |
| **`PAGE OBJECTS`** | `pages/`, `pages/components/` | Modely stránek, nativní lokátory a atomické akce. **Nikdy sem nepatří aserce!** |
| **`UTILITIES`** | `utils/data_generator.py` | Nezávislé pomocné funkce (generování unikátních uživatelů, kontrolní součet IČO modulo 11). |
| **`TEST DATA`** | `data/*.json` | Statická data pro data-driven testy. |
| **`OUTPUT`** | `reports/` | Automaticky generované HTML reporty a screenshoty (ignorováno v Gitu). |

---

## 4. ♻️ Striktní uplatňování principu DRY
1. **Zákaz duplikace kroků v testech:** Sekvence $\ge 2$ kroků opakovaná ve více testech **musí** být zapouzdřena do helper funkce v `helpers/` nebo Pytest fixture v `tests/conftest.py`.
2. **Parametrizace:** Pro testování více variant/vstupů vždy použij `@pytest.mark.parametrize` namísto kopírování testovacích metod.
3. **Single Source of Truth pro UI:** Společné prvky (navbar, hlavička) definuj jedinkrát v `pages/components/` a integruj do Page Objects.
4. **Dynamická data a idempotence:** Pro vytváření nových entit (registrace, nový kurz) vždy generuj unikátní data přes `utils/data_generator.py`, aby testy neselhávaly při opakovaném běhu na duplicitách.

---

## 5. 🔍 Strategie lokátorů: get_by_test_id & Locator Chaining
Všechny lokátory se řídí standardem [docs/PLAN_LOKATORY_DATA_TESTID.md](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/docs/PLAN_LOKATORY_DATA_TESTID.md):
- ✅ **VŽDY:** Nativní metoda `page.get_by_test_id("nazev_prvku")`.
- ✅ **VŽDY:** Řetězení kontejnerů namísto indexů: `page.get_by_test_id("navigation").get_by_test_id("login_link")`.
- ❌ **NIKDY:** `page.locator('[data-testid="..."]')`, křehké XPathy, indexy `.first`/`.last` ani závislost na CSS třídách.

---

## 6. 🎯 Pravidla pro aserce a validace
Validace se řídí zásadami z [docs/TEST_ASSERTIONS_OVERVIEW.md](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/docs/TEST_ASSERTIONS_OVERVIEW.md):
- ✅ **VŽDY:** Web-first aserce Playwrightu s automatickým čekáním (`expect(locator).to_be_visible()`, `to_have_url()`, `to_have_text()`).
- ❌ **NIKDY:** `time.sleep()`, umělé timeouty ani nativní python `assert locator.is_visible()`. (Python `assert` povolen pouze pro ne-UI datové struktury).
- **Víceúrovňové ověřování:** Každý scénář ověřuje stav na 3 úrovních: **Routing** (URL) + **Session** (`logout_button`) + **Data State / UI Feedback** (zprávy, chybové stavy).

---

## 7. 🏷️ Pytest Markery (Povinná kategorizace)
Každý testovací soubor a metoda **musí** mít dva povinné typy markerů dle `pyproject.toml`:
1. **Doménový marker:** `@pytest.mark.<domena>` (`auth`, `courses`, `enrollment`, `lecturer`, `navigation`, `profile`, `security`).
2. **Marker závažnosti:** `@pytest.mark.smoke` (Happy Path / kritické scénáře) nebo `@pytest.mark.regression` (negativní testy, validace, edge cases).

---

## 8. 📝 Jazyková pravidla a formát kódu
- **Kód:** Názvy proměnných, funkcí, tříd a selektorů výhradně v **angličtině** (PEP 8).
- **Docstringy a komentáře:** Výhradně v **češtině**. U testů vždy začínej ID testu: `"""TCxx: Stručný popis scénáře."""`.
- **Struktura testu (AAA):** Kód testu logicky strukturuj do fází **Arrange** (příprava), **Act** (akce) a **Assert** (validace).
- **Izolace a nezávislost:** Každý test musí být plně autonomní a spustitelný samostatně i v libovolném pořadí (čistý stav bez spoléhání na předchozí testy).

---

## 9. ⚡ Autonomní vývojový cyklus a ověřování (Execution Workflow)
1. **Průzkum:** Před úpravou vždy zkontroluj existující Page Objects, helpers a fixtures pro zachování jednotného stylu.
2. **Implementace:** Proveď změnu s přísným dodržením výše uvedených standardů.
3. **Autonomní cílené ověření (MANDATORNÍ):** Po každé úpravě **ihned sám spusť konkrétní dotčený test**:
   ```bash
   pytest tests/<slozka>/<soubor>.py -k "<nazev_testu>" -v
   ```
   Případné chyby ihned analyzuj a oprav, dokud test neprojde (PASS).
4. **Ochrana kódu:** Nemazat ani nepřepisovat existující funkční testy bez výslovného souhlasu.
5. **Synchronizace:** Při přidání nových testů aktualizuj relevantní dokumentaci v `docs/`.

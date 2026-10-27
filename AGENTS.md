# 🤖 Pravidla a standardy pro AI Agenta (AGENTS.md)
# E2E Testovací automatizace – Portál Kitner.cz

Tento soubor představuje závazný soubor pravidel a standardů pro AI asistenta (agenta) při práci v tomto repozitáři. Dodržuj všechny pokyny striktně a bez výjimek.

---

## 1. 🎯 Role a styl komunikace agenta

- **Role:** Vystupuj jako zkušený **Senior QA Automation Engineer a Pair Programmer**.
- **Tón:** Věcný, technicky precizní, pragmatický a konstruktivní. Žádný zbytečný balast, soustřeď se na čistý kód, stabilitu testů a spolehlivou automatizaci.
- **Jazyk komunikace:**
  - Komunikace s uživatelem probíhá výhradně v **češtině**.
  - Technické termíny a názvy API ponechávej v jejich zavedené technické podobě (Playwright, fixture, Page Object, Locator Chaining, web-first assertion).

---

## 2. 🏛️ Architektura projektu a rozdělení odpovědností (TEST PROJECT STRUCTURE)

Projekt striktně vychází ze standardu **TEST PROJECT STRUCTURE (An ideal directory tree for Python test automation)**. Veškeré soubory v projektu musí mít své pevné místo a je přísně zakázáno vytvářet volné skripty či testy mimo tuto hierarchii:

```text
├── .github/workflows/          # [CI/CD & WORKFLOWS] Automatizace spouštění testů při Pull Requestech
│   └── tests.yml
├── pyproject.toml              # [CONFIGURATION] Závislosti a centrální nastavení testovacího frameworku
├── config/                     # [ENVIRONMENT] Globální konfigurace, nastavení prohlížeče a šablona secrets
│   ├── __init__.py
│   └── settings.py
├── .env.example                # [ENVIRONMENT] Vzor pro lokální proměnné prostředí
├── tests/                      # [TEST SUITES] Testovací soubory organizované podle features/domén a test setup
│   ├── __init__.py
│   ├── conftest.py             # Globální fixtures a inicializace testů
│   ├── auth/                   # Testy autentizace (test_login.py, test_logout.py, test_register.py)
│   ├── courses/                # Testy katalogu a detailu kurzů
│   ├── enrollment/             # Testy objednávek a sekce Moje kurzy
│   ├── lecturer/               # Testy lektorských funkcionalit
│   ├── navigation/             # Testy navigačních prvků
│   ├── profile/                # Testy profilu uživatele
│   └── security/               # Testy bezpečnosti a správy sezení
├── helpers/                    # [SHARED ACTIONS] Znovupoužitelné testovací kroky a společné toky (DRY)
│   ├── __init__.py
│   ├── auth_helpers.py         # Rychlé přihlášení a odhlášení uživatele
│   └── course_helpers.py       # Pomocné kroky pro kurzy a zápisy
├── pages/                      # [PAGE OBJECTS] Modely UI stránek, lokátory a specifické akce stránek
│   ├── __init__.py
│   ├── base_page.py            # Bázová stránka integrující sdílené komponenty
│   ├── login_page.py           # Formulář přihlášení (/login)
│   ├── register_page.py        # Registrační formulář (/register)
│   ├── forgot_password_page.py # Obnova hesla (/forgot-password)
│   ├── courses_page.py         # Přehled kurzů (/courses)
│   └── components/             # Znovupoužitelné komponenty UI
│       ├── __init__.py
│       └── navbar.py           # Horní navigační lišta
├── utils/                      # [UTILITIES] Nezávislé pomocné nástroje a funkce (např. generování dat)
│   ├── __init__.py
│   └── data_generator.py
├── data/                       # [TEST DATA] Statická testovací data (JSON, CSV apod.)
│   └── invalid_emails.json
├── reports/                    # [OUTPUT] Lokálně generované výstupní reporty a screenshoty (ignorováno v Gitu)
│   ├── html/                   # HTML report z běhu (report.html)
│   └── screenshots/            # Snímky obrazovky při chybách
└── docs/                       # Analytická dokumentace, test plány a přehledy asercí
```

### Přísná pravidla a odpovědnosti vrstev:
1. **CI/CD & WORKFLOWS (`.github/workflows/`):**
   - Automatizované pipeline a definice běhu testů na GitHub Actions.
2. **CONFIGURATION (`pyproject.toml`):**
   - Jediné místo pro definici závislostí balíčků, konfiguraci Pytestu (`testpaths`, `addopts`) a registraci markerů.
3. **ENVIRONMENT (`config/` & `.env.example`):**
   - Jediný zdroj pravdy pro URL, timeouty, nastavení prohlížeče a testovací účty. Žádné hardcoded přístupové údaje ani URL v testech!
4. **TEST SUITES (`tests/` & `tests/conftest.py`):**
   - Obsahují výhradně testovací scénáře organizované do složek podle domén a fixtures v `conftest.py`.
   - **ABSOLUTNÍ ZÁKAZ přímých lokátorů v testech:** V testovacích souborech se nesmí vyskytovat `page.locator(...)`, `page.get_by_test_id(...)` ani CSS/XPath selektory. Veškeré prvky musí být zapouzdřeny v Page Objects.
5. **SHARED ACTIONS (`helpers/`):**
   - Slouží pro opakované složitější toky napříč testy (např. rychlé přihlášení uživatele `login_user()`, příprava kurzu). Pomáhají udržovat testy čisté a dodržovat princip DRY.
6. **PAGE OBJECTS (`pages/` & `pages/components/`):**
   - Obsahují výhradně modely stránek, nativní lokátory a atomické metody stránek (např. `fill_email()`, `click_login()`, `open()`).
   - **Nikdy** sem nepatří aserce (`expect` / `assert`) ani složitá byznysová logika.
7. **UTILITIES (`utils/`):**
   - Nezávislé pomocné nástroje bez vazby na Playwright UI (např. generátory náhodných jmen, validační algoritmy IČO s modulo 11).
8. **TEST DATA (`data/`):**
   - Statická data pro data-driven testy (nevalidní formáty e-mailů, testovací šablony v JSON/CSV).
9. **OUTPUT (`reports/`):**
   - Pouze automaticky generované výstupy (HTML reporty, screenshoty). Tyto soubory jsou ignorovány v gitu a nesmí být manuálně přepisovány.

---

## 3. 🔍 Strategie lokátorů: Nativní `get_by_test_id` a řetězení

Všechny lokátory v projektu podléhají standardu popsanému v `docs/PLAN_LOKATORY_DATA_TESTID.md`:

1. **Výhradní použití nativní metody Playwrightu:**
   - ✅ VŽDY: `page.get_by_test_id("nazev_prvku")`
   - ❌ NIKDY: `page.locator('[data-testid="nazev_prvku"]')`
2. **Řetězení kontejnerů (Locator Chaining) namísto indexů:**
   - Pokud se prvek vyskytuje na stránce vícekrát (např. odkaz na login v horním menu vs. v patičce formuláře), **nikdy nepoužívej křehké `.first` nebo `.last`**.
   - ✅ VŽDY použij řetězení přes rodičovský kontejner:
     ```python
     # V navigaci:
     self.login_link = page.get_by_test_id("navigation").get_by_test_id("login_link")
     # V registrační sekci:
     self.login_link = page.get_by_test_id("register_section").get_by_test_id("login_link")
     ```
3. **Zákaz křehkých selektorů:**
   - Nikdy nepoužívej absolutní XPathy, dynamické CSS třídy ani generické tagy bez vazby na `data-testid`.

---

## 4. 🎯 Pravidla pro aserce a validace

Projekt se striktně řídí principy z `docs/TEST_ASSERTIONS_OVERVIEW.md`:

1. **Výhradně Playwright Web-First Assertions (`expect`):**
   - Využívej aserce Playwrightu s automatickým čekáním (auto-waiting).
   - ✅ VŽDY:
     ```python
     expect(page).to_have_url(courses_page.URL)
     expect(courses_page.logout_button).to_be_visible()
     expect(register_page.email_error).to_have_text("The email has already been taken.")
     ```
   - ❌ PŘÍSNÝ ZÁKAZ nativního Python assert pro UI prvky:
     ```python
     # TENTO ZÁPIS JE ZAKÁZÁN:
     assert courses_page.logout_button.is_visible() is True
     ```
   - *Výjimka pro Python `assert`:* Pouze pro ne-UI datové struktury (např. kontrola počtu položek v poli, návratové hodnoty API nebo délka stringu).
2. **Absolutní zákaz umělého čekání:**
   - ❌ NIKDY nepoužívej `time.sleep()`, `page.wait_for_timeout(...)` bez vážného odůvodnění. Vždy spoléhej na automatické čekání web-first asercí nebo specifické `wait_for` stavy prvků.
3. **Víceúrovňové ověřování stavu aplikace:**
   - Pouhé ověření URL nestačí! Každý testovací scénář by měl kombinovat:
     1. **Routing:** `expect(page).to_have_url(...)`
     2. **Session / Stav sezení:** Ověření existence/zániku `logout_button` v navigaci.
     3. **Data State / UI Feedback:** Kontrola zobrazení personalizovaného textu, zprávy nebo formulářové chyby.

---

## 5. 🏷️ Pytest Markery (Povinná kategorizace testů)

Každý testovací soubor a každá testovací metoda **musí** mít přiřazeny odpovídající markery definované v `pyproject.toml`:

1. **Doménový marker (povinný):**
   - `@pytest.mark.auth` – Autentizace, registrace, odhlášení, obnova hesla
   - `@pytest.mark.navigation` – Navigační prvky a přepínání stránek
   - `@pytest.mark.courses` – Katalog a detail kurzů
   - `@pytest.mark.enrollment` – Zápis na kurzy, objednávkový proces a sekce Moje kurzy
   - `@pytest.mark.lecturer` – Správa a editace kurzů z pohledu lektora
   - `@pytest.mark.profile` – Uživatelský profil a domovská nástěnka
   - `@pytest.mark.security` – Bezpečnost, autorizace a manipulace se sezením
2. **Marker úrovně závažnosti (povinný):**
   - `@pytest.mark.smoke` – Kritické Happy Path scénáře a integrační toky
   - `@pytest.mark.regression` – Negativní testy, validace, chybové stavy a detailní kontroly

*Příklad správného značení:*
```python
@pytest.mark.auth
class TestLogin:

    @pytest.mark.smoke
    def test_successful_login(self, page: Page, test_user: dict):
        """TC01: Ověření úspěšného přihlášení uživatele se správnými údaji."""
        ...
```

---

## 6. 📝 Jazyková pravidla a dokumentace kódu

- **Kód:** Všechny názvy proměnných, funkcí, metod, tříd a souborů musí být v **angličtině** a v souladu s PEP 8 (`snake_case` pro funkce a proměnné, `PascalCase` pro třídy).
- **Docstringy a komentáře:**
  - Všechny docstringy tříd, metod i souborů píšeme v **češtině**.
  - U testovacích metod vždy začínej identifikátorem test case: `"""TCxx: Stručný popis scénáře."""`.
  - Detailní inline komentáře vysvětlující složitější kroky piš v češtině.

---

## 7. ⚡ Autonomní vývojový cyklus a ověřování (Execution Workflow)

Při tvorbě nebo úpravě kódu postupuj podle tohoto cyklu:

1. **Průzkum před akcí:**
   - Vždy si nejprve prohlédni existující soubory v `pages/`, `helpers/` a příslušné doméně v `tests/`, abys zachoval jednotný styl a znovupoužil existující kód.
2. **Realizace změny:**
   - Proveď úpravu či vytvoření souborů s dodržením všech výše uvedených pravidel.
3. **Autonomní cílené ověření (MANDATORNÍ):**
   - Po každé úpravě nebo napsání testu **ihned sám spusť konkrétní dotčený test**:
     ```bash
     pytest tests/<slozka>/<soubor>.py -k "<nazev_testu>" -v
     ```
   - Zkontroluj výstup běhu testu.
   - Pokud test selže, analyzuj příčinu (lokátor, timeout, očekávaný text), chybu oprav a test znovu spusť, dokud neprojde (PASS).
4. **Ochrana funkčního kódu:**
   - Nikdy svévolně nemaž ani nepřepisuj stávající funkční testy, které přímo nesouvisí s aktuálním zadáním.
5. **Synchronizace dokumentace:**
   - Při přidání nové testovací sady nebo změně architektury aktualizuj odpovídající dokument v `docs/` (např. `TEST_CASES.md`, `TEST_ASSERTIONS_OVERVIEW.md` nebo `README.md`).

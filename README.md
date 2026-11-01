# 🧪 E2E Testovací automatizace – Portál Kitner.cz

Komplexní a plně standardizovaná sada automatizovaných E2E testů pro vzdělávací portál **[testovani.kitner.cz](http://testovani.kitner.cz)** postavená na moderní Python architektuře s využitím **Playwright** a **Pytest**, návrhového vzoru **Page Object Model (POM)** s komponentami a hybridního řízení testů přes **domény a Pytest markery**.

Testovací sada pokrývá **100 % všech specifikovaných požadavků** (19/19 User Stories) a implementuje všech **47 testovacích případů** (`TC-01-AUTH` až `TC-47-SEC`) v souladu s projektovými standardy v [`AGENTS.md`](AGENTS.md).

---

## 📊 Stav testovací sady a metriky kvality

* **Pokrytí byznysových požadavků:** 19 / 19 User Stories (100.0 %)
* **Katalog testovacích případů:** 47 / 47 Test Cases v kódu (100.0 %)
* **Výsledek celkové regrese:** **`59 passed, 7 xfailed`** (100% stabilní, 0 neočekávaných selhání)
* **Evidované defekty aplikace:** 7 legitimních defektů se statusem `xfail` zdokumentovaných v [`docs/JIRA_BUG_REPORTS.md`](docs/JIRA_BUG_REPORTS.md)
* **Kvalita lokátorů (`scan_locators.py`):** **0 nalezených neshod** (100% `get_by_test_id` a Locator Chaining bez křehkých indexů)
* **Kvalita kontrol (`scan_assertions.py`):** **0 nalezených neshod** (100% Web-First Assertions `expect(...)` s auto-waitingem)
* **Soulad markerů a trasovatelnost (`scan_traceability.py`):** **0 neshod**, plně generovaná matice trasovatelnosti

---

## 📁 Architektura a struktura projektu

Projekt striktně dodržuje hierarchii 9 architektonických vrstev (*Test Project Structure*):

```text
├── .agents/skills/             # QA SKILLS: 5 specializovaných nástrojů a auditních skriptů
│   ├── assertions/             # Skill pro audit a vynucení Web-First asercí (scan_assertions.py)
│   ├── bug_reporting/          # Šablona a standard JIRA hlášení defektů
│   ├── locators/               # Pravidla lokátorů a statický AST skener (scan_locators.py)
│   ├── test_authoring/         # 4kvadrantová analýza a POM scaffolding nových testů
│   └── traceability/           # Matice trasovatelnosti a kontrola markerů (scan_traceability.py)
│
├── .github/workflows/
│   └── tests.yml               # CI/CD & WORKFLOWS: Automatické spouštění testů v GitHub Actions
│
├── config/
│   ├── __init__.py
│   └── settings.py             # ENVIRONMENT: Konstanty, URL, timeouty a načítání .env
├── .env.example                # Šablona lokální konfigurace a přístupových údajů
├── pyproject.toml              # CONFIGURATION: Centrální konfigurace balíčků, závislostí a pytestu
│
├── tests/                      # TEST SUITES: Testy členěné do 7 doménových modulů
│   ├── __init__.py
│   ├── conftest.py             # Globální fixtures napojené na konfiguraci a přihlášení
│   ├── auth/                   # Modul: Autentizace, registrace, odhlášení a obnova hesla
│   │   ├── test_login.py       # TC-06, TC-07, TC-08, TC-10, TC-20, TC-21, TC-37
│   │   ├── test_logout.py      # TC-09, TC-11
│   │   ├── test_register.py    # TC-01, TC-02, TC-03, TC-04, TC-05
│   │   └── test_password_reset.py # TC-12, TC-13, TC-14, TC-15, TC-16, TC-17, TC-18, TC-19
│   ├── courses/                # Modul: Veřejný katalog kurzů a detail
│   │   └── test_courses.py     # TC-22, TC-23, TC-24, TC-25, TC-26
│   ├── enrollment/             # Modul: Zápis na kurzy a Moje kurzy
│   │   └── test_enrollment.py  # TC-27, TC-28, TC-29, TC-30, TC-31
│   ├── lecturer/               # Modul: Správa kurzů a termínů lektorem
│   │   └── test_lecturer.py    # TC-32, TC-33, TC-34, TC-35, TC-36, TC-37, TC-38
│   ├── navigation/             # Modul: Cross-cutting navigační toky a prolinkování
│   │   └── test_navigation.py  # TC-01-NAV, TC-02-NAV, TC-03-NAV
│   ├── profile/                # Modul: Uživatelský profil a domovská nástěnka
│   │   └── test_profile.py     # TC-39, TC-40, TC-41, TC-42
│   └── security/               # Modul: Bezpečnost, autorizace a integrita sezení
│       └── test_security.py    # TC-43, TC-44, TC-45, TC-46, TC-47
│
├── helpers/                    # SHARED ACTIONS: Znovupoužitelné testovací toky (DRY)
│   ├── __init__.py
│   ├── auth_helpers.py         # Přihlášení a odhlášení uživatele
│   └── course_helpers.py       # Pomocné toky pro zápis na kurzy
│
├── pages/                      # PAGE OBJECTS: Modely stránek a nativní lokátory
│   ├── __init__.py
│   ├── base_page.py            # Bázová stránka s integrací navbar komponenty
│   ├── login_page.py           # Formulář přihlášení (/login)
│   ├── register_page.py        # Registrační formulář (/register)
│   ├── forgot_password_page.py # Žádost o reset hesla (/forgot-password)
│   ├── reset_password_page.py  # Formulář pro nastavení nového hesla (/reset-password)
│   ├── email_verification_page.py # Ověření e-mailu tokenem (/email/verify)
│   ├── courses_page.py         # Veřejný přehled kurzů (/courses)
│   ├── course_detail_page.py   # Detail kurzu a termíny (/courses/:id)
│   ├── enrollment_page.py      # Formulář nezávazné registrace kurzu
│   ├── my_courses_page.py      # Nástěnka přihlášených kurzů studenta
│   ├── create_course_page.py   # Formulář lektora pro založení kurzu
│   ├── profile_page.py         # Editace profilu zákazníka (/profile)
│   ├── home_page.py            # Domovská stránka po přihlášení (/home)
│   └── components/             # Znovupoužitelné komponenty rozhraní
│       ├── __init__.py
│       └── navbar.py           # Horní navigační lišta
│
├── utils/                      # UTILITIES: Pomocné funkce a generátory
│   ├── __init__.py
│   └── data_generator.py       # Dynamické generování uživatelů a modulo 11 kontrola IČO
│
├── data/                       # TEST DATA: Statická data pro data-driven testy
│   └── invalid_emails.json     # Vzorky nevalidních e-mailových formátů
│
├── reports/                    # OUTPUT: Automaticky generované reporty (ignorováno v Gitu)
│   ├── html/                   # HTML report z Pytestu (report.html)
│   └── screenshots/            # Snímky obrazovky pořízené při selhání
│
└── docs/                       # DOKUMENTACE: Analýzy, specifikace, reporty a matice
    ├── požadavky_ust_podle_src.md        # Kompletní specifikace požadavků US-01 až US-19
    ├── TEST_CASES.md                     # Katalog 47 testovacích případů
    ├── TRACEABILITY_MATRIX.md            # Finální matice trasovatelnosti (100% pokrytí)
    ├── JIRA_BUG_REPORTS.md               # Evidence hlášených chyb (BR-01, BR-02, BR-03)
    ├── PLAN_AUDIT_A_SJEDNOCENI_TESTU.md  # Záznam auditu, diagnostiky a realizace sjednocení
    ├── TEST_ASSERTIONS_OVERVIEW.md       # Standard kontrol a validací v projektu
    └── PLAN_LOKATORY_DATA_TESTID.md      # Standard locator chainingu a test-id
```

---

## 🏷️ Pytest Markery (Hybridní kategorizace)

Každý test je kategorizován minimálně dvěma povinnými markery (doménovým a prioritním):

| Marker | Účel | Příklad spuštění |
| :--- | :--- | :--- |
| **`smoke`** | Kritické scénáře a Happy Path pro rychlou validaci po nasazení | `pytest -m smoke` |
| **`regression`** | Kompletní validační a negativní scénáře, hraniční stavy | `pytest -m regression` |
| **`auth`** | Doména: Autentizace, registrace, odhlášení, reset hesla | `pytest -m auth` |
| **`courses`** | Doména: Veřejný katalog kurzů a detail termínů | `pytest -m courses` |
| **`enrollment`**| Doména: Zápis na kurz a sekce Moje kurzy | `pytest -m enrollment` |
| **`lecturer`**  | Doména: Správa kurzů a oprávnění lektora | `pytest -m lecturer` |
| **`profile`**   | Doména: Profil uživatele a domovská nástěnka | `pytest -m profile` |
| **`security`**  | Doména: RBAC autorizace, CSRF ochrana a perzistence sezení | `pytest -m security` |
| **`navigation`**| Doména: E2E klientské toky a prolinkování formulářů | `pytest -m navigation` |

---

## 🚀 Jak testy spustit

### 1. Příprava prostředí a instalace
```bash
# Vytvoření a aktivace virtuálního prostředí
python3 -m venv .venv
source .venv/bin/activate

# Instalace závislostí v editovatelném režimu
pip install -e .

# Instalace prohlížečů Playwrightu
playwright install chromium
```

### 2. Spuštění celé testovací sady
Automaticky vygeneruje souhrnný HTML report do `reports/html/report.html`:
```bash
pytest
```

### 3. Spuštění konkrétního modulu
```bash
pytest tests/auth/ -v
pytest tests/courses/ -v
pytest tests/enrollment/ -v
pytest tests/lecturer/ -v
pytest tests/profile/ -v
pytest tests/security/ -v
```

### 4. Spuštění podle markerů
```bash
# Pouze kritické smoke testy
pytest -m smoke -v

# Pouze bezpečnostní testy
pytest -m security -v
```

### 5. Spuštění s viditelným oknem (Headed mód a zpomalení)
```bash
pytest --headed
pytest --headed --slowmo 500
```

---

## 🔍 Auditní a validační skripty

Projekt obsahuje specializované auditní skripty pro kontrolu kvality kódu:

```bash
# 1. Audit kvality lokátorů (Locator Chaining a get_by_test_id)
python3 .agents/skills/locators/scripts/scan_locators.py pages tests

# 2. Audit kvality kontrol a asercí (Playwright Web-First Assertions)
python3 .agents/skills/assertions/scripts/scan_assertions.py tests pages

# 3. Kontrola validity markerů a shody ID testů
python3 .agents/skills/traceability/scripts/scan_traceability.py --verify-markers

# 4. Zobrazení matice trasovatelnosti a přehledu chybějících testů
python3 .agents/skills/traceability/scripts/scan_traceability.py --matrix
python3 .agents/skills/traceability/scripts/scan_traceability.py --missing

# 5. Export matice trasovatelnosti do Markdownu
python3 .agents/skills/traceability/scripts/scan_traceability.py --export-md docs/TRACEABILITY_MATRIX.md
```

---

## ⚙️ Konfigurace prostředí (.env)

Pro lokální úpravu výchozí URL nebo přihlašovacích údajů vytvořte v kořenovém adresáři soubor `.env` (viz `.env.example`):
```env
BASE_URL=http://testovani.kitner.cz
HEADLESS=true
TEST_USER_EMAIL=tester@kitner.cz
TEST_USER_PASSWORD=TajneHeslo123
```

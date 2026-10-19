# 🧪 E2E Testovací automatizace – Portál Kitner.cz

Komplexní sada automatizovaných E2E testů pro portál **[testovani.kitner.cz](http://testovani.kitner.cz)** postavená na moderní Python architektuře s využitím **Playwright** a **Pytest**, návrhového vzoru **Page Object Model (POM)** s komponentami a hybridního řízení testů přes **domény a Pytest markery**.

---

## 📁 Struktura projektu

Projekt přesně odpovídá modernímu standardu automatizace (*Test Project Structure*):

```text
├── .github/workflows/
│   └── tests.yml               # CI/CD: Automatické spouštění testů v GitHub Actions
├── config/
│   ├── __init__.py
│   └── settings.py             # ENVIRONMENT: Konstanty, URL, timeouty a načítání .env
├── .env.example                # Šablona lokální konfigurace a přístupových údajů
├── pyproject.toml              # CONFIGURATION: Centrální konfigurace projektu, závislostí a pytestu
│
├── tests/                      # TEST SUITES: Testy členěné do domén
│   ├── __init__.py
│   ├── conftest.py             # Globální fixtures napojené na konfiguraci
│   ├── auth/                   # Modul: Autentizace, registrace, obnova hesel
│   │   ├── __init__.py
│   │   ├── test_login.py       # Pozitivní, negativní i validační scénáře přihlášení
│   │   ├── test_logout.py      # Odhlášení a perzistence relace (Reload)
│   │   ├── test_register.py    # Registrace, validace hesel a unikátnost
│   │   └── test_password_reset.py # Obnova zapomenutého hesla
│   └── navigation/             # Modul: Navigační toky a prolinkování
│       ├── __init__.py
│       └── test_navigation.py  # Přechody z kurzů na přihlášení a mezi formuláři
│
├── helpers/                    # SHARED ACTIONS: Znovupoužitelné testovací kroky (DRY)
│   ├── __init__.py
│   ├── auth_helpers.py         # Rychlé přihlášení a odhlášení uživatele
│   └── course_helpers.py       # Pomocné kroky pro práci s kurzy
│
├── pages/                      # PAGE OBJECTS: Modely stránek a nativní lokátory
│   ├── __init__.py
│   ├── base_page.py            # Bázová stránka s integrací navbar komponenty
│   ├── login_page.py           # Formulář přihlášení (/login)
│   ├── register_page.py        # Registrační formulář (/register)
│   ├── forgot_password_page.py # Formulář obnovy hesla (/forgot-password)
│   ├── courses_page.py         # Přehled kurzů (/courses)
│   └── components/             # Reusable UI komponenty
│       ├── __init__.py
│       └── navbar.py           # Horní navigační lišta
│
├── utils/                      # UTILITIES: Nezávislé pomocné nástroje
│   ├── __init__.py
│   └── data_generator.py       # Generátor dynamických testovacích uživatelů a e-mailů
│
├── data/                       # TEST DATA: Statická data pro data-driven testy
│   └── invalid_emails.json     # Sada nevalidních formátů emailu pro validace
│
├── reports/                    # OUTPUT: Lokálně generované výstupy (ignorováno v Gitu)
│   ├── html/                   # HTML reporty (report.html)
│   └── screenshots/            # Snímky obrazovky při chybách
│
└── docs/                       # DOKUMENTACE: Analýzy požadavků a reporty
    ├── požadavky_ust_podle_src.md
    ├── TEST_ASSERTIONS_OVERVIEW.md
    ├── TEST_EXECUTION_REPORT.md
    └── PLAN_LOKATORY_DATA_TESTID.md
```

---

## 🏷️ Pytest Markery (Hybridní spouštění)

Testy jsou označeny markery pro selektivní spouštění:

| Marker | Popis | Příklad spuštění |
| :--- | :--- | :--- |
| **`smoke`** | Rychlé kritické scénáře (Happy Path přihlášení, registrace, navigace) | `pytest -m smoke` |
| **`regression`** | Kompletní regresní sada (všechny negativní testy, validace a UI kontroly) | `pytest -m regression` |
| **`auth`** | Všechny testy autentizace (přihlášení, odhlášení, registrace, hesla) | `pytest -m auth` |
| **`navigation`** | Testy navigačních prvků | `pytest -m navigation` |

---

## 🚀 Jak testy spustit

### 1. Instalace projektu (v aktivovaném virtuálním prostředí)
```bash
source .venv/bin/activate
pip install -e .
playwright install chromium
```

### 2. Spuštění celé testovací sady
Automaticky vygeneruje HTML report do `reports/html/report.html`:
```bash
pytest
```

### 3. Spuštění konkrétní domény
```bash
# Pouze testy přihlášení a správy účtů:
pytest tests/auth/

# Pouze testy navigace:
pytest tests/navigation/
```

### 4. Spuštění podle markerů
```bash
# Pouze kritické smoke testy:
pytest -m smoke

# Pouze regresní validační testy:
pytest -m regression
```

### 5. Spuštění s viditelným oknem (Headed mód)
```bash
pytest --headed
```

### 6. Spuštění se zpomalením pro vizuální sledování
```bash
pytest --headed --slowmo 500
```

---

## ⚙️ Konfigurace prostředí (.env)
Pro změnu výchozí URL nebo přihlašovacích údajů vytvořte v kořenu soubor `.env` (inspirovat se můžete vzorem v `.env.example`):
```env
BASE_URL=http://testovani.kitner.cz
HEADLESS=true
TEST_USER_EMAIL=tester@kitner.cz
TEST_USER_PASSWORD=TajneHeslo123
```

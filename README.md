# Automatizované testy pro Demo Login (kitner.cz)

Tento projekt obsahuje sadu automatizovaných E2E testů pro přihlašovací modul webové aplikace **[http://testovani.kitner.cz](http://testovani.kitner.cz/courses)**.

Testy jsou implementovány v jazyce **Python** s využitím frameworku **Playwright** a **pytest** s architekturou **Page Object Model (POM)** a **parametrizací (`@pytest.mark.parametrize`)** pro čistý a snadno udržitelný kód (DRY princip).

---

## 📁 Struktura projektu

```text
├── .venv/                  # Virtuální prostředí Pythonu
├── pages/                  # Page Object Model třídy (reprezentace stránek a elementů)
│   ├── __init__.py
│   ├── base_page.py        # Základní bázová stránka se společnými metodami
│   ├── login_page.py       # Lokátory a akce pro přihlašovací stránku (/login)
│   └── courses_page.py     # Lokátory a akce pro stránku s kurzy a navigaci (/courses)
├── tests/                  # Testovací scénáře
│   ├── __init__.py
│   └── test_login.py       # Zrefaktorovaná parametrizovaná sada testů
├── conftest.py             # Globální pytest fixtures (přihlašovací údaje, URL)
├── pytest.ini              # Konfigurace spouštěče testů pytest
├── requirements.txt        # Seznam závislostí
└── report.html             # Vygenerovaný grafický report výsledků testů
```

---

## 🧪 Zrefaktorovaná sada testů

Testy jsou rozděleny do 6 modulárních testovacích funkcí, které pomocí parametrů pokrývají **14 scénářů**:

### 1. `test_successful_login_variants` (Parametrizovaný Happy Path)
- **`standard-click`**: Běžné přihlášení kliknutím na tlačítko *Přihlásit*.
- **`enter-key`**: Odeslání formuláře stiskem klávesy *Enter*.
- **`uppercase-email`**: Přihlášení s velkými písmeny v e-mailu (*Case Insensitivity*).

### 2. `test_login_from_courses_navigation` (Integrační test)
- Přechod z horní navigace na `/login` $\rightarrow$ přihlášení $\rightarrow$ návrat na `/courses`.

### 3. `test_login_and_logout_lifecycle` (E2E životní cyklus)
- Přihlášení $\rightarrow$ odhlášení $\rightarrow$ ověření obnovení nepřihlášeného stavu.

### 4. `test_session_persists_after_page_reload` (Perzistence relace)
- Ověření, že uživatel zůstává přihlášen i po obnovení stránky (*F5 / reload*).

### 5. `test_invalid_and_incomplete_login_credentials` (Parametrizované chyby a validace)
- **`invalid-password`**: Neplatné heslo $\rightarrow$ chybová hláška.
- **`non-existent-user`**: Neexistující účet $\rightarrow$ chybová hláška.
- **`empty-password-required`**: Vyplněný e-mail bez hesla $\rightarrow$ validační hláška *„The password field is required.“*
- **`empty-form-submit`**: Prázdný formulář $\rightarrow$ zabránění odeslání.
- **`invalid-email-format`**: Text bez e-mailového formátu $\rightarrow$ zabránění odeslání.

### 6. `test_login_form_navigation_links` (Parametrizované odkazy)
- **`forgot-password-link`**: Odkaz *„Zapomněli jste heslo?“* $\rightarrow$ `/forgot-password`.
- **`register-link`**: Odkaz *„Zaregistrujte se“* $\rightarrow$ `/register`.

### 7. `test_login_page_title_and_password_masking` (UI & Bezpečnost)
- Kontrola HTML tagu `<title>` a maskování hesla (`type="password"`).

---

## 🚀 Jak testy spustit

### 1. Aktivace virtuálního prostředí
```bash
source .venv/bin/activate
```

### 2. Spuštění testů na pozadí (Headless mód)
```bash
pytest
```

### 3. Spuštění s viditelným oknem prohlížeče (Headed mód)
```bash
pytest --headed
```

### 4. Spuštění se zpomalením kroků (pro vizuální sledování průběhu)
```bash
pytest --headed --slowmo 1000
```

### 5. Spuštění a vygenerování HTML reportu
```bash
pytest --html=report.html --self-contained-html
```
Report si můžete otevřít v prohlížeči (soubor `report.html`).

---

## 🔑 Testovací účet
- **Email:** `tester@kitner.cz`
- **Heslo:** `TajneHeslo123`

# 📋 Plán přechodu na nativní metodu Playwrightu `page.get_by_test_id("...")` s řetězením

Tento plán popisuje konkrétní kroky pro přechod všech lokátorů v projektu ze zápisu CSS atributů `page.locator('[data-testid="..."]')` na **čistou, doporučenou nativní metodu Playwrightu `page.get_by_test_id("...")`** se zachováním **řetězení kontejnerů (Locator Chaining)** namísto indexů `.first` a `.last`.

---

## 🎯 Cílový stav (Target Architecture)

| Umístění / Prvek | Původní stav (CSS / indexy) | Cílový stav (Nativní `get_by_test_id` + chaining) |
|---|---|---|
| **Běžná pole (např. e-mail)** | `page.locator('[data-testid="email_input"]')` | `page.get_by_test_id("email_input")` |
| **Odkaz na login v navigaci** | `page.locator('[data-testid="login_link"]').first` | `page.get_by_test_id("navigation").get_by_test_id("login_link")` |
| **Odkaz na login pod registrací** | `page.locator('[data-testid="login_link"]').last` | `page.get_by_test_id("register_section").get_by_test_id("login_link")` |
| **Odkaz na login na forgot-password** | `page.locator('[data-testid="login_link"]').last` | `page.get_by_test_id("navigation").get_by_test_id("login_link")` |
| **Tlačítko „Přidat kurz“ lektora** | `header.locator('button, a').filter(has_text="Přidat kurz")` | `page.get_by_test_id("courses_header").get_by_test_id("registration_link")` |
| **Tlačítko odhlášení v menu** | `page.locator('[data-testid="logout_button"]')` | `page.get_by_test_id("navigation").get_by_test_id("logout_button")` |
| **Uvítací blok po registraci** | `page.locator('[data-testid="home_section"]')` | `page.get_by_test_id("home_section")` |
| **Formulář pro vytvoření kurzu** | `page.locator('[data-testid="course_form"]')` | `page.get_by_test_id("course_form")` |

---

## 💡 Výhody nativní metody `get_by_test_id`

1. **Čistší a čitelnější kód:** Není potřeba psát hranaté závorky ani uvozovky CSS selektorů `['data-testid="..."]`.
2. **Přímá podpora Playwrightu:** Jde o oficiální doporučený způsob Playwrightu pro práci s testovacími identifikátory.
3. **Plná podpora řetězení:** Metoda `.get_by_test_id()` se dá plynule řetězit za sebou:
   `page.get_by_test_id("navigation").get_by_test_id("login_link")`.

---

## 🛠️ Fáze realizace plánu

### Fáze 1: Refaktoring Page Object tříd v `pages/`

1. **`pages/login_page.py`:**
   * Převést všechny lokátory z `page.locator('[data-testid="..."]')` na `page.get_by_test_id("...")`:
     * `self.email_input = page.get_by_test_id("email_input")`
     * `self.password_input = page.get_by_test_id("password_input")`
     * `self.login_button = page.get_by_test_id("login_button")`
     * `self.email_error = page.get_by_test_id("email_input_errors")`
     * `self.password_error = page.get_by_test_id("password_input_errors")`
     * `self.heading = page.get_by_test_id("login_text")`
     * `self.register_link = page.get_by_test_id("register_link")`
     * `self.forgot_password_link = page.get_by_test_id("forgot_password_link")`

2. **`pages/register_page.py`:**
   * Převést formulářová pole a errory na `page.get_by_test_id(...)`.
   * Nahradit `self.login_link`:
     * Původní: `page.locator('[data-testid="login_link"]').last`
     * Nové (řetězení): `page.get_by_test_id("register_section").get_by_test_id("login_link")`

3. **`pages/courses_page.py`:**
   * `self.courses_header = page.get_by_test_id("courses_header")`
   * `self.logout_button = page.get_by_test_id("navigation").get_by_test_id("logout_button")`
   * `self.login_link = page.get_by_test_id("navigation").get_by_test_id("login_link")`
   * `self.courses_link = page.get_by_test_id("navigation").get_by_test_id("courses_link")`
   * `self.add_course_button`:
     * Původní: `self.courses_header.locator('button, a').filter(has_text="Přidat kurz")`
     * Nové (řetězení): `self.courses_header.get_by_test_id("registration_link")`

4. **`pages/forgot_password_page.py`:**
   * `self.email_input = page.get_by_test_id("email_input")`
   * `self.submit_button = page.get_by_test_id("submit_button")`
   * `self.info_text = page.get_by_test_id("forget_password_p")`
   * `self.login_link = page.get_by_test_id("navigation").get_by_test_id("login_link")`

---

### Fáze 2: Refaktoring testovacích souborů v `tests/`

1. **`tests/test_demo_login.py`:**
   * Převést přímé lokátory v testech na `page.get_by_test_id(...)`:
     * TC01: `page.get_by_test_id("home_section")`
     * TC06 & TC10: použít `courses_page.login_link` nebo `page.get_by_test_id("navigation").get_by_test_id("login_link")` (místo `.first`)
     * TC07: `page.get_by_test_id("course_form")`, `page.get_by_test_id("course_name_input")`
     * TC08: použít `courses_page.logout_button` (místo přímého lokátoru)

2. **`tests/test_login.py` (pro zachování stability starších testů):**
   * Odstranit explicitní indexy `.first`, kde se používaly přes `courses_page.login_link`.

---

### Fáze 3: Exekuce a verifikace

1. Spustit všechny testy v `tests/test_demo_login.py` v prohlížeči Chromium.
2. Spustit testy v `tests/test_login.py`.
3. Zkontrolovat, že všech 13 položek testovací sady úspěšně prošlo (100 % pass).

---

### Fáze 4: Aktualizace dokumentace

1. Aktualizovat [`TEST_ASSERTIONS_OVERVIEW.md`](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/TEST_ASSERTIONS_OVERVIEW.md).
2. Aktualizovat [`TEST_EXECUTION_REPORT.md`](file:///Users/andreawank/Software%20tester/AI%20automatizovan%C3%A9%20testov%C3%A1n%C3%AD/TEST_EXECUTION_REPORT.md).

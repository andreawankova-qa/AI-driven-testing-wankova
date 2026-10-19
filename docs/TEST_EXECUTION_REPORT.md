# 📊 Report z exekuce automatizovaných testů (Test Execution Report)

* **Projekt:** Automatizované E2E testování – Demo Login & Registration
* **Cílová aplikace:** [http://testovani.kitner.cz](http://testovani.kitner.cz)
* **Testovací soubor:** [`tests/test_demo_login.py`](tests/test_demo_login.py)
* **Datum a čas běhu:** 12. října 2026, 23:07
* **Použitý stack:** Python 3.9.6, Pytest 8.4.2, Playwright (Chromium), Page Object Model (POM)
* **Pravidlo pro lokátory:** Výhradně nativní metoda Playwrightu `get_by_test_id(...)` a řetězení kontejnerů (Locator Chaining). Žádné CSS selektory, žádný XPath, žádné HTML tagy ani indexy `.first` / `.last`.
* **Záloha původních verzí souborů:** Složka [`původní test/`](původní%20test/) (obsahuje verze před refaktoringem s příponou `_old`)
* **Interaktivní HTML report:** [`report_demo_login.html`](report_demo_login.html)

---

## 📈 Souhrnný výsledek (Executive Summary)

| Metrika | Hodnota |
|---|---|
| **Celkem spuštěných testů** | **13** (12 testovacích případů, TC03 má 2 parametrizované běhy) |
| **Úspěšné testy (PASSED)** | **13** (100 %) |
| **Selhání (FAILED)** | **0** (0 %) |
| **Chyby (ERRORS)** | **0** (0 %) |
| **Celková doba běhu** | **14.59 s** |
| **Konečný stav sady** | 🟢 **VŠECHNY TESTY PROŠLY (100 % SUCCESS)** |

---

## 📋 Přehledová tabulka výsledků testů

| ID | Název testovací metody | Oblast testu | Použitá syntaxe lokátorů | Výsledek |
|:---:|---|---|---|:---:|
| **TC01** | `test_tc01_successful_registration_and_password_masking` | Registrace (Happy Path + Bezpečnost) | `get_by_test_id` + chaining v navigaci | 🟢 **PASSED** |
| **TC02** | `test_tc02_registration_required_fields_validation` | Registrace (Validace prázdného formuláře) | `get_by_test_id` pro všechny errory | 🟢 **PASSED** |
| **TC03a** | `test_tc03_...[different-password]` | Registrace (Neshodné heslo v potvrzení) | `get_by_test_id` | 🟢 **PASSED** |
| **TC03b** | `test_tc03_...[empty-password-again]` | Registrace (Prázdné pole heslo znovu) | `get_by_test_id` | 🟢 **PASSED** |
| **TC04** | `test_tc04_registration_short_password` | Registrace (Minimální délka hesla < 8) | `get_by_test_id` | 🟢 **PASSED** |
| **TC05** | `test_tc05_registration_duplicate_email` | Registrace (Integrita – duplicitní e-mail) | `get_by_test_id` | 🟢 **PASSED** |
| **TC06** | `test_tc06_registration_and_subsequent_login_with_enter_key` | E2E Flow (Registrace -> Logout -> Login s Enterem) | `courses_page.login_link` (chaining) | 🟢 **PASSED** |
| **TC07** | `test_tc07_lecturer_successful_login_and_rights` | Autorizace lektora (Login + RBAC + Přidat kurz) | `courses_header.get_by_test_id(...)` | 🟢 **PASSED** |
| **TC08** | `test_tc08_login_invalid_credentials` | Přihlášení (Negativní test – neplatné údaje) | `courses_page.logout_button` (chaining) | 🟢 **PASSED** |
| **TC09** | `test_tc09_session_persistence_after_reload` | Session (Perzistence přihlášení po Reload / F5) | `courses_page.logout_button` (chaining) | 🟢 **PASSED** |
| **TC10** | `test_tc10_logout_lifecycle` | Životní cyklus (Odhlášení a ukončení relace) | `courses_page.login_link` (chaining) | 🟢 **PASSED** |
| **TC11** | `test_tc11_navigation_links_between_login_and_registration` | UX & Navigace (Obousměrné přepínání formulářů) | `register_section.get_by_test_id(...)` | 🟢 **PASSED** |
| **TC12** | `test_tc12_forgot_password_request_submission` | Autentizační tok (Odeslání požadavku na reset hesla) | `get_by_test_id` | 🟢 **PASSED** |

---

## 🧩 Přehled všech Page Object lokátorů v projektu (Důkaz použití výhradně `get_by_test_id`)

Následující tabulky dokládají, že **veškeré prvky ve všech Page Object třídách projektu jsou definovány výhradně pomocí metody `get_by_test_id`** a řetězení kontejnerů:

### 1. Přihlašovací stránka (`LoginPage` – `pages/login_page.py`)
| Proměnná Page Objectu | Definice v kódu (100% `get_by_test_id`) | Typ elementu |
|---|---|---|
| `email_input` | `page.get_by_test_id("email_input")` | Vstupní pole pro e-mail |
| `password_input` | `page.get_by_test_id("password_input")` | Vstupní pole pro heslo |
| `login_button` | `page.get_by_test_id("login_button")` | Tlačítko pro přihlášení |
| `email_error` | `page.get_by_test_id("email_input_errors")` | Chybové hlášení e-mailu / údajů |
| `password_error` | `page.get_by_test_id("password_input_errors")` | Validační hláška hesla |
| `heading` | `page.get_by_test_id("login_text")` | Nadpis přihlašovacího formuláře |
| `register_link` | `page.get_by_test_id("register_link")` | Odkaz na registraci |
| `forgot_password_link` | `page.get_by_test_id("forgot_password_link")` | Odkaz na zapomenuté heslo |

### 2. Registrační stránka (`RegisterPage` – `pages/register_page.py`)
| Proměnná Page Objectu | Definice v kódu (100% `get_by_test_id` + Chaining) | Typ elementu |
|---|---|---|
| `name_input` | `page.get_by_test_id("name_input")` | Vstupní pole pro jméno |
| `email_input` | `page.get_by_test_id("email_input")` | Vstupní pole pro e-mail |
| `password_input` | `page.get_by_test_id("password_input")` | Vstupní pole pro heslo |
| `password_again_input` | `page.get_by_test_id("password_again_input")` | Potvrzení hesla (*Heslo znovu*) |
| `register_button` | `page.get_by_test_id("register_button")` | Tlačítko pro registraci |
| `register_form` | `page.get_by_test_id("register_form")` | Registrační formulář |
| `heading` | `page.get_by_test_id("register_text")` | Nadpis registračního formuláře |
| `name_error` | `page.get_by_test_id("name_input_errors")` | Validační hláška jména |
| `email_error` | `page.get_by_test_id("email_input_errors")` | Validační hláška e-mailu |
| `password_error` | `page.get_by_test_id("password_input_errors")` | Validační hláška hesla / potvrzení |
| `login_link` | `page.get_by_test_id("register_section").get_by_test_id("login_link")` | **Řetězení:** odkaz na login pod formulářem |
| `forgot_password_link` | `page.get_by_test_id("forgot_password_link")` | Odkaz na obnovu hesla |

### 3. Stránka kurzů a navigace (`CoursesPage` – `pages/courses_page.py`)
| Proměnná Page Objectu | Definice v kódu (100% `get_by_test_id` + Chaining) | Typ elementu |
|---|---|---|
| `courses_header` | `page.get_by_test_id("courses_header")` | Záhlaví stránky s kurzy |
| `add_course_button` | `self.courses_header.get_by_test_id("registration_link")` | **Řetězení:** lektorské tlačítko *Přidat kurz* |
| `logout_button` | `page.get_by_test_id("navigation").get_by_test_id("logout_button")` | **Řetězení:** tlačítko pro odhlášení v menu |
| `login_link` | `page.get_by_test_id("navigation").get_by_test_id("login_link")` | **Řetězení:** odkaz na přihlášení v menu |
| `courses_link` | `page.get_by_test_id("navigation").get_by_test_id("courses_link")` | **Řetězení:** odkaz na kurzy v navigaci |

### 4. Zapomenuté heslo (`ForgotPasswordPage` – `pages/forgot_password_page.py`)
| Proměnná Page Objectu | Definice v kódu (100% `get_by_test_id` + Chaining) | Typ elementu |
|---|---|---|
| `email_input` | `page.get_by_test_id("email_input")` | Vstupní pole pro e-mail |
| `submit_button` | `page.get_by_test_id("submit_button")` | Tlačítko pro odeslání (*Potvrdit*) |
| `info_text` | `page.get_by_test_id("forget_password_p")` | Informační text s instrukcemi |
| `login_link` | `page.get_by_test_id("navigation").get_by_test_id("login_link")` | **Řetězení:** návrat na přihlášení |

### 5. Přímé kontroly stavu v testech (`tests/test_demo_login.py`)
* Uvítací blok po registraci: `page.get_by_test_id("home_section")`
* Formulář pro vytvoření kurzu: `page.get_by_test_id("course_form")`
* Pole pro název kurzu: `page.get_by_test_id("course_name_input")`

---

## 🔍 Detailní rozpis jednotlivých testů

---

### TC01: Úspěšná registrace nového uživatele & Maskování hesel
* **Cíl:** Ověřit kompletní proces úspěšné registrace nového unikátního studenta a bezpečnostní maskování hesel přes nativní metodu `get_by_test_id`.
* **Kroky testu:**
  1. Otevření registrační stránky `/register`.
  2. Kontrola atributu `type="password"` u obou polí hesel.
  3. Vyplnění jména, e-mailu a shodných hesel do obou polí.
  4. Odeslání formuláře kliknutím na *„Registrovat“*.
* **Provedené asserty (kontroly):**
  * `expect(register_page.password_input).to_have_attribute("type", "password")`
  * `expect(register_page.password_again_input).to_have_attribute("type", "password")`
  * `expect(page).to_have_url("http://testovani.kitner.cz/home")`
  * `expect(page.get_by_test_id("home_section")).to_be_visible()`
  * `expect(page.get_by_test_id("home_section")).to_contain_text(f"Vítej uživateli {user_name}!")`
  * `expect(page.get_by_test_id("navigation").get_by_test_id("logout_button")).to_be_visible()`
* **Výsledek:** 🟢 **PASSED**

---

### TC02: Validace povinných polí registrace (Prázdný formulář)
* **Cíl:** Ověřit chování aplikace při pokusu o registraci bez vyplnění jakýchkoliv údajů.
* **Kroky testu:**
  1. Otevření stránky `/register`.
  2. Okamžité kliknutí na tlačítko *„Registrovat“* bez zadání dat.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url(register_page.URL)`
  * `expect(register_page.name_error).to_have_text("The name field is required.")`
  * `expect(register_page.email_error).to_have_text("The email field is required.")`
  * `expect(register_page.password_error).to_have_text("The password field is required.")`
* **Výsledek:** 🟢 **PASSED**

---

### TC03: Negativní test – Neplatné potvrzení hesla (Neshoda i prázdné pole)
* **Cíl:** Ověřit validaci potvrzení hesla pro obě chybové varianty.
* **Kroky testu:**
  1. Otevření stránky `/register`.
  2. Vyplnění jména, unikátního e-mailu a hesla.
  3. Zadání testovací hodnoty do potvrzovacího pole (odlišné heslo nebo prázdné pole).
  4. Odeslání formuláře.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url(register_page.URL)`
  * `expect(register_page.password_error).to_be_visible()`
  * `expect(register_page.password_error).to_have_text("The password field confirmation does not match.")`
* **Výsledek:** 🟢 **PASSED** (obě varianty)

---

### TC04: Negativní test – Heslo kratší než 8 znaků
* **Cíl:** Ověřit vynucení minimální délky hesla.
* **Kroky testu:**
  1. Otevření `/register`.
  2. Vyplnění jména, e-mailu a 5místného hesla do obou polí.
  3. Odeslání formuláře.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url(register_page.URL)`
  * `expect(register_page.password_error).to_be_visible()`
  * `expect(register_page.password_error).to_have_text("The password field must be at least 8 characters.")`
* **Výsledek:** 🟢 **PASSED**

---

### TC05: Negativní test – Registrace s existujícím e-mailem (Duplicita)
* **Cíl:** Ověřit zamezení duplicitních registrací stejného e-mailu v databázi.
* **Kroky testu:**
  1. Otevření `/register`.
  2. Vyplnění existujícího e-mailu lektora a platného hesla.
  3. Odeslání formuláře.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url(register_page.URL)`
  * `expect(register_page.email_error).to_be_visible()`
  * `expect(register_page.email_error).to_have_text("The email has already been taken.")`
* **Výsledek:** 🟢 **PASSED**

---

### TC06: Kompletní E2E životní cyklus (Registrace ➔ Logout ➔ Login s Enterem)
* **Cíl:** Ověřit celý životní cyklus bez indexů `.first` s využitím zřetězených lokátorů.
* **Kroky testu:**
  1. Registrace nového uživatele na `/register`.
  2. Odhlášení kliknutím na *„Odhlásit se“*.
  3. Ověření, že v navigaci je viditelný odkaz *„Přihlásit se“* (`courses_page.login_link`).
  4. Přihlášení přes `/login` pomocí stisku klávesy `Enter`.
  5. Ověření úspěšného návratu na `/courses`.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url("http://testovani.kitner.cz/home")`
  * `expect(courses_page.login_link).to_be_visible()`
  * `expect(page).to_have_url(courses_page.URL)`
  * `expect(courses_page.logout_button).to_be_visible()`
* **Výsledek:** 🟢 **PASSED**

---

### TC07: Úspěšné přihlášení lektora & Oprávnění & Akce „Přidat kurz“
* **Cíl:** Ověřit zobrazení lektorského tlačítka a otevření formuláře bez závislosti na HTML tagu či textu přes `courses_header.get_by_test_id("registration_link")`.
* **Kroky testu:**
  1. Přihlášení lektora.
  2. Kontrola přítomnosti lektorského tlačítka *„Přidat kurz“*.
  3. Kliknutí na tlačítko *„Přidat kurz“*.
  4. Kontrola přechodu na `/courses/create` a vykreslení formuláře.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url(courses_page.URL)`
  * `expect(courses_page.logout_button).to_be_visible()`
  * `expect(courses_page.courses_header).to_contain_text("Přidat kurz")`
  * `expect(courses_page.add_course_button).to_be_visible()`
  * `expect(page).to_have_url("http://testovani.kitner.cz/courses/create")`
  * `expect(page.get_by_test_id("course_form")).to_be_visible()`
  * `expect(page.get_by_test_id("course_name_input")).to_be_visible()`
* **Výsledek:** 🟢 **PASSED**

---

### TC08: Negativní test přihlášení – Neplatné údaje
* **Cíl:** Ověřit reakci systému na pokus o přihlášení neexistujícího uživatele.
* **Kroky testu:**
  1. Otevření přihlašovací stránky `/login`.
  2. Zadání neplatných údajů a odeslání.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url(login_page.URL)`
  * `expect(login_page.email_error).to_be_visible()`
  * `expect(login_page.email_error).to_have_text("These credentials do not match our records.")`
  * `expect(courses_page.logout_button).not_to_be_visible()`
* **Výsledek:** 🟢 **PASSED**

---

### TC09: Perzistence přihlašovací relace (Session Persistence po Reload / F5)
* **Cíl:** Ověřit stabilitu autentizační session při obnovení stránky v prohlížeči.
* **Kroky testu:**
  1. Přihlášení uživatele na `/courses`.
  2. Provedení obnovení stránky (`page.reload()`).
  3. Ověření, že uživatel zůstal přihlášen.
* **Provedené asserty (kontroly):**
  * `expect(page).to_have_url(courses_page.URL)`
  * `expect(courses_page.logout_button).to_be_visible(timeout=5000)`
* **Výsledek:** 🟢 **PASSED**

---

### TC10: Životní cyklus odhlášení (Logout Lifecycle)
* **Cíl:** Ověřit ukončení uživatelské relace po kliknutí na *„Odhlásit se“*.
* **Kroky testu:**
  1. Přihlášení lektora.
  2. Kliknutí na tlačítko *„Odhlásit se“*.
* **Provedené asserty (kontroly):**
  * `expect(courses_page.logout_button).not_to_be_visible()`
  * `expect(courses_page.login_link).to_be_visible()`
* **Výsledek:** 🟢 **PASSED**

---

### TC11: Vzájemná obousměrná navigace (Login ⟷ Registrace)
* **Cíl:** Ověřit přepínání mezi formuláři pomocí zřetězeného lokátoru `register_section` namísto `.last`.
* **Kroky testu:**
  1. Na `/login` kliknutí na *„Zaregistrujte se“*.
  2. Kontrola formuláře na `/register`.
  3. Na `/register` kliknutí na zřetězený odkaz *„Přihlásit se“*.
  4. Kontrola návratu na `/login`.
* **Provedené asserty (kontroly):**
  * `expect(login_page.register_link).to_be_visible()`
  * `expect(page).to_have_url(register_page.URL)`
  * `expect(register_page.register_button).to_be_visible()`
  * `expect(register_page.login_link).to_be_visible()`
  * `expect(page).to_have_url(login_page.URL)`
  * `expect(login_page.login_button).to_be_visible()`
* **Výsledek:** 🟢 **PASSED**

---

### TC12: Odeslání požadavku na obnovu zapomenutého hesla
* **Cíl:** Ověřit dostupnost formuláře pro reset hesla a korektní odeslání požadavku přes `get_by_test_id`.
* **Kroky testu:**
  1. Na `/login` kliknutí na *„Zapoměli jste své heslo?“*.
  2. Vyplnění e-mailu a odeslání požadavku.
* **Provedené asserty (kontroly):**
  * `expect(login_page.forgot_password_link).to_be_visible()`
  * `expect(page).to_have_url(forgot_password_page.URL)`
  * `expect(forgot_password_page.info_text).to_contain_text("Zapoměli jste své heslo?")`
  * `expect(forgot_password_page.submit_button).to_be_visible()`
* **Výsledek:** 🟢 **PASSED**

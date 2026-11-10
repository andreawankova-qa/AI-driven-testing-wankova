# 🐞 Centrální registr chyb (JIRA Bug Reports)

Tento dokument slouží jako **centrální registr zjištěných chyb a incidentů** v projektu Demo-login.  
Každá zaznamenaná chyba má přiděleno unikátní identifikační číslo (`BR-XX`) a je připravena ve standardizovaném formátu pro přímé zkopírování do systému **Atlassian JIRA** (nebo jiného issue trackeru).

---

## 📊 Přehled nahlášených chyb (Defect Summary Table)

| ID chyby | Modul / Téma | Název incidentu | Závažnost | Priorita | Vázaná US | Stav |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| [**BR-01**](#br-01-rbac-chybějící-ochrana-url-coursescreate--formulář-pro-vytvoření-kurzu-je-přístupný-pro-roli-zákazník) | `SEC / RBAC` | Chybějící ochrana URL `/courses/create` pro roli Zákazník | **Critical** | **High** | US-18, US-13 | 🔴 Otevřeno |
| [**BR-02**](#br-02-lec-chybějící-klientská-validace-formuláře-kurzu-a-přesměrování-při-chybě-api-http-422) | `LEC` | Chybějící klientská validace formuláře kurzu a přesměrování při chybě API (HTTP 422) | **Medium** | **Medium** | US-13 | 🔴 Otevřeno |
| [**BR-03**](#br-03-auth-chybějící-klientské-rozhraní-pro-dokončení-obnovy-hesla-na-reset-password) | `AUTH` | Chybějící klientské rozhraní pro dokončení obnovy hesla na `/reset-password` | **High** | **High** | US-05 | 🔴 Otevřeno |
| [**BR-04**](#br-04-enr-chybná-validace-nepovinného-ičo--prázdné-pole-způsobuje-chybu-neplatné-ičo-a-blokuje-zápis) | `ENR` | Chybná validace nepovinného IČO – prázdné pole blokuje registraci s chybou „Neplatné IČO“ | **Medium** | **High** | US-11 | 🔴 Otevřeno |

> [!NOTE]
> **Životní cyklus stavů incidentu:** `🔴 Otevřeno (Open)` ➔ `🟡 V řešení (In Progress)` ➔ `🟢 Vyřešeno (Closed / Verified)`  
> *Nové chyby (např. `BR-02`, `BR-03`...) se přidávají do této přehledové tabulky a jejich detailní formulář se připojuje na konec dokumentu.*

---

## 📌 Detailní specifikace JIRA ticketů

---

### 🐞 BR-01 [RBAC]: Chybějící ochrana URL /courses/create – formulář pro vytvoření kurzu je přístupný pro roli Zákazník

#### JIRA Ticket Metadata
* **Project:** Demo Login & Courses Portal (`DLCP`)
* **Issue Type:** 🐞 Bug / Defect
* **Summary (Název):** `[RBAC/Security] Chybějící ochrana URL /courses/create – formulář pro vytvoření kurzu je přístupný pro roli Zákazník`
* **Komponenta:** Frontend / Routing / Autorizace (RBAC)
* **Závažnost (Severity):** Critical (Bezpečnostní zranitelnost – Broken Access Control dle OWASP Top 10 A01)
* **Priorita (Priority):** High (Kritické bezpečnostní riziko neoprávněného obcházení přístupových práv)
* **Reprodukovatelnost:** Vždy (100 %)
* **Vázané User Stories:** 
  - [`US-18: Řízení přístupu na základě rolí (RBAC)`](požadavky_ust_podle_src.md#us-18-řízení-přístupu-na-základě-rolí-rbac)
  - [`US-13: Vytvoření nového kurzu lektorem`](požadavky_ust_podle_src.md#us-13-vytvoření-nového-kurzu-lektorem)
* **Související Test Casy:** 
  - `TC-38-LEC` (v [`tests/lecturer/test_lecturer.py`](../tests/lecturer/test_lecturer.py))
  - `TC-44-SEC` (v [`tests/security/test_security.py`](../tests/security/test_security.py))
* **Prostředí:** Testovací prostředí (`http://testovani.kitner.cz`), Browser: Chromium / Playwright
* **Nahlásil:** Andrea Wanková
* **Datum nálezu:** 19. 10. 2026

---

#### 📝 Popis problému (Description)
Aplikace na klientské straně (Single Page Application router) neprovádí kontrolu uživatelské role při přímém přechodu na URL adresu pro vytváření nových kurzů (`/courses/create`). 

Běžný přihlášený uživatel s klientskou rolí **Zákazník (Customer)** tak po manuálním zadání URL adresy do prohlížeče získá plný přístup k formuláři pro tvorbu a editaci kurzů (`course_form`), ačkoliv má být tato funkcionalita striktně vyhrazena roli **Lektor (Lector)** nebo administrátorům.

---

#### ⚙️ Předpoklady (Preconditions)
1. V systému existuje aktivní uživatelský účet s rolí **Zákazník (Customer)**:
   - **E-mail:** `tester@kitner.cz`
   - **Heslo:** `TajneHeslo123`

---

#### 👣 Kroky k reprodukci (Steps to Reproduce)
1. Otevři v prohlížeči přihlašovací formulář: `http://testovani.kitner.cz/login`.
2. Přihlas se pomocí zákaznického účtu (`tester@kitner.cz` / `TajneHeslo123`).
3. Po úspěšném přihlášení a přesměrování zadej do adresního řádku prohlížeče přímo chráněnou URL:  
   👉 `http://testovani.kitner.cz/courses/create`
4. Stiskni klávesu `Enter` a zkontroluj zobrazený obsah stránky.

---

#### ✅ Očekávané chování (Expected Result)
* Klientský router i backend ověří oprávnění přihlášeného uživatele a detekují roli **Zákazník**.
* Přístup k lektorskému formuláři je okamžitě zablokován:
  - Uživatel je **přesměrován** zpět na veřejný katalog kurzů `/courses` (či nástěnku `/home`) s varovnou zprávou o nedostatečných právech, **NEBO**
  - Je mu zobrazena standardní chybová stránka **`403 Forbidden`** (*„K této akci nemáte dostatečná oprávnění“*).
* Formulářový prvek `<form data-testid="course_form">` se zákazníkovi **v žádném případě nesmí vykreslit**.

---

#### ❌ Skutečné chování (Actual Result)
* Aplikace bez jakékoliv autorizační kontroly či přesměrování kompletně vykreslí editační formulář kurzu (`<form data-testid="course_form">`).
* Zákazníkovi jsou plně přístupná pole pro zadání názvu kurzu, popisu, kapacity účastníků, ceny a nahrání náhledového obrázku včetně odesílacího tlačítka.

---

#### ⚠️ Bezpečnostní a byznysový dopad (Security & Business Impact)
* **Porušení RBAC a principu nejmenších privilegií (Principle of Least Privilege):** Uživatel získává neoprávněný přístup k modulům správy obsahu jiné role.
* **Klasifikace zranitelnosti:** **OWASP Top 10:2021 – A01 (Broken Access Control)** – fatální absence autorizačních filtrů na chráněných trasách.
* **Integrita dat:** Zákazníci mohou potenciálně zanést do veřejného katalogu neautorizované či podvodné kurzy.

---

#### 💻 Technický důkaz a vizuální záznamy (Failure Log & Visual Evidence)
* **Výstup z běhu testů:** `tests/lecturer/test_lecturer.py::TestLecturerCourseManagement::test_tc38_lec_customer_cannot_access_lecturer_create_course` a `tests/security/test_security.py::TestSecurityAndAuthorization::test_tc44_sec_customer_cannot_access_lecturer_operations`
* **Chybový výpis z Playwrightu (AssertionError & Call Log):**

```text
> expect(create_course_page.form).not_to_be_visible()
E AssertionError: Locator expected not to be visible
E Actual value: visible
E Call log:
E   - Expect "to_be_visible" with timeout 5000ms
E   - waiting for get_by_test_id("course_form")
E     14 × locator resolved to <form data-test="course_form" data-testid="course_form">…</form>
E        - unexpected value "visible"
```

---

#### 💡 Doporučené řešení pro vývojáře (Fix Recommendation)
1. **Frontend (Vue / SPA router):**  
   Přidat navigační strážce (`Navigation Guard` / `beforeEnter`) pro routu `/courses/create`, který ověří `user.role === 'lector'`. Pokud role neodpovídá, provést přesměrování na `/courses` s chybovou notifikací.
2. **Backend API:**  
   Zajistit, aby koncový bod `POST /api/courses` (příp. `POST /courses`) striktně validoval token sezení a při pokusu o uložení uživatelem bez role lektora vrátil HTTP stavový kód `403 Forbidden`.

---

#### 🔄 Záznam o verifikaci opravy (Verification Log)
* **Datum re-testu:** *(vyplní se po nasazení opravy)*
* **Verifikoval:** *(jméno testera po re-testu)*
* **Výsledek re-testu:** *(zatím neproveden)*

---

### 🐞 BR-02 [LEC]: Chybějící klientská validace formuláře kurzu a přesměrování při chybě API (HTTP 422)

#### JIRA Ticket Metadata
* **Project:** Demo Login & Courses Portal (`DLCP`)
* **Issue Type:** 🐞 Bug / Defect
* **Summary (Název):** `[LEC/Validace] Chybějící klientská validace formuláře pro vytvoření kurzu a neošetření HTTP 422`
* **Komponenta:** Frontend / Lektor / Validace
* **Závažnost (Severity):** Medium (Absence klientské validace povinných polí formuláře a ignorování chybové odpovědi API ze strany SPA routeru)
* **Priorita (Priority):** Medium (Běžná validační a funkční vada s existujícím workaroundem – správné vyplnění všech polí)
* **Reprodukovatelnost:** Vždy (100 %)
* **Vázané User Stories:** 
  - [`US-13: Vytvoření nového kurzu lektorem`](požadavky_ust_podle_src.md#us-13-vytvoření-nového-kurzu-lektorem)
* **Související Test Casy:** 
  - `TC-34-LEC` (v [`tests/lecturer/test_lecturer.py`](../tests/lecturer/test_lecturer.py))
* **Prostředí:** Testovací prostředí (`http://testovani.kitner.cz`), Browser: Chromium / Playwright
* **Nahlásil:** Andrea Wanková
* **Datum nálezu:** 28. 10. 2026

---

#### 📝 Popis problému (Description)
Při vytváření nového kurzu na stránce `/courses/create` v roli lektora chybí klientská validace povinných polí (název kurzu, popis, kapacita, cena). 

Pokud lektor odešle prázdný formulář kliknutím na tlačítko *„Vytvořit kurz“*, formulář se bez varování odešle na backend (`POST /api/courses`). Backendová služba požadavek správně odmítne s chybovým stavem `HTTP 422 Unprocessable Entity`, avšak klientská aplikace (SPA router) tuto chybu nezachytí, nezobrazí uživateli žádné validační zprávy u prázdných polí a bezpodmínečně provede přesměrování do katalogu kurzů (`/courses/`).

Lektor tak ztrácí kontext, nezíská žádnou zpětnou vazbu o neúspěšném uložení kurzu a formulář je opuštěn.

---

#### ⚙️ Předpoklady (Preconditions)
1. V systému existuje aktivní účet s rolí **Lektor (Lecturer)**:
   - **E-mail:** `lector@lector.com`
   - **Heslo:** `lector@lector.com`
2. Uživatel je přihlášen a nachází se na formuláři pro vytvoření kurzu:
   - **URL:** `http://testovani.kitner.cz/courses/create`

---

#### 👣 Kroky k reprodukci (Steps to Reproduce)
1. Otevři v prohlížeči přihlašovací formulář: `http://testovani.kitner.cz/login`.
2. Přihlas se pomocí lektorského účtu (`lector@lector.com` / `lector@lector.com`).
3. Přejdi na stránku pro vytvoření kurzu: `http://testovani.kitner.cz/courses/create`.
4. Ponechej všechna vstupní pole (`Název kurzu`, `Popis kurzu`, `Kapacita`, `Cena`) zcela prázdná.
5. Klikni na odesílací tlačítko *„Vytvořit kurz“* (`data-testid="registration_link"`).
6. Sleduj reakci rozhraní a síťové požadavky (DevTools).

---

#### ✅ Očekávané chování (Expected Result)
* Klientský formulář zachytí neúplné odeslání a zabrání odeslání požadavku na server, **NEBO** při obdržení chybového kódu `HTTP 422` ze serveru zůstane uživatel na formuláři (`/courses/create`).
* Formulářový prvek `<form data-testid="course_form">` zůstane viditelný.
* U jednotlivých povinných polí se vykreslí srozumitelná validační hlášení (např. *„Název kurzu je povinný“*, *„Kapacita musí být kladné celé číslo“*).
* K přesměrování do katalogu kurzů dojde výhradně po úspěšném uložení platného kurzu (dle US-13).

---

#### ❌ Skutečné chování (Actual Result)
* Klientská aplikace provede `POST` požadavek na `/api/courses` s prázdnými/nulovými hodnotami.
* Backend vrátí stav `HTTP 422 Unprocessable Entity`.
* Klientský router chybu ignoruje, nezobrazí žádné validační hlášky a okamžitě přesměruje uživatele na stránku `/courses/`.
* Formulář se zavře a lektor nemá zpětnou vazbu, proč kurz nebyl vytvořen.

---

#### ⚠️ Bezpečnostní a byznysový dopad (Security & Business Impact)
* **Byznysový dopad / UX:** Závažné zmatení uživatele (lektora), který se domnívá, že kurz byl vytvořen, přestože jej backend odmítl. Ztráta vyplněných dat v případě částečně chybného formuláře.
* **Zatížení backendu:** Zbytečné odesílání nevalidních požadavků na server kvůli absenci frontendové validace.
* **Dopad na testování:** Selhání validačního testu `TC-34-LEC` v testovací sadě [tests/lecturer/test_lecturer.py](../tests/lecturer/test_lecturer.py).

---

#### 💻 Technický důkaz a vizuální záznamy (Failure Log & Visual Evidence)
* **Výstup z běhu testu:** `tests/lecturer/test_lecturer.py::TestLecturerCourseManagement::test_tc34_lec_validation_required_fields_and_numeric_values`
* **Zachycená síťová komunikace:**
```text
Request: POST http://testovani.kitner.cz/api/courses
Payload: name="", description="", capacity=0, price=0
Response: HTTP 422 Unprocessable Entity
Action: SPA Router unconditionally navigates to /courses/
```
* **Chybový výpis z Playwrightu:**
```text
> expect(create_page.form).to_be_visible()
E AssertionError: Locator expected to be visible
E Actual value: hidden
E Call log:
E   - Expect "to_be_visible" with timeout 5000ms
E   - waiting for get_by_test_id("course_form")
E     Error: element(s) not found (Page redirected to /courses/)
```

---

#### 💡 Doporučené řešení pro vývojáře (Fix Recommendation)
1. **Frontend (Formulářová validace & SPA router):**  
   - Doplnit klientskou validaci před odesláním formuláře (HTML5 atributy `required`, `min="1"` u číselných polí nebo validační knihovnu).
   - V obsluze odeslání zachytit chybový stav API (`catch (error)`) a při kódu `422` zobrazit chybové zprávy u příslušných polí namísto navigace `router.push('/courses')`.
2. **Backend API:**  
   - Backend správně vrací `422`, doporučuje se zachovat strukturovanou JSON odpověď s konkrétními chybami pro jednotlivá pole (např. `{"errors": {"name": ["The name field is required."]}}`).

---

#### 🔄 Záznam o verifikaci opravy (Verification Log)
* **Datum re-testu:** *(vyplní se po nasazení opravy)*
* **Verifikoval:** *(jméno testera po re-testu)*
* **Výsledek re-testu:** *(zatím neproveden)*

---

### 🐞 BR-03 [AUTH]: Chybějící klientské rozhraní pro dokončení obnovy hesla na /reset-password

#### JIRA Ticket Metadata
* **Project:** Demo Login & Courses Portal (`DLCP`)
* **Issue Type:** 🐞 Bug / Defect
* **Summary (Název):** `[AUTH/Reset] Chybějící klientské rozhraní formuláře pro nastavení nového hesla na /reset-password`
* **Komponenta:** Frontend / Autentizace / Reset hesla
* **Závažnost (Severity):** High (Uživatel po obdržení resetovacího odkazu nemůže dokončit změnu zapomenutého hesla)
* **Priorita (Priority):** High (Závažná funkční překážka v klíčovém bezpečnostním procesu obnovy přístupu)
* **Reprodukovatelnost:** Vždy (100 %)
* **Vázané User Stories:** 
  - [`US-05: Dokončení změny hesla pomocí tokenu`](požadavky_ust_podle_src.md#us-05-dokončení-změny-hesla-pomocí-tokenu)
* **Související Test Casy:** 
  - `TC-14-AUTH` (v [`tests/auth/test_password_reset.py`](../tests/auth/test_password_reset.py))
  - `TC-16-AUTH` (v [`tests/auth/test_password_reset.py`](../tests/auth/test_password_reset.py))
* **Prostředí:** Testovací prostředí (`http://testovani.kitner.cz`), Browser: Chromium / Playwright
* **Nahlásil:** Andrea Wanková
* **Datum nálezu:** 1. 11. 2026

---

#### 📝 Popis problému (Description)
Aplikace má funkční odeslání žádosti o reset zapomenutého hesla na `/forgot-password` (US-04). 
Pokud však uživatel otevře odkaz pro dokončení resetu hesla s tokenem (např. `/reset-password?token=XYZ&email=tester@kitner.cz`), klientská SPA aplikace vykreslí pouze prázdnou stránku (`<div data-testid="page_container">`) bez jakéhokoliv formuláře, vstupních polí pro nové heslo a potvrzení hesla, i bez tlačítka pro odeslání.

---

#### 👣 Kroky k reprodukci (Steps to Reproduce)
1. Otevři v prohlížeči URL: `http://testovani.kitner.cz/reset-password?token=platny_token_123&email=tester@kitner.cz`.
2. Počkej na dokončení načtení sítě (`networkidle`).
3. Zkontroluj zobrazený obsah stránky.

---

#### ✅ Očekávané chování (Expected Result)
* Zobrazí se formulář pro nastavení nového hesla obsahující:
  - Vstupní pole pro nové heslo (`data-testid="password_input"`).
  - Vstupní pole pro kontrolní potvrzení hesla (`data-testid="password_again_input"`).
  - Odesílací tlačítko (`data-testid="submit_button"`).

---

#### ❌ Skutečné chování (Actual Result)
* Stránka je zcela prázdná, žádná vstupní pole ani formulář se nevykreslí.
* Test `TC-14-AUTH` selže na timeoutu při čekání na `get_by_test_id("password_input")`.

---

#### 💻 Technický důkaz (Failure Log)
```text
> expect(reset_page.password_input).to_be_visible()
E AssertionError: Locator expected to be visible
E Call log:
E   - Expect "to_be_visible" with timeout 5000ms
E   - waiting for get_by_test_id("password_input")
```

---

#### 💡 Doporučené řešení pro vývojáře (Fix Recommendation)
1. Do Vue routeru implementovat komponentu formuláře nového hesla pro trasu `/reset-password`.
2. Propojit formulář s backendovým koncovým bodem pro uložení nového hesla.

---

### 🐞 BR-04 [ENR]: Chybná validace nepovinného IČO – prázdné pole způsobuje chybu „Neplatné IČO“ a blokuje zápis

#### JIRA Ticket Metadata
* **Project:** Demo Login & Courses Portal (`DLCP`)
* **Issue Type:** 🐞 Bug / Defect
* **Summary (Název):** `[Enrollment/Validation] Formulář nezávazné registrace kurzu nepovoluje odeslání bez IČO a hlásí „Neplatné IČO“`
* **Komponenta:** Frontend / Zápis na kurz / Validace formuláře
* **Závažnost (Severity):** Medium (Uživatel bez IČO – nepodnikající fyzická osoba – se nemůže přihlásit na kurz)
* **Priorita (Priority):** High (Blokuje zápis běžných studentů / soukromých zájemců bez živnostenského oprávnění)
* **Reprodukovatelnost:** Vždy (100 %)
* **Vázané User Stories:** 
  - [`US-11: Nezávazná registrace na běh kurzu`](požadavky_ust_podle_src.md#us-11-nezávazná-registrace-na-běh-kurzu-s-validací-ičo-a-telefonu) (AK-1, AK-3)
* **Související Test Casy:** 
  - `TC-28-ENR` (v [`tests/enrollment/test_enrollment.py`](../tests/enrollment/test_enrollment.py))
* **Prostředí:** Testovací prostředí (`http://testovani.kitner.cz`), Browser: Chromium / Playwright
* **Nahlásil:** Andrea Wanková
* **Datum nálezu:** 9. 11. 2026

---

#### 📝 Popis problému (Description)
Dle akceptačního kritéria AK-3 v US-11 má být IČO nepovinným údajem: validace algoritmem kontrolního součtu modulo 11 má proběhnout **pouze tehdy, pokud uživatel IČO zadá**.
V aplikaci však validační logika na klientské straně vyhodnocuje i prázdný řetězec v poli IČO jako neplatné IČO, zobrazí hlášku `Neplatné IČO` a zablokuje odeslání nezávazné registrace. Zákazník bez IČO tak nemůže dokončit zápis.

---

#### ⚙️ Předpoklady (Preconditions)
1. Přihlášený uživatel v roli **Zákazník** (`tester@kitner.cz` / `TajneHeslo123`).
2. Uživatel se nachází na objednávkovém formuláři volného běhu kurzu (např. `/courses/76/register`).

---

#### 👣 Kroky k reprodukci (Steps to Reproduce)
1. Přejdi na formulář zápisu na kurz: `http://testovani.kitner.cz/courses/76/register`.
2. Do pole **Telefon** zadej platné telefonní číslo: `+420 777 123 456`.
3. Pole **IČO** ponech zcela prázdné.
4. Klikni na tlačítko **„Nezávazná registrace“** (`data-testid="registration_link"`).

---

#### ✅ Očekávané chování (Expected Result)
* Protože IČO je nepovinné, formulář projde validací.
* Objednávka je úspěšně odeslána a vytvořen zápis studenta.
* Zákazník je přesměrován do sekce `http://testovani.kitner.cz/my-courses`.

---

#### ❌ Skutečné chování (Actual Result)
* Formulář se neodešle a zůstává na adrese `/courses/76/register`.
* U pole IČO se zobrazí červená chybová hláška **„Neplatné IČO“**.

---

#### 💻 Technický důkaz (Failure Log)
```text
> expect(page).to_have_url(my_courses_page.URL)
E AssertionError: Page URL expected to be 'http://testovani.kitner.cz/my-courses'
E Actual value: http://testovani.kitner.cz/courses/76/register
E Call log:
E   - Expect "to_have_url" with timeout 5000ms
E     14 × unexpected value "http://testovani.kitner.cz/courses/76/register"
```

---

#### 💡 Doporučené řešení pro vývojáře (Fix Recommendation)
V klientské validační funkci upravit podmínku tak, aby se validace kontrolního součtu modulo 11 spouštěla pouze v případě neprázdné hodnoty:
```javascript
if (ico && ico.trim() !== "") {
    // spustit validaci modulo 11
}
```


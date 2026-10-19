# 🐞 Centrální registr chyb (JIRA Bug Reports)

Tento dokument slouží jako **centrální registr zjištěných chyb a incidentů** v projektu Demo-login.  
Každá zaznamenaná chyba má přiděleno unikátní identifikační číslo (`BR-XX`) a je připravena ve standardizovaném formátu pro přímé zkopírování do systému **Atlassian JIRA** (nebo jiného issue trackeru).

---

## 📊 Přehled nahlášených chyb (Defect Summary Table)

| ID chyby | Modul / Téma | Název incidentu | Závažnost | Priorita | Vázaná US | Stav |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| [**BR-01**](#br-01-rbac-chybějící-ochrana-url-coursescreate--formulář-pro-vytvoření-kurzu-je-přístupný-pro-roli-zákazník) | `SEC / RBAC` | Chybějící ochrana URL `/courses/create` pro roli Zákazník | **High / Critical** | **High** | US-18, US-13 | 🔴 Otevřeno |

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
* **Závažnost (Severity):** High / Critical (Bezpečnostní zranitelnost – Broken Access Control dle OWASP Top 10)
* **Priorita (Priority):** High
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

#### 💻 Technický důkaz z automatizovaného testu (Failure Log)
Při spuštění automatizovaných testů v Playwrightu selhávají testy `test_tc38_lec_customer_cannot_access_lecturer_create_course` a `test_tc44_sec_customer_cannot_access_lecturer_operations` na kontrolním assertu:

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

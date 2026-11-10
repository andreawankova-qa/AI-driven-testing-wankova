# 📋 Přehled automatizovaných testů (Test Steps & Checks Overview)

> **Automaticky vygenerovaná živá dokumentace testovací sady Playwright & Pytest.**  
> *Tento dokument mapuje všech **59** automatizovaných testů v projektu, jejich hierarchii, konkrétní uživatelské kroky, formulářové vstupy a veškeré prováděné kontroly (Web-First assertions).*

*Poslední aktualizace: **10. 11. 2026, 12:25:04** | Zdrojové testy: `tests/**/*.py`*

---

## 📊 Manažerský souhrn a metriky testovací sady

| Metrika | Hodnota | Poznámka |
| :--- | :---: | :--- |
| **Celkem automatizovaných testů (AT)** | **59** | Unikátní implementované testovací metody |
| **Pokrytých doménových modulů** | **7** | AUTH, CRS, ENR, LEC, NAV, PRF, SEC |
| **Kritické scénáře (Smoke / P1)** | **26** | `@pytest.mark.smoke` – rychlá regrese jádra |
| **Regresní a validační testy** | **33** | `@pytest.mark.regression` – edge cases, chyby, limity |
| **Evidované defekty (`xfail`)** | **9** | Očekávaně selhávající testy navázané na JIRA tickety |
| **Celkový počet akčních kroků** | **303** | Navigace, kliknutí, formuláře, příprava |
| **Celkový počet ověření a kontrol** | **244** | Playwright `expect()` web-first aserce |

### 🧭 Rychlá navigace po modulech

- [🔐 **Autentizace a správa sezení (AUTH)**](#modul-auth) – `28 testů` (kroků: 145, kontrol: 96)
- [📚 **Katalog kurzů a detail běhů (CRS)**](#modul-crs) – `5 testů` (kroků: 18, kontrol: 29)
- [📝 **Zápis na kurz a Moje kurzy (ENR)**](#modul-enr) – `6 testů` (kroků: 39, kontrol: 45)
- [🎓 **Lektorská správa kurzů (LEC)**](#modul-lec) – `8 testů` (kroků: 40, kontrol: 44)
- [🧭 **Navigace a integrace stránek (NAV)**](#modul-nav) – `3 testů` (kroků: 14, kontrol: 8)
- [👤 **Uživatelský profil a nástěnka (PRF)**](#modul-prf) – `4 testů` (kroků: 20, kontrol: 11)
- [🛡️ **Bezpečnost, RBAC a architektura (SEC)**](#modul-sec) – `5 testů` (kroků: 27, kontrol: 11)

---

## 📑 Souhrnná tabulka všech testů

| ID testu | Název a cíl testu | Modul | Typ / Marker | Kroky | Kontroly | Soubor |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| [`TC-01-AUTH`](#tc-01-auth-sp-n-registrace-nov-ho-u-ivatele-a-kontrola-maskov-n-hesel) | Úspěšná registrace nového uživatele a kontrola maskování hesel. | `AUTH` | 🔥 Smoke | 5 | 6 | `tests/auth/test_register.py` |
| [`TC-01-AUTH`](#tc-01-auth-registrace-nov-ho-u-ivatele-odhl-en-a-n-sledn-p-ihl-en-kl-vesou-enter) | Registrace nového uživatele, odhlášení a následné přihlášení klávesou Enter. | `AUTH` | 🔥 Smoke | 12 | 3 | `tests/auth/test_register.py` |
| [`TC-01-AUTH`](#tc-01-auth-sp-n-registrace-z-kaznick-ho-tu-happy-path) | Úspěšná registrace zákaznického účtu (Happy Path). | `AUTH` | 🔥 Smoke | 5 | 8 | `tests/auth/test_register_experiment.py` |
| [`TC-02-AUTH`](#tc-02-auth-negativn-test-registrace-pokus-o-registraci-s-ji-obsazen-m-e-mailem) | Negativní test registrace – pokus o registraci s již obsazeným e-mailem. | `AUTH` | 🛡️ Regression | 3 | 3 | `tests/auth/test_register.py` |
| [`TC-03-AUTH`](#tc-03-auth-negativn-test-registrace-neshoda-hesel-a-pr-zdn-potvrzen) | Negativní test registrace – neshoda hesel a prázdné potvrzení. | `AUTH` | 🛡️ Regression | 4 | 3 | `tests/auth/test_register.py` |
| [`TC-04-AUTH`](#tc-04-auth-validace-povinn-ch-pol-p-i-odesl-n-pr-zdn-ho-formul-e) | Validace povinných polí při odeslání prázdného formuláře. | `AUTH` | 🛡️ Regression | 3 | 7 | `tests/auth/test_register.py` |
| [`TC-04-AUTH`](#tc-04-auth-negativn-test-registrace-heslo-krat-ne-8-znak) | Negativní test registrace – heslo kratší než 8 znaků. | `AUTH` | 🛡️ Regression | 4 | 3 | `tests/auth/test_register.py` |
| [`TC-04-AUTH`](#tc-04-auth-negativn-test-registrace-neplatn-form-t-e-mailov-adresy) | Negativní test registrace – neplatný formát e-mailové adresy. | `AUTH` | 🛡️ Regression | 4 | 4 | `tests/auth/test_register.py` |
| [`TC-05-AUTH`](#tc-05-auth-normalizace-e-mailu-o-ez-n-mezer-case-insensitive) | Normalizace e-mailu (ořezání mezer, case-insensitive). | `AUTH` | 🛡️ Regression | 12 | 3 | `tests/auth/test_register.py` |
| [`TC-06-AUTH`](#tc-06-auth-ov-en-sp-n-ho-p-ihl-en-u-ivatele-happy-path-a-jeho-varianty) | Ověření úspěšného přihlášení uživatele (Happy Path a jeho varianty). | `AUTH` | 🔥 Smoke | 9 | 5 | `tests/auth/test_login.py` |
| [`TC-06-AUTH`](#tc-06-auth-kontrola-metadat-str-nky-title-a-bezpe-nostn-ho-maskov-n-hesla) | Kontrola metadat stránky (<title>) a bezpečnostního maskování hesla. | `AUTH` | 🔥 Smoke | 2 | 2 | `tests/auth/test_login.py` |
| [`TC-06-AUTH`](#tc-06-auth-kontrola-v-choz-ho-stavu-ui-prvk-p-ihla-ovac-ho-formul-e) | Kontrola výchozího stavu UI prvků přihlašovacího formuláře. | `AUTH` | 🔥 Smoke | 2 | 5 | `tests/auth/test_login.py` |
| [`TC-07-AUTH`](#tc-07-auth-negativn-a-valida-n-test-pro-chybn-i-ne-pln-p-ihla-ovac-daje) | Negativní a validační test pro chybné či neúplné přihlašovací údaje. | `AUTH` | 🔥 Smoke | 10 | 2 | `tests/auth/test_login.py` |
| [`TC-08-AUTH`](#tc-08-auth-data-driven-ov-en-zamezen-odesl-n-p-i-neplatn-ch-form-tech-e-mailu-ze-souboru-data-invalid-emails-json) | Data-driven ověření zamezení odeslání při neplatných formátech e-mailu (ze souboru data/invalid_emails.json). | `AUTH` | 🛡️ Regression | 5 | 1 | `tests/auth/test_login.py` |
| [`TC-09-AUTH`](#tc-09-auth-ov-en-perzistence-p-ihl-en-po-obnoven-str-nky-reload-f5) | Ověření perzistence přihlášení po obnovení stránky (Reload / F5). | `AUTH` | 🔥 Smoke | 2 | 2 | `tests/auth/test_logout.py` |
| [`TC-10-AUTH`](#tc-10-auth-navigace-kl-vesnic-tab-enter-ve-formul-i) | Navigace klávesnicí (Tab + Enter) ve formuláři. | `AUTH` | 🛡️ Regression | 8 | 3 | `tests/auth/test_login.py` |
| [`TC-11-AUTH`](#tc-11-auth-e2e-test-kompletn-ho-ivotn-ho-cyklu-login-logout) | E2E test kompletního životního cyklu (Login -> Logout). | `AUTH` | 🔥 Smoke | 2 | 2 | `tests/auth/test_logout.py` |
| [`TC-12-AUTH`](#tc-12-auth-odesl-n-po-adavku-na-obnovu-zapomenut-ho-hesla-p-mo-p-es-page-object-dry-princip) | Odeslání požadavku na obnovu zapomenutého hesla přímo přes Page Object (DRY princip). | `AUTH` | 🛡️ Regression | 3 | 4 | `tests/auth/test_password_reset.py` |
| [`TC-13-AUTH`](#tc-13-auth-dost-o-reset-s-neplatn-m-pr-zdn-m-e-mailem) | Žádost o reset s neplatným / prázdným e-mailem. | `AUTH` | 🛡️ Regression | 5 | 3 | `tests/auth/test_password_reset.py` |
| [`TC-14-AUTH`](#tc-14-auth-sp-n-zm-na-hesla-pomoc-platn-ho-tokenu) | Úspěšná změna hesla pomocí platného tokenu. | `AUTH` | 🛡️ Regression (⚠️ BR-03) | 4 | 4 | `tests/auth/test_password_reset.py` |
| [`TC-15-AUTH`](#tc-15-auth-pokus-o-zm-nu-hesla-s-neplatn-m-nebo-expirovan-m-tokenem) | Pokus o změnu hesla s neplatným nebo expirovaným tokenem. | `AUTH` | 🛡️ Regression | 2 | 2 | `tests/auth/test_password_reset.py` |
| [`TC-16-AUTH`](#tc-16-auth-zm-na-hesla-s-neshodn-m-potvrzen-m-nov-ho-hesla) | Změna hesla s neshodným potvrzením nového hesla. | `AUTH` | 🛡️ Regression (⚠️ BR-03) | 3 | 3 | `tests/auth/test_password_reset.py` |
| [`TC-16-AUTH`](#tc-16-auth-zm-na-hesla-s-heslem-nespl-uj-c-m-minim-ln-d-lku-8-znak) | Změna hesla s heslem nesplňujícím minimální délku 8 znaků. | `AUTH` | 🛡️ Regression (⚠️ BR-03) | 3 | 3 | `tests/auth/test_password_reset.py` |
| [`TC-17-AUTH`](#tc-17-auth-sp-n-ov-en-e-mailu-p-es-platn-odkaz) | Úspěšné ověření e-mailu přes platný odkaz. | `AUTH` | 🛡️ Regression | 2 | 1 | `tests/auth/test_password_reset.py` |
| [`TC-18-AUTH`](#tc-18-auth-pokus-o-ov-en-e-mailu-s-neplatn-m-odkazem) | Pokus o ověření e-mailu s neplatným odkazem. | `AUTH` | 🛡️ Regression | 2 | 1 | `tests/auth/test_password_reset.py` |
| [`TC-19-AUTH`](#tc-19-auth-znovuzasl-n-ov-ovac-ho-e-mailu-a-asov-limit) | Znovuzaslání ověřovacího e-mailu a časový limit. | `AUTH` | 🛡️ Regression | 2 | 1 | `tests/auth/test_password_reset.py` |
| [`TC-20-AUTH`](#tc-20-auth-do-asn-blokace-po-5-ne-sp-n-ch-pokusech-o-p-ihl-en) | Dočasná blokace po 5 neúspěšných pokusech o přihlášení. | `AUTH` | 🔥 Smoke | 11 | 4 | `tests/auth/test_login.py` |
| [`TC-21-AUTH`](#tc-21-auth-vynulov-n-po-tadla-ne-sp-ch-po-sp-n-m-p-ihl-en) | Vynulování počítadla neúspěchů po úspěšném přihlášení. | `AUTH` | 🛡️ Regression | 16 | 8 | `tests/auth/test_login.py` |
| [`TC-22-CRS`](#tc-22-crs-zobrazen-katalogu-kurz-pro-nep-ihl-en-ho-n-v-t-vn-ka) | Zobrazení katalogu kurzů pro nepřihlášeného návštěvníka. | `CRS` | 🔥 Smoke | 2 | 4 | `tests/courses/test_courses.py` |
| [`TC-23-CRS`](#tc-23-crs-ov-en-zobrazen-atribut-kurzu-v-katalogu) | Ověření zobrazení atributů kurzu v katalogu. | `CRS` | 🛡️ Regression | 3 | 7 | `tests/courses/test_courses.py` |
| [`TC-24-CRS`](#tc-24-crs-zobrazen-detailu-kurzu-a-seznamu-vypsan-ch-term-n) | Zobrazení detailu kurzu a seznamu vypsaných termínů. | `CRS` | 🔥 Smoke | 4 | 10 | `tests/courses/test_courses.py` |
| [`TC-25-CRS`](#tc-25-crs-zobrazen-tla-tka-z-pisu-u-term-nu-s-volnou-kapacitou-pro-p-ihl-en-ho-z-kazn-ka) | Zobrazení tlačítka zápisu u termínu s volnou kapacitou pro přihlášeného zákazníka. | `CRS` | 🔥 Smoke | 5 | 4 | `tests/courses/test_courses.py` |
| [`TC-26-CRS`](#tc-26-crs-zamezen-registrace-a-indikace-pln-obsazen-ho-b-hu-i-v-zva-pro-nep-ihl-en-ho) | Zamezení registrace a indikace plně obsazeného běhu i výzva pro nepřihlášeného. | `CRS` | 🛡️ Regression | 4 | 4 | `tests/courses/test_courses.py` |
| [`TC-27-ENR`](#tc-27-enr-sp-n-z-pis-na-kurz-s-platn-m-telefonem-a-platn-m-i-o) | Úspěšný zápis na kurz s platným telefonem a platným IČO. | `ENR` | 🔥 Smoke | 11 | 9 | `tests/enrollment/test_enrollment.py` |
| [`TC-28-ENR`](#tc-28-enr-sp-n-z-pis-na-kurz-bez-vypln-n-ho-i-o-i-o-je-nepovinn) | Úspěšný zápis na kurz bez vyplněného IČO (IČO je nepovinné). | `ENR` | 🛡️ Regression (⚠️ xfail) | 8 | 6 | `tests/enrollment/test_enrollment.py` |
| [`TC-29-ENR`](#tc-29-enr-z-pis-s-neplatn-m-i-o-chyba-kontroln-ho-sou-tu-modulo-11) | Zápis s neplatným IČO (chyba kontrolního součtu modulo 11). | `ENR` | 🛡️ Regression | 7 | 2 | `tests/enrollment/test_enrollment.py` |
| [`TC-30-ENR`](#tc-30-enr-z-pis-s-neplatn-m-telefonem-m-n-ne-9-slic) | Zápis s neplatným telefonem (méně než 9 číslic). | `ENR` | 🛡️ Regression | 6 | 2 | `tests/enrollment/test_enrollment.py` |
| [`TC-31-ENR`](#tc-31-enr-zobrazen-p-ehledu-m-ch-zapsan-ch-kurz-a-detailu-lekc) | Zobrazení přehledu mých zapsaných kurzů a detailu lekcí. | `ENR` | 🔥 Smoke | 4 | 20 | `tests/enrollment/test_enrollment.py` |
| [`TC-48-ENR`](#tc-48-enr-zobrazen-sekce-moje-kurzy-bez-aktivn-ch-z-pis-empty-state) | Zobrazení sekce Moje kurzy bez aktivních zápisů (Empty State). | `ENR` | 🛡️ Regression | 3 | 6 | `tests/enrollment/test_enrollment.py` |
| [`TC-32-LEC`](#tc-32-lec-vytvo-en-nov-ho-kurzu-s-n-hledem-s-pom-rem-stran-16-9) | Vytvoření nového kurzu s náhledem s poměrem stran 16:9. | `LEC` | 🔥 Smoke | 4 | 6 | `tests/lecturer/test_lecturer.py` |
| [`TC-33-LEC`](#tc-33-lec-odm-tnut-n-hledov-ho-obr-zku-s-nevyhovuj-c-m-pom-rem-stran) | Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran. | `LEC` | 🛡️ Regression (⚠️ xfail) | 5 | 1 | `tests/lecturer/test_lecturer.py` |
| [`TC-34-LEC`](#tc-34-lec-validace-povinn-ch-pol-a-seln-kapacity-ceny-kurzu) | Validace povinných polí a číselné kapacity/ceny kurzu. | `LEC` | 🛡️ Regression (⚠️ xfail) | 7 | 2 | `tests/lecturer/test_lecturer.py` |
| [`TC-35-LEC`](#tc-35-lec-sp-n-vyps-n-nov-ho-term-nu-kurzu-lektorem) | Úspěšné vypsání nového termínu kurzu lektorem. | `LEC` | 🛡️ Regression | 6 | 5 | `tests/lecturer/test_lecturer.py` |
| [`TC-36-LEC`](#tc-36-lec-validace-povinn-ch-pol-p-i-vyps-n-term-nu) | Validace povinných polí při vypsání termínu. | `LEC` | 🛡️ Regression (⚠️ xfail) | 4 | 2 | `tests/lecturer/test_lecturer.py` |
| [`TC-37-LEC`](#tc-37-lec-sp-n-p-ihl-en-lektora-a-ov-en-lektorsk-ch-pr-v-p-idat-kurz) | Úspěšné přihlášení lektora a ověření lektorských práv (přidat kurz). | `LEC` | 🔥 Smoke | 5 | 7 | `tests/auth/test_login.py` |
| [`TC-37-LEC`](#tc-37-lec-zobrazen-detailu-kurzu-a-ov-en-tabulky-astn-k-se-sloupci-jm-no-email-telefon-a-i-o) | Zobrazení detailu kurzu a ověření tabulky účastníků se sloupci Jméno, Email, Telefon a IČO. | `LEC` | 🔥 Smoke | 5 | 20 | `tests/lecturer/test_lecturer.py` |
| [`TC-38-LEC`](#tc-38-lec-zamezen-p-stupu-k-lektorsk-m-operac-m-pro-b-n-ho-z-kazn-ka) | Zamezení přístupu k lektorským operacím pro běžného zákazníka. | `LEC` | 🔥 Smoke (⚠️ BR-01) | 4 | 1 | `tests/lecturer/test_lecturer.py` |
| [`TC-01-NAV`](#tc-01-nav-integra-n-test-p-echod-z-p-ehledu-kurz-na-p-ihl-en-a-n-vrat-zp-t) | Integrační test – přechod z přehledu kurzů na přihlášení a návrat zpět. | `NAV` | 🔥 Smoke | 5 | 3 | `tests/navigation/test_navigation.py` |
| [`TC-02-NAV`](#tc-02-nav-funk-nost-dopl-kov-ch-odkaz-ve-spodn-sti-p-ihla-ovac-ho-formul-e-login-forgot-password-register) | Funkčnost doplňkových odkazů ve spodní části přihlašovacího formuláře (/login -> /forgot-password, /register). | `NAV` | 🛡️ Regression | 5 | 2 | `tests/navigation/test_navigation.py` |
| [`TC-03-NAV`](#tc-03-nav-n-vratov-odkaz-p-ihl-sit-se-z-registra-n-str-nky-zp-t-na-p-ihl-en-register-login) | Návratový odkaz 'Přihlásit se' z registrační stránky zpět na přihlášení (/register -> /login). | `NAV` | 🔥 Smoke | 4 | 3 | `tests/navigation/test_navigation.py` |
| [`TC-39-PRF`](#tc-39-prf-zobrazen-personalizovan-ho-uv-t-n-na-domovsk-n-st-nce) | Zobrazení personalizovaného uvítání na domovské nástěnce. | `PRF` | 🔥 Smoke | 2 | 2 | `tests/profile/test_profile.py` |
| [`TC-40-PRF`](#tc-40-prf-p-edvypln-n-daj-sp-n-aktualizace-profilu-a-p-esm-rov-n-na-home) | Předvyplnění údajů, úspěšná aktualizace profilu a přesměrování na /home. | `PRF` | 🔥 Smoke | 9 | 7 | `tests/profile/test_profile.py` |
| [`TC-41-PRF`](#tc-41-prf-validace-form-tu-i-o-a-telefonu-v-profilu) | Validace formátu IČO a telefonu v profilu. | `PRF` | 🛡️ Regression | 4 | 1 | `tests/profile/test_profile.py` |
| [`TC-42-PRF`](#tc-42-prf-pokus-o-zm-nu-e-mailu-na-ji-obsazenou-adresu-je-odm-tnut) | Pokus o změnu e-mailu na již obsazenou adresu je odmítnut. | `PRF` | 🛡️ Regression | 5 | 1 | `tests/profile/test_profile.py` |
| [`TC-43-SEC`](#tc-43-sec-p-esm-rov-n-nep-ihl-en-ho-u-ivatele-z-priv-tn-ch-url-na-katalog) | Přesměrování nepřihlášeného uživatele z privátních URL na katalog. | `SEC` | 🔥 Smoke | 4 | 3 | `tests/security/test_security.py` |
| [`TC-44-SEC`](#tc-44-sec-z-kaz-lektorsk-ch-operac-pro-u-ivatele-v-roli-z-kazn-ka) | Zákaz lektorských operací pro uživatele v roli zákazníka. | `SEC` | 🔥 Smoke (⚠️ BR-01) | 4 | 1 | `tests/security/test_security.py` |
| [`TC-45-SEC`](#tc-45-sec-z-kaz-z-pisu-na-kurz-pro-u-ivatele-v-roli-lektora) | Zákaz zápisu na kurz pro uživatele v roli lektora. | `SEC` | 🛡️ Regression | 2 | 2 | `tests/security/test_security.py` |
| [`TC-46-SEC`](#tc-46-sec-ochrana-formul-csrf-tokenem-p-tomnost-xsrf-token) | Ochrana formulářů CSRF tokenem (přítomnost XSRF-TOKEN). | `SEC` | 🔥 Smoke | 6 | 1 | `tests/security/test_security.py` |
| [`TC-47-SEC`](#tc-47-sec-regenerace-session-id-p-i-p-ihl-en-a-odhl-en-ochrana-proti-session-fixation) | Regenerace session ID při přihlášení a odhlášení (ochrana proti Session Fixation). | `SEC` | 🛡️ Regression | 11 | 4 | `tests/security/test_security.py` |

---

## 🔍 Detailní rozpad kroků a kontrol jednotlivých testů

<a id="modul-auth"></a>
### 🔐 Modul: Autentizace a správa sezení (AUTH)

*Počet testů v modulu: **28** | Celkem akcí: **145** | Celkem kontrol: **96***

<a id="tc-01-auth-sp-n-registrace-nov-ho-u-ivatele-a-kontrola-maskov-n-hesel"></a>
#### `TC-01-AUTH`: Úspěšná registrace nového uživatele a kontrola maskování hesel.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc01_auth_successful_registration_and_password_masking()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:27`](tests/auth/test_register.py#L27) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `HomePage(page)` do proměnné `home_page`
   `home_page = HomePage(page)`
3. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_user()` -> `new_user`
   `new_user = generate_random_user()`
4. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
5. **🔍 Kontrola:** Ověření HTML atributu prvku `register_page.password_input` ('type', 'password') — *(Bezpečnostní kontrola typu password)*
   `expect(register_page.password_input).to_have_attribute("type", "password")`
6. **🔍 Kontrola:** Ověření HTML atributu prvku `register_page.password_again_input` ('type', 'password')
   `expect(register_page.password_again_input).to_have_attribute("type", "password")`
7. **▶️ Krok:** Vyvolání akce `register_page.register()` — *(Registrace)*
   `register_page.register( name=new_user["name"], email=new_user["email"], password=new_user["password"], password_again=new_user["password"] )`
8. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: home_page.URL) — *(Ověření uvítání na /home přes HomePage model)*
   `expect(page).to_have_url(home_page.URL, timeout=10000)`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `home_page.welcome_section` na stránce
   `expect(home_page.welcome_section).to_be_visible()`
10. **🔍 Kontrola:** Ověření, že text prvku `home_page.welcome_section` obsahuje ...
   `expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {new_user['name']}!")`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `home_page.navbar.logout_button` na stránce — *(Ověření přihlášeného stavu přes sdílenou navbar komponentu)*
   `expect(home_page.navbar.logout_button).to_be_visible()`

<a id="tc-01-auth-registrace-nov-ho-u-ivatele-odhl-en-a-n-sledn-p-ihl-en-kl-vesou-enter"></a>
#### `TC-01-AUTH`: Registrace nového uživatele, odhlášení a následné přihlášení klávesou Enter.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc01_auth_registration_and_subsequent_login_with_enter_key()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:158`](tests/auth/test_register.py#L158) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `HomePage(page)` do proměnné `home_page`
   `home_page = HomePage(page)`
3. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
4. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
5. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_user()` -> `new_user`
   `new_user = generate_random_user(name_prefix="Novy Student")`
6. **🌐 Navigace:** Otevření stránky `register_page` — *(1. Registrace)*
   `register_page.open()`
7. **▶️ Krok:** Vyvolání akce `register_page.register(new_user['name'], new_user['email'], new_user['password'], new_user['password'])`
   `register_page.register(new_user["name"], new_user["email"], new_user["password"], new_user["password"])`
8. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: home_page.URL)
   `expect(page).to_have_url(home_page.URL, timeout=10000)`
9. **🚪 Odhlášení:** Odhlášení uživatele z portálu — *(2. Odhlášení přes sdílený helper (DRY))*
   `logout_user(page)`
10. **🌐 Navigace:** Otevření stránky `login_page` — *(3. Přihlášení přes Enter)*
   `login_page.open()`
11. **✍️ Vstup:** Vyplnění pole `email` hodnotou new_user['email']
   `login_page.fill_email(new_user["email"])`
12. **✍️ Vstup:** Vyplnění pole `password` hodnotou new_user['password']
   `login_page.fill_password(new_user["password"])`
13. **⌨️ Klávesa:** Stisk klávesy 'Enter' v rámci `login_page.password_input`
   `login_page.password_input.press("Enter")`
14. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL) — *(4. Ověření)*
   `expect(page).to_have_url(courses_page.URL, timeout=10000)`
15. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce
   `expect(courses_page.logout_button).to_be_visible()`

<a id="tc-01-auth-sp-n-registrace-z-kaznick-ho-tu-happy-path"></a>
#### `TC-01-AUTH`: Úspěšná registrace zákaznického účtu (Happy Path).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc01_auth_successful_registration()` |
| **Testovací třída** | `TestRegistrationExperiment` |
| **Zdrojový soubor** | [`tests/auth/test_register_experiment.py:20`](tests/auth/test_register_experiment.py#L20) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page` — *(Arrange – Příprava testovacího prostředí, Page Objectů a dynamických dat)*
   `register_page = RegisterPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `HomePage(page)` do proměnné `home_page`
   `home_page = HomePage(page)`
3. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_user()` -> `new_user`
   `new_user = generate_random_user(name_prefix="Jan Novák")`
4. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.name_input` na stránce — *(Krok 1: Kontrola viditelnosti polí formuláře)*
   `expect(register_page.name_input).to_be_visible()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.email_input` na stránce
   `expect(register_page.email_input).to_be_visible()`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.password_input` na stránce
   `expect(register_page.password_input).to_be_visible()`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.password_again_input` na stránce
   `expect(register_page.password_again_input).to_be_visible()`
9. **▶️ Krok:** Vyvolání akce `register_page.register()` — *(Act – Vyplnění údajů a odeslání registračního formuláře (Kroky 2-6))*
   `register_page.register( name=new_user["name"], email=new_user["email"], password=new_user["password"], password_again=new_user["password"], )`
10. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: home_page.URL) — *(Assert – 3úrovňová validační pyramida (Routing, Session, Data State) | 1. Úroveň: Routing – Přesměrování na domovskou stránku /home)*
   `expect(page).to_have_url(home_page.URL)`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `home_page.navbar.logout_button` na stránce — *(2. Úroveň: Session State – Uživatel je přihlášen (zobrazeno tlačítko odhlášení))*
   `expect(home_page.navbar.logout_button).to_be_visible()`
12. **🔍 Kontrola:** Ověření viditelnosti prvku `home_page.welcome_section` na stránce — *(3. Úroveň: Data State & UI Feedback – Uvítací zpráva s personalizovaným jménem)*
   `expect(home_page.welcome_section).to_be_visible()`
13. **🔍 Kontrola:** Ověření, že text prvku `home_page.welcome_section` obsahuje ...
   `expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {new_user['name']}!")`

<a id="tc-02-auth-negativn-test-registrace-pokus-o-registraci-s-ji-obsazen-m-e-mailem"></a>
#### `TC-02-AUTH`: Negativní test registrace – pokus o registraci s již obsazeným e-mailem.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc02_auth_registration_duplicate_email()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:141`](tests/auth/test_register.py#L141) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
3. **▶️ Krok:** Vyvolání akce `register_page.register()`
   `register_page.register( name="Duplicitni Lektor", email=lecturer_user["email"], password="PlatneHeslo123", password_again="PlatneHeslo123" )`
4. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: register_page.URL)
   `expect(page).to_have_url(register_page.URL)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.email_error` na stránce
   `expect(register_page.email_error).to_be_visible()`
6. **🔍 Kontrola:** Ověření přesného textu prvku `register_page.email_error` (očekáváno: 'The email has already been taken.')
   `expect(register_page.email_error).to_have_text("The email has already been taken.")`

<a id="tc-03-auth-negativn-test-registrace-neshoda-hesel-a-pr-zdn-potvrzen"></a>
#### `TC-03-AUTH`: Negativní test registrace – neshoda hesel a prázdné potvrzení.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc03_auth_registration_password_mismatch_and_empty_confirmation()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:81`](tests/auth/test_register.py#L81) |
| **Pytest Markery** | `@auth`, `@regression`, `@parametrize` |
| **Data-driven varianty** | Parametry: `'password_again_value, scenario_id'`, Scénáře: `['different-password', 'empty-password-again']` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_email()` -> `test_email`
   `test_email = generate_random_email(prefix=f"mismatch_{scenario_id}")`
3. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
4. **▶️ Krok:** Vyvolání akce `register_page.register()`
   `register_page.register( name="Test Potvrzeni Hesla", email=test_email, password="HesloPrvni123", password_again=password_again_value )`
5. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: register_page.URL)
   `expect(page).to_have_url(register_page.URL)`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.password_error` na stránce
   `expect(register_page.password_error).to_be_visible()`
7. **🔍 Kontrola:** Ověření přesného textu prvku `register_page.password_error` (očekáváno: 'The password field confirmation does not match.')
   `expect(register_page.password_error).to_have_text("The password field confirmation does not match.")`

<a id="tc-04-auth-validace-povinn-ch-pol-p-i-odesl-n-pr-zdn-ho-formul-e"></a>
#### `TC-04-AUTH`: Validace povinných polí při odeslání prázdného formuláře.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc04_auth_registration_required_fields_validation()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:56`](tests/auth/test_register.py#L56) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
3. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `register_page_register`
   `register_page.click_register()`
4. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: register_page.URL)
   `expect(page).to_have_url(register_page.URL)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.name_error` na stránce
   `expect(register_page.name_error).to_be_visible()`
6. **🔍 Kontrola:** Ověření přesného textu prvku `register_page.name_error` (očekáváno: 'The name field is required.')
   `expect(register_page.name_error).to_have_text("The name field is required.")`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.email_error` na stránce
   `expect(register_page.email_error).to_be_visible()`
8. **🔍 Kontrola:** Ověření přesného textu prvku `register_page.email_error` (očekáváno: 'The email field is required.')
   `expect(register_page.email_error).to_have_text("The email field is required.")`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.password_error` na stránce
   `expect(register_page.password_error).to_be_visible()`
10. **🔍 Kontrola:** Ověření přesného textu prvku `register_page.password_error` (očekáváno: 'The password field is required.')
   `expect(register_page.password_error).to_have_text("The password field is required.")`

<a id="tc-04-auth-negativn-test-registrace-heslo-krat-ne-8-znak"></a>
#### `TC-04-AUTH`: Negativní test registrace – heslo kratší než 8 znaků.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc04_auth_registration_short_password()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:101`](tests/auth/test_register.py#L101) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_email()` -> `test_email`
   `test_email = generate_random_email(prefix="short")`
3. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
4. **▶️ Krok:** Vyvolání akce `register_page.register()`
   `register_page.register( name="Kratke Heslo", email=test_email, password="12345", password_again="12345" )`
5. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: register_page.URL)
   `expect(page).to_have_url(register_page.URL)`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.password_error` na stránce
   `expect(register_page.password_error).to_be_visible()`
7. **🔍 Kontrola:** Ověření přesného textu prvku `register_page.password_error` (očekáváno: 'The password field must be at least 8 characters.')
   `expect(register_page.password_error).to_have_text("The password field must be at least 8 characters.")`

<a id="tc-04-auth-negativn-test-registrace-neplatn-form-t-e-mailov-adresy"></a>
#### `TC-04-AUTH`: Negativní test registrace – neplatný formát e-mailové adresy.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc04_auth_registration_invalid_email_format()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:119`](tests/auth/test_register.py#L119) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
3. **▶️ Krok:** Vyvolání akce `register_page.register()` — *(Pokus o odeslání registrace s e-mailem bez zavináče a domény)*
   `register_page.register( name="Neplatny Email", email="neplatny_email_bez_zavinace", password="PlatneHeslo123", password_again="PlatneHeslo123" )`
4. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: register_page.URL) — *(Formulář se neodešle (zůstává na URL registrace))*
   `expect(page).to_have_url(register_page.URL)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.register_button` na stránce
   `expect(register_page.register_button).to_be_visible()`
6. **🔍 Kontrola:** Ověření HTML atributu prvku `register_page.email_input` ('type', 'email') — *(Ověření klientské HTML5 validace pole typu email)*
   `expect(register_page.email_input).to_have_attribute("type", "email")`
7. **⚙️ Příprava:** Nastavení lokální proměnné `is_valid` = `register_page.email_input.evaluate('el => el.checkValidity()')`
   `is_valid = register_page.email_input.evaluate("el => el.checkValidity()")`
8. **🔍 Kontrola:** Ověření podmínky datového stavu: `assert is_valid is False`
   `assert is_valid is False`

<a id="tc-05-auth-normalizace-e-mailu-o-ez-n-mezer-case-insensitive"></a>
#### `TC-05-AUTH`: Normalizace e-mailu (ořezání mezer, case-insensitive).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc05_auth_email_normalization_on_registration()` |
| **Testovací třída** | `TestRegistration` |
| **Zdrojový soubor** | [`tests/auth/test_register.py:186`](tests/auth/test_register.py#L186) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page` — *(===================================================================== | 1. ARRANGE | =====================================================================)*
   `register_page = RegisterPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `HomePage(page)` do proměnné `home_page`
   `home_page = HomePage(page)`
3. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
4. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
5. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_user()` -> `base_user`
   `base_user = generate_random_user(name_prefix="Normalizace User")`
6. **⚙️ Příprava:** Nastavení lokální proměnné `clean_email` = `base_user['email'].lower()`
   `clean_email = base_user["email"].lower()`
7. **⚙️ Příprava:** Nastavení lokální proměnné `padded_email` = `...`
   `padded_email = f"  {clean_email.upper()}  "`
8. **🌐 Navigace:** Otevření stránky `register_page` — *(===================================================================== | 2. ACT | ===================================================================== | 1. Registrace s mezerami a velkými písmeny)*
   `register_page.open()`
9. **▶️ Krok:** Vyvolání akce `register_page.register()`
   `register_page.register( name=base_user["name"], email=padded_email, password=base_user["password"], password_again=base_user["password"] )`
10. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: home_page.URL)
   `expect(page).to_have_url(home_page.URL, timeout=10000)`
11. **🚪 Odhlášení:** Odhlášení uživatele z portálu — *(2. Odhlášení)*
   `logout_user(page)`
12. **🌐 Navigace:** Otevření stránky `login_page` — *(3. Přihlášení s čistým malým e-mailem bez mezer)*
   `login_page.open()`
13. **🔑 Autentizace:** Provedení přihlášení uživatele (clean_email, base_user['password'])
   `login_page.login(clean_email, base_user["password"])`
14. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL) — *(===================================================================== | 3. ASSERT | =====================================================================)*
   `expect(page).to_have_url(courses_page.URL, timeout=10000)`
15. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce
   `expect(courses_page.logout_button).to_be_visible()`

<a id="tc-06-auth-ov-en-sp-n-ho-p-ihl-en-u-ivatele-happy-path-a-jeho-varianty"></a>
#### `TC-06-AUTH`: Ověření úspěšného přihlášení uživatele (Happy Path a jeho varianty).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc06_auth_successful_login_variants()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:41`](tests/auth/test_login.py#L41) |
| **Pytest Markery** | `@auth`, `@smoke`, `@parametrize` |
| **Data-driven varianty** | Parametry: `'email_transformer, submit_method, test_id'`, Scénáře: `['standard-click', 'enter-key', 'uppercase-email', ...]` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
3. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.heading` na stránce
   `expect(login_page.heading).to_be_visible()`
5. **🔍 Kontrola:** Ověření přesného textu prvku `login_page.heading` (očekáváno: 'Přihlášení')
   `expect(login_page.heading).to_have_text("Přihlášení")`
6. **⚙️ Příprava:** Nastavení lokální proměnné `email_to_use` = `email_transformer(test_user['email'])`
   `email_to_use = email_transformer(test_user["email"])`
7. **✍️ Vstup:** Vyplnění pole `email` hodnotou email_to_use
   `login_page.fill_email(email_to_use)`
8. **✍️ Vstup:** Vyplnění pole `password` hodnotou test_user['password']
   `login_page.fill_password(test_user["password"])`
9. **🔀 Větvení:** Podmíněná větev: pokud platí `submit_method ...`
   `if submit_method ...:`
  1. **⌨️ Klávesa:** Stisk klávesy 'Enter' v rámci `login_page.password_input`
     `login_page.password_input.press("Enter")`
   *Jinak:*
  1. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `login_page_login`
     `login_page.click_login()`
10. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL)
   `expect(page).to_have_url(courses_page.URL, timeout=10000)`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce
   `expect(courses_page.logout_button).to_be_visible(timeout=5000)`
12. **🔍 Kontrola:** Ověření přesného textu prvku `courses_page.logout_button` (očekáváno: 'Odhlásit se')
   `expect(courses_page.logout_button).to_have_text("Odhlásit se")`

<a id="tc-06-auth-kontrola-metadat-str-nky-title-a-bezpe-nostn-ho-maskov-n-hesla"></a>
#### `TC-06-AUTH`: Kontrola metadat stránky (<title>) a bezpečnostního maskování hesla.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc06_auth_title_and_password_masking()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:154`](tests/auth/test_login.py#L154) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
3. **🔍 Kontrola:** Ověření titulku webové stránky `<title>` (očekáváno: 'Testování - přihlášení')
   `expect(page).to_have_title("Testování - přihlášení")`
4. **🔍 Kontrola:** Ověření HTML atributu prvku `login_page.password_input` ('type', 'password')
   `expect(login_page.password_input).to_have_attribute("type", "password")`

<a id="tc-06-auth-kontrola-v-choz-ho-stavu-ui-prvk-p-ihla-ovac-ho-formul-e"></a>
#### `TC-06-AUTH`: Kontrola výchozího stavu UI prvků přihlašovacího formuláře.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc06_auth_form_ui_elements_state()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:163`](tests/auth/test_login.py#L163) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
3. **🔍 Kontrola:** Ověření HTML atributu prvku `login_page.email_input` ('placeholder', 'Email')
   `expect(login_page.email_input).to_have_attribute("placeholder", "Email")`
4. **🔍 Kontrola:** Ověření, že prvek `login_page.email_input` je aktivní a povolený (enabled)
   `expect(login_page.email_input).to_be_enabled()`
5. **🔍 Kontrola:** Ověření, že prvek `login_page.password_input` je aktivní a povolený (enabled)
   `expect(login_page.password_input).to_be_enabled()`
6. **🔍 Kontrola:** Ověření přesného textu prvku `login_page.login_button` (očekáváno: 'Přihlásit')
   `expect(login_page.login_button).to_have_text("Přihlásit")`
7. **🔍 Kontrola:** Ověření, že prvek `login_page.login_button` je aktivní a povolený (enabled)
   `expect(login_page.login_button).to_be_enabled()`

<a id="tc-07-auth-negativn-a-valida-n-test-pro-chybn-i-ne-pln-p-ihla-ovac-daje"></a>
#### `TC-07-AUTH`: Negativní a validační test pro chybné či neúplné přihlašovací údaje.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc07_auth_invalid_and_incomplete_login_credentials()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:106`](tests/auth/test_login.py#L106) |
| **Pytest Markery** | `@auth`, `@smoke`, `@parametrize` |
| **Data-driven varianty** | Parametry: `'email, password, error_field, expected_error_text'`, Scénáře: `['invalid-password', 'non-existent-user', 'empty-password-required', ...]` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
3. **🔀 Větvení:** Podmíněná větev: pokud platí `email`
   `if email:`
  1. **✍️ Vstup:** Vyplnění pole `email` hodnotou email
     `login_page.fill_email(email)`
4. **🔀 Větvení:** Podmíněná větev: pokud platí `password`
   `if password:`
  1. **✍️ Vstup:** Vyplnění pole `password` hodnotou password
     `login_page.fill_password(password)`
5. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `login_page_login`
   `login_page.click_login()`
6. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: login_page.URL)
   `expect(page).to_have_url(login_page.URL)`
7. **🔀 Větvení:** Podmíněná větev: pokud platí `error_field ...`
   `if error_field ...:`
  1. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.email_error` na stránce
     `expect(login_page.email_error).to_be_visible(timeout=5000)`
  2. **🔀 Větvení:** Podmíněná větev: pokud platí `expected_error_text`
     `if expected_error_text:`
    1. **🔍 Kontrola:** Ověření přesného textu prvku `login_page.email_error` (očekáváno: expected_error_text)
       `expect(login_page.email_error).to_have_text(expected_error_text)`
   *Jinak:*
  1. **🔀 Větvení:** Podmíněná větev: pokud platí `error_field ...`
     `if error_field ...:`
    1. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.password_error` na stránce
       `expect(login_page.password_error).to_be_visible(timeout=5000)`
    2. **🔀 Větvení:** Podmíněná větev: pokud platí `expected_error_text`
       `if expected_error_text:`
      1. **🔍 Kontrola:** Ověření přesného textu prvku `login_page.password_error` (očekáváno: expected_error_text)
         `expect(login_page.password_error).to_have_text(expected_error_text)`

<a id="tc-08-auth-data-driven-ov-en-zamezen-odesl-n-p-i-neplatn-ch-form-tech-e-mailu-ze-souboru-data-invalid-emails-json"></a>
#### `TC-08-AUTH`: Data-driven ověření zamezení odeslání při neplatných formátech e-mailu (ze souboru data/invalid_emails.json).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc08_auth_invalid_email_format_validation()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:137`](tests/auth/test_login.py#L137) |
| **Pytest Markery** | `@auth`, `@regression`, `@parametrize` |
| **Data-driven varianty** | Parametry: `'item'`, Scénáře: `...` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
3. **✍️ Vstup:** Vyplnění pole `email` hodnotou item['email']
   `login_page.fill_email(item["email"])`
4. **✍️ Vstup:** Vyplnění pole `password` hodnotou 'PlatneHeslo123'
   `login_page.fill_password("PlatneHeslo123")`
5. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `login_page_login`
   `login_page.click_login()`
6. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: login_page.URL) — *(Uživatel musí zůstat na přihlašovací stránce (prohlížeč zamezí odeslání nevalidního e-mailu))*
   `expect(page).to_have_url(login_page.URL)`

<a id="tc-09-auth-ov-en-perzistence-p-ihl-en-po-obnoven-str-nky-reload-f5"></a>
#### `TC-09-AUTH`: Ověření perzistence přihlášení po obnovení stránky (Reload / F5).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc09_auth_session_persists_after_page_reload()` |
| **Testovací třída** | `TestLogoutAndSession` |
| **Zdrojový soubor** | [`tests/auth/test_logout.py:33`](tests/auth/test_logout.py#L33) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Přihlášení uživatele přes pomocný helper: `login_user(page, test_user['email'], ...)` -> `courses_page` — *(1. Přihlášení přes sdílený helper (DRY princip))*
   `courses_page = login_user(page, test_user["email"], test_user["password"])`
2. **🔄 Obnovení:** Obnovení aktuální stránky v prohlížeči (Reload / F5) — *(2. Obnovení stránky)*
   `page.reload()`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce — *(3. Ověření, že uživatel zůstal přihlášen)*
   `expect(courses_page.logout_button).to_be_visible(timeout=5000)`
4. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL)
   `expect(page).to_have_url(courses_page.URL)`

<a id="tc-10-auth-navigace-kl-vesnic-tab-enter-ve-formul-i"></a>
#### `TC-10-AUTH`: Navigace klávesnicí (Tab + Enter) ve formuláři.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc10_auth_keyboard_navigation_tab_and_enter()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:262`](tests/auth/test_login.py#L262) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page` — *(===================================================================== | 1. ARRANGE | =====================================================================)*
   `login_page = LoginPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
3. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
4. **▶️ Krok:** Vyvolání akce `login_page.email_input.focus()` — *(===================================================================== | 2. ACT | ===================================================================== | 1. Zafokusovat e-mail a zadat text)*
   `login_page.email_input.focus()`
5. **✍️ Vstup:** Simulace psaní na klávesnici: test_user['email']
   `page.keyboard.type(test_user["email"])`
6. **⌨️ Klávesa:** Stisk klávesy 'Tab' v rámci `page.keyboard` — *(2. Stisknout Tab pro přechod na heslo)*
   `page.keyboard.press("Tab")`
7. **🔍 Kontrola:** Ověření fokusu na poli / prvku `login_page.password_input`
   `expect(login_page.password_input).to_be_focused()`
8. **✍️ Vstup:** Simulace psaní na klávesnici: test_user['password'] — *(3. Napsat heslo a odeslat klávesou Enter)*
   `page.keyboard.type(test_user["password"])`
9. **⌨️ Klávesa:** Stisk klávesy 'Enter' v rámci `page.keyboard`
   `page.keyboard.press("Enter")`
10. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL) — *(===================================================================== | 3. ASSERT | =====================================================================)*
   `expect(page).to_have_url(courses_page.URL, timeout=10000)`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce
   `expect(courses_page.logout_button).to_be_visible()`

<a id="tc-11-auth-e2e-test-kompletn-ho-ivotn-ho-cyklu-login-logout"></a>
#### `TC-11-AUTH`: E2E test kompletního životního cyklu (Login -> Logout).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc11_auth_login_and_logout_lifecycle()` |
| **Testovací třída** | `TestLogoutAndSession` |
| **Zdrojový soubor** | [`tests/auth/test_logout.py:20`](tests/auth/test_logout.py#L20) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Přihlášení uživatele přes pomocný helper: `login_user(page, test_user['email'], ...)` -> `courses_page` — *(1. Přihlášení přes sdílený helper (DRY princip))*
   `courses_page = login_user(page, test_user["email"], test_user["password"])`
2. **🚪 Odhlášení:** Odhlášení uživatele z portálu — *(2. Odhlášení)*
   `courses_page.logout()`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.login_link` na stránce — *(3. Ověření ukončení relace (nejprve pozitivní indikátor ustálení nového stavu))*
   `expect(courses_page.login_link).to_be_visible()`
4. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `courses_page.logout_button`
   `expect(courses_page.logout_button).not_to_be_visible()`

<a id="tc-12-auth-odesl-n-po-adavku-na-obnovu-zapomenut-ho-hesla-p-mo-p-es-page-object-dry-princip"></a>
#### `TC-12-AUTH`: Odeslání požadavku na obnovu zapomenutého hesla přímo přes Page Object (DRY princip).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc12_auth_forgot_password_request_submission()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:24`](tests/auth/test_password_reset.py#L24) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ForgotPasswordPage(page)` do proměnné `forgot_password_page`
   `forgot_password_page = ForgotPasswordPage(page)`
2. **🌐 Navigace:** Otevření stránky `forgot_password_page`
   `forgot_password_page.open()`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `forgot_password_page.info_text` na stránce
   `expect(forgot_password_page.info_text).to_be_visible()`
4. **🔍 Kontrola:** Ověření, že text prvku `forgot_password_page.info_text` obsahuje 'Zapoměli jste své heslo?'
   `expect(forgot_password_page.info_text).to_contain_text("Zapoměli jste své heslo?")`
5. **▶️ Krok:** Vyvolání akce `forgot_password_page.request_password_reset(lecturer_user['email'])`
   `forgot_password_page.request_password_reset(lecturer_user["email"])`
6. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: forgot_password_page.URL)
   `expect(page).to_have_url(forgot_password_page.URL)`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `forgot_password_page.submit_button` na stránce
   `expect(forgot_password_page.submit_button).to_be_visible()`

<a id="tc-13-auth-dost-o-reset-s-neplatn-m-pr-zdn-m-e-mailem"></a>
#### `TC-13-AUTH`: Žádost o reset s neplatným / prázdným e-mailem.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc13_auth_forgot_password_invalid_or_empty_email_validation()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:38`](tests/auth/test_password_reset.py#L38) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ForgotPasswordPage(page)` do proměnné `forgot_password_page`
   `forgot_password_page = ForgotPasswordPage(page)`
2. **🌐 Navigace:** Otevření stránky `forgot_password_page`
   `forgot_password_page.open()`
3. **▶️ Krok:** Vyvolání akce `forgot_password_page.submit()` — *(1. Prázdný e-mail)*
   `forgot_password_page.submit()`
4. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: forgot_password_page.URL)
   `expect(page).to_have_url(forgot_password_page.URL)`
5. **✍️ Vstup:** Vyplnění pole `email` hodnotou 'neplatny-email-bez-zavinace' — *(2. Neplatný formát e-mailu)*
   `forgot_password_page.fill_email("neplatny-email-bez-zavinace")`
6. **▶️ Krok:** Vyvolání akce `forgot_password_page.submit()`
   `forgot_password_page.submit()`
7. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: forgot_password_page.URL)
   `expect(page).to_have_url(forgot_password_page.URL)`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `forgot_password_page.submit_button` na stránce
   `expect(forgot_password_page.submit_button).to_be_visible()`

<a id="tc-14-auth-sp-n-zm-na-hesla-pomoc-platn-ho-tokenu"></a>
#### `TC-14-AUTH`: Úspěšná změna hesla pomocí platného tokenu.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc14_auth_successful_password_reset_with_valid_token()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:62`](tests/auth/test_password_reset.py#L62) |
| **Pytest Markery** | `@auth`, `@regression`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **BR-03: Chybějící klientské rozhraní formuláře pro nastavení nového hesla na /reset-password** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ResetPasswordPage(page)` do proměnné `reset_page`
   `reset_page = ResetPasswordPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
3. **🌐 Navigace:** Otevření stránky `reset_page` — *(Otevření stránky resetu s platným tokenem)*
   `reset_page.open(token="valid_sample_token_xyz123", email="tester@kitner.cz")`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_input` na stránce — *(Ověření zobrazení formuláře pro zadání nového hesla)*
   `expect(reset_page.password_input).to_be_visible()`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_again_input` na stránce
   `expect(reset_page.password_again_input).to_be_visible()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.submit_button` na stránce
   `expect(reset_page.submit_button).to_be_visible()`
7. **▶️ Krok:** Vyvolání akce `reset_page.reset_password()` — *(Odeslání nového hesla)*
   `reset_page.reset_password(password="NoveBezpecneHeslo123!", password_again="NoveBezpecneHeslo123!")`
8. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: login_page.URL) — *(Ověření přesměrování na login s potvrzením)*
   `expect(page).to_have_url(login_page.URL, timeout=10000)`

<a id="tc-15-auth-pokus-o-zm-nu-hesla-s-neplatn-m-nebo-expirovan-m-tokenem"></a>
#### `TC-15-AUTH`: Pokus o změnu hesla s neplatným nebo expirovaným tokenem.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc15_auth_password_reset_invalid_or_expired_token()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:82`](tests/auth/test_password_reset.py#L82) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ResetPasswordPage(page)` do proměnné `reset_page`
   `reset_page = ResetPasswordPage(page)`
2. **🌐 Navigace:** Otevření stránky `reset_page` — *(Otevření stránky resetu s neplatným tokenem)*
   `reset_page.open(token="neplatny_nebo_expirovany_token_404", email="tester@kitner.cz")`
3. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `reset_page.form` — *(Systém musí zamezit přístupu k formuláři změny hesla)*
   `expect(reset_page.form).not_to_be_visible()`
4. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `reset_page.password_input`
   `expect(reset_page.password_input).not_to_be_visible()`

<a id="tc-16-auth-zm-na-hesla-s-neshodn-m-potvrzen-m-nov-ho-hesla"></a>
#### `TC-16-AUTH`: Změna hesla s neshodným potvrzením nového hesla.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc16_auth_password_reset_mismatched_confirmation()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:98`](tests/auth/test_password_reset.py#L98) |
| **Pytest Markery** | `@auth`, `@regression`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **BR-03: Chybějící klientské rozhraní formuláře pro nastavení nového hesla na /reset-password** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ResetPasswordPage(page)` do proměnné `reset_page`
   `reset_page = ResetPasswordPage(page)`
2. **🌐 Navigace:** Otevření stránky `reset_page`
   `reset_page.open(token="valid_sample_token_xyz123", email="tester@kitner.cz")`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_input` na stránce
   `expect(reset_page.password_input).to_be_visible()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_again_input` na stránce
   `expect(reset_page.password_again_input).to_be_visible()`
5. **▶️ Krok:** Vyvolání akce `reset_page.reset_password()`
   `reset_page.reset_password(password="PrvniHeslo123!", password_again="DruheOdlišneHeslo456!")`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_error` na stránce
   `expect(reset_page.password_error).to_be_visible()`

<a id="tc-16-auth-zm-na-hesla-s-heslem-nespl-uj-c-m-minim-ln-d-lku-8-znak"></a>
#### `TC-16-AUTH`: Změna hesla s heslem nesplňujícím minimální délku 8 znaků.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc16_auth_password_reset_short_password()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:114`](tests/auth/test_password_reset.py#L114) |
| **Pytest Markery** | `@auth`, `@regression`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **BR-03: Chybějící klientské rozhraní formuláře pro nastavení nového hesla na /reset-password** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ResetPasswordPage(page)` do proměnné `reset_page`
   `reset_page = ResetPasswordPage(page)`
2. **🌐 Navigace:** Otevření stránky `reset_page`
   `reset_page.open(token="valid_sample_token_xyz123", email="tester@kitner.cz")`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_input` na stránce
   `expect(reset_page.password_input).to_be_visible()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_again_input` na stránce
   `expect(reset_page.password_again_input).to_be_visible()`
5. **▶️ Krok:** Vyvolání akce `reset_page.reset_password()`
   `reset_page.reset_password(password="12345", password_again="12345")`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `reset_page.password_error` na stránce
   `expect(reset_page.password_error).to_be_visible()`

<a id="tc-17-auth-sp-n-ov-en-e-mailu-p-es-platn-odkaz"></a>
#### `TC-17-AUTH`: Úspěšné ověření e-mailu přes platný odkaz.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc17_auth_email_verification_success()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:130`](tests/auth/test_password_reset.py#L130) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `EmailVerificationPage(page)` do proměnné `verify_page`
   `verify_page = EmailVerificationPage(page)`
2. **▶️ Krok:** Vyvolání akce `verify_page.open_verification_link()`
   `verify_page.open_verification_link(token="platny_verifikacni_token_123")`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `verify_page.container` na stránce — *(Ověření, že systém přijal požadavek a zobrazil stránku)*
   `expect(verify_page.container).to_be_visible()`

<a id="tc-18-auth-pokus-o-ov-en-e-mailu-s-neplatn-m-odkazem"></a>
#### `TC-18-AUTH`: Pokus o ověření e-mailu s neplatným odkazem.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc18_auth_email_verification_invalid_link()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:139`](tests/auth/test_password_reset.py#L139) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `EmailVerificationPage(page)` do proměnné `verify_page`
   `verify_page = EmailVerificationPage(page)`
2. **▶️ Krok:** Vyvolání akce `verify_page.open_verification_link()`
   `verify_page.open_verification_link(token="neplatny_token_xyz")`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `verify_page.container` na stránce
   `expect(verify_page.container).to_be_visible()`

<a id="tc-19-auth-znovuzasl-n-ov-ovac-ho-e-mailu-a-asov-limit"></a>
#### `TC-19-AUTH`: Znovuzaslání ověřovacího e-mailu a časový limit.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc19_auth_resend_verification_email_rate_limit()` |
| **Testovací třída** | `TestPasswordReset` |
| **Zdrojový soubor** | [`tests/auth/test_password_reset.py:147`](tests/auth/test_password_reset.py#L147) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `EmailVerificationPage(page)` do proměnné `verify_page`
   `verify_page = EmailVerificationPage(page)`
2. **▶️ Krok:** Vyvolání akce `verify_page.open_prompt()`
   `verify_page.open_prompt()`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `verify_page.container` na stránce
   `expect(verify_page.container).to_be_visible()`

<a id="tc-20-auth-do-asn-blokace-po-5-ne-sp-n-ch-pokusech-o-p-ihl-en"></a>
#### `TC-20-AUTH`: Dočasná blokace po 5 neúspěšných pokusech o přihlášení.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc20_auth_temporary_lockout_after_five_failed_logins()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:179`](tests/auth/test_login.py#L179) |
| **Pytest Markery** | `@auth`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page` — *(===================================================================== | 1. ARRANGE (Příprava izolovaného uživatele a Page Objectů) | =====================================================================)*
   `register_page = RegisterPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
3. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_user()` -> `user`
   `user = generate_random_user(name_prefix="RateLimit P1")`
4. **🌐 Navigace:** Otevření stránky `register_page` — *(Registrace a odhlášení nového uživatele)*
   `register_page.open()`
5. **▶️ Krok:** Vyvolání akce `register_page.register(user['name'], user['email'], user['password'])`
   `register_page.register(user["name"], user["email"], user["password"])`
6. **🚪 Odhlášení:** Odhlášení uživatele z portálu
   `logout_user(page)`
7. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
8. **⚙️ Příprava:** Nastavení lokální proměnné `invalid_password` = `'ChybneHeslo999!'`
   `invalid_password = "ChybneHeslo999!"`
9. **🔁 Cyklus:** Iterace kroků (`pro _ v range(5)`) — *(===================================================================== | 2. ACT (5 neúspěšných pokusů za sebou) | =====================================================================)*
   `for _ in range(5):`
  1. **🔑 Autentizace:** Provedení přihlášení uživatele (user['email'], invalid_password)
     `login_page.login(user["email"], invalid_password)`
  2. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.email_error` na stránce
     `expect(login_page.email_error).to_be_visible()`
10. **🔑 Autentizace:** Provedení přihlášení uživatele (user['email'], invalid_password) — *(6. pokus o přihlášení)*
   `login_page.login(user["email"], invalid_password)`
11. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: login_page.URL) — *(===================================================================== | 3. ASSERT (3úrovňová validace: Routing + Session + Data State) | =====================================================================)*
   `expect(page).to_have_url(login_page.URL)`
12. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.email_error` na stránce
   `expect(login_page.email_error).to_be_visible()`
13. **🔍 Kontrola:** Ověření, že text prvku `login_page.email_error` obsahuje re.compile('Too many login attempts.*seconds', re.IGNORECASE)
   `expect(login_page.email_error).to_contain_text(re.compile(r"Too many login attempts.*seconds", re.IGNORECASE))`

<a id="tc-21-auth-vynulov-n-po-tadla-ne-sp-ch-po-sp-n-m-p-ihl-en"></a>
#### `TC-21-AUTH`: Vynulování počítadla neúspěchů po úspěšném přihlášení.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc21_auth_reset_failed_login_counter_on_success()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:214`](tests/auth/test_login.py#L214) |
| **Pytest Markery** | `@auth`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page` — *(===================================================================== | 1. ARRANGE (Příprava izolovaného uživatele a Page Objectů) | =====================================================================)*
   `register_page = RegisterPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
3. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
4. **🎲 Test Data:** Dynamické generování testovacích dat `generate_random_user()` -> `user`
   `user = generate_random_user(name_prefix="RateReset P2")`
5. **🌐 Navigace:** Otevření stránky `register_page` — *(Registrace a odhlášení nového uživatele)*
   `register_page.open()`
6. **▶️ Krok:** Vyvolání akce `register_page.register(user['name'], user['email'], user['password'])`
   `register_page.register(user["name"], user["email"], user["password"])`
7. **🚪 Odhlášení:** Odhlášení uživatele z portálu
   `logout_user(page)`
8. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
9. **⚙️ Příprava:** Nastavení lokální proměnné `invalid_password` = `'ChybneHeslo999!'`
   `invalid_password = "ChybneHeslo999!"`
10. **🔁 Cyklus:** Iterace kroků (`pro _ v range(3)`) — *(===================================================================== | 2. ACT (3 neúspěšné pokusy + úspěšné přihlášení + odhlášení + 3 neúspěchy) | =====================================================================)*
   `for _ in range(3):`
  1. **🔑 Autentizace:** Provedení přihlášení uživatele (user['email'], invalid_password)
     `login_page.login(user["email"], invalid_password)`
  2. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.email_error` na stránce
     `expect(login_page.email_error).to_be_visible()`
11. **🔑 Autentizace:** Provedení přihlášení uživatele (user['email'], user['password']) — *(Úspěšné přihlášení vynuluje počítadlo neúspěchů)*
   `login_page.login(user["email"], user["password"])`
12. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL)
   `expect(page).to_have_url(courses_page.URL, timeout=10000)`
13. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce
   `expect(courses_page.logout_button).to_be_visible()`
14. **🚪 Odhlášení:** Odhlášení uživatele z portálu — *(Odhlášení)*
   `courses_page.logout()`
15. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.login_link` na stránce
   `expect(courses_page.login_link).to_be_visible()`
16. **🌐 Navigace:** Otevření stránky `login_page` — *(Další 3 neúspěšné pokusy (celkem 6 pokusů přerušených úspěchem))*
   `login_page.open()`
17. **🔁 Cyklus:** Iterace kroků (`pro _ v range(3)`)
   `for _ in range(3):`
  1. **🔑 Autentizace:** Provedení přihlášení uživatele (user['email'], invalid_password)
     `login_page.login(user["email"], invalid_password)`
  2. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.email_error` na stránce
     `expect(login_page.email_error).to_be_visible()`
18. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: login_page.URL) — *(===================================================================== | 3. ASSERT (Uživatel není zablokován po celkových 6 neúspěších) | =====================================================================)*
   `expect(page).to_have_url(login_page.URL)`
19. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.email_error` na stránce
   `expect(login_page.email_error).to_be_visible()`
20. **🔍 Kontrola:** Ověření, že text prvku `login_page.email_error` neobsahuje re.compile('Too many login attempts', re.IGNORECASE)
   `expect(login_page.email_error).not_to_contain_text(re.compile(r"Too many login attempts", re.IGNORECASE))`

<a id="modul-crs"></a>
### 📚 Modul: Katalog kurzů a detail běhů (CRS)

*Počet testů v modulu: **5** | Celkem akcí: **18** | Celkem kontrol: **29***

<a id="tc-22-crs-zobrazen-katalogu-kurz-pro-nep-ihl-en-ho-n-v-t-vn-ka"></a>
#### `TC-22-CRS`: Zobrazení katalogu kurzů pro nepřihlášeného návštěvníka.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc22_crs_catalog_display_for_guest()` |
| **Testovací třída** | `TestCoursesCatalog` |
| **Zdrojový soubor** | [`tests/courses/test_courses.py:26`](tests/courses/test_courses.py#L26) |
| **Pytest Markery** | `@courses`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
2. **🌐 Navigace:** Otevření stránky `courses_page`
   `courses_page.open()`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.courses_header` na stránce — *(Ověření zobrazení záhlaví a karet kurzů)*
   `expect(courses_page.courses_header).to_be_visible()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.primary_course_card` na stránce
   `expect(courses_page.primary_course_card).to_be_visible()`
5. **🔍 Kontrola:** Ověření, že počet prvků `courses_page.course_cards` není 0
   `expect(courses_page.course_cards).not_to_have_count(0)`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.navbar.login_link` na stránce — *(Ověření přítomnosti výzvy k registraci pod katalogem pro nepřihlášeného)*
   `expect(courses_page.navbar.login_link).to_be_visible()`

<a id="tc-23-crs-ov-en-zobrazen-atribut-kurzu-v-katalogu"></a>
#### `TC-23-CRS`: Ověření zobrazení atributů kurzu v katalogu.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc23_crs_course_card_attributes()` |
| **Testovací třída** | `TestCoursesCatalog` |
| **Zdrojový soubor** | [`tests/courses/test_courses.py:40`](tests/courses/test_courses.py#L40) |
| **Pytest Markery** | `@courses`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
2. **🌐 Navigace:** Otevření stránky `courses_page`
   `courses_page.open()`
3. **⚙️ Příprava:** Nastavení lokální proměnné `card` = `courses_page.primary_course_card` — *(Karta kurzu přes Page Object (stabilní get_by_test_id bez křehkého indexu .first))*
   `card = courses_page.primary_course_card`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `card` na stránce
   `expect(card).to_be_visible()`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.get_card_name(card)` na stránce — *(Kontrola názvu, popisu, ceny, kapacity a náhledu přes Page Object)*
   `expect(courses_page.get_card_name(card)).to_be_visible()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.get_card_description(card)` na stránce
   `expect(courses_page.get_card_description(card)).to_be_visible()`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.get_card_price(card)` na stránce
   `expect(courses_page.get_card_price(card)).to_be_visible()`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.get_card_capacity(card)` na stránce
   `expect(courses_page.get_card_capacity(card)).to_be_visible()`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.get_card_image(card)` na stránce
   `expect(courses_page.get_card_image(card)).to_be_visible()`
10. **🔍 Kontrola:** Ověření, že text prvku `courses_page.get_card_price(card)` obsahuje re.compile('Kč|\\d+', re.IGNORECASE) — *(Cena obsahuje měnu a je zaokrouhlena (např. Kč) – web-first ověření)*
   `expect(courses_page.get_card_price(card)).to_contain_text(re.compile(r"Kč|\d+", re.IGNORECASE))`

<a id="tc-24-crs-zobrazen-detailu-kurzu-a-seznamu-vypsan-ch-term-n"></a>
#### `TC-24-CRS`: Zobrazení detailu kurzu a seznamu vypsaných termínů.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc24_crs_course_detail_and_iterations_display()` |
| **Testovací třída** | `TestCoursesCatalog` |
| **Zdrojový soubor** | [`tests/courses/test_courses.py:60`](tests/courses/test_courses.py#L60) |
| **Pytest Markery** | `@courses`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page` — *(1. ARRANGE & ACT: Přechod z katalogu na detail kurzu (US-08 AK-4))*
   `courses_page = CoursesPage(page)`
2. **🌐 Navigace:** Otevření stránky `courses_page`
   `courses_page.open()`
3. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `courses_page_course_detail`
   `courses_page.click_course_detail()`
4. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail` — *(2. ASSERT: 3úrovňové ověření detailu kurzu a jeho atributů (US-09 AK-1, AK-2, AK-3))*
   `course_detail = CourseDetailPage(page, course_id=1)`
5. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: course_detail.URL)
   `expect(page).to_have_url(course_detail.URL)`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.heading` na stránce — *(Název, popis, cena kurzu)*
   `expect(course_detail.heading).to_be_visible()`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.description` na stránce
   `expect(course_detail.description).to_be_visible()`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.price` na stránce
   `expect(course_detail.price).to_be_visible()`
9. **🔍 Kontrola:** Ověření, že text prvku `course_detail.price` obsahuje 'Kč'
   `expect(course_detail.price).to_contain_text("Kč")`
10. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.runs_heading` na stránce — *(Sekce běhů kurzu a organizační údaje (zahájení, ukončení, kapacita))*
   `expect(course_detail.runs_heading).to_be_visible()`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.primary_iteration` na stránce
   `expect(course_detail.primary_iteration).to_be_visible()`
12. **🔍 Kontrola:** Ověření, že text prvku `course_detail.primary_iteration` obsahuje 'Zahájení:'
   `expect(course_detail.primary_iteration).to_contain_text("Zahájení:")`
13. **🔍 Kontrola:** Ověření, že text prvku `course_detail.primary_iteration` obsahuje 'Ukončení:'
   `expect(course_detail.primary_iteration).to_contain_text("Ukončení:")`
14. **🔍 Kontrola:** Ověření, že text prvku `course_detail.primary_iteration` obsahuje 'Kapacita:'
   `expect(course_detail.primary_iteration).to_contain_text("Kapacita:")`

<a id="tc-25-crs-zobrazen-tla-tka-z-pisu-u-term-nu-s-volnou-kapacitou-pro-p-ihl-en-ho-z-kazn-ka"></a>
#### `TC-25-CRS`: Zobrazení tlačítka zápisu u termínu s volnou kapacitou pro přihlášeného zákazníka.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc25_crs_enrollment_button_for_available_capacity()` |
| **Testovací třída** | `TestCoursesCatalog` |
| **Zdrojový soubor** | [`tests/courses/test_courses.py:85`](tests/courses/test_courses.py#L85) |
| **Pytest Markery** | `@courses`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page, test_user['email'], test_user['password']) — *(1. ARRANGE: Přihlášení zákazníka a přechod na detail kurzu)*
   `login_user(page, test_user["email"], test_user["password"])`
2. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail`
   `course_detail = CourseDetailPage(page, course_id=1)`
3. **🌐 Navigace:** Otevření stránky `course_detail`
   `course_detail.open()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.available_run_enroll_button` na stránce — *(2. ACT & ASSERT: Ověření tlačítka zápisu u vypsaného běhu s volnou kapacitou)*
   `expect(course_detail.available_run_enroll_button).to_be_visible()`
5. **🔍 Kontrola:** Ověření přesného textu prvku `course_detail.available_run_enroll_button` (očekáváno: 'Nezávazná registrace')
   `expect(course_detail.available_run_enroll_button).to_have_text("Nezávazná registrace")`
6. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `course_detail_first_enroll_button` — *(Kliknutí na tlačítko a ověření přesměrování do objednávkového formuláře)*
   `course_detail.click_first_enroll_button()`
7. **⚙️ Příprava:** Inicializace Page Objectu `EnrollmentPage(page)` do proměnné `enrollment_page`
   `enrollment_page = EnrollmentPage(page)`
8. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: re.compile('.*/courses/\\d+/register.*'))
   `expect(page).to_have_url(re.compile(r".*/courses/\d+/register.*"))`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `enrollment_page.form` na stránce
   `expect(enrollment_page.form).to_be_visible()`

<a id="tc-26-crs-zamezen-registrace-a-indikace-pln-obsazen-ho-b-hu-i-v-zva-pro-nep-ihl-en-ho"></a>
#### `TC-26-CRS`: Zamezení registrace a indikace plně obsazeného běhu i výzva pro nepřihlášeného.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc26_crs_indication_when_capacity_full_or_unauthenticated()` |
| **Testovací třída** | `TestCoursesCatalog` |
| **Zdrojový soubor** | [`tests/courses/test_courses.py:104`](tests/courses/test_courses.py#L104) |
| **Pytest Markery** | `@courses`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail`
   `course_detail = CourseDetailPage(page, course_id=1)`
2. **🌐 Navigace:** Otevření stránky `course_detail` — *(1. Krok: Nepřihlášený návštěvník nemá tlačítko přímého zápisu, ale výzvu k přihlášení/registraci)*
   `course_detail.open()`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.guest_registration_prompt` na stránce
   `expect(course_detail.guest_registration_prompt).to_be_visible()`
4. **🔑 Autentizace:** Provedení přihlášení uživatele (page, test_user['email'], test_user['password']) — *(2. Krok: Přihlášený zákazník na detailu kurzu – ověření plně obsazeného termínu)*
   `login_user(page, test_user["email"], test_user["password"])`
5. **🌐 Navigace:** Otevření stránky `course_detail`
   `course_detail.open()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.full_iteration` na stránce — *(Vyhledání běhu s plně obsazenou kapacitou (např. 12/12))*
   `expect(course_detail.full_iteration).to_be_visible()`
7. **🔍 Kontrola:** Ověření, že text prvku `course_detail.full_iteration` obsahuje re.compile('Kapacita:\\s*12/12')
   `expect(course_detail.full_iteration).to_contain_text(re.compile(r"Kapacita:\s*12/12"))`
8. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `course_detail.full_iteration.get_by_test_id('registration_link')` — *(Zamezení registrace: plně obsazený běh nemá tlačítko pro registraci)*
   `expect(course_detail.full_iteration.get_by_test_id("registration_link")).not_to_be_visible()`

<a id="modul-enr"></a>
### 📝 Modul: Zápis na kurz a Moje kurzy (ENR)

*Počet testů v modulu: **6** | Celkem akcí: **39** | Celkem kontrol: **45***

<a id="tc-27-enr-sp-n-z-pis-na-kurz-s-platn-m-telefonem-a-platn-m-i-o"></a>
#### `TC-27-ENR`: Úspěšný zápis na kurz s platným telefonem a platným IČO.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc27_enr_successful_enrollment_with_ico_and_phone()` |
| **Testovací třída** | `TestCourseEnrollment` |
| **Zdrojový soubor** | [`tests/enrollment/test_enrollment.py:35`](tests/enrollment/test_enrollment.py#L35) |
| **Pytest Markery** | `@enrollment`, `@smoke` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail` — *(1. ARRANGE: Otevření detailu kurzu a přechod do formuláře zápisu)*
   `course_detail = CourseDetailPage(page, course_id=1)`
2. **🌐 Navigace:** Otevření stránky `course_detail`
   `course_detail.open()`
3. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `course_detail_first_enroll_button`
   `course_detail.click_first_enroll_button()`
4. **⚙️ Příprava:** Inicializace Page Objectu `EnrollmentPage(page)` do proměnné `enrollment_page`
   `enrollment_page = EnrollmentPage(page)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `enrollment_page.form` na stránce
   `expect(enrollment_page.form).to_be_visible()`
6. **🎲 Test Data:** Dynamické generování testovacích dat `generate_valid_ico()` -> `valid_ico`
   `valid_ico = generate_valid_ico()`
7. **⚙️ Příprava:** Nastavení lokální proměnné `valid_phone` = `'+420 777 123 456'`
   `valid_phone = "+420 777 123 456"`
8. **✍️ Vstup:** Vyplnění pole `enrollment_form` hodnotou  — *(2. ACT: Vyplnění platných údajů a odeslání nezávazné registrace)*
   `enrollment_page.fill_enrollment_form(phone=valid_phone, ico=valid_ico)`
9. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `enrollment_page.phone_input` (očekáváno: valid_phone)
   `expect(enrollment_page.phone_input).to_have_value(valid_phone)`
10. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `enrollment_page.ico_input` (očekáváno: valid_ico)
   `expect(enrollment_page.ico_input).to_have_value(valid_ico)`
11. **▶️ Krok:** Vyvolání akce `enrollment_page.submit()`
   `enrollment_page.submit()`
12. **⚙️ Příprava:** Inicializace Page Objectu `MyCoursesPage(page)` do proměnné `my_courses_page` — *(3. ASSERT: 3úrovňové ověření (Routing, Session, Data State a propsání do profilu))*
   `my_courses_page = MyCoursesPage(page)`
13. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: my_courses_page.URL)
   `expect(page).to_have_url(my_courses_page.URL)`
14. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.navbar.logout_button` na stránce
   `expect(my_courses_page.navbar.logout_button).to_be_visible()`
15. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.section` na stránce
   `expect(my_courses_page.section).to_be_visible()`
16. **🔍 Kontrola:** Ověření, že text prvku `my_courses_page.section` obsahuje 'Mé zapsané kurzy'
   `expect(my_courses_page.section).to_contain_text("Mé zapsané kurzy")`
17. **⚙️ Příprava:** Inicializace Page Objectu `ProfilePage(page)` do proměnné `profile_page` — *(Ověření propsání zadaných údajů do profilu zákazníka (US-11 AK-7))*
   `profile_page = ProfilePage(page)`
18. **🌐 Navigace:** Otevření stránky `profile_page`
   `profile_page.open()`
19. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `profile_page.phone_input` (očekáváno: valid_phone)
   `expect(profile_page.phone_input).to_have_value(valid_phone)`
20. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `profile_page.ico_input` (očekáváno: valid_ico)
   `expect(profile_page.ico_input).to_have_value(valid_ico)`

<a id="tc-28-enr-sp-n-z-pis-na-kurz-bez-vypln-n-ho-i-o-i-o-je-nepovinn"></a>
#### `TC-28-ENR`: Úspěšný zápis na kurz bez vyplněného IČO (IČO je nepovinné).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc28_enr_successful_enrollment_without_ico()` |
| **Testovací třída** | `TestCourseEnrollment` |
| **Zdrojový soubor** | [`tests/enrollment/test_enrollment.py:69`](tests/enrollment/test_enrollment.py#L69) |
| **Pytest Markery** | `@enrollment`, `@regression`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **Aplikace v rozporu s US-11 AK-3 vyžaduje IČO jako povinné a při prázdném poli hlásí Neplatné IČO** |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail` — *(1. ARRANGE: Otevření detailu kurzu a přechod do formuláře zápisu)*
   `course_detail = CourseDetailPage(page, course_id=1)`
2. **🌐 Navigace:** Otevření stránky `course_detail`
   `course_detail.open()`
3. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `course_detail_first_enroll_button`
   `course_detail.click_first_enroll_button()`
4. **⚙️ Příprava:** Inicializace Page Objectu `EnrollmentPage(page)` do proměnné `enrollment_page`
   `enrollment_page = EnrollmentPage(page)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `enrollment_page.form` na stránce
   `expect(enrollment_page.form).to_be_visible()`
6. **⚙️ Příprava:** Nastavení lokální proměnné `valid_phone` = `'777123456'`
   `valid_phone = "777123456"`
7. **✍️ Vstup:** Vyplnění pole `enrollment_form` hodnotou  — *(2. ACT: Vyplnění pouze telefonu (IČO nepovinné) a odeslání)*
   `enrollment_page.fill_enrollment_form(phone=valid_phone, ico="")`
8. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `enrollment_page.phone_input` (očekáváno: valid_phone)
   `expect(enrollment_page.phone_input).to_have_value(valid_phone)`
9. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `enrollment_page.ico_input` (očekáváno: '')
   `expect(enrollment_page.ico_input).to_have_value("")`
10. **▶️ Krok:** Vyvolání akce `enrollment_page.submit()`
   `enrollment_page.submit()`
11. **⚙️ Příprava:** Inicializace Page Objectu `MyCoursesPage(page)` do proměnné `my_courses_page` — *(3. ASSERT: Přesměrování do Moje kurzy a zobrazení zapsaných kurzů)*
   `my_courses_page = MyCoursesPage(page)`
12. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: my_courses_page.URL)
   `expect(page).to_have_url(my_courses_page.URL)`
13. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.navbar.logout_button` na stránce
   `expect(my_courses_page.navbar.logout_button).to_be_visible()`
14. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.section` na stránce
   `expect(my_courses_page.section).to_be_visible()`

<a id="tc-29-enr-z-pis-s-neplatn-m-i-o-chyba-kontroln-ho-sou-tu-modulo-11"></a>
#### `TC-29-ENR`: Zápis s neplatným IČO (chyba kontrolního součtu modulo 11).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc29_enr_invalid_ico_validation()` |
| **Testovací třída** | `TestCourseEnrollment` |
| **Zdrojový soubor** | [`tests/enrollment/test_enrollment.py:94`](tests/enrollment/test_enrollment.py#L94) |
| **Pytest Markery** | `@enrollment`, `@regression` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail`
   `course_detail = CourseDetailPage(page, course_id=1)`
2. **🌐 Navigace:** Otevření stránky `course_detail`
   `course_detail.open()`
3. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `course_detail_first_enroll_button`
   `course_detail.click_first_enroll_button()`
4. **⚙️ Příprava:** Inicializace Page Objectu `EnrollmentPage(page)` do proměnné `enrollment_page`
   `enrollment_page = EnrollmentPage(page)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `enrollment_page.form` na stránce
   `expect(enrollment_page.form).to_be_visible()`
6. **🎲 Test Data:** Dynamické generování testovacích dat `generate_invalid_ico()` -> `invalid_ico`
   `invalid_ico = generate_invalid_ico()`
7. **✍️ Vstup:** Vyplnění pole `enrollment_form` hodnotou 
   `enrollment_page.fill_enrollment_form(phone="777123456", ico=invalid_ico)`
8. **▶️ Krok:** Vyvolání akce `enrollment_page.submit()`
   `enrollment_page.submit()`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `enrollment_page.form` na stránce — *(Uživatel zůstává na formuláři, objednávka není dokončena)*
   `expect(enrollment_page.form).to_be_visible()`

<a id="tc-30-enr-z-pis-s-neplatn-m-telefonem-m-n-ne-9-slic"></a>
#### `TC-30-ENR`: Zápis s neplatným telefonem (méně než 9 číslic).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc30_enr_short_phone_validation()` |
| **Testovací třída** | `TestCourseEnrollment` |
| **Zdrojový soubor** | [`tests/enrollment/test_enrollment.py:111`](tests/enrollment/test_enrollment.py#L111) |
| **Pytest Markery** | `@enrollment`, `@regression` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail`
   `course_detail = CourseDetailPage(page, course_id=1)`
2. **🌐 Navigace:** Otevření stránky `course_detail`
   `course_detail.open()`
3. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `course_detail_first_enroll_button`
   `course_detail.click_first_enroll_button()`
4. **⚙️ Příprava:** Inicializace Page Objectu `EnrollmentPage(page)` do proměnné `enrollment_page`
   `enrollment_page = EnrollmentPage(page)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `enrollment_page.form` na stránce
   `expect(enrollment_page.form).to_be_visible()`
6. **✍️ Vstup:** Vyplnění pole `enrollment_form` hodnotou 
   `enrollment_page.fill_enrollment_form(phone="12345", ico=generate_valid_ico())`
7. **▶️ Krok:** Vyvolání akce `enrollment_page.submit()`
   `enrollment_page.submit()`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `enrollment_page.form` na stránce — *(Formulář se neodešle a zůstává zobrazen)*
   `expect(enrollment_page.form).to_be_visible()`

<a id="tc-31-enr-zobrazen-p-ehledu-m-ch-zapsan-ch-kurz-a-detailu-lekc"></a>
#### `TC-31-ENR`: Zobrazení přehledu mých zapsaných kurzů a detailu lekcí.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc31_enr_my_courses_overview_display()` |
| **Testovací třída** | `TestCourseEnrollment` |
| **Zdrojový soubor** | [`tests/enrollment/test_enrollment.py:127`](tests/enrollment/test_enrollment.py#L127) |
| **Pytest Markery** | `@enrollment`, `@smoke` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `MyCoursesPage(page)` do proměnné `my_courses_page` — *(1. ARRANGE: Otevření sekce Moje kurzy pro přihlášeného studenta)*
   `my_courses_page = MyCoursesPage(page)`
2. **🌐 Navigace:** Otevření stránky `my_courses_page`
   `my_courses_page.open()`
3. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: my_courses_page.URL) — *(2. ASSERT: 3úrovňové ověření (Routing, Session, Data State) | Routing & Session (AK-1))*
   `expect(page).to_have_url(my_courses_page.URL)`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.navbar.logout_button` na stránce
   `expect(my_courses_page.navbar.logout_button).to_be_visible()`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.header` na stránce
   `expect(my_courses_page.header).to_be_visible()`
6. **🔍 Kontrola:** Ověření přesného textu prvku `my_courses_page.title` (očekáváno: 'Mé zapsané kurzy')
   `expect(my_courses_page.title).to_have_text("Mé zapsané kurzy")`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.primary_course_card` na stránce — *(Karta zapsaného kurzu a její atributy: název, popis, cena, obrázek (AK-2, AK-3))*
   `expect(my_courses_page.primary_course_card).to_be_visible()`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.course_name` na stránce
   `expect(my_courses_page.course_name).to_be_visible()`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.course_description` na stránce
   `expect(my_courses_page.course_description).to_be_visible()`
10. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.course_price` na stránce
   `expect(my_courses_page.course_price).to_be_visible()`
11. **🔍 Kontrola:** Ověření, že text prvku `my_courses_page.course_price` obsahuje 'Kč'
   `expect(my_courses_page.course_price).to_contain_text("Kč")`
12. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.course_image` na stránce
   `expect(my_courses_page.course_image).to_be_visible()`
13. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.date_time_from` na stránce — *(Organizační údaje lekcí běhu kurzu: data, den, čas, místo (AK-4, AK-5, AK-6))*
   `expect(my_courses_page.date_time_from).to_be_visible()`
14. **🔍 Kontrola:** Ověření, že text prvku `my_courses_page.date_time_from` obsahuje 'První lekce:'
   `expect(my_courses_page.date_time_from).to_contain_text("První lekce:")`
15. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.date_time_to` na stránce
   `expect(my_courses_page.date_time_to).to_be_visible()`
16. **🔍 Kontrola:** Ověření, že text prvku `my_courses_page.date_time_to` obsahuje 'Poslední lekce:'
   `expect(my_courses_page.date_time_to).to_contain_text("Poslední lekce:")`
17. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.day_information` na stránce
   `expect(my_courses_page.day_information).to_be_visible()`
18. **🔍 Kontrola:** Ověření, že text prvku `my_courses_page.day_information` obsahuje 'Kdy:'
   `expect(my_courses_page.day_information).to_contain_text("Kdy:")`
19. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.place_information` na stránce
   `expect(my_courses_page.place_information).to_be_visible()`
20. **🔍 Kontrola:** Ověření, že text prvku `my_courses_page.place_information` obsahuje 'Kde:'
   `expect(my_courses_page.place_information).to_contain_text("Kde:")`
21. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `my_courses_page_course_detail` — *(Přechod na detail daného kurzu (AK-7))*
   `my_courses_page.click_course_detail()`
22. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail`
   `course_detail = CourseDetailPage(page, course_id=1)`
23. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: course_detail.URL)
   `expect(page).to_have_url(course_detail.URL)`
24. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail.container` na stránce
   `expect(course_detail.container).to_be_visible()`

<a id="tc-48-enr-zobrazen-sekce-moje-kurzy-bez-aktivn-ch-z-pis-empty-state"></a>
#### `TC-48-ENR`: Zobrazení sekce Moje kurzy bez aktivních zápisů (Empty State).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc48_enr_empty_state_my_courses_without_enrollments()` |
| **Testovací třída** | `TestMyCoursesOverview` |
| **Zdrojový soubor** | [`tests/enrollment/test_enrollment.py:173`](tests/enrollment/test_enrollment.py#L173) |
| **Pytest Markery** | `@enrollment`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **▶️ Krok:** Vyvolání akce `register_and_login_user(page)` — *(===================================================================== | 1. ARRANGE: Registrace a přihlášení nového uživatele bez zapsaných kurzů | =====================================================================)*
   `register_and_login_user(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `MyCoursesPage(page)` do proměnné `my_courses_page`
   `my_courses_page = MyCoursesPage(page)`
3. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `my_courses_page.navbar_my_courses` — *(===================================================================== | 2. ACT: Přechod do sekce Moje kurzy přes horní navigaci | =====================================================================)*
   `my_courses_page.navbar.click_my_courses()`
4. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: my_courses_page.URL) — *(===================================================================== | 3. ASSERT: 3úrovňová validace (Routing, Session, Data State - Empty) | ===================================================================== | Úroveň 1: Routing)*
   `expect(page).to_have_url(my_courses_page.URL)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.navbar.logout_button` na stránce — *(Úroveň 2: Session)*
   `expect(my_courses_page.navbar.logout_button).to_be_visible()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.section` na stránce — *(Úroveň 3: Data State / UI Feedback (zobrazení sekce a absence kurzových karet))*
   `expect(my_courses_page.section).to_be_visible()`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.header` na stránce
   `expect(my_courses_page.header).to_be_visible()`
8. **🔍 Kontrola:** Ověření přesného textu prvku `my_courses_page.title` (očekáváno: 'Mé zapsané kurzy')
   `expect(my_courses_page.title).to_have_text("Mé zapsané kurzy")`
9. **🔍 Kontrola:** Ověření přesného počtu prvků `my_courses_page.course_cards`: 0
   `expect(my_courses_page.course_cards).to_have_count(0)`

<a id="modul-lec"></a>
### 🎓 Modul: Lektorská správa kurzů (LEC)

*Počet testů v modulu: **8** | Celkem akcí: **40** | Celkem kontrol: **44***

<a id="tc-32-lec-vytvo-en-nov-ho-kurzu-s-n-hledem-s-pom-rem-stran-16-9"></a>
#### `TC-32-LEC`: Vytvoření nového kurzu s náhledem s poměrem stran 16:9.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc32_lec_create_course_with_16_9_aspect_ratio_image()` |
| **Testovací třída** | `TestLecturerCourseManagement` |
| **Zdrojový soubor** | [`tests/lecturer/test_lecturer.py:35`](tests/lecturer/test_lecturer.py#L35) |
| **Pytest Markery** | `@lecturer`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page)
   `login_lecturer(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CreateCoursePage(page)` do proměnné `create_page`
   `create_page = CreateCoursePage(page)`
3. **🌐 Navigace:** Otevření stránky `create_page`
   `create_page.open()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `create_page.title` na stránce
   `expect(create_page.title).to_be_visible()`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `create_page.form` na stránce
   `expect(create_page.form).to_be_visible()`
6. **✍️ Vstup:** Vyplnění pole `course_form` hodnotou 
   `create_page.fill_course_form( name="Playwright Testování Pokročilý", description="Detailní kurz automatizace", capacity="15", price="14900", file_path=IMAGE_16_9 )`
7. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `create_page.name_input` (očekáváno: 'Playwright Testování Pokročilý')
   `expect(create_page.name_input).to_have_value("Playwright Testování Pokročilý")`
8. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `create_page.capacity_input` (očekáváno: '15')
   `expect(create_page.capacity_input).to_have_value("15")`
9. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `create_page.price_input` (očekáváno: '14900')
   `expect(create_page.price_input).to_have_value("14900")`
10. **🔍 Kontrola:** Ověření viditelnosti prvku `create_page.submit_button` na stránce
   `expect(create_page.submit_button).to_be_visible()`

<a id="tc-33-lec-odm-tnut-n-hledov-ho-obr-zku-s-nevyhovuj-c-m-pom-rem-stran"></a>
#### `TC-33-LEC`: Odmítnutí náhledového obrázku s nevyhovujícím poměrem stran.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc33_lec_reject_invalid_aspect_ratio_image()` |
| **Testovací třída** | `TestLecturerCourseManagement` |
| **Zdrojový soubor** | [`tests/lecturer/test_lecturer.py:60`](tests/lecturer/test_lecturer.py#L60) |
| **Pytest Markery** | `@lecturer`, `@regression`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **Aplikace v testovacím prostředí v rozporu s US-13 nekontroluje poměr stran obrázku na frontendu** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page)
   `login_lecturer(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CreateCoursePage(page)` do proměnné `create_page`
   `create_page = CreateCoursePage(page)`
3. **🌐 Navigace:** Otevření stránky `create_page`
   `create_page.open()`
4. **✍️ Vstup:** Vyplnění pole `course_form` hodnotou 
   `create_page.fill_course_form( name="Kurz s chybným poměrem", description="Testovací popis", capacity="10", price="9900", file_path=IMAGE_1_1 )`
5. **▶️ Krok:** Vyvolání akce `create_page.submit()`
   `create_page.submit()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `create_page.form` na stránce — *(Podle US-13 má systém zůstat na formuláři s chybou)*
   `expect(create_page.form).to_be_visible()`

<a id="tc-34-lec-validace-povinn-ch-pol-a-seln-kapacity-ceny-kurzu"></a>
#### `TC-34-LEC`: Validace povinných polí a číselné kapacity/ceny kurzu.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc34_lec_validation_required_fields_and_numeric_values()` |
| **Testovací třída** | `TestLecturerCourseManagement` |
| **Zdrojový soubor** | [`tests/lecturer/test_lecturer.py:81`](tests/lecturer/test_lecturer.py#L81) |
| **Pytest Markery** | `@lecturer`, `@regression`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **Aplikace v testovacím prostředí postrádá validaci povinných polí a číselných hodnot** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page)
   `login_lecturer(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CreateCoursePage(page)` do proměnné `create_page`
   `create_page = CreateCoursePage(page)`
3. **🌐 Navigace:** Otevření stránky `create_page`
   `create_page.open()`
4. **▶️ Krok:** Vyvolání akce `create_page.submit()` — *(Odeslání s prázdnými poli)*
   `create_page.submit()`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `create_page.form` na stránce
   `expect(create_page.form).to_be_visible()`
6. **✍️ Vstup:** Vyplnění pole `pole` hodnotou '-5' — *(Pokus o nečíselné / záporné hodnoty)*
   `create_page.capacity_input.fill("-5")`
7. **✍️ Vstup:** Vyplnění pole `pole` hodnotou 'zdarma'
   `create_page.price_input.fill("zdarma")`
8. **▶️ Krok:** Vyvolání akce `create_page.submit()`
   `create_page.submit()`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `create_page.form` na stránce
   `expect(create_page.form).to_be_visible()`

<a id="tc-35-lec-sp-n-vyps-n-nov-ho-term-nu-kurzu-lektorem"></a>
#### `TC-35-LEC`: Úspěšné vypsání nového termínu kurzu lektorem.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc35_lec_create_course_iteration_by_lecturer()` |
| **Testovací třída** | `TestLecturerCourseManagement` |
| **Zdrojový soubor** | [`tests/lecturer/test_lecturer.py:99`](tests/lecturer/test_lecturer.py#L99) |
| **Pytest Markery** | `@lecturer`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Přihlášení uživatele přes pomocný helper: `login_lecturer(page)` -> `courses_page` — *(1. ARRANGE: Přihlášení lektora a otevření formuláře pro nový termín kurzu)*
   `courses_page = login_lecturer(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CreateIterationPage(page)` do proměnné `create_iter_page`
   `create_iter_page = CreateIterationPage(page)`
3. **🌐 Navigace:** Otevření stránky `create_iter_page`
   `create_iter_page.open(course_id=1)`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `create_iter_page.form` na stránce
   `expect(create_iter_page.form).to_be_visible()`
5. **✍️ Vstup:** Vyplnění pole `iteration_form` hodnotou  — *(2. ACT: Vyplnění formuláře rozvrhu a uložení nového termínu)*
   `create_iter_page.fill_iteration_form( start_date="2026-12-01", end_date="2026-12-20", day="Úterý", time="18:00", location="Online (Google Meet)" )`
6. **▶️ Krok:** Vyvolání akce `create_iter_page.submit()`
   `create_iter_page.submit()`
7. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail_page` — *(3. ASSERT: 3úrovňové ověření (Routing, Session, Data State))*
   `course_detail_page = CourseDetailPage(page, course_id=1)`
8. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: course_detail_page.URL)
   `expect(page).to_have_url(course_detail_page.URL)`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.navbar.logout_button` na stránce
   `expect(courses_page.navbar.logout_button).to_be_visible()`
10. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail_page.container` na stránce
   `expect(course_detail_page.container).to_be_visible()`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail_page.heading` na stránce
   `expect(course_detail_page.heading).to_be_visible()`

<a id="tc-36-lec-validace-povinn-ch-pol-p-i-vyps-n-term-nu"></a>
#### `TC-36-LEC`: Validace povinných polí při vypsání termínu.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc36_lec_validation_iteration_required_fields()` |
| **Testovací třída** | `TestLecturerCourseManagement` |
| **Zdrojový soubor** | [`tests/lecturer/test_lecturer.py:127`](tests/lecturer/test_lecturer.py#L127) |
| **Pytest Markery** | `@lecturer`, `@regression`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **Aplikace v testovacím prostředí odesílá formulář termínu bez klientské validace povinných polí (US-14 AK-3)** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page)
   `login_lecturer(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CreateIterationPage(page)` do proměnné `create_iter_page`
   `create_iter_page = CreateIterationPage(page)`
3. **🌐 Navigace:** Otevření stránky `create_iter_page`
   `create_iter_page.open(course_id=1)`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `create_iter_page.form` na stránce
   `expect(create_iter_page.form).to_be_visible()`
5. **▶️ Krok:** Vyvolání akce `create_iter_page.submit()` — *(Pokus o odeslání prázdného formuláře)*
   `create_iter_page.submit()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `create_iter_page.form` na stránce — *(Dle US-14 AK-3 má systém zůstat na formuláři s validační chybou)*
   `expect(create_iter_page.form).to_be_visible()`

<a id="tc-37-lec-sp-n-p-ihl-en-lektora-a-ov-en-lektorsk-ch-pr-v-p-idat-kurz"></a>
#### `TC-37-LEC`: Úspěšné přihlášení lektora a ověření lektorských práv (přidat kurz).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc37_lec_lecturer_successful_login_and_rights()` |
| **Testovací třída** | `TestLogin` |
| **Zdrojový soubor** | [`tests/auth/test_login.py:67`](tests/auth/test_login.py#L67) |
| **Pytest Markery** | `@auth`, `@smoke`, `@lecturer` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
3. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
4. **🔑 Autentizace:** Provedení přihlášení uživatele (lecturer_user['email'], lecturer_user['password'])
   `login_page.login(lecturer_user["email"], lecturer_user["password"])`
5. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL)
   `expect(page).to_have_url(courses_page.URL, timeout=10000)`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce
   `expect(courses_page.logout_button).to_be_visible()`
7. **🔍 Kontrola:** Ověření, že text prvku `courses_page.courses_header` obsahuje 'Přidat kurz'
   `expect(courses_page.courses_header).to_contain_text("Přidat kurz")`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.add_course_button` na stránce
   `expect(courses_page.add_course_button).to_be_visible()`
9. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `courses_page.add_course_button`
   `courses_page.add_course_button.click()`
10. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.CREATE_URL)
   `expect(page).to_have_url(courses_page.CREATE_URL)`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.course_form` na stránce
   `expect(courses_page.course_form).to_be_visible()`
12. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.course_name_input` na stránce
   `expect(courses_page.course_name_input).to_be_visible()`

<a id="tc-37-lec-zobrazen-detailu-kurzu-a-ov-en-tabulky-astn-k-se-sloupci-jm-no-email-telefon-a-i-o"></a>
#### `TC-37-LEC`: Zobrazení detailu kurzu a ověření tabulky účastníků se sloupci Jméno, Email, Telefon a IČO.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc37_lec_lecturer_interface_and_navigation()` |
| **Testovací třída** | `TestLecturerCourseManagement` |
| **Zdrojový soubor** | [`tests/lecturer/test_lecturer.py:143`](tests/lecturer/test_lecturer.py#L143) |
| **Pytest Markery** | `@lecturer`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Přihlášení uživatele přes pomocný helper: `login_lecturer(page)` -> `courses_page` — *(1. ARRANGE: Přihlášení lektora a příprava Page Objectů)*
   `courses_page = login_lecturer(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CourseDetailPage(page)` do proměnné `course_detail_page`
   `course_detail_page = CourseDetailPage(page)`
3. **⚙️ Příprava:** Inicializace Page Objectu `ParticipantsPage(page)` do proměnné `participants_page`
   `participants_page = ParticipantsPage(page)`
4. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `courses_page_course_detail` — *(2. ACT: Rozkliknutí detailu kurzu a přechod do seznamu účastníků běhu)*
   `courses_page.click_course_detail()`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail_page.container` na stránce
   `expect(course_detail_page.container).to_be_visible()`
6. **🔍 Kontrola:** Ověření viditelnosti prvku `course_detail_page.runs_heading` na stránce
   `expect(course_detail_page.runs_heading).to_be_visible()`
7. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `course_detail_page_iteration_participants`
   `course_detail_page.click_iteration_participants()`
8. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: participants_page.URL_PATTERN) — *(3. ASSERT: 3úrovňové ověření (Routing, Session, Data State / UI Feedback) | Routing & Session)*
   `expect(page).to_have_url(participants_page.URL_PATTERN)`
9. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.navbar.logout_button` na stránce
   `expect(courses_page.navbar.logout_button).to_be_visible()`
10. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.header_title` na stránce — *(Záhlaví a tabulka účastníků)*
   `expect(participants_page.header_title).to_be_visible()`
11. **🔍 Kontrola:** Ověření přesného textu prvku `participants_page.header_title` (očekáváno: 'Seznam přihlášených')
   `expect(participants_page.header_title).to_have_text("Seznam přihlášených")`
12. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.table` na stránce
   `expect(participants_page.table).to_be_visible()`
13. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.name_header` na stránce — *(Sloupce tabulky: Jméno, Email, Telefon, IČO)*
   `expect(participants_page.name_header).to_be_visible()`
14. **🔍 Kontrola:** Ověření, že text prvku `participants_page.name_header` obsahuje 'Jméno'
   `expect(participants_page.name_header).to_contain_text("Jméno", ignore_case=True)`
15. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.email_header` na stránce
   `expect(participants_page.email_header).to_be_visible()`
16. **🔍 Kontrola:** Ověření, že text prvku `participants_page.email_header` obsahuje 'Email'
   `expect(participants_page.email_header).to_contain_text("Email", ignore_case=True)`
17. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.phone_header` na stránce
   `expect(participants_page.phone_header).to_be_visible()`
18. **🔍 Kontrola:** Ověření, že text prvku `participants_page.phone_header` obsahuje 'Telefon'
   `expect(participants_page.phone_header).to_contain_text("Telefon", ignore_case=True)`
19. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.ico_header` na stránce
   `expect(participants_page.ico_header).to_be_visible()`
20. **🔍 Kontrola:** Ověření, že text prvku `participants_page.ico_header` obsahuje 'IČO'
   `expect(participants_page.ico_header).to_contain_text("IČO", ignore_case=True)`
21. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.primary_row` na stránce — *(Skutečné zobrazení záznamů účastníků v tabulce (konkrétní buňky přes get_by_test_id bez indexu .first))*
   `expect(participants_page.primary_row).to_be_visible()`
22. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.primary_name` na stránce
   `expect(participants_page.primary_name).to_be_visible()`
23. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.primary_email` na stránce
   `expect(participants_page.primary_email).to_be_visible()`
24. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.primary_phone` na stránce
   `expect(participants_page.primary_phone).to_be_visible()`
25. **🔍 Kontrola:** Ověření viditelnosti prvku `participants_page.primary_ico` na stránce
   `expect(participants_page.primary_ico).to_be_visible()`

<a id="tc-38-lec-zamezen-p-stupu-k-lektorsk-m-operac-m-pro-b-n-ho-z-kazn-ka"></a>
#### `TC-38-LEC`: Zamezení přístupu k lektorským operacím pro běžného zákazníka.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc38_lec_customer_cannot_access_lecturer_create_course()` |
| **Testovací třída** | `TestLecturerCourseManagement` |
| **Zdrojový soubor** | [`tests/lecturer/test_lecturer.py:189`](tests/lecturer/test_lecturer.py#L189) |
| **Pytest Markery** | `@lecturer`, `@smoke`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **BR-01: Aplikace v rozporu s US-18 nezabezpečuje /courses/create před rolí Zákazník** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page, test_user['email'], test_user['password'])
   `login_user(page, test_user["email"], test_user["password"])`
2. **⚙️ Příprava:** Inicializace Page Objectu `CreateCoursePage(page)` do proměnné `create_page`
   `create_page = CreateCoursePage(page)`
3. **🌐 Navigace:** Otevření stránky `create_page`
   `create_page.open()`
4. **⏳ Čekání:** Čekání na ustálení síťového a vykreslovacího stavu ('networkidle')
   `page.wait_for_load_state("networkidle")`
5. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `create_page.form` — *(Zákazník nesmí mít přístup k lektorskému formuláři)*
   `expect(create_page.form).not_to_be_visible()`

<a id="modul-nav"></a>
### 🧭 Modul: Navigace a integrace stránek (NAV)

*Počet testů v modulu: **3** | Celkem akcí: **14** | Celkem kontrol: **8***

<a id="tc-01-nav-integra-n-test-p-echod-z-p-ehledu-kurz-na-p-ihl-en-a-n-vrat-zp-t"></a>
#### `TC-01-NAV`: Integrační test – přechod z přehledu kurzů na přihlášení a návrat zpět.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc01_nav_login_from_courses_navigation()` |
| **Testovací třída** | `TestNavigation` |
| **Zdrojový soubor** | [`tests/navigation/test_navigation.py:23`](tests/navigation/test_navigation.py#L23) |
| **Pytest Markery** | `@navigation`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
3. **🌐 Navigace:** Otevření stránky `courses_page`
   `courses_page.open()`
4. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `courses_page.login_link`
   `courses_page.login_link.click()`
5. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: login_page.URL)
   `expect(page).to_have_url(login_page.URL)`
6. **🔑 Autentizace:** Provedení přihlášení uživatele (test_user['email'], test_user['password'])
   `login_page.login(test_user["email"], test_user["password"])`
7. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: courses_page.URL)
   `expect(page).to_have_url(courses_page.URL)`
8. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.logout_button` na stránce
   `expect(courses_page.logout_button).to_be_visible()`

<a id="tc-02-nav-funk-nost-dopl-kov-ch-odkaz-ve-spodn-sti-p-ihla-ovac-ho-formul-e-login-forgot-password-register"></a>
#### `TC-02-NAV`: Funkčnost doplňkových odkazů ve spodní části přihlašovacího formuláře (/login -> /forgot-password, /register).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc02_nav_login_form_footer_links()` |
| **Testovací třída** | `TestNavigation` |
| **Zdrojový soubor** | [`tests/navigation/test_navigation.py:47`](tests/navigation/test_navigation.py#L47) |
| **Pytest Markery** | `@navigation`, `@regression`, `@parametrize` |
| **Data-driven varianty** | Parametry: `'link_attr, expected_page_class'`, Scénáře: `['to-forgot-password', 'to-register']` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **⚙️ Příprava:** Nastavení lokální proměnné `target_page` = `expected_page_class(page)`
   `target_page = expected_page_class(page)`
3. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
4. **⚙️ Příprava:** Nastavení lokální proměnné `link` = `getattr(login_page, link_attr)`
   `link = getattr(login_page, link_attr)`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `link` na stránce
   `expect(link).to_be_visible()`
6. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `link`
   `link.click()`
7. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: target_page.URL)
   `expect(page).to_have_url(target_page.URL)`

<a id="tc-03-nav-n-vratov-odkaz-p-ihl-sit-se-z-registra-n-str-nky-zp-t-na-p-ihl-en-register-login"></a>
#### `TC-03-NAV`: Návratový odkaz 'Přihlásit se' z registrační stránky zpět na přihlášení (/register -> /login).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc03_nav_register_page_login_link_returns_to_login()` |
| **Testovací třída** | `TestNavigation` |
| **Zdrojový soubor** | [`tests/navigation/test_navigation.py:60`](tests/navigation/test_navigation.py#L60) |
| **Pytest Markery** | `@navigation`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `RegisterPage(page)` do proměnné `register_page`
   `register_page = RegisterPage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
3. **🌐 Navigace:** Otevření stránky `register_page`
   `register_page.open()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `register_page.login_link` na stránce
   `expect(register_page.login_link).to_be_visible()`
5. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `register_page.login_link`
   `register_page.login_link.click()`
6. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: login_page.URL)
   `expect(page).to_have_url(login_page.URL)`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `login_page.login_button` na stránce
   `expect(login_page.login_button).to_be_visible()`

<a id="modul-prf"></a>
### 👤 Modul: Uživatelský profil a nástěnka (PRF)

*Počet testů v modulu: **4** | Celkem akcí: **20** | Celkem kontrol: **11***

<a id="tc-39-prf-zobrazen-personalizovan-ho-uv-t-n-na-domovsk-n-st-nce"></a>
#### `TC-39-PRF`: Zobrazení personalizovaného uvítání na domovské nástěnce.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc39_prf_personalized_welcome_dashboard()` |
| **Testovací třída** | `TestUserProfileAndDashboard` |
| **Zdrojový soubor** | [`tests/profile/test_profile.py:29`](tests/profile/test_profile.py#L29) |
| **Pytest Markery** | `@profile`, `@smoke` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `HomePage(page)` do proměnné `home_page`
   `home_page = HomePage(page)`
2. **🌐 Navigace:** Otevření stránky `home_page`
   `home_page.open()`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `home_page.welcome_section` na stránce
   `expect(home_page.welcome_section).to_be_visible()`
4. **🔍 Kontrola:** Ověření, že text prvku `home_page.welcome_section` obsahuje test_user['name']
   `expect(home_page.welcome_section).to_contain_text(test_user["name"])`

<a id="tc-40-prf-p-edvypln-n-daj-sp-n-aktualizace-profilu-a-p-esm-rov-n-na-home"></a>
#### `TC-40-PRF`: Předvyplnění údajů, úspěšná aktualizace profilu a přesměrování na /home.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc40_prf_display_and_update_profile()` |
| **Testovací třída** | `TestUserProfileAndDashboard` |
| **Zdrojový soubor** | [`tests/profile/test_profile.py:38`](tests/profile/test_profile.py#L38) |
| **Pytest Markery** | `@profile`, `@smoke` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ProfilePage(page)` do proměnné `profile_page`
   `profile_page = ProfilePage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `HomePage(page)` do proměnné `home_page`
   `home_page = HomePage(page)`
3. **🌐 Navigace:** Otevření stránky `profile_page`
   `profile_page.open()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `profile_page.heading` na stránce
   `expect(profile_page.heading).to_be_visible()`
5. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `profile_page.name_input` (očekáváno: test_user['name'])
   `expect(profile_page.name_input).to_have_value(test_user["name"])`
6. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `profile_page.email_input` (očekáváno: test_user['email'])
   `expect(profile_page.email_input).to_have_value(test_user["email"])`
7. **🎲 Test Data:** Dynamické generování testovacích dat `generate_valid_ico()` -> `valid_ico`
   `valid_ico = generate_valid_ico()`
8. **⚙️ Příprava:** Nastavení lokální proměnné `valid_phone` = `'+420 777 999 888'`
   `valid_phone = "+420 777 999 888"`
9. **▶️ Krok:** Vyvolání akce `profile_page.update_profile()`
   `profile_page.update_profile(ico=valid_ico, phone=valid_phone)`
10. **🔍 Kontrola:** Ověření přesměrování a URL adresy (očekáváno: home_page.URL) — *(US-17: Po uložení je uživatel přesměrován na domovskou stránku)*
   `expect(page).to_have_url(home_page.URL, timeout=10000)`
11. **🔍 Kontrola:** Ověření viditelnosti prvku `home_page.welcome_section` na stránce
   `expect(home_page.welcome_section).to_be_visible()`
12. **⏳ Čekání:** Čekání na ustálení síťového a vykreslovacího stavu ('networkidle')
   `page.wait_for_load_state("networkidle")`
13. **🌐 Navigace:** Otevření stránky `profile_page` — *(Ověření perzistence uložených dat po návratu do profilu)*
   `profile_page.open()`
14. **⏳ Čekání:** Čekání na ustálení síťového a vykreslovacího stavu ('networkidle')
   `page.wait_for_load_state("networkidle")`
15. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `profile_page.ico_input` (očekáváno: valid_ico)
   `expect(profile_page.ico_input).to_have_value(valid_ico)`
16. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `profile_page.phone_input` (očekáváno: valid_phone)
   `expect(profile_page.phone_input).to_have_value(valid_phone)`

<a id="tc-41-prf-validace-form-tu-i-o-a-telefonu-v-profilu"></a>
#### `TC-41-PRF`: Validace formátu IČO a telefonu v profilu.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc41_prf_ico_and_phone_validation_in_profile()` |
| **Testovací třída** | `TestUserProfileAndDashboard` |
| **Zdrojový soubor** | [`tests/profile/test_profile.py:65`](tests/profile/test_profile.py#L65) |
| **Pytest Markery** | `@profile`, `@regression` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ProfilePage(page)` do proměnné `profile_page`
   `profile_page = ProfilePage(page)`
2. **🌐 Navigace:** Otevření stránky `profile_page`
   `profile_page.open()`
3. **🎲 Test Data:** Dynamické generování testovacích dat `generate_invalid_ico()` -> `invalid_ico`
   `invalid_ico = generate_invalid_ico()`
4. **▶️ Krok:** Vyvolání akce `profile_page.update_profile()`
   `profile_page.update_profile(ico=invalid_ico, phone="123")`
5. **🔍 Kontrola:** Ověření viditelnosti prvku `profile_page.form` na stránce — *(Formulář zůstává zobrazen)*
   `expect(profile_page.form).to_be_visible()`

<a id="tc-42-prf-pokus-o-zm-nu-e-mailu-na-ji-obsazenou-adresu-je-odm-tnut"></a>
#### `TC-42-PRF`: Pokus o změnu e-mailu na již obsazenou adresu je odmítnut.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc42_prf_duplicate_email_change_rejected()` |
| **Testovací třída** | `TestUserProfileAndDashboard` |
| **Zdrojový soubor** | [`tests/profile/test_profile.py:77`](tests/profile/test_profile.py#L77) |
| **Pytest Markery** | `@profile`, `@regression` |
| **Automatické předpoklady (Fixtures)** | `setup_logged_in_user` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ProfilePage(page)` do proměnné `profile_page`
   `profile_page = ProfilePage(page)`
2. **🌐 Navigace:** Otevření stránky `profile_page`
   `profile_page.open()`
3. **✍️ Vstup:** Vyplnění pole `pole` hodnotou lecturer_user['email'] — *(Pokus o nastavení e-mailu existujícího lektora)*
   `profile_page.email_input.fill(lecturer_user["email"])`
4. **🖱️ Kliknutí:** Kliknutí na prvek / tlačítko `profile_page.save_button`
   `profile_page.save_button.click()`
5. **🌐 Navigace:** Otevření stránky `profile_page` — *(Znovunačtení profilu ověří, že e-mail nebyl přepsán na cizí adresu)*
   `profile_page.open()`
6. **🔍 Kontrola:** Ověření hodnoty ve formulářovém poli `profile_page.email_input` (očekáváno: test_user['email'])
   `expect(profile_page.email_input).to_have_value(test_user["email"])`

<a id="modul-sec"></a>
### 🛡️ Modul: Bezpečnost, RBAC a architektura (SEC)

*Počet testů v modulu: **5** | Celkem akcí: **27** | Celkem kontrol: **11***

<a id="tc-43-sec-p-esm-rov-n-nep-ihl-en-ho-u-ivatele-z-priv-tn-ch-url-na-katalog"></a>
#### `TC-43-SEC`: Přesměrování nepřihlášeného uživatele z privátních URL na katalog.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc43_sec_unauthenticated_private_url_access_blocked()` |
| **Testovací třída** | `TestSecurityAndAuthorization` |
| **Zdrojový soubor** | [`tests/security/test_security.py:29`](tests/security/test_security.py#L29) |
| **Pytest Markery** | `@security`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `ProfilePage(page)` do proměnné `profile_page`
   `profile_page = ProfilePage(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `MyCoursesPage(page)` do proměnné `my_courses_page`
   `my_courses_page = MyCoursesPage(page)`
3. **🌐 Navigace:** Otevření stránky `profile_page` — *(1. Pokus o přístup na /profile bez přihlášení)*
   `profile_page.open()`
4. **🔍 Kontrola:** Ověření viditelnosti prvku `profile_page.navbar.login_link` na stránce
   `expect(profile_page.navbar.login_link).to_be_visible()`
5. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `profile_page.form`
   `expect(profile_page.form).not_to_be_visible()`
6. **🌐 Navigace:** Otevření stránky `my_courses_page` — *(2. Pokus o přístup na /my-courses bez přihlášení)*
   `my_courses_page.open()`
7. **🔍 Kontrola:** Ověření viditelnosti prvku `my_courses_page.navbar.login_link` na stránce
   `expect(my_courses_page.navbar.login_link).to_be_visible()`

<a id="tc-44-sec-z-kaz-lektorsk-ch-operac-pro-u-ivatele-v-roli-z-kazn-ka"></a>
#### `TC-44-SEC`: Zákaz lektorských operací pro uživatele v roli zákazníka.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc44_sec_customer_cannot_access_lecturer_operations()` |
| **Testovací třída** | `TestSecurityAndAuthorization` |
| **Zdrojový soubor** | [`tests/security/test_security.py:45`](tests/security/test_security.py#L45) |
| **Pytest Markery** | `@security`, `@smoke`, `@xfail` |
| **⚠️ Evidovaný defekt (xfail)** | **BR-01: Aplikace v rozporu s US-18 nezabezpečuje /courses/create před rolí Zákazník** |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page, test_user['email'], test_user['password'])
   `login_user(page, test_user["email"], test_user["password"])`
2. **⚙️ Příprava:** Inicializace Page Objectu `CreateCoursePage(page)` do proměnné `create_course_page`
   `create_course_page = CreateCoursePage(page)`
3. **🌐 Navigace:** Otevření stránky `create_course_page`
   `create_course_page.open()`
4. **⏳ Čekání:** Čekání na ustálení síťového a vykreslovacího stavu ('networkidle')
   `page.wait_for_load_state("networkidle")`
5. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `create_course_page.form` — *(Zákazník nemá přístup k formuláři pro tvorbu kurzu)*
   `expect(create_course_page.form).not_to_be_visible()`

<a id="tc-45-sec-z-kaz-z-pisu-na-kurz-pro-u-ivatele-v-roli-lektora"></a>
#### `TC-45-SEC`: Zákaz zápisu na kurz pro uživatele v roli lektora.

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc45_sec_lecturer_cannot_enroll_as_customer()` |
| **Testovací třída** | `TestSecurityAndAuthorization` |
| **Zdrojový soubor** | [`tests/security/test_security.py:57`](tests/security/test_security.py#L57) |
| **Pytest Markery** | `@security`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🔑 Autentizace:** Provedení přihlášení uživatele (page)
   `login_lecturer(page)`
2. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
3. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.courses_header` na stránce — *(Lektor otevře katalog)*
   `expect(courses_page.courses_header).to_be_visible()`
4. **🔍 Kontrola:** Ověření přesného textu prvku `courses_page.add_course_button` (očekáváno: 'Přidat kurz') — *(V horní liště má tlačítko pro přidání kurzu, nikoliv klientské registrace)*
   `expect(courses_page.add_course_button).to_have_text("Přidat kurz")`

<a id="tc-46-sec-ochrana-formul-csrf-tokenem-p-tomnost-xsrf-token"></a>
#### `TC-46-SEC`: Ochrana formulářů CSRF tokenem (přítomnost XSRF-TOKEN).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc46_sec_csrf_cookie_present_for_stateful_forms()` |
| **Testovací třída** | `TestSecurityAndAuthorization` |
| **Zdrojový soubor** | [`tests/security/test_security.py:69`](tests/security/test_security.py#L69) |
| **Pytest Markery** | `@security`, `@smoke` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **⚙️ Příprava:** Inicializace Page Objectu `LoginPage(page)` do proměnné `login_page`
   `login_page = LoginPage(page)`
2. **🌐 Navigace:** Otevření stránky `login_page`
   `login_page.open()`
3. **⏳ Čekání:** Čekání na ustálení síťového a vykreslovacího stavu ('networkidle')
   `page.wait_for_load_state("networkidle")`
4. **⚙️ Příprava:** Nastavení lokální proměnné `cookies` = `context.cookies()`
   `cookies = context.cookies()`
5. **⚙️ Příprava:** Nastavení lokální proměnné `cookie_names` = `...`
   `cookie_names = [c["name"] for c in cookies]`
6. **⚙️ Příprava:** Nastavení lokální proměnné `has_security_cookie` = `any(...)` — *(Aplikace nastavuje bezpečnostní CSRF / session tokeny)*
   `has_security_cookie = any("XSRF" in name or "session" in name.lower() for name in cookie_names)`
7. **🔍 Kontrola:** Ověření podmínky datového stavu: `assert has_security_cookie, f"Očekáván bezpečnostní token v cookies, nalezeno: {cookie_names}"` (Očekáváno: ...)
   `assert has_security_cookie, f"Očekáván bezpečnostní token v cookies, nalezeno: {cookie_names}"`

<a id="tc-47-sec-regenerace-session-id-p-i-p-ihl-en-a-odhl-en-ochrana-proti-session-fixation"></a>
#### `TC-47-SEC`: Regenerace session ID při přihlášení a odhlášení (ochrana proti Session Fixation).

| Vlastnost | Hodnota |
| :--- | :--- |
| **Kód funkce** | `test_tc47_sec_session_regeneration_on_login_and_logout()` |
| **Testovací třída** | `TestSecurityAndAuthorization` |
| **Zdrojový soubor** | [`tests/security/test_security.py:84`](tests/security/test_security.py#L84) |
| **Pytest Markery** | `@security`, `@regression` |

##### 👣 Postup testu (Kroky & Kontroly):

1. **🌐 Navigace:** Přímá navigace na URL ...
   `page.goto(f"{settings.BASE_URL}/login")`
2. **⏳ Čekání:** Čekání na ustálení síťového a vykreslovacího stavu ('networkidle')
   `page.wait_for_load_state("networkidle")`
3. **⚙️ Příprava:** Nastavení lokální proměnné `initial_cookies` = `...`
   `initial_cookies = {c["name"]: c["value"] for c in context.cookies()}`
4. **⚙️ Příprava:** Nastavení lokální proměnné `initial_session` = `initial_cookies.get('laravel_session')`
   `initial_session = initial_cookies.get("laravel_session")`
5. **🔑 Autentizace:** Provedení přihlášení uživatele (page, test_user['email'], test_user['password']) — *(Přihlášení)*
   `login_user(page, test_user["email"], test_user["password"])`
6. **⚙️ Příprava:** Nastavení lokální proměnné `logged_in_cookies` = `...`
   `logged_in_cookies = {c["name"]: c["value"] for c in context.cookies()}`
7. **⚙️ Příprava:** Nastavení lokální proměnné `logged_in_session` = `logged_in_cookies.get('laravel_session')`
   `logged_in_session = logged_in_cookies.get("laravel_session")`
8. **🔍 Kontrola:** Ověření podmínky datového stavu: `assert logged_in_session is not None` — *(Session ID se po úspěšném přihlášení změnilo)*
   `assert logged_in_session is not None`
9. **🔀 Větvení:** Podmíněná větev: pokud platí `initial_session`
   `if initial_session:`
  1. **🔍 Kontrola:** Ověření podmínky datového stavu: `assert logged_in_session != initial_session, "Session ID musí být při přihlášení regenerováno"` (Očekáváno: 'Session ID musí být při přihlášení regenerováno')
     `assert logged_in_session != initial_session, "Session ID musí být při přihlášení regenerováno"`
10. **🚪 Odhlášení:** Odhlášení uživatele z portálu — *(Odhlášení)*
   `logout_user(page)`
11. **⚙️ Příprava:** Nastavení lokální proměnné `logged_out_cookies` = `...`
   `logged_out_cookies = {c["name"]: c["value"] for c in context.cookies()}`
12. **⚙️ Příprava:** Inicializace Page Objectu `CoursesPage(page)` do proměnné `courses_page`
   `courses_page = CoursesPage(page)`
13. **🔍 Kontrola:** Ověření viditelnosti prvku `courses_page.login_link` na stránce
   `expect(courses_page.login_link).to_be_visible()`
14. **🔍 Kontrola:** Ověření nepřítomnosti / skrytí prvku `courses_page.logout_button`
   `expect(courses_page.logout_button).not_to_be_visible()`

---

*(Konec vygenerovaného přehledu testů)*
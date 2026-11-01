# 🗺️ Doménové mapování a trasovatelnost (Domain & Traceability Mapping)

Tento referenční soubor slouží agentovi k bleskovému vyhledání relevantních **User Stories** (`docs/požadavky_ust_podle_src.md`) a **Test Casů** (`docs/TEST_CASES.md`) při tvorbě JIRA hlášení.

---

## 🏛️ Přehled domén, komponent a vazeb

| Modul | Kód | Komponenta | Dotčené User Stories | Pokryté Test Casy | Umístění automatizovaných testů |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Autentizace & Sezení** | `AUTH` | `Frontend / Auth / Session` | **US-01** (Registrace)<br>**US-02** (Přihlášení)<br>**US-03** (Odhlášení)<br>**US-04** (Reset hesla)<br>**US-05** (Změna hesla)<br>**US-06** (Ověření e-mailu)<br>**US-07** (Rate limit) | `TC-01-AUTH` až `TC-21-AUTH` | `tests/auth/test_login.py`<br>`tests/auth/test_registration.py` |
| **Katalog a Detail kurzů** | `CRS` | `Frontend / UI / Katalog` | **US-08** (Katalog kurzů)<br>**US-09** (Detail kurzu)<br>**US-10** (Kapacita běhu) | `TC-22-CRS` až `TC-26-CRS` | `tests/courses/test_courses.py` |
| **Zápis & Moje kurzy** | `ENR` | `Frontend / Formuláře / Zápis` | **US-11** (Zápis s IČO/tel)<br>**US-12** (Přehled mých kurzů) | `TC-27-ENR` až `TC-31-ENR` | `tests/enrollment/test_enrollment.py` |
| **Správa lektorem** | `LEC` | `Frontend / Lektor / Správa` | **US-13** (Tvorba kurzu)<br>**US-14** (Vypsání termínu)<br>**US-15** (Seznam studentů) | `TC-32-LEC` až `TC-38-LEC` | `tests/lecturer/test_lecturer.py` |
| **Profil & Nástěnka** | `PRF` | `Frontend / Profil` | **US-16** (Domovská nástěnka)<br>**US-17** (Správa profilu) | `TC-39-PRF` až `TC-42-PRF` | `tests/profile/test_profile.py` |
| **Bezpečnost & RBAC** | `SEC` | `Routing / Autorizace (RBAC)` | **US-18** (Řízení přístupu RBAC)<br>**US-19** (CSRF ochrana) | `TC-43-SEC` až `TC-47-SEC` | `tests/security/test_security.py` |

---

## 🔗 Rychlé hypertextové odkazy do projektové dokumentace

Při vyplňování sekcí **Vázané User Stories** a **Související Test Casy** v JIRA bug reportu použijte následující přesné markdown formáty:

### User Stories:
* `[`US-01: Registrace zákaznického účtu`](požadavky_ust_podle_src.md#us-01-registrace-zákaznického-účtu-s-automatickým-přihlášením)`
* `[`US-02: Přihlášení do aplikace`](požadavky_ust_podle_src.md#us-02-přihlášení-do-aplikace)`
* `[`US-03: Bezpečné odhlášení ze systému`](požadavky_ust_podle_src.md#us-03-bezpečné-odhlášení-ze-systému)`
* `[`US-08: Prohlížení katalogu kurzů`](požadavky_ust_podle_src.md#us-08-prohlížení-katalogu-kurzů-pro-návštěvníky)`
* `[`US-09: Detail kurzu a vypsané termíny`](požadavky_ust_podle_src.md#us-09-detail-kurzu-a-vypsané-termíny)`
* `[`US-10: Indikace a zamezení zápisu při naplněné kapacitě`](požadavky_ust_podle_src.md#us-10-indikace-a-zamezení-zápisu-při-naplněné-kapacitě)`
* `[`US-11: Nezávazná registrace na běh kurzu`](požadavky_ust_podle_src.md#us-11-nezávazná-registrace-na-běh-kurzu-zákazníkem)`
* `[`US-12: Přehled mých zapsaných kurzů`](požadavky_ust_podle_src.md#us-12-přehled-mých-zapsaných-kurzů)`
* `[`US-13: Vytvoření nového kurzu lektorem`](požadavky_ust_podle_src.md#us-13-vytvoření-nového-kurzu-lektorem)`
* `[`US-14: Vypsání nového termínu kurzu`](požadavky_ust_podle_src.md#us-14-vypsání-nového-termínu-kurzu)`
* `[`US-15: Zobrazení seznamu přihlášených účastníků`](požadavky_ust_podle_src.md#us-15-zobrazení-seznamu-přihlášených-účastníků)`
* `[`US-18: Řízení přístupu na základě rolí (RBAC)`](požadavky_ust_podle_src.md#us-18-řízení-přístupu-na-základě-rolí-rbac)`

### Test Casy:
Uvádět kód test casu a odkaz na konkrétní testovací soubor, např.:
* ``TC-38-LEC` (v [`tests/lecturer/test_lecturer.py`](../tests/lecturer/test_lecturer.py))`
* ``TC-44-SEC` (v [`tests/security/test_security.py`](../tests/security/test_security.py))`
* ``TC-07-AUTH` (v [`tests/auth/test_login.py`](../tests/auth/test_login.py))`
* ``TC-29-ENR` (v [`tests/enrollment/test_enrollment.py`](../tests/enrollment/test_enrollment.py))`

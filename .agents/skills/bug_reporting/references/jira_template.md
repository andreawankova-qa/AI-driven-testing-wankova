# 📋 Standardní JIRA šablona hlášení chyb (Defect Report Template)

Tato šablona definuje povinnou strukturu pro hlášení incidentů a chyb v projektu **Demo Login & Courses Portal (`DLCP`)**. Každé hlášení musí obsahovat všechny níže uvedené sekce, aby bylo plně reprodukovatelné vývojáři a trasovatelné v testovací dokumentaci.

---

## 🐞 Vzor JIRA hlášení

```markdown
### 🐞 BR-XX [MODUL]: <Stručný a výstižný název problému – Co, Kde a Za jakých podmínek>

#### JIRA Ticket Metadata
* **Project:** Demo Login & Courses Portal (`DLCP`)
* **Issue Type:** 🐞 Bug / Defect
* **Summary (Název):** `[MODUL/Komponenta] <Stručný popis incidentu>`
* **Komponenta:** <Frontend / Backend / Routing / Autorizace (RBAC) / Validace / UI>
* **Závažnost (Severity):** <Critical / High / Medium / Low> (<Stručné technické odůvodnění dle matice>)
* **Priorita (Priority):** <High / Medium / Low> (<Stručné byznysové odůvodnění dle matice>)
* **Reprodukovatelnost:** <Vždy (100 %) / Nahodile (Intermittent / Flaky) / Pouze jednou>
* **Vázané User Stories:** 
  - [`US-XX: <Název User Story>`](požadavky_ust_podle_src.md#us-xx-...)
* **Související Test Casy:** 
  - `TC-XX-MOD` (v [`tests/<modul>/test_<soubor>.py`](../tests/<modul>/test_<soubor>.py))
* **Prostředí:** Testovací prostředí (`http://testovani.kitner.cz`), Browser: Chromium / Playwright
* **Nahlásil:** Andrea Wanková
* **Datum nálezu:** <DD. MM. RRRR>

---

#### 📝 Popis problému (Description)
<Jasný a srozumitelný souhrn problému. Co přesně nefunguje, v jakém kontextu k chybě dochází a jaký je základní projev.>

---

#### ⚙️ Předpoklady (Preconditions)
1. <Výchozí stav systému před zahájením kroků (např. existující uživatel s konkrétní rolí, stav databáze, odhlášený stav)>.
   - **E-mail:** `<email>`
   - **Heslo:** `<heslo>`

---

#### 👣 Kroky k reprodukci (Steps to Reproduce)
1. Otevři v prohlížeči URL: `<přesná_URL>`.
2. Proveď akci <konkrétní vstup, kliknutí, odeslání>.
3. <Následující krok reprodukce>.
4. Zkontroluj zobrazený výsledek na stránce.

---

#### ✅ Očekávané chování (Expected Result)
* <Popis správného chování dle specifikace / User Story>.
* <Co má systém zobrazit, jaké přesměrování má nastat, jaký HTTP kód se má vrátit>.
* <Negativní podmínka: co se naopak nesmí stát / vykreslit>.

---

#### ❌ Skutečné chování (Actual Result)
* <Přesný popis toho, co systém reálně udělal v rozporu se specifikací>.
* <Chybové hlášení v UI, chybějící přesměrování, neočekávaný prvek, chybový kód>.

---

#### ⚠️ Bezpečnostní a byznysový dopad (Security & Business Impact)
* **Byznysový dopad:** <Jak chyba ovlivňuje uživatele, data, prodej nebo integritu portálu>.
* **Bezpečnostní klasifikace:** <Pokud relevantní, např. OWASP Top 10:2021 – A01 (Broken Access Control) / A03 (Injection) / A07 (Identification and Authentication Failures)>.
* **Dopad na testování:** <Zda chyba blokuje další testovací případy (Blocker)>.

---

#### 💻 Technický důkaz a vizuální záznamy (Failure Log & Visual Evidence)
* **Screenshot / Vizuální důkaz:** `reports/screenshots/<nazev_screenshotu>.png` (nebo odkaz na obrázek)
* **Playwright Trace:** `reports/traces/<nazev_trace>.zip` (případně odkaz na HTML report v `reports/html/report.html`)
* **Chybový výpis z testu (Console / Call Log / Traceback):**

```text
> expect(locator).to_be_visible()
E AssertionError: Locator expected to be visible
E Actual value: hidden
E Call log:
E   - Expect "to_be_visible" with timeout 5000ms
```

---

#### 💡 Doporučené řešení pro vývojáře (Fix Recommendation)
1. **Frontend (<např. Vue router / komponenta>):**  
   <Konkrétní technický návrh opravy – např. přidat Navigation Guard, opravit validaci v Page/Komponentě, přidat ošetření stavu>.
2. **Backend API:**  
   <Konkrétní technický návrh pro backend – např. ověřit JWT/session na endpointu, vrátit HTTP 403/422>.

---

#### 🔄 Záznam o verifikaci opravy (Verification Log)
* **Datum re-testu:** *(vyplní se po nasazení opravy)*
* **Verifikoval:** *(jméno testera po re-testu)*
* **Výsledek re-testu:** *(zatím neproveden)*
```

---

## 📌 Pravidla pro tvorbu polí

1. **ID chyby:** Formát `BR-XX` s dvoumístným indexem s vedoucí nulou (`BR-01`, `BR-02`, ..., `BR-10`).
2. **Summary (Název):**
   - Vždy začíná prefixem modulu v hranatých závorkách: `[MODUL/Komponenta]`.
   - Popisuje incident podle schématu: *Kde se stalo + Co se stalo + Za jakých podmínek*.
   - Příklad: `[RBAC/Security] Chybějící ochrana URL /courses/create – formulář je přístupný pro roli Zákazník`.
3. **Kroky k reprodukci:**
   - Musí být deterministické, číslované a minimální nutné k vyvolání chyby.
   - Žádné vágní instrukce typu *„Zkus se přihlásit a něco vyplň“*.
4. **Oddělení Očekávaného vs. Skutečného:**
   - Očekávané chování čerpá ze schválených User Stories (`docs/požadavky_ust_podle_src.md`).
   - Skutečné chování popisuje reálný stav systému bez dohadů.

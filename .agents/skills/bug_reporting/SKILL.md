---
name: bug_reporting
description: >-
  POVINNĚ aktivuj tento skill VŽDY, když agent při vytváření, psaní, spouštění, kontrole nebo úpravě
  automatizovaných testů (tests/), Page Objectů či assertů narazí na selhání testu, chybové chování aplikace,
  regresi nebo defekt, a to i v případě, že uživatel slova jako 'bug', 'chyba' či 'JIRA' v promptu výslovně
  neuvede (např. při 'proč test selhal?', 'oprav padající scénář', 'prověř chování stránky'). Vynucuje
  autonomní pokus o reprodukci, striktní zákaz zakládání JIRA ticketů pro chyby v testu (test bug),
  kompletní šablonu hlášení do docs/JIRA_BUG_REPORTS.md, objektivní ISTQB Severity/Priority a provázání
  s User Stories (US-xx) a Test Casy (TC-xx). Aktivuj jej také, když uživatel požaduje hromadné
  spuštění všech testů s reportováním nalezených chyb, přehled nahlášených chyb nebo vygenerování
  či aktualizaci HTML reportu bugů (docs/bug_reports.html).
---

# 🐞 Bug Reporting – Standardy hlášení chyb a správa incidentů (JIRA)

Metodika pro profesionální tvorbu a evidenci hlášení chyb (Defect Reports) v projektu vzdělávacího portálu Kitner.cz podle standardů **ISTQB** a projektového registru [docs/JIRA_BUG_REPORTS.md](../../../docs/JIRA_BUG_REPORTS.md).

> **Základní princip:**  
> *Každé hlášení musí být reprodukované, ne-duplicitní, opřené o technické důkazy a přímo trasovatelné na User Story a Test Case.*

---

## 🧭 Základní workflow agenta (Krok za krokem)

```mermaid
flowchart TD
    A[Vstup: Spuštění všech testů / Pád testu / Manuální popis] --> V[1. Spuštění testů a reprodukce]
    V -->|pytest celé sady NEBO konkrétního testu| T{Byl u padajícího testu potvrzen defekt?}
    T -->|NE: Test prošel / Aplikace v pořádku| STOP[🛑 Konec: JIRA se nezakládá - zpráva testerovi]
    T -->|Test Bug / Flaky test| T1[Oprava kódu testu a opětovný běh - JIRA se nezakládá]
    T -->|Podezření na Product Bug| DUP{2. Kontrola duplicity v registru}
    DUP -->|Chyba již evidována - DUPLICITA| DUP_STOP[🛑 Odkaz na existující BR-XX]
    DUP -->|Nová dosud neevidovaná chyba| BV[3. Živé ověření v prohlížeči - bug_verification]
    BV -->|Nereprodukováno| T1
    BV -->|Reprodukováno + screenshot| B[4. Doménové mapování a trasovatelnost]
    B --> C[5. Objektivní určení Severity & Priority]
    C --> D[6. Sestavení JIRA reportu dle šablony]
    D --> F[7. Bezpečný zápis: manage_bug_reports.py append]
    F --> H[8. Vygenerování/aktualizace docs/bug_reports.html]
    H --> G[Hotovo: Souhrn reportů + odkaz na HTML přehled]
```

---

## 1. 📥 Verifikace, Triáž a Kontrola duplicity (MANDATORNÍ)

Zlaté pravidlo QA: **Nehlásit neověřené chyby, nehlásit chyby testovacího kódu a nezakládat duplicity.**

### 🔍 Krok 1: Spuštění testů a autonomní reprodukce
Agent **vždy nejprve aktivně ověří** stav testů a reprodukuje chybu:
* **Hromadný běh všech automatizovaných testů:**  
  Pokud je cílem zkontrolovat celou sadu a nahlásit všechny chyby, spustí kompletní testovací sadu včetně zachycení důkazů:  
  `./.venv/bin/pytest --screenshot only-on-failure --tracing retain-on-failure`  
  - Následně projde **každý padající test** z běhu a pro každý zvlášť provede kroky 2–5 níže.
* **Jednotlivý test:** Spustí dotčený test v terminálu:  
  `./.venv/bin/pytest tests/<slozka>/<soubor>.py -k "<nazev_testu>" --screenshot only-on-failure --tracing retain-on-failure -v`  
  - *Pokud test projde (PASS):* **JIRA ticket se ZÁSADNĚ NEZAKLÁDÁ!** Agent informuje uživatele s výstupem testu.
  - *Pokud test selže (FAIL):* Získá čerstvý důkaz (log, timeout, screenshot, trace) a pokračuje.
* **U manuálního hlášení:** Ověří chování spuštěním testu nebo prověřením stránky.  
  - *Pokud aplikace funguje správně:* **JIRA ticket se NEZAKLÁDÁ.** Agent vysvětlí korektní stav doložený akceptačním kritériem.

### 🛑 Krok 2: Triáž incidentu a kontrola duplicity
* 🛑 **Test Bug / Flaky Test:** Selhání kvůli lokátoru, setupu nebo flaky síti (aplikace je v pořádku) ➔ **JIRA se nezakládá**, agent test opraví a znovu jej spustí.
* 🔎 **Kontrola duplicity v registru:** U podezření na *Product Bug* agent nejprve ověří stávající incidenty:  
  `python3 .agents/skills/bug_reporting/scripts/manage_bug_reports.py list`
  - **Pokud již chyba existuje (DUPLICITA):** **Nový ticket se NEVYTVÁŘÍ.** Agent odkáže na existující `BR-XX` a jeho stav (`🔴 Otevřeno` / `🟡 V řešení`).

### 🌐 Krok 3: Povinné živé ověření v prohlížeči (`bug_verification`)
Před založením nového `BR-XX` agent aktivuje skill `bug_verification` a pokusí se chybu nasimulovat přímo přes `browser` subagenta (nikoli jen testem), přičemž pořídí screenshot do `reports/screenshots/`:
* Pokud se chyba v prohlížeči **NEreprodukuje** ➔ **JIRA se nezakládá**, jde pravděpodobně o *Test Bug* (opravit a znovu spustit test).
* Pokud se chyba v prohlížeči **reprodukuje** ➔ *Product Bug* je potvrzen, do metadat se zapíše `* **Ověření v prohlížeči:** Reprodukováno (<DD. MM. RRRR>)` a přiloží se screenshot.

---

## 2. 🗺️ Doménové mapování a trasovatelnost

Vazby agent vyhledá v [domain_mapping.md](./references/domain_mapping.md):
1. **Modul & Komponenta:** `AUTH`, `CRS`, `ENR`, `LEC`, `PRF` nebo `SEC`.
2. **Vázané User Stories:** Odkaz do [docs/požadavky_ust_podle_src.md](../../../docs/požadavky_ust_podle_src.md) (např. `US-18`, lze i více).
3. **Související Test Case:** Kód z [docs/TEST_CASES.md](../../../docs/TEST_CASES.md) a cesta k testu (pokud test neexistuje: `Zatím nepokryto`).
4. **Inspekce kódu testu:** Z fází *Arrange* a *Act* v `tests/` zrekonstruuje číslované **Kroky k reprodukci**.

---

## 3. ⚖️ Určení Závažnosti (Severity) a Priority (Priority)

Hodnoty se určují výhradně podle matice v [severity_vs_priority.md](./references/severity_vs_priority.md):
* **Severity (Technický dopad):**
  - `Critical / Blocker`: Bezpečnostní zranitelnost (OWASP), pád či zamrznutí aplikace, poškození či ztráta dat, blokace testování.
  - `High`: Závažné selhání byznysové cesty bez workaroundu, blokace akce na podporovaných zařízeních/rozlišeních.
  - `Medium`: Běžná funkční či validační chyba s workaroundem, pomalá odezva či výkonnostní propad.
  - `Low`: Kosmetická, typografická nebo drobná UX/layoutová vada.
* **Priority (Byznysová naléhavost):**
  - `High`: Blokuje release, testování, kritický nákupní proces nebo bezpečnost.
  - `Medium`: Plánovaná oprava v následujícím sprintu.
  - `Low`: Odložitelné do backlogu, drobná estetická úprava.

---

## 4. 📋 Standardní formát JIRA ticketu

Ticket se striktně řídí šablonou v [jira_template.md](./references/jira_template.md). Každé hlášení musí obsahovat:
* **JIRA Metadata:** ID (`BR-XX`), Summary s modulem `[MODUL/Komponenta]`, Komponenta, Severity, Priority, **Reprodukovatelnost** (`Vždy (100 %)` / `Nahodile` / `Pouze jednou`), vázané US, TC, Prostředí, Nahlásil (`Andrea Wanková`), Datum.
* **Obsah:** Popis, Předpoklady, Kroky k reprodukci, Očekávané vs. Skutečné chování, Bezpečnostní/Byznysový dopad (OWASP), **Technický důkaz a vizuální záznamy** (screenshot z `reports/screenshots/`, trace z `reports/traces/`, failure log), Doporučené řešení (Frontend/Backend) a Verifikaci.

---

## 5. 💾 Bezpečný zápis a generování HTML přehledu

Pro každý potvrzený a dosud neevidovaný *Product Bug* agent zapíše hlášení rovnou do centrálního registru `docs/JIRA_BUG_REPORTS.md` a zajistí aktuální HTML přehled:

1. **Zjištění nového ID:**
   ```bash
   python3 .agents/skills/bug_reporting/scripts/manage_bug_reports.py next-id
   ```
2. **Validace a bezpečný zápis:** Agent připraví report podle šablony (včetně kroků k reprodukci, očekávaného a skutečného výsledku, prostředí a odkazu na screenshot nebo trace) a zapíše jej pomocí nástroje `manage_bug_reports.py` (příkaz `append` zároveň **automaticky přegeneruje** `docs/bug_reports.html`):
   ```bash
   python3 .agents/skills/bug_reporting/scripts/manage_bug_reports.py append <cesta_k_souboru>
   ```
3. **Aktualizace a ověření HTML přehledu:**  
   Po zpracování všech padajících testů (nebo po ruční úpravě `docs/JIRA_BUG_REPORTS.md`) agent ověří, že je HTML přehled všech nalezených chyb aktuální, případně jej přegeneruje příkazem:
   ```bash
   python3 .agents/skills/bug_reporting/scripts/manage_bug_reports.py html
   ```
4. **Prezentace souhrnu uživateli:** Na konci agent předá přehled vytvořených (případně duplicitních) `BR-XX` reportů, identifikovaných *Test Bugů* a odkaz na [docs/JIRA_BUG_REPORTS.md](../../../docs/JIRA_BUG_REPORTS.md) i HTML přehled [docs/bug_reports.html](../../../docs/bug_reports.html).

---

## 📚 Referenční dokumentace a nástroje

* **[manage_bug_reports.py](./scripts/manage_bug_reports.py):** CLI nástroj pro `list`, `next-id`, `validate`, `append` (s auto-generováním HTML) a `html`.
* **[generate_bug_reports.py](./scripts/generate_bug_reports.py):** Generátor interaktivního HTML přehledu [docs/bug_reports.html](../../../docs/bug_reports.html).
* **[jira_template.md](./references/jira_template.md):** Kompletní vzorová JIRA šablona se všemi sekcemi.
* **[severity_vs_priority.md](./references/severity_vs_priority.md):** Rozhodovací matice Závažnosti a Priority (ISTQB + OWASP).
* **[domain_mapping.md](./references/domain_mapping.md):** Trasovací matice modulů, User Stories a Test Casů.
* **[JIRA_BUG_REPORTS.md](../../../docs/JIRA_BUG_REPORTS.md):** Centrální registr všech evidovaných incidentů v projektu (Single Source of Truth).
* **[bug_reports.html](../../../docs/bug_reports.html):** Interaktivní HTML dashboard bug reportů pro prohlížeč a GitHub.

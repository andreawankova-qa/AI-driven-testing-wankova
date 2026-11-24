---
name: bug_verification
description: >-
  POVINNĚ aktivuj tento skill VŽDY před založením nového bug reportu (BR-XX) z bug_reporting i kdykoliv
  uživatel požaduje ověření, zda je chyba nebo nahlášený BR-XX report skutečný (např. 'ověř chybu v prohlížeči',
  'zkontroluj BR-01', 'reprodukuj chybu', 'je ten bug reálný?'). Vynucuje živou simulaci kroků přímo v prohlížeči
  přes browser subagenta (nikoli spuštěním automatizovaného testu), pořízení screenshotu do reports/screenshots/
  a doplnění stavu 'Reprodukováno' / 'Nereprodukováno' do docs/JIRA_BUG_REPORTS.md a docs/bug_reports.html.
---

# 🌐 Bug Verification – Živé ověření chyby v prohlížeči

Metodika pro nezávislé ověření, zda je hlášená nebo testem zachycená chyba skutečným defektem aplikace (*Product Bug*), pomocí přímé simulace v živém prohlížeči.

> **Zlaté pravidlo:**  
> *Neověřuj bug testem, který ho nahlásil. Otevři aplikaci jako reálný uživatel v prohlížeči, kroky ručně projdi a dolož výsledek čerstvým screenshotem.*

---

## 🧭 Workflow ověření

1. **Vstup:**
   - **Nový pád testu (z `bug_reporting`):** URL, přihlašovací údaje, kroky a očekávané chování ze selhaného testu nebo zadání.
   - **Existující report (`BR-XX`):** Záznam v [docs/JIRA_BUG_REPORTS.md](../../../docs/JIRA_BUG_REPORTS.md) (předpoklady, účet, URL, kroky k reprodukci, očekávané vs. skutečné chování).
2. **Živá simulace přes `browser` subagenta:**
   - Deleguj kroky na vestavěného `browser` subagenta (živý Chrome přes DevTools) s konkrétní URL, účtem a kroky.
   - **Čistý výchozí stav:** Před spuštěním kroků zajisti, aby stav prohlížeče odpovídal *Preconditions* (pokud je z předchozího ověření přihlášen jiný uživatel/role, nejprve se odhlaš).
   - U API/JS chyb nech subagenta zkontrolovat i síťové odpovědi nebo konzoli prohlížeče.
   - **Výpadek prohlížeče nebo prostředí:** Pokud `browser` subagent selže či cílová URL není dostupná, zastav se a nahlaš blokátor (neoznačuj chybu mylně jako *Test Bug* ani neobcházej zákaz `pytest`).
   - **Zákaz:** Nepoužívej `pytest` ani náhradní Playwright skript jako důkaz živé reprodukce.
3. **Pořízení a uložení screenshotu:**
   - `browser` subagent nemá přístup k souborovému systému — pořídí screenshot výsledného stavu a vrátí cestu ke souboru.
   - **Hlavní agent** zajistí existenci cílové složky (`mkdir -p reports/screenshots`) a screenshot do ní zkopíruje:
     - existující report: `reports/screenshots/verify_BR-XX_<YYYYMMDD_HHMM>.png`
     - nový nález: `reports/screenshots/verify_<modul>_<YYYYMMDD_HHMM>.png`
4. **Vyhodnocení a zápis:**
   - **Reprodukováno** *(aplikace v prohlížeči skutečně chybuje)*:
     - *Nový pád testu:* Potvrď *Product Bug* a předej screenshot + stav `Reprodukováno` do `bug_reporting` k založení `BR-XX`.
     - *Existující `BR-XX`:* Doplň nebo aktualizuj v `docs/JIRA_BUG_REPORTS.md` stav `Reprodukováno` a cestu ke screenshotu (viz formát níže).
   - **Nereprodukováno** *(aplikace v prohlížeči funguje podle specifikace)*:
     - *Nový pád testu:* **JIRA ticket se NEZAKLÁDÁ!** Nahlásíš možný *Test Bug* / *Flaky test*, přiložíš screenshot funkčního stavu a **opravíš + znovu spustíš dotčený test** (jinak jej Stop hook `check_bug_dod.py` vyhodnotí jako neohlášený pád v `lastfailed`).
     - *Existující `BR-XX`:* Doplň nebo aktualizuj v `docs/JIRA_BUG_REPORTS.md` stav `Nereprodukováno` a cestu ke screenshotu aktuálního stavu. Navrhni uzavření reportu nebo kontrolu testu (stav `🔴 Otevřeno` v tabulce neměň bez potvrzení uživatele).
5. **Aktualizace HTML přehledu:**
   - Po každé úpravě `docs/JIRA_BUG_REPORTS.md` přegeneruj HTML přehled:
     ```bash
     python3 .agents/skills/bug_reporting/scripts/manage_bug_reports.py html
     ```

---

## 📋 Formát zápisu do `docs/JIRA_BUG_REPORTS.md`

* **V sekci `#### JIRA Ticket Metadata`:**
  ```markdown
  * **Ověření v prohlížeči:** Reprodukováno (24. 11. 2026)
  ```
  *(nebo `Nereprodukováno (24. 11. 2026)`)*
* **V sekci `#### 💻 Technický důkaz a vizuální záznamy`:**
  ```markdown
  * **Screenshot z živého ověření:** `reports/screenshots/verify_BR-01_20261124_1245.png`
  ```
* Generátor `generate_bug_reports.py` z těchto údajů automaticky vykreslí náhled obrázku i stavový badge v [docs/bug_reports.html](../../../docs/bug_reports.html).

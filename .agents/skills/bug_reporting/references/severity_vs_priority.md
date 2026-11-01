# ⚖️ Rozhodovací matice: Závažnost (Severity) vs. Priorita (Priority)

Při hlášení chyb podle standardů **ISTQB** a osvědčených QA postupů je klíčové striktně rozlišovat mezi **technickou závažností incidentu** (Severity) a **byznysovou prioritou jeho nápravy** (Priority).

---

## 🧭 Základní definice (ISTQB Standard)

| Pojem | Otázka | Kdo rozhoduje | Definice |
| :--- | :--- | :--- | :--- |
| **Závažnost (Severity)** | *„Jak moc to rozbilo systém?“* | **QA Tester / Test Automation Engineer** | Technický a funkční dopad vady na chování, stabilitu, bezpečnost a integritu systému. |
| **Priorita (Priority)** | *„Jak rychle to musíme opravit?“* | **Product Owner / QA Lead / Tým** | Byznysová naléhavost opravy vady vzhledem k plánovaným releasům, reputaci a dopadu na uživatele. |

---

## 🌡️ Klasifikace závažnosti (Severity Levels)

### 1. 🔴 Critical / Blocker
- **Definice:** Systém je zcela nepoužitelný, došlo k pádu aplikace (crash) či zamrznutí UI (freeze), nedostupnosti klíčové funkce bez možnosti náhrady, tichému poškození či ztrátě dat (data corruption), nebo zásadní bezpečnostní zranitelnosti.
- **Bezpečnostní dopad:** Kritické zranitelnosti dle **OWASP Top 10** (např. *A01 Broken Access Control* umožňující neoprávněnou manipulaci, *A03 Injection*, *A07 Authentication Bypass*).
- **Příklady v portálu:**
  - Zákazník může přes přímou URL přistoupit a uložit lektorský kurz.
  - Pokus o přihlášení končí bílou obrazovkou a HTTP 500 chybou serveru.
  - Aplikace při uložení profilu tiše přepíše data jiného uživatele v databázi.
  - Testovací suite je zablokován a nelze pokračovat v exekuci testů.

### 2. 🟠 High (Závažná vada)
- **Definice:** Závažná funkční porucha hlavní byznysové funkcionality. Existuje buď velmi komplikovaný workaround, nebo workaround neexistuje, ale problém neshodí celou aplikaci. Zahrnuje i kompletní blokaci nákupní cesty na podporovaných mobilních zařízeních/rozlišeních.
- **Příklady v portálu:**
  - Zákazník se nemůže zapsat na běh kurzu, přestože kapacita není naplněna a zadaný telefon je validní.
  - Na mobilním rozlišení překryje plovoucí lišta tlačítko *„Objednat kurz“* a nelze jej stisknout.
  - Po přihlášení lektora se nezobrazuje seznam přihlášených studentů.
  - Rate limiting (ochrana proti brutální síle) nezablokuje účet ani po 10 neplatných pokusech.

### 3. 🟡 Medium (Střední vada)
- **Definice:** Běžná funkční či validační vada, která ovlivňuje vedlejší funkce nebo má jednoduchý a intuitivní workaround. Zahrnuje i výrazný propad výkonu (pomalé načítání či timeouty).
- **Příklady v portálu:**
  - Chybí ořezání mezer (trim) u e-mailu při přihlášení, uživatel s mezerou na konci dostane hlášku o neplatném heslu.
  - Validační hláška u pole IČO je nepřesná nebo se zobrazí anglicky namísto česky.
  - Načtení detailu kurzu trvá neúměrně dlouho (např. 15 sekund) kvůli neoptimalizovanému dotazu.
  - Nefunguje filtrování kurzů podle jedné konkrétní kategorie, ale fulltextové vyhledávání funguje.

### 4. 🟢 Low / Minor / Trivial (Drobná vada)
- **Definice:** Kosmetická, vizuální, typografická vada nebo drobná neshoda s UX/přístupností, která nebrání provedení jakékoliv byznysové akce.
- **Příklady v portálu:**
  - Překlep v popisu kurzu nebo v patičce stránky.
  - Tlačítko má mírně posunutý okraj (padding) v prohlížeči Firefox o 2px.
  - Chybějící `aria-label` u ikony, který nemá vliv na funkčnost formuláře.

---

## ⏱️ Klasifikace priority (Priority Levels)

| Priorita | Označení v JIRA | Časový rámec opravy | Typické použití |
| :---: | :---: | :--- | :--- |
| **High / Urgent** | `High` | Okamžitě / v aktuálním sprintu / Hotfix | Blokuje release, blokuje testování, bezpečnostní riziko, kritická nákupní cesta. |
| **Medium** | `Medium` | V příštím plánovaném sprintu | Běžné chyby v produktech s existujícím workaroundem. |
| **Low** | `Low` | Až zbyde čas / Backlog | Kosmetické úpravy, drobné překlepy, edge-case situace s minimálním výskytem. |

---

## 🧩 Rozhodovací matice (Severity vs. Priority Matrix)

Kombinace Severity a Priority nemusí být vždy stejná. Níže uvedená matice pomáhá určit správnou kombinaci:

| Scénář incidentu | Severity | Priority | Příklad v projektu Demo-login |
| :--- | :---: | :---: | :--- |
| **Kritický dopad + Okamžitá oprava** | `Critical` | `High` | Únik hesel, Broken Access Control (`/courses/create` dostupné pro studenta), pád registrace. |
| **Vysoká závažnost + Nižší priorita** | `High` | `Medium` | Selhání zápisu na kurz, ale POUZE v Internet Exploreru 11 (který není oficiálně podporován). |
| **Nízká závažnost + Vysoká priorita** | `Low` | `High` | Hrubý gramatický překlep v hlavním logu společnosti na domovské stránce (`testovani.kitner.cz`). Funkčně ničemu nevadí, ale poškozuje značku. |
| **Běžná funkční vada** | `Medium` | `Medium` | Nefunguje validace kontrolního součtu IČO (modulo 11) a formulář propustí neplatné IČO. |
| **Kosmetická vada** | `Low` | `Low` | Mírný vizuální posun ikony lupy ve vyhledávacím poli v rozlišení 1024x768. |

---

## 🛡️ Bezpečnostní mapování (OWASP Top 10)

Pokud incident souvisí s bezpečností, uveďte v poli **Bezpečnostní a byznysový dopad** konkrétní kategorii OWASP:

* **A01:2021 – Broken Access Control:** Přístup uživatele k URL, tlačítkům či API jiné role bez ověření (VŽDY `Severity: Critical / High`).
* **A02:2021 – Cryptographic Failures:** Přenos citlivých dat (hesla, tokeny) nešifrovaně v URL parametrech (VŽDY `Severity: High`).
* **A03:2021 – Injection:** Možnost vložit XSS do názvu kurzu nebo komentáře (`Severity: High`).
* **A07:2021 – Identification & Auth Failures:** Chybějící ochrana proti brutální síle, nezneplatnění sezení po odhlášení (`Severity: High / Critical`).

# Šablona pro Test Casy (story-to-testcases)

Při návrhu test casů v Kroku 2 použijte následující strukturu. Každý test case musí mít unikátní ID, přímou vazbu na akceptační kritérium (AK), předpoklady, testovací data, číslované kroky a očekávaný výsledek.

---

### Přehledová tabulka scénářů

| ID testu | Akceptační kritérium | Název testovacího případu | Typ testu | Priorita |
| :--- | :--- | :--- | :--- | :--- |
| `TC-01-MODUL` | AK-1 | Stručný a výstižný název scénáře | Happy Path / Pozitivní | P1 (Kritická) |
| `TC-02-MODUL` | AK-1 | Test chování při neplatném vstupu | Negativní | P2 (Vysoká) |
| `TC-03-MODUL` | AK-2 | Test limitní / hraniční hodnoty | Hraniční (BVA) | P2 (Vysoká) |

---

### Detailní specifikace testovacích případů

#### `TC-01-MODUL`: Název testovacího případu
* **Pokrytí:** US-xx (AK-1)
* **Typ testu:** Happy Path / Pozitivní
* **Priorita:** P1
* **Předpoklady:** 
  - Uživatel je na konkrétní stránce (např. `/registrace`).
  - Systém je v počátečním stavu (např. uživatel není přihlášen).
* **Testovací data:** 
  - Jméno: `Jan Novák`
  - E-mail: `jan.novak@example.com` (unikátní)
* **Kroky:**
  1. Otevřete stránku aplikace.
  2. Zadejte do formuláře testovací data.
  3. Klikněte na potvrzovací tlačítko.
* **Očekávaný výsledek:**
  - Akce se úspěšně dokončí.
  - Systém přesměruje uživatele na cílovou stránku.
  - Zobrazí se potvrzovací hláška nebo nový stav entity.

---

#### `TC-02-MODUL`: Název negativního testu
* **Pokrytí:** US-xx (AK-1)
* **Typ testu:** Negativní / Validační
* **Priorita:** P2
* **Předpoklady:**
  - Uživatel je na formuláři.
* **Testovací data:**
  - E-mail: `neplatny-format`
* **Kroky:**
  1. Vyplňte formulář s neplatným e-mailem.
  2. Odešlete formulář.
* **Očekávaný výsledek:**
  - Formulář se neodešle.
  - Zobrazí se validační chybová hláška specifikující chybný e-mail.

# 📐 Techniky návrhu testů a 4kvadrantová analýza (Test Design Guide)

Tento dokument slouží jako metodická příručka pro QA inženýry a AI asistenta při návrhu nových testovacích případů (Test Cases) na portálu `testovani.kitner.cz`.

---

## 🧭 Metodika: Povinná 4kvadrantová analýza scénářů

Pro každý nový byznysový požadavek (User Story v `docs/požadavky_ust_podle_src.md`) nebo novou funkcionalitu je povinné analyzovat a navrhnout scénáře ve **4 klíčových kvadrantech**:

```
                       +-----------------------------------+-----------------------------------+
                       |    KVADRANT 1: HAPPY PATH / SMOKE |     KVADRANT 2: NEGATIVNÍ TOKY    |
                       |    🔴 Priorita: P1 (Kritické)     |     🟡 Priorita: P2 (Regresní)    |
                       |    • Základní úspěšný průchod     |     • Chybné/neplatné vstupy      |
                       |    • Standardní byznysový tok     |     • Duplicitní záznamy          |
                       |    • Primární cíl uživatele       |     • Odmítnutí neplatných stavů  |
                       +-----------------------------------+-----------------------------------+
                       |    KVADRANT 3: HRANIČNÍ A BVA/EP  |     KVADRANT 4: BEZPEČNOST & RBAC |
                       |    🟢 Priorita: P2 / P3           |     🔴 Priorita: P1 / P2          |
                       |    • Ekvivalenční třídy (EP)      |     • Matice oprávnění (RBAC)     |
                       |    • Hraniční hodnoty (BVA)       |     • Ochrana tras a odhlášení    |
                       |    • Prázdné a mezní formáty      |     • CSRF a ochrana sezení       |
                       +-----------------------------------+-----------------------------------+
```

---

## 🔍 Detail jednotlivých kvadrantů s příklady z projektu

### 1. Kvadrant: Happy Path / Smoke (Priorita P1)
* **Cíl:** Ověřit, že základní byznysová hodnota funguje bez chyb.
* **Typický rozsah:** 1–2 testy na User Story.
* **Příklad:**
  * `TC-01-AUTH`: Úspěšná registrace zákaznického účtu.
  * `TC-06-AUTH`: Úspěšné přihlášení uživatele s platnými údaji.
  * `TC-27-ENR`: Úspěšný zápis na kurz s platným telefonem a platným IČO.
* **Požadavek na automatizaci:** Marker `@pytest.mark.smoke`.

### 2. Kvadrant: Negativní a alternativní toky (Priorita P2)
* **Cíl:** Ověřit, že systém korektně zachytí uživatelskou chybu, nezhroutí se a poskytne srozumitelnou zpětnou vazbu.
* **Typický rozsah:** 2–3 testy na User Story.
* **Příklad:**
  * `TC-02-AUTH`: Registrace s již existujícím e-mailem.
  * `TC-07-AUTH`: Přihlášení s neplatným heslem / neexistujícím e-mailem.
  * `TC-42-PRF`: Pokus o změnu e-mailu na již obsazenou adresu.
* **Požadavek na automatizaci:** Marker `@pytest.mark.regression`.

### 3. Kvadrant: Validační a hraniční scénáře (BVA + Ekvivalenční třídy) (Priorita P2/P3)
* **Cíl:** Prověřit hrany povolených intervalů, formáty a speciální znaky.

#### Aplikace na specifická doménová pravidla projektu:
1. **Telefonní číslo (min. 9 číslic):**
   * *Platná ekvivalence:* 9 číslic (`777123456`), s mezinárodní předvolbou (`+420 777 123 456`), s mezerami (`777 123 456`).
   * *Neplatná ekvivalence:* 8 číslic (hrana $-1$), písmena, speciální znaky, prázdný řetězec.
2. **IČO (8 číslic s kontrolním součtem modulo 11):**
   * *Platná ekvivalence:* 8místné IČO s platným kontrolním váženým součtem (`generate_valid_ico()`).
   * *Neplatná ekvivalence:* 7 číslic, 9 číslic, neplatný modulo 11 součet (`generate_invalid_ico()`).
   * *Hrana:* Vynechání pole (IČO je nepovinné).
3. **Kapacita a termíny kurzů:**
   * *Platná ekvivalence:* Kapacita $> 0$.
   * *Hraniční hodnota:* Přesně 1 zbývající místo vs. 0 zbývajících míst (tlačítko zápisu zmizí a objeví se štítek „Obsazeno“).
4. **Poměr stran obrázků (16:9):**
   * *Platná ekvivalence:* Poměr stran 16:9 (např. 1920×1080).
   * *Neplatná ekvivalence:* Čtvercový obrázek 1:1, vertikální obrázek 9:16.

### 4. Kvadrant: Bezpečnost a RBAC (Role-Based Access Control) (Priorita P1/P2)
* **Cíl:** Zaručit, že žádná role nemůže provádět operace vyhrazené jiné roli, a ověřit integritu sezení.

#### Matice rolí na testovani.kitner.cz:
| Trasa / Akce | Role `Guest` (Nepřihlášen) | Role `Customer` (Zákazník) | Role `Lecturer` (Lektor) |
| :--- | :---: | :---: | :---: |
| Veřejný katalog kurzů (`/kurzy`) | ✅ Povoleno | ✅ Povoleno | ✅ Povoleno |
| Detail kurzu a termíny (`/kurzy/:id`) | ✅ Povoleno | ✅ Povoleno | ✅ Povoleno |
| Přímý zápis na kurz (`/kurzy/:id/zapis`) | ❌ Přesměrování na login | ✅ Povoleno | ❌ Zakázáno / skryto |
| Moje kurzy (`/moje-kurzy`) | ❌ Přesměrování na login | ✅ Povoleno | ❌ Zakázáno |
| Profil uživatele (`/profil`) | ❌ Přesměrování na login | ✅ Povoleno | ✅ Povoleno |
| Vytvoření nového kurzu (`/lektor/novy-kurz`)| ❌ 403 / Login | ❌ 403 Forbidden | ✅ Povoleno |
| Seznam zapsaných účastníků | ❌ 403 / Login | ❌ 403 Forbidden | ✅ Povoleno |

---

## 📝 Standard zápisu Test Casu v `docs/TEST_CASES.md`

Každý nově navržený test musí striktně dodržet následující Markdown formát:

```markdown
#### `TC-xx-MODUL`: Výstižný název testovacího případu
* **Pokrytí:** US-xx
* **Předpoklady:** Přesně definovaný výchozí stav (role, přihlášení, URL).
* **Testovací data:** Konkrétní nebo generované hodnoty (jméno, platné IČO, e-mail).
* **Kroky:**
  1. První atomická akce uživatele.
  2. Druhá akce (vyplnění formuláře, kliknutí).
  3. Odeslání požadavku.
* **Očekávaný výsledek:**
  - 1. Úroveň (Routing): Přesměrování na očekávanou URL.
  - 2. Úroveň (Session): Zobrazení správných navigačních tlačítek dle role.
  - 3. Úroveň (Data State / UI): Zobrazení úspěšné hlášky nebo chybového textu.
```

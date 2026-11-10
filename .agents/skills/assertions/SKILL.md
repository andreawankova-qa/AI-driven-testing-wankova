---
name: assertions
description: >-
  POVINNĚ aktivuj tento skill VŽDY, když agent samostatně vytváří, píše, kontroluje, upravuje
  nebo refaktoruje jakékoliv automatizované testy, scénáře, Page Objecty, asserty či validace,
  a to i v případě, že uživatel tato klíčová slova v promptu výslovně neuvede (např. při obecném zadání
  'přidej test', 'oprav kód', 'ověř funkčnost', 'implementuj scénář' nebo jakékoliv práci se soubory v tests/).
  Vynucuje 3úrovňové ověřování stavu (Routing, Session, Data State / UI Feedback), striktní zákaz Python
  assert pro UI prvky ve prospěch Playwright web-first assertions (expect), zákaz time.sleep(), zákaz assertů
  v Page Objects (pages/), prevenci falešné pozitivity u negativních asercí (not_to_be_visible) a bezpečné
  ověřování chybových hlášek. Zahrnuje AST skener scan_assertions.py pro statickou analýzu s možností --fix.
---

# 🎯 Assertions – Standardy, validace a audit kontrol (Playwright & Pytest)

Tento skill představuje ucelenou metodiku pro návrh, zápis a revizi testovacích kontrol a assertů v automatizovaných testech.

> **Základní princip ověřování:**  
> *Test bez kvalitních assertů je pouhým skriptem pro klikání. Skutečnou hodnotu testu určuje schopnost spolehlivě prokázat správnost stavu aplikace bez falešně pozitivních i falešně negativních výsledků.*

---

## 🏆 5 zlatých pravidel pro asserty v projektu

1. **Web-First Assertions (`expect(...)`):**  
   Pro veškeré prvky DOMu a UI stavy se výhradně používají aserce Playwrightu s automatickým čekáním (`expect(locator).to_be_visible()`, `to_have_text()`, `to_have_value()`). Nativní Python `assert` je pro UI prvky přísně zakázán.
2. **3úrovňová validační pyramida:**  
   Při každé změně stavu (přihlášení, odhlášení, formulář, zápis na kurz) se ověřují 3 úrovně:
   - **1. Routing:** `expect(page).to_have_url(...)`
   - **2. Session State:** `expect(navbar.logout_button).to_be_visible()` (existence/zánik relace)
   - **3. Data State / UI Feedback:** `expect(section).to_contain_text(...)` / chybové hlášky
3. **Žádné aserce v Page Objects:**  
   Metody v `pages/` obsahují výhradně lokátory a atomické uživatelské akce. Aserce a validace patří striktně do testů v `tests/`.
4. **Přesnost negativních testů:**  
   Při negativním scénáři se nikdy nespokojíme s pouhým setrváním na URL. Vždy musí být ověřeno zobrazení konkrétní validační hlášky a zachování dat ve formuláři.
5. **Prevence falešné pozitivity u `not_to_be_visible()`:**  
   Absence prvku se nikdy neověřuje bezprostředně po akci bez ustálení stavu. Vždy nejprve ověřte pozitivní přechod (URL, načtení nového layoutu) nebo počkejte na síťové požadavky.

---

## 🧭 Přehled QA úrovní validace a doporučeného zápisu

Podrobný katalog a příklady najdete v [assertion_patterns.md](./references/assertion_patterns.md).

| Úroveň validace | Cíl kontroly (QA Standard) | Doporučená Playwright metoda | Příklad správného zápisu |
| :---: | :--- | :--- | :--- |
| **1. Routing** | Změna URL a navigace | `expect(page).to_have_url(...)` | `expect(page).to_have_url(courses_page.URL)` |
| **2. Session** | Autentizace a stav relace | `expect(locator).to_be_visible()` | `expect(navbar.logout_button).to_be_visible()` |
| **3. Data State** | Personalizovaná a načtená data | `expect(locator).to_contain_text(...)` | `expect(welcome).to_contain_text(user["name"])` |
| **4. Formuláře** | Vstupy, hodnoty, atributy | `expect(input).to_have_value(...)` | `expect(input).to_have_value("Jan Novák")` |
| **5. Validace chyb** | Chybové stavy a přesné hlášky | `expect(error).to_have_text(...)` | `expect(email_err).to_have_text("The email has...")` |
| **6. Ne-UI Data** | Cookies, session tokeny, JSON | Python `assert condition, "zpráva"` | `assert has_csrf, "Chybí CSRF cookie!"` |

---

## 🤝 Pravidlo transparentnosti (Human-in-the-Loop)

**Agent NESMÍ provádět automatické změny nebo refaktoring testů bez předchozího vědomí a schválení uživatelem.**

Při zjištění neshod nebo návrhu vylepšení assertů agent:
1. Zobrazí nalezený kód a **Before & After diff**:
   ```diff
   - assert login_page.email_error.is_visible()
   + expect(login_page.email_error).to_be_visible()
   ```
2. Edukativně vysvětlí důvod změny (např. auto-waiting Playwrightu vs. okamžité vyhodnocení booleanu).
3. **Vyžádá si schválení:** *„Chcete, abych tuto úpravu provedl?“* a kód změní až po výslovném potvrzení.
4. Po provedení změny **ihned autonomně spustí dotčený test** pro ověření funkčnosti:
   ```bash
   pytest tests/<cesta>/<soubor>.py -k "<nazev_testu>" -v
   ```

---

## 🚀 Rychlé operační workflow

1. **Statický audit assertů v projektu (pouze čtení):**
   ```bash
   python3 .agents/skills/assertions/scripts/scan_assertions.py tests pages
   ```
2. **Prezentace nálezů uživateli:**  
   Agent projde výstup skeneru, sestaví přehledný report dle [review_template.md](./references/review_template.md) a předloží návrhy diffů.
3. **Aplikace schválených úprav:**  
   Pro bezpečné syntaktické záměny lze použít přepínač `--fix`:
   ```bash
   python3 .agents/skills/assertions/scripts/scan_assertions.py tests pages --fix
   ```
4. **Validace chování testů:**  
   Spuštění testovací sady s detailním výpisem:
   ```bash
   pytest tests/ -v
   ```

---

## 📚 Referenční dokumentace a nástroje

* **[scan_assertions.py](./scripts/scan_assertions.py):** Spustitelný AST skener assertů pro detekci anti-patternů a bezpečné opravy `--fix`.
* **[assertion_patterns.md](./references/assertion_patterns.md):** Katalog doporučených Playwright web-first vzorů pro URL, formuláře, texty a stavy.
* **[anti_patterns.md](./references/anti_patterns.md):** Katalog zakázaných postupů se srovnáním nesprávného (BAD) a správného (GOOD) kódu.
* **[assertion_checklist.md](./references/assertion_checklist.md):** Bodový hodnotící checklist se 7 dimenzemi kvality pro review test casů.
* **[review_template.md](./references/review_template.md):** Standardizovaná šablona výstupního hodnotícího reportu z auditu testů.

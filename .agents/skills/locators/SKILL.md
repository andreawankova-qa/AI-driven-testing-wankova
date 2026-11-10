---
name: locators
description: >-
  POVINNĚ aktivuj tento skill VŽDY, když agent samostatně vytváří, píše, kontroluje, upravuje
  nebo refaktoruje Page Objecty, komponenty (pages/), automatizované testy (tests/) či lokátory a selektory,
  a to i v případě, že uživatel tato klíčová slova v promptu výslovně neuvede (např. při přidávání UI prvků,
  formulářů, tlačítek, úpravě stránek nebo při implementaci uživatelských kroků v aplikaci). Vynucuje 6stupňovou
  sestupnou prioritu (priorita #1 get_by_test_id, přístupnost role/label, stabilní ID/name, viditelný text,
  funkční CSS atributy, relativní kontext), Locator Chaining, zákaz indexů (.first/.last/.nth) a striktní
  zákaz přímých selektorů v testech (POM-First). Zahrnuje auditní skener scan_locators.py.
---

# 🎯 Locators – Standardy a audit lokátorů (Playwright & POM)

Metodika pro návrh a kontrolu lokátorů podle kurzu *Jak řídit AI automatizaci testů*.

> **Základní princip hledání prvků:**  
> *Nejdřív hledá značky pro stroje, pak zkoumá účel a název. Teprve když vše selže, orientuje se podle struktury kódu.*

---

## 🧭 Sestupná priorita hledání prvků (1–6)

Podrobný rozbor, diagram a JIRA šablonu najdete v [locator_hierarchy.md](./references/locator_hierarchy.md).

| Priorita | Úroveň lokátoru | Doporučená Playwright metoda | Poznámka / Na co dát pozor |
| :---: | :--- | :--- | :--- |
| **1.** | **Dedikované strojové atributy** | `page.get_by_test_id("...")` | VŽDY priorita #1, imunní vůči designu. |
| **2.** | **Strom přístupnosti (Role + Název)** | `get_by_role(...)`, `get_by_label(...)` | Sémantika přístupnosti pro čtečky. |
| **3.** | **Stabilní identifikátory** | `locator("#id")`, `locator('[name="..."]')` | Vyhnout se dynamickým ID (`#input_854`). |
| **4.** | **Viditelný text** | `get_by_text("...", exact=True)` | Pozor na změny copywritera a jazyky. |
| **5.** | **Funkční CSS atributy** | `locator('button[type="submit"]')` | POUZE technické vlastnosti, NIKDY styly! |
| **6.** | **Kontextové zužování (Relativní)** | `container.get_by_...` / Chaining | Od pevného bodu, NIKDY od začátku stránky. |

### 🚫 Čemu se musí AI agent absolutně vyhnout ❌
* ❌ **Absolutní cesty a pozice:** Indexy `.first`, `.last`, `.nth(i)` a absolutní XPathy (`/html/body/...`).
* ❌ **Vizuální a generované CSS třídy:** Třídy stylu (`.btn-primary`, `.text-red-500`) nebo hashe (`.css-1x84a9`).
* ❌ **Přímé lokátory v testech:** Lokátory patří do Page Objects, v `tests/` je přímé volání zakázáno.
* ❌ **Aserce v Page Objects:** Validace a `expect(...)` patří výhradně do testů.

---

## 🤝 Pravidlo transparentnosti (Human-in-the-Loop)

**Agent NESMÍ provádět automatické opravy kódu bez vědomí a schválení uživatele.**

Při zjištění neshod agent:
1. Zobrazí nalezenou chybu a **Before & After diff**:
   ```diff
   - self.email = page.locator('[data-testid="email_input"]')
   + self.email = page.get_by_test_id("email_input")
   ```
2. Edukativně vysvětlí důvod změny (odkaz na Prioritu 1–6).
3. **Vyžádá si schválení:** *„Chcete, abych tuto úpravu provedl?“* a kód změní až po potvrzení.

---

## 🚀 Rychlé operační workflow

1. **Audit lokátorů v projektu (pouze čtení):**
   ```bash
   python3 .agents/skills/locators/scripts/scan_locators.py pages tests
   ```
2. **Prezentace návrhů oprav uživateli:** Agent projde výstup skeneru, předloží diffy a vyžádá si souhlas.
3. **Provedení úprav a ověření testů:** Po potvrzení uživatelem aplikovat změny a spustit testy:
   ```bash
   pytest tests/ -v
   ```

---

## 📚 Referenční dokumentace a nástroje

* **[scan_locators.py](./scripts/scan_locators.py):** Spustitelný skener lokátorů s návrhy oprav a edukativními tipy.
* **[locator_hierarchy.md](./references/locator_hierarchy.md):** Kompletní rozbor priorit 1–6, diagram a JIRA šablona pro chybějící test-id.
* **[locator_patterns.md](./references/locator_patterns.md):** Katalog doporučených vzorů v projektu (chaining, regexy, navbar).
* **[anti_patterns.md](./references/anti_patterns.md):** Katalog zakázaných postupů se srovnáním BAD vs. GOOD kódu.

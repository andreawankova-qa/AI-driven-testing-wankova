# ✅ Kontrolní seznam autora testů (Authoring Checklist)

Tento checklist slouží jako kontrolní brána před odevzdáním nového testovacího scénáře nebo kódu do projektu.

---

## 📋 1. Analytická fáze (Návrh & Specifikace)
- [ ] Byla provedena **4kvadrantová analýza** pro danou User Story (Happy Path, Negativní, Hraniční/BVA, RBAC)?
- [ ] Bylo přiděleno správné kanonické ID ve formátu `TC-xx-MODUL` (s průběžným číslováním zjištěným přes `author_test.py next-id <MODUL>`)?
- [ ] Má test jasně definované předpoklady (role, přihlášení, stav dat)?
- [ ] Jsou testovací data specifikována dynamicky nebo s reálnými parametry (IČO, formát telefonu)?
- [ ] Jsou kroky očíslovány a atomické?
- [ ] Obsahuje očekávaný výsledek **3úrovňové ověření** (Routing + Session + Data State / Feedback)?
- [ ] Byl záznam vložen do správné sekce v `docs/TEST_CASES.md` a byl zapsán řádek do přehledové tabulky?

---

## 🧩 2. Příprava Page Objects & Helpers (POM-First)
- [ ] Existují v `pages/` všechny potřebné Page Objects a metody pro daný scénář?
- [ ] Pokud byla vytvořena nová stránka, dědí z `BasePage` a má definovanou konstantu `URL`?
- [ ] Využívají všechny lokátory výhradně `self.page.get_by_test_id("...")`?
- [ ] Jsou kontejnerové prvky řetězeny (`navbar.logout_button`) bez křehkých indexů (`.nth()`, `.first`)?
- [ ] **Jsou Page Objects 100% prosté asercí** (žádné `expect` ani `assert` uvnitř tříd v `pages/`)?
- [ ] Jsou opakované přípravné toky ($\ge 2$ kroků, např. přihlášení) zapouzdřeny v `helpers/` nebo conftest fixture namísto kopírování kroků?

---

## 💻 3. Implementace kódu v Pytestu (`tests/`)
- [ ] Je testovací třída označena doménovým markerem (`@pytest.mark.<domain>`)?
- [ ] Je metoda označena správným markerem závažnosti (`@pytest.mark.smoke` pro P1, `@pytest.mark.regression` pro P2/P3)?
- [ ] Začíná název metody konvencí `test_tc{cislo}_{modul}_{popis}`?
- [ ] Obsahuje docstring přesné ID `TC-xx-MODUL: Název testu.`?
- [ ] Je kód členěn do 3 bloků **ARRANGE**, **ACT**, **ASSERT**?
- [ ] Využívá test dynamický generátor `utils.data_generator` (žádné hardcoded e-maily ani statická IČO)?
- [ ] Jsou pro testování více variant vstupu použity parametry (`@pytest.mark.parametrize`) namísto duplikace metod?
- [ ] Jsou v testu použity výhradně web-first aserce (`expect(page)...`, `expect(locator)...`)?
- [ ] V testu není ani jednou použito `time.sleep()`?
- [ ] V testu není žádný přímý lokátor na objektu `page`?

---

## 🚀 4. Pre-Flight audit & Verifikace během běhu
- [ ] Prošel soubor pre-flight kontrolou:
  ```bash
  python3 .agents/skills/test_authoring/scripts/author_test.py pre-flight tests/<modul>/test_<soubor>.py
  ```
- [ ] Byl test úspěšně spuštěn a prošel bez chyb (PASS):
  ```bash
  pytest tests/<modul>/test_<soubor>.py -k "test_tc<cislo>" -v
  ```
- [ ] Byla zkontrolována trasovatelnost:
  ```bash
  python3 .agents/skills/traceability/scripts/scan_traceability.py --find test_tc<cislo>
  ```

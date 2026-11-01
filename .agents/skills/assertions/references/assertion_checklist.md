# ✅ Kontrolní checklist kvality assertů (7 dimenzí kvality)

Tento checklist slouží jako standard pro review testovacích scénářů, kontrolu nově psaných testů a hodnocení stávající testovací sady.

---

## 🧭 Souhrnná matice 7 dimenzí

| # | Dimenze | Klíčová otázka | Splněno? |
|---|---|---|:---:|
| **1.** | **Víceúrovňovost (Multi-Level)** | Ověřuje test stavovou změnu na úrovni Routingu, Session i Dat? | [ ] |
| **2.** | **Web-First & Odolnost** | Jsou použity výhradně aserce `expect(...)` bez `time.sleep()`? | [ ] |
| **3.** | **Separace odpovědností** | Jsou veškeré aserce pouze v `tests/` a žádné v `pages/` (POM)? | [ ] |
| **4.** | **Přesnost negativních testů** | Ověřují negativní testy konkrétní validační hlášku a blokaci? | [ ] |
| **5.** | **Prevence falešné pozitivity** | Má `not_to_be_visible()` před sebou ustálení stavu / přechod? | [ ] |
| **6.** | **Dynamická integrita dat** | Ověřují se unikátní data z generátoru namísto křehkých konstant? | [ ] |
| **7.** | **Diagnostická hodnota** | Bude z failure reportu v CI okamžitě jasné, co selhalo? | [ ] |

---

## 🔍 Detailní kritéria jednotlivých dimenzí

### Dimenze 1: Víceúrovňové ověřování (Multi-Level)
- [ ] U testů měnících stav (přihlášení, odhlášení, registrace, vytvoření kurzu) je ověřena změna URL (`expect(page).to_have_url(...)`).
- [ ] Je ověřen stav uživatelské relace (přítomnost nebo absence `logout_button` / `login_link`).
- [ ] Je ověřena odezva dat (např. uvítací hláška se jménem uživatele, přítomnost nové položky v tabulce).
- [ ] Test není „mělký“ – nespokojí se pouze s URL přesměrováním.

### Dimenze 2: Web-First Assertions & Flakiness Prevention
- [ ] Žádné volání `time.sleep()` v testech ani v pomocných funkcích.
- [ ] Žádné synchronní volání `assert locator.is_visible()`, `assert locator.is_enabled()`.
- [ ] Žádné hledání textu přes `assert "..." in page.content()`.
- [ ] Využití automatického čekání (auto-waiting) Playwrightu přes `expect(locator)...`.
- [ ] Nativní Python `assert` je použit výhradně pro ne-UI datové struktury (cookies, seznamy, JSON data).

### Dimenze 3: Separace odpovědností (POM vs. Testy)
- [ ] Třídy Page Object v `pages/` obsahují výhradně lokátory a akční metody.
- [ ] V žádné metodě Page Objectu se nevyskytuje volání `expect(...)` ani `assert`.
- [ ] Testovací metody v `tests/` realizují veškerou validační logiku.

### Dimenze 4: Přesnost negativních testů a validací
- [ ] Při nevalidním vstupu test ověřuje nejen setrvání na stránce, ale i zobrazení chybového elementu.
- [ ] Je ověřen přesný text nebo vzor chybové hlášky (`expect(error).to_have_text(...)`).
- [ ] Je ověřeno, že nedošlo k nežádoucímu odeslání dat na server ani k vytvoření entity.

### Dimenze 5: Časování a prevence falešné pozitivity
- [ ] Negativní aserce (`not_to_be_visible()`) se nevolá okamžitě po kliknutí, kdy ještě nedošlo k překreslení DOMu.
- [ ] Před kontrolou zániku prvku je nejprve ověřen pozitivní přechod (změna URL, načtení nového layoutu).
- [ ] V případě potřeby je počkáno na ustálení síťové komunikace.

### Dimenze 6: Dynamická integrita a idempotence
- [ ] Očekávané hodnoty v assertech pocházejí z generátoru testovacích dat (`utils/data_generator.py`) nebo fixtures.
- [ ] Test nespoléhá na statické hodnoty, které mohl změnit jiný paralelní běh.
- [ ] Test je plně nezávislý a opakovatelný.

### Dimenze 7: Diagnostická hodnota (Actionability)
- [ ] Lokátory v assertech jsou jednoznačné a čitelné (přednostně `get_by_test_id`).
- [ ] Při selhání je z názvu testu a aserce jednoznačně patrné, která byznysová podmínka nebyla splněna.
- [ ] Není použit obecný `assert True` ani vágní matcher `to_contain_text("")`.

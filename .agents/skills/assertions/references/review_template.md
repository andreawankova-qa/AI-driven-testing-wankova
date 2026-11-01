# 📊 Šablona reportu review kvality assertů (Assertion Review Report)

Tuto šablonu používá AI agent při provádění auditu a prezentaci výsledků kontroly testovacích sad uživateli.

---

# Audit kvality assertů – [Název modulu / souboru]

**Datum kontroly:** YYYY-MM-DD  
**Analyzovaný soubor / složka:** `tests/...`  
**Celkový počet testovacích metod:** X  
**Stav testovací sady:** ✅ VYHOVUJE / ⚠️ VYŽADUJE ÚPRAVU / ❌ NEVYHOVUJE  

---

## 🧭 Scorecard kvality (7 dimenzí)

| Dimenze kvality | Stav | Hodnocení & Komentář |
|---|:---:|---|
| **1. Víceúrovňovost (Multi-Level)** | ✅ / ⚠️ / ❌ | [Komentář k pokrytí Routing, Session a Data State] |
| **2. Web-First & Odolnost** | ✅ / ⚠️ / ❌ | [Výskyt time.sleep, synchronních assertů na DOM] |
| **3. Separace POM vs Testy** | ✅ / ⚠️ / ❌ | [Kontrola nepřítomnosti assertů v Page Objects] |
| **4. Negativní testy & Validace** | ✅ / ⚠️ / ❌ | [Ověření přesných chybových hlášek vs slepé testy] |
| **5. Prevence falešné pozitivity** | ✅ / ⚠️ / ❌ | [Časování u not_to_be_visible] |
| **6. Dynamická data** | ✅ / ⚠️ / ❌ | [Použití generátoru dat a idempotence] |
| **7. Diagnostická hodnota** | ✅ / ⚠️ / ❌ | [Čitelnost a srozumitelnost pádů v CI] |

---

## 🔍 Detailní nálezy a zjištěné neshody

### 🔴 Kritické nálezy (Vysoké riziko flakiness / falešné pozitivity)
* **[ID-01] Název chyby / Anti-pattern**
  * **Soubor & řádek:** `tests/auth/test_login.py:45`
  * **Popis problému:** [Vysvětlení, proč je kód problematický]
  * **Doporučená náprava:**

```diff
- assert login_page.email_error.is_visible()
+ expect(login_page.email_error).to_be_visible()
```

---

### 🟡 Doporučení ke zlepšení (Střední závažnost / Mělké asserty)
* **[ID-02] Chybějící ověření stavu sezení**
  * **Soubor & řádek:** `tests/courses/test_courses.py:78`
  * **Popis problému:** Test ověřuje pouze URL, chybí ověření stavu přihlášeného uživatele v navigaci.
  * **Doporučená náprava:**

```diff
  expect(page).to_have_url(courses_page.URL)
+ expect(courses_page.navbar.logout_button).to_be_visible()
```

---

## 🎯 Akční plán a další kroky
1. Schválit navržené změny (využití pravidla Human-in-the-Loop).
2. Spustit automatickou opravu přes `python3 .agents/skills/assertions/scripts/scan_assertions.py tests/ --fix` (nebo aplikovat schválené diffy).
3. Ověřit stabilitu testů příkazem:
   ```bash
   pytest tests/<soubor>.py -v
   ```

# 📘 Doporučené vzory assertů (Playwright Web-First Assertions)

Tato referenční příručka obsahuje oficiální standardy pro zápis validací a assertů v projektu.

---

## 🎯 Proč Web-First Assertions?

Tradiční testovací nástroje a nativní Python konstrukce `assert locator.is_visible()` vyhodnocují stav prvku v jediném okamžiku. V moderních webových aplikacích (SPA, dynamický rendering, AJAX) dochází k asynchronnímu načítání, což u okamžitých kontrol způsobuje falešná selhání (**flakiness**).

**Playwright Web-First Assertions (`expect(...)`)** řeší tento problém vestavěným retry mechanismem:
- **Automatické čekání (Auto-waiting):** Playwright opakovaně kontroluje podmínku až do splnění nebo vypršení timeoutu (výchozí 5 000 ms).
- **Informativní chybové zprávy:** Při selhání vypíše přesný stav DOMu, očekávanou vs. skutečnou hodnotu a časový průběh (call log).
- **Odolnost vůči časování:** Není nutné používat `time.sleep()` ani umělé čekání.

---

## 🏛️ 3úrovňová validační pyramida (Multi-Level Assertions)

Při každé operaci, která mění stav aplikace (přihlášení, odhlášení, odeslání formuláře, zápis na kurz), se striktně uplatňuje víceúrovňové ověřování:

```text
       ▲
      / \     3. DATA STATE / UI FEEDBACK (Personalizovaná data, texty zpráv, hodnoty)
     /   \    2. SESSION STATE (logout_button / login_link – důkaz autorizační relace)
    /     \   1. ROUTING (to_have_url – směrování po dokončení akce)
   /_______\
```

### Příklad kompletní 3úrovňové validace:
```python
# 1. Úroveň: Směrování (Routing)
expect(page).to_have_url(courses_page.URL)

# 2. Úroveň: Stav sezení (Session)
expect(courses_page.navbar.logout_button).to_be_visible()

# 3. Úroveň: Kontextová data (Data State)
expect(home_page.welcome_section).to_contain_text(f"Vítej uživateli {test_user['name']}!")
```

---

## 📋 Katalog doporučených Playwright vzorů

### 1. Směrování a URL
```python
# Přesná shoda URL
expect(page).to_have_url("http://testovani.kitner.cz/courses")

# Shoda s regulárním výrazem (pro dynamická ID v URL)
import re
expect(page).to_have_url(re.compile(r"/courses/\d+"))

# Titulek stránky
expect(page).to_have_title("Kitner.cz - Vzdělávací portál")
```

### 2. Viditelnost prvků
```python
# Prvek musí být viditelný pro uživatele
expect(login_page.login_button).to_be_visible()

# Prvek nesmí být viditelný (skrytý nebo nepřítomný v DOMu)
# DŮLEŽITÉ: Používejte až po ustálení stavu stránky!
expect(login_page.login_link).not_to_be_visible()
```

### 3. Formulářová pole a vstupy
```python
# Kontrola předvyplněné nebo zadané hodnoty
expect(profile_page.name_input).to_have_value("Jan Novák")

# Prázdné pole
expect(enrollment_page.ico_input).to_be_empty()

# Typ vstupu (např. maskování hesla)
expect(register_page.password_input).to_have_attribute("type", "password")

# Hodnota obecného HTML atributu
expect(login_page.email_input).to_have_attribute("required", "")
```

### 4. Texty a validační hlášky
```python
# Přesná shoda celého textu prvku
expect(login_page.heading).to_have_text("Přihlášení")

# Částečná shoda textu (obsahuje podřetězec)
expect(home_page.welcome_section).to_contain_text("Vítej uživateli")

# Case-insensitive shoda nebo regulární výraz
expect(course_card.price).to_have_text(re.compile(r"\d+\s*Kč", re.IGNORECASE))
```

### 5. Stavy tlačítek a ovládacích prvků
```python
# Tlačítko je aktivní a klikatelné
expect(enrollment_page.submit_button).to_be_enabled()

# Tlačítko je deaktivované (např. před vyplněním povinných polí)
expect(enrollment_page.submit_button).to_be_disabled()

# Zaškrtávací pole je vybráno
expect(register_page.terms_checkbox).to_be_checked()
```

### 6. Seznamy a kolekce prvků
```python
# Přesný počet položek v seznamu
expect(courses_page.course_cards).to_have_count(8)

# Ověření, že seznam není prázdný (nativní assertion countu pro nekonečné streamy / kolekce)
assert courses_page.course_cards.count() > 0

# Ověření atributu konkrétního prvku v seznamu
first_card = courses_page.course_cards.first
expect(first_card.get_by_test_id("course_name")).to_be_visible()
```

### 7. Pokročilé techniky (Advanced Assertions)

#### A. Vlastní diagnostické zprávy (Custom Failure Messages)
Do `expect` lze jako druhý parametr předat text, který se zobrazí v CI/CD reportu při selhání:
```python
expect(
    login_page.heading,
    "Chyba navigace: Po kliknutí na odkaz se neotevřel přihlašovací formulář!"
).to_be_visible()
```

#### B. Měkké aserce (Soft Assertions – `expect.soft`)
Umožňují zkontrolovat více atributů jedné komponenty (např. karty kurzu nebo detailu profilu) bez předčasného ukončení testu při první chybě:
```python
# Pokud selže název, test nepadne hned, ale zkontroluje i cenu a kapacitu:
expect.soft(card.get_by_test_id("course_name")).to_have_text("Playwright")
expect.soft(card.get_by_test_id("course_price")).to_have_text("14 900 Kč")
expect.soft(card.get_by_test_id("course_capacity")).to_have_text("15")
```

#### C. Síťové a stavové aserce (Network & API Response)
Při odesílání formulářů ověřuje správnou odpověď backendového API bez zkoumání DOMu:
```python
# Ověření, že požadavek vrátil HTTP 200/302 (OK) a nikoliv 500 (Server Error)
with page.expect_response("**/api/**") as response_info:
    enrollment_page.submit()
response = response_info.value
expect(response).to_be_ok()
```

---

## 🔒 Výjimky: Kdy je povolen nativní Python `assert`

Nativní Python `assert` je přísně zakázán pro interakci s DOMem a UI prvky. Je však **jediným správným nástrojem** pro ověřování čistě pythonovských datových struktur:

1. **Bezpečnostní cookies v kontextu prohlížeče:**
   ```python
   cookies = context.cookies()
   has_csrf = any("XSRF" in c["name"] for c in cookies)
   assert has_csrf, "CSRF cookie XSRF-TOKEN nebyla v browser kontextu nalezena."
   ```

2. **Porovnání hodnot před a po (např. session regeneration):**
   ```python
   assert session_after != session_before, "Session ID nebylo po přihlášení regenerováno!"
   ```

3. **Integrita externích datových souborů a JSON struktur:**
   ```python
   invalid_emails = load_json_data("invalid_emails.json")
   assert len(invalid_emails) >= 5, "Testovací datová sada neobsahuje dostatek vzorků."
   ```

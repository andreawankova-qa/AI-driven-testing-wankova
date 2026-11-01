# 🚫 Anti-patterny v assertech (Katalog chyb BAD vs. GOOD)

Tento přehled shrnuje nejčastější chyby, nešvary a zakázané praktiky při psaní testovacích kontrol s ukázkami nesprávného a opraveného kódu.

---

### 1. The "Sleep-and-Pray" Pattern 😴
*Umělé čekání na vykreslení prvku namísto automatického retry mechanismu.*

❌ **ŠPATNĚ (BAD):**
```python
import time

login_page.submit()
time.sleep(3)  # Flaky a pomalé! Může projít lokálně, ale selhat v CI/CD
assert page.url == "http://testovani.kitner.cz/courses"
```

✅ **SPRÁVNĚ (GOOD):**
```python
login_page.submit()
# Playwright automaticky čeká až do splnění podmínky
expect(page).to_have_url(courses_page.URL)
expect(courses_page.navbar.logout_button).to_be_visible()
```

---

### 2. The Flaky Boolean Assertion ⚠️
*Použití nativního pythonovského `assert` s boolean metodami Playwrightu namísto web-first aserce.*

❌ **ŠPATNĚ (BAD):**
```python
# is_visible() se vyhodnotí okamžitě bez čekání na dokončení asynchronního dotazu!
assert login_page.email_error.is_visible()
assert login_page.name_input.input_value() == "Jan Novák"
```

✅ **SPRÁVNĚ (GOOD):**
```python
# expect() opakovaně zkouší stav prvku s auto-waiting
expect(login_page.email_error).to_be_visible()
expect(login_page.name_input).to_have_value("Jan Novák")
```

---

### 3. The Content Scraping Pattern 📄
*Hledání textu v surovém HTML kódu celé stránky (`page.content()`).*

❌ **ŠPATNĚ (BAD):**
```python
# Projde i když je text skrytý v komentáři, v patičce nebo jinde v HTML
assert "Chybný email" in page.content()
```

✅ **SPRÁVNĚ (GOOD):**
```python
# Kontroluje se konkrétní cílový prvek v DOMu
expect(login_page.email_error).to_have_text("The email has already been taken.")
```

---

### 4. The Shallow Assertion (Mělký assert) 🕳️
*Test ověřuje pouze změnu URL, ale neověřuje, zda se data načetla a uživatel je skutečně autentizován.*

❌ **ŠPATNĚ (BAD):**
```python
login_page.login(email, password)
# Pouhé přesměrování negarantuje platnou session ani načtení dat
expect(page).to_have_url(courses_page.URL)
```

✅ **SPRÁVNĚ (GOOD):**
```python
login_page.login(email, password)
# 3úrovňová validace: Routing + Session + Data
expect(page).to_have_url(courses_page.URL)
expect(courses_page.navbar.logout_button).to_be_visible()
expect(courses_page.courses_header).to_be_visible()
```

---

### 5. Hidden Asserts in Page Objects 🎭
*Umísťování validací a asercí do metod Page Object tříd namísto do testů.*

❌ **ŠPATNĚ (BAD):**
```python
# pages/login_page.py
class LoginPage:
    def verify_login_successful(self):
        # Aserce v POM porušují Single Responsibility Principle!
        expect(self.page).to_have_url("/courses")
```

✅ **SPRÁVNĚ (GOOD):**
```python
# pages/login_page.py obsahuje POUZE lokátory a atomické akce
class LoginPage:
    def submit_login(self, email, password):
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

# tests/auth/test_login.py provádí veškeré aserce
def test_successful_login(page):
    ...
    login_page.submit_login(email, password)
    expect(page).to_have_url(courses_page.URL)
```

---

### 6. The Blind Negative Test (Slepý negativní test) 🙈
*Při chybě se pouze ověří, že uživatel zůstal na stránce, ale neověří se chybová hláška ani zablokování odeslání.*

❌ **ŠPATNĚ (BAD):**
```python
enrollment_page.fill_form(phone="123")  # Neplatný telefon
enrollment_page.submit()
# Pouhá kontrola URL nestačí – formulář mohl tiše selhat nebo zamrznout
expect(page).to_have_url(enrollment_page.URL)
```

✅ **SPRÁVNĚ (GOOD):**
```python
enrollment_page.fill_form(phone="123")
enrollment_page.submit()
# Ověření setrvání na stránce + zobrazení specifické validační chyby
expect(page).to_have_url(enrollment_page.URL)
expect(enrollment_page.phone_error).to_be_visible()
expect(enrollment_page.phone_error).to_have_text("Telefonní číslo musí mít alespoň 9 číslic.")
```

---

### 7. Premature Negative Assertion (Falešně pozitivní negativní kontrola) 👻
*Volání `not_to_be_visible()` bezprostředně po akci bez předchozího ustálení stavu.*

❌ **ŠPATNĚ (BAD):**
```python
home_page.navbar.logout_button.click()
# Okamžitě po kliknutí může být logout_button ještě na 20 ms v DOMu,
# nebo naopak stránka ještě nezačala zpracovávat odhlášení
expect(courses_page.logout_button).not_to_be_visible()
```

✅ **SPRÁVNĚ (GOOD):**
```python
home_page.navbar.logout_button.click()
# Nejprve ověříme pozitivní přechod / přesměrování a layout
expect(page).to_have_url(login_page.URL)
expect(login_page.login_button).to_be_visible()
# Teprve poté ověříme zánik session prvku
expect(navbar.logout_button).not_to_be_visible()
```

---

### 8. The Tautological / Vacuous Assert 🤡
*Ověřování prázdného řetězce nebo porovnávání proměnné se sebou samou.*

❌ **ŠPATNĚ (BAD):**
```python
# Prázdný text obsahuje jakýkoliv prvek – projde vždy!
expect(course_card.title).to_contain_text("")

# Testuje pouze pythonovskou proměnnou, nikoliv UI
phone = "777123456"
assert phone == "777123456"
```

✅ **SPRÁVNĚ (GOOD):**
```python
# Kontrola skutečného, neprázdného obsahu v DOMu
expect(course_card.title).not_to_be_empty()
expect(course_card.title).to_have_text("Playwright Automatizace")

# Ověření, že se hodnota propsala do formulářového pole v DOMu
expect(enrollment_page.phone_input).to_have_value(phone)
```

# 🚫 Katalog anti-patternů lokátorů (Anti-Patterns Catalog)

Tento přehled shrnuje zakázané přístupy a anti-patterny při práci s lokátory v tomto projektu spolu s ukázkami správného řešení (**BAD** vs. **GOOD**). Vychází ze standardů a zákazů kurzu *Jak řídit AI automatizaci testů*.

---

### 1. The CSS Attr Selector (Atributový zápis místo nativní metody)

* **Problém:** Použití obecného `page.locator('[data-testid="..."]')` je zbytečně upovídané, náchylné k překlepům a ignoruje optimalizace nativní metody Playwrightu.
* ❌ **ŠPATNĚ (BAD):**
  ```python
  self.email_input = page.locator('[data-testid="email_input"]')
  self.login_button = page.locator("button[data-testid='login_button']")
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  self.email_input = page.get_by_test_id("email_input")
  self.login_button = page.get_by_test_id("login_button")
  ```

---

### 2. The Positional Gamble (Indexy `.first`, `.last`, `.nth()`)

* **Problém:** Navádění typu *„třetí prvek v pátém kontejneru“*. Pořadí prvků v DOMu se změní při dynamickém načtení dat, redesignu nebo přidání notifikační lišty.
* ❌ **ŠPATNĚ (BAD):**
  ```python
  # Spoléhání se na to, že navigační odkaz je vždy první v DOMu
  self.login_link = page.get_by_test_id("login_link").first
  
  # Spoléhání se na to, že odkaz pod formulářem je poslední
  self.register_login_link = page.get_by_test_id("login_link").last
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  # Řetězení z rodičovského kontejneru (Locator Chaining)
  self.login_link = page.get_by_test_id("navigation").get_by_test_id("login_link")
  self.register_login_link = page.get_by_test_id("register_section").get_by_test_id("login_link")
  ```

---

### 3. The Dynamic ID Trap (Dynamicky generovaná ID)

* **Problém:** Systémy jako React, Angular nebo Vue často generují náhodná nebo sekvenční ID (např. `input_854`, `field-1234`), která se mění s každým obnovením stránky či sestavením (buildem).
* ❌ **ŠPATNĚ (BAD):**
  ```python
  # ID vygenerované frameworkem při renderu komponenty
  self.phone_input = page.locator("#input_854")
  self.dropdown = page.locator("#react-select-3-input")
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  # Pokud existuje data-testid:
  self.phone_input = page.get_by_test_id("phone_input")
  # Pokud ne: sémantický label nebo stabilní name atribut:
  self.phone_input = page.get_by_label("Telefonní číslo")
  # Nebo stabilní statický atribut:
  self.dropdown = page.locator('select[name="category"]')
  ```

---

### 4. The Visual & Generated CSS Trap (Třídy vzhledu a generované hash třídy)

* **Problém:** Použití CSS tříd definujících vzhled (barvy, okraje, mřížka) nebo tříd generovaných bundlerem (např. `.css-1x84a9`). Při redesignu test okamžitě selže.
* ❌ **ŠPATNĚ (BAD):**
  ```python
  # Závislost na vzhledu (Tailwind / Bootstrap)
  self.submit_btn = page.locator(".btn.btn-primary.mt-4.rounded-lg")
  # Generované hash třídy
  self.card = page.locator("div.css-1x84a9")
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  # Hledání výhradně podle funkčního technického atributu (Priorita 5):
  self.submit_btn = page.locator('button[type="submit"]')
  # Nebo podle stromu přístupnosti:
  self.submit_btn = page.get_by_role("button", name="Uložit")
  ```

---

### 5. Absolute XPath vs. Contextual Scoping (Absolutní cesty)

* **Problém:** Absolutní XPath (`/html/body/...`) začíná od kořene stránky. Sebemenší změna obalového `<div>` rozbije celý selektor.
* ❌ **ŠPATNĚ (BAD):**
  ```python
  self.delete_btn = page.locator("/html/body/div[2]/div/table/tbody/tr[3]/td[5]/button")
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  # Relativní kontextové hledání od nalezeného pevného bodu (Priorita 6):
  product_row = page.locator("tr").filter(has_text="Kurz Python")
  self.delete_btn = product_row.get_by_role("button", name="Smazat")
  ```

---

### 6. The Leaky Abstraction (Přímé lokátory v testech)

* **Problém:** Přímé používání `page.locator(...)` nebo `page.get_by_test_id(...)` v těle testu (`tests/`) porušuje standard Page Object Model (vrstva 3 vs. vrstva 6). Při změně selektoru je nutné upravovat desítky testů.
* ❌ **ŠPATNĚ (BAD):**
  ```python
  def test_login_success(page: Page):
      page.goto("http://testovani.kitner.cz/login")
      page.get_by_test_id("email_input").fill("user@example.com")
      page.get_by_test_id("login_button").click()
      expect(page.get_by_test_id("home_section")).to_be_visible()
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  def test_login_success(login_page: LoginPage, home_page: HomePage):
      login_page.open().login("user@example.com", "password")
      expect(home_page.welcome_section).to_be_visible()
  ```

---

### 7. Hidden Assertions in Page Objects (Aserce uvnitř POM)

* **Problém:** Vkládání `assert` nebo `expect(...)` do Page Object tříd porušuje Single Responsibility Principle. Page Object má poskytovat stav a akce, validace patří výhradně do testu.
* ❌ **ŠPATNĚ (BAD):**
  ```python
  class LoginPage(BasePage):
      def verify_email_error(self):
          assert self.email_error.is_visible()  # CHYBA: Aserce v POM!
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  # V Page Object: pouze vystavení lokátoru
  class LoginPage(BasePage):
      def __init__(self, page: Page):
          self.email_error = page.get_by_test_id("email_input_errors")

  # V testu: explicitní web-first aserce
  def test_invalid_email(login_page: LoginPage):
      login_page.login("invalid", "heslo")
      expect(login_page.email_error).to_be_visible()
  ```

---

### 8. Overly Loose Text Matcher (Příliš volný textový selektor)

* **Problém:** `page.get_by_text("Přihlásit")` bez upřesnění může zachytit nadpis, popisek i tlačítko na různých místech stránky.
* ❌ **ŠPATNĚ (BAD):**
  ```python
  self.button = page.get_by_text("Přihlásit")
  ```
* ✅ **SPRÁVNĚ (GOOD):**
  ```python
  # Pokud existuje testid:
  self.button = page.get_by_test_id("login_button")
  # Pokud je nutný textový fallback: zpřesnit na roli a kontejner:
  self.button = page.get_by_test_id("login_form").get_by_role("button", name="Přihlásit")
  ```
